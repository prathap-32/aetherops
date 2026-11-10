import time
import uuid
from typing import Dict, Any, List, Optional
from app.schemas import AuditEventCreate, AuditEvent

_EVENTS: List[Dict[str, Any]] = [
    {
        "event_id": f"evt-{uuid.uuid4().hex[:12]}",
        "event_type": "SYSTEM_INITIALIZED",
        "module_key": "PLATFORM",
        "tenant_id": "ten_default",
        "project_id": None,
        "environment_id": None,
        "actor": "system",
        "entity_id": "platform",
        "details": {"message": "AetherOps Audit & History Engine online."},
        "occurred_at": time.time() - 3600
    }
]

def record_event(evt: AuditEventCreate) -> AuditEvent:
    event_id = f"evt-{uuid.uuid4().hex[:12]}"
    record = {
        "event_id": event_id,
        "event_type": evt.event_type,
        "module_key": evt.module_key,
        "tenant_id": evt.tenant_id or "ten_default",
        "project_id": evt.project_id,
        "environment_id": evt.environment_id,
        "actor": evt.actor,
        "entity_id": evt.entity_id,
        "details": evt.details,
        "occurred_at": time.time()
    }
    _EVENTS.append(record)
    return AuditEvent(**record)

def list_events(
    project_id: Optional[str] = None,
    environment_id: Optional[str] = None,
    module_key: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    filtered = _EVENTS
    if project_id:
        filtered = [e for e in filtered if e.get("project_id") == project_id]
    if environment_id:
        filtered = [e for e in filtered if e.get("environment_id") == environment_id]
    if module_key:
        filtered = [e for e in filtered if e.get("module_key") == module_key]
    return list(reversed(filtered))[:limit]
