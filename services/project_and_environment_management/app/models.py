# services/project_and_environment_management/app/models.py
import datetime
from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from app.database import Base


class Tenant(Base):
    """
    Represents an isolation boundary (workspace) for projects, environments,
    cloud credentials, and members.

    Every user belongs to at least one personal workspace, and may belong to
    multiple organization workspaces.
    """
    __tablename__ = "aether_tenants"

    id          = Column(String(36),  primary_key=True, index=True)          # UUID v4
    name        = Column(String(100), nullable=False)
    slug        = Column(String(100), nullable=False, unique=True, index=True)
    tenant_type = Column(String(20),  nullable=False, default="PERSONAL")     # PERSONAL | ORGANIZATION
    status      = Column(String(20),  nullable=False, default="ACTIVE")       # ACTIVE | SUSPENDED | ARCHIVED
    created_at  = Column(DateTime,    nullable=False, default=datetime.datetime.utcnow)
    updated_at  = Column(DateTime,    nullable=False, default=datetime.datetime.utcnow,
                         onupdate=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            "id":          self.id,
            "name":        self.name,
            "slug":        self.slug,
            "tenant_type": self.tenant_type,
            "status":      self.status,
            "created_at":  self.created_at.isoformat() if self.created_at else None,
            "updated_at":  self.updated_at.isoformat() if self.updated_at else None,
        }


class TenantMembership(Base):
    """
    Associates a user (by stable UUID or historical username) with a Tenant,
    assigning a role within that tenant boundary.
    """
    __tablename__ = "aether_tenant_memberships"

    id         = Column(String(36), primary_key=True, index=True)           # UUID v4
    tenant_id  = Column(String(36), nullable=False, index=True)
    user_id    = Column(String(36), nullable=False, index=True)            # AdminUser.uuid or legacy username
    role       = Column(String(20), nullable=False, default="MEMBER")       # OWNER | ADMIN | MEMBER | VIEWER
    status     = Column(String(20), nullable=False, default="ACTIVE")       # ACTIVE | INVITED | SUSPENDED
    created_at = Column(DateTime,   nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime,   nullable=False, default=datetime.datetime.utcnow,
                        onupdate=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("tenant_id", "user_id", name="_tenant_user_uc"),
    )

    def to_dict(self):
        return {
            "id":         self.id,
            "tenant_id":  self.tenant_id,
            "user_id":    self.user_id,
            "role":       self.role,
            "status":     self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class AetherProject(Base):
    """
    Represents a user- or team-owned project — the top-level boundary for deployments.

    A project holds one or more environments (Development, Staging, Production …).
    Scoped by tenant_id for tenant isolation, while retaining owner for backward compatibility.
    """
    __tablename__ = "aether_projects"

    id                 = Column(String(36),  primary_key=True, index=True)          # UUID v4
    name               = Column(String(100), nullable=False, index=True)
    description        = Column(String(500), nullable=True)
    project_type       = Column(String(50),  nullable=False)                         # web_application | api_service | …
    owner              = Column(String(100), nullable=False, index=True)             # username (backward compat)
    tenant_id          = Column(String(36),  nullable=True,  index=True)             # Tenant.id
    created_by_user_id = Column(String(36),  nullable=True,  index=True)             # AdminUser.uuid
    status             = Column(String(30),  nullable=False, default="CREATED")      # CREATED | ACTIVE | ARCHIVED
    environment_count  = Column(Integer,     nullable=False, default=0)              # denormalised for fast dashboard render
    created_at         = Column(DateTime,    nullable=False, default=datetime.datetime.utcnow)
    updated_at         = Column(DateTime,    nullable=False, default=datetime.datetime.utcnow,
                                onupdate=datetime.datetime.utcnow)

    def to_dict(self, environments=None):
        return {
            "id":                 self.id,
            "name":               self.name,
            "description":        self.description,
            "project_type":       self.project_type,
            "owner":              self.owner,
            "tenant_id":          self.tenant_id,
            "created_by_user_id": self.created_by_user_id,
            "status":             self.status,
            "environment_count":  self.environment_count,
            "environments":       [e.to_dict() for e in (environments or [])],
            "created_at":         self.created_at.isoformat() if self.created_at else None,
            "updated_at":         self.updated_at.isoformat() if self.updated_at else None,
        }


class AetherEnvironment(Base):
    """
    Represents a deployment boundary inside a project.

    Each environment has its own AWS region, lifecycle state, and — eventually —
    its own repository branch, architecture, Terraform state, and monitoring data.
    The lifecycle state is advanced by later modules via the status PATCH endpoint.
    """
    __tablename__ = "aether_environments"

    id                 = Column(String(36),  primary_key=True, index=True)             # UUID v4
    project_id         = Column(String(36),  nullable=False, index=True)               # soft FK → AetherProject.id
    tenant_id          = Column(String(36),  nullable=True,  index=True)               # Tenant.id
    created_by_user_id = Column(String(36),  nullable=True,  index=True)               # AdminUser.uuid
    name               = Column(String(100), nullable=False)                            # user-defined label
    env_type           = Column(String(30),  nullable=False)                            # development | staging | production
    aws_region         = Column(String(50),  nullable=False)                            # e.g. ap-south-1
    description        = Column(String(500), nullable=True)
    status             = Column(String(40),  nullable=False, default="CREATED")
    # Lifecycle: CREATED → CONFIGURED → REPOSITORY_CONNECTED → ANALYZED →
    #            ARCHITECTURE_READY → VALIDATED → READY_TO_DEPLOY →
    #            DEPLOYING → ACTIVE  |  FAILED

    created_at         = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at         = Column(DateTime, nullable=False, default=datetime.datetime.utcnow,
                                onupdate=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("project_id", "name", name="_project_env_name_uc"),
    )

    def to_dict(self):
        return {
            "id":                 self.id,
            "project_id":         self.project_id,
            "tenant_id":          self.tenant_id,
            "created_by_user_id": self.created_by_user_id,
            "name":               self.name,
            "env_type":           self.env_type,
            "aws_region":         self.aws_region,
            "description":        self.description,
            "status":             self.status,
            "created_at":         self.created_at.isoformat() if self.created_at else None,
            "updated_at":         self.updated_at.isoformat() if self.updated_at else None,
        }
