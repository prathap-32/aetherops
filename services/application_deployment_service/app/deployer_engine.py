import time
import uuid
import hashlib
from typing import Dict, Any, List, Optional
from app.schemas import DeploymentRequest, DeploymentResponse

_RELEASES: Dict[str, Dict[str, Any]] = {}

def deploy_application(req: DeploymentRequest) -> DeploymentResponse:
    release_id = f"rel-{uuid.uuid4().hex[:10]}"
    sha = req.commit_sha or "HEAD"
    image_digest = f"sha256:{hashlib.sha256((req.service_name + sha).encode()).hexdigest()}"
    endpoint_url = f"https://{req.service_name}.aetherops.internal"

    now = time.time()
    release_record = {
        "release_id": release_id,
        "status": "DEPLOYED",
        "service_name": req.service_name,
        "target_region": req.target_region,
        "image_digest": image_digest,
        "endpoint_url": endpoint_url,
        "health_status": "HEALTHY",
        "deployed_at": now,
        "project_id": req.project_id,
        "environment_id": req.environment_id,
        "commit_sha": sha
    }
    _RELEASES[release_id] = release_record

    return DeploymentResponse(**release_record)

def list_releases(project_id: Optional[str] = None) -> List[Dict[str, Any]]:
    if project_id:
        return [r for r in _RELEASES.values() if r.get("project_id") == project_id]
    return list(_RELEASES.values())
