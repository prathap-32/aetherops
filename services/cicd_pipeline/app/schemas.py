# services/cicd_pipeline/app/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class PipelineGenerationRequest(BaseModel):
    project_name: str = Field(default="workload-delivery")
    platform: str = Field(default="github_actions", description="github_actions, gitlab_ci")
    iac_tool: str = Field(default="terraform")
    enable_security_scan: bool = Field(default=True)
    enable_cost_budget_gate: bool = Field(default=True)
    auto_apply_on_main: bool = Field(default=False)
    target_branch: str = Field(default="main")

class PipelineFile(BaseModel):
    filepath: str
    content: str

class PipelineGenerationResponse(BaseModel):
    status: str
    project_name: str
    platform: str
    files: List[PipelineFile]
    stages: List[str]
