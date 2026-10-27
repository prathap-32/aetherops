# services/project_and_environment_management/app/tenant_context.py
import uuid
import re
import logging
from typing import Optional, Dict, Any, List

from fastapi import Request, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth import get_current_admin
from app.models import Tenant, TenantMembership

logger = logging.getLogger("project-manager-tenant-context")

TENANT_ROLES = {"OWNER", "ADMIN", "MEMBER", "VIEWER"}
PLATFORM_SUPER_ADMIN_ROLES = {"SUPER_ADMIN"}


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = re.sub(r"^-+|-+$", "", text)
    return text or "workspace"


class TenantContext:
    """
    Encapsulates the tenant and authorization context for the current request.
    Enforces deny-by-default role-based access control.
    """
    def __init__(
        self,
        tenant: Tenant,
        membership: Optional[TenantMembership],
        user: Dict[str, Any],
        is_platform_admin: bool = False,
    ):
        self.tenant = tenant
        self.membership = membership
        self.user = user
        self.is_platform_admin = is_platform_admin

    @property
    def role(self) -> str:
        if self.is_platform_admin and not self.membership:
            return "SUPER_ADMIN"
        return self.membership.role if self.membership else "VIEWER"

    def require_role(self, *allowed_roles: str) -> None:
        """
        Deny-by-default role validation.
        Allows platform super admin to bypass tenant-level role restrictions for platform ops/auditing.
        """
        if self.is_platform_admin and self.user.get("role") in PLATFORM_SUPER_ADMIN_ROLES:
            return

        if not self.membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: active tenant membership required.",
            )

        if self.membership.status != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: membership status is '{self.membership.status}'.",
            )

        normalized_allowed = {r.strip().upper() for r in allowed_roles}
        if self.membership.role.upper() not in normalized_allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Access denied: action requires one of {sorted(normalized_allowed)}. "
                    f"Current tenant role is '{self.membership.role}'."
                ),
            )


async def create_personal_workspace_for_user(
    db: AsyncSession,
    user_uuid: str,
    username: str,
    tenant_id_override: Optional[str] = None,
) -> Tenant:
    """
    Create or retrieve a default personal workspace for a user with TENANT_OWNER membership.
    Safe against concurrent execution and retries via deterministic slug and existing unique constraint.
    """
    clean_name = username.strip()
    user_identifier = user_uuid or clean_name
    deterministic_slug = f"personal-{slugify(clean_name)}-{user_identifier[:8].lower()}"

    # 1. Check if user already has an active personal workspace
    existing_query = (
        select(Tenant)
        .join(TenantMembership, Tenant.id == TenantMembership.tenant_id)
        .where(
            (TenantMembership.user_id == clean_name)
            | (Tenant.slug.like(f"personal-{slugify(clean_name)}%")),
            Tenant.tenant_type == "PERSONAL",
            TenantMembership.role == "OWNER",
        )
    )
    res = await db.execute(existing_query)
    existing_tenant = res.scalars().first()
    if existing_tenant:
        return existing_tenant

    # 2. Concurrency-safe creation using deterministic slug
    try:
        tenant_id = tenant_id_override or str(uuid.uuid4())
        tenant = Tenant(
            id=tenant_id,
            name=f"{clean_name}'s Workspace",
            slug=deterministic_slug,
            tenant_type="PERSONAL",
            status="ACTIVE",
        )
        db.add(tenant)
        await db.flush()

        membership = TenantMembership(
            id=str(uuid.uuid4()),
            tenant_id=tenant.id,
            user_id=user_identifier,
            role="OWNER",
            status="ACTIVE",
        )
        db.add(membership)
        await db.commit()
        await db.refresh(tenant)
        logger.info(f"Provisioned personal workspace '{tenant.name}' ({tenant.id}) for user '{clean_name}'")
        return tenant
    except Exception:
        await db.rollback()
        # In case of concurrency race, retrieve winning tenant with this slug
        res = await db.execute(select(Tenant).where(Tenant.slug == deterministic_slug))
        winning = res.scalar_one_or_none()
        if winning:
            return winning
        raise


async def get_tenant_context(
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Dict[str, Any] = Depends(get_current_admin),
) -> TenantContext:
    """
    Extracts tenant context from X-Tenant-ID header or query param.
    If omitted, resolves to the authenticated user's personal workspace.
    Verifies membership and role; clients cannot supply unverified tenant IDs.
    """
    user_name = admin.get("username", "")
    user_uuid = admin.get("uuid") or user_name
    is_platform_super_admin = admin.get("role") in PLATFORM_SUPER_ADMIN_ROLES

    path_tenant_id = None
    if "/api/v1/tenants/" in request.url.path:
        parts = request.url.path.split("/api/v1/tenants/", 1)[1].split("/")
        if parts and parts[0] and parts[0] not in ("current",):
            path_tenant_id = parts[0]

    tenant_id_header = (
        request.headers.get("X-Tenant-ID")
        or request.query_params.get("tenant_id")
        or request.path_params.get("tenant_id")
        or path_tenant_id
    )
    if tenant_id_header:
        tenant_id_header = tenant_id_header.strip()

    if tenant_id_header:
        # Client specified a tenant boundary
        res = await db.execute(
            select(Tenant).where(
                (Tenant.id == tenant_id_header) | (Tenant.slug == tenant_id_header)
            )
        )
        tenant = res.scalar_one_or_none()
        if not tenant:
            # Lazily provision personal workspace for authenticated user if matching token tenant
            try:
                tenant = await create_personal_workspace_for_user(
                    db, user_uuid, user_name, tenant_id_override=tenant_id_header
                )
            except Exception:
                pass

        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tenant '{tenant_id_header}' not found.",
            )

        if tenant.status == "SUSPENDED" and not is_platform_super_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Tenant '{tenant.name}' is currently suspended.",
            )

        # Check membership
        mem_res = await db.execute(
            select(TenantMembership).where(
                TenantMembership.tenant_id == tenant.id,
                (TenantMembership.user_id == user_uuid) | (TenantMembership.user_id == user_name),
            )
        )
        membership = mem_res.scalars().first()

        if not membership:
            if is_platform_super_admin:
                return TenantContext(
                    tenant=tenant,
                    membership=None,
                    user=admin,
                    is_platform_admin=True,
                )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: you are not a member of tenant '{tenant_id_header}'.",
            )

        if membership.status != "ACTIVE" and not is_platform_super_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Tenant membership is not active (status: {membership.status}).",
            )

        return TenantContext(
            tenant=tenant,
            membership=membership,
            user=admin,
            is_platform_admin=is_platform_super_admin,
        )

    # No X-Tenant-ID specified: resolve default personal workspace
    mem_query = (
        select(TenantMembership, Tenant)
        .join(Tenant, Tenant.id == TenantMembership.tenant_id)
        .where(
            (TenantMembership.user_id == user_uuid) | (TenantMembership.user_id == user_name),
            Tenant.tenant_type == "PERSONAL",
            TenantMembership.role == "OWNER",
        )
    )
    res = await db.execute(mem_query)
    row = res.first()

    if row:
        membership, tenant = row
        return TenantContext(
            tenant=tenant,
            membership=membership,
            user=admin,
            is_platform_admin=is_platform_super_admin,
        )

    # User does not have a personal workspace yet: lazily provision one
    tenant = await create_personal_workspace_for_user(db, user_uuid, user_name)
    mem_res = await db.execute(
        select(TenantMembership).where(
            TenantMembership.tenant_id == tenant.id,
            TenantMembership.user_id == (user_uuid or user_name),
        )
    )
    membership = mem_res.scalar_one_or_none()

    return TenantContext(
        tenant=tenant,
        membership=membership,
        user=admin,
        is_platform_admin=is_platform_super_admin,
    )
