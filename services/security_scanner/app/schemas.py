# services/security_scanner/app/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class SecurityScanRequest(BaseModel):
    project_name: str = Field(default="workload-security")
    target_frameworks: List[str] = Field(default_factory=lambda: ["CIS-AWS-1.5", "SOC2-Type-II"])
    open_ingress_ports: List[int] = Field(default_factory=lambda: [80, 443])
    kms_encryption_enabled: bool = Field(default=True)
    waf_enabled: bool = Field(default=True)
    iam_wildcard_permissions: bool = Field(default=False)
    public_s3_buckets: bool = Field(default=False)

class SecurityFinding(BaseModel):
    check_id: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, PASS
    title: str
    description: str
    remediation: str

class SecurityScanResponse(BaseModel):
    status: str
    project_name: str
    security_posture_score: int  # 0 to 100
    total_checks_evaluated: int
    passed_count: int
    failed_count: int
    findings: List[SecurityFinding]
    compliance_status: Dict[str, str]
