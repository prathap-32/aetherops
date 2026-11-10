import time
import logging
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, status, Request, Query
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import AuditEvent, AuditEventCreate
from app.audit_engine import record_event, list_events, _EVENTS

logger = logging.getLogger("audit-history-service")

app = FastAPI(
    title="AetherOps AI - Audit & History Service",
    description="Module 14: Centralized event collection, timeline traceability, and cross-service audit trail (Port 8012)",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "service": "AetherOps AI — Audit & History Service (Module 14)",
        "version": "2.0.0",
        "port": 8012,
        "endpoints": {
            "health": "/health",
            "events": "/api/v1/audit/events",
            "record": "/api/v1/audit/record",
            "docs": "/docs"
        }
    }

@app.get("/health", status_code=status.HTTP_200_OK)
@app.get("/api/v1/audit/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "healthy",
        "service": "audit-history-service",
        "port": 8012,
        "timestamp": time.time()
    }

@app.post("/api/v1/audit/record", response_model=AuditEvent, status_code=status.HTTP_201_CREATED)
async def create_event(evt: AuditEventCreate):
    logger.info(f"Recording audit event: {evt.event_type} from {evt.module_key}")
    try:
        res = record_event(evt)
        return res
    except Exception as e:
        logger.error(f"Audit event recording failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audit recording failure: {str(e)}"
        )

@app.get("/api/v1/audit/events", status_code=status.HTTP_200_OK)
async def get_events(
    project_id: Optional[str] = Query(None),
    environment_id: Optional[str] = Query(None),
    module_key: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500)
):
    events = list_events(project_id=project_id, environment_id=environment_id, module_key=module_key, limit=limit)
    return {"total": len(events), "events": events}

@app.get("/api/v1/audit/projects/{project_id}", status_code=status.HTTP_200_OK)
async def get_project_events(project_id: str, limit: int = 50):
    events = list_events(project_id=project_id, limit=limit)
    return {"project_id": project_id, "total": len(events), "events": events}
