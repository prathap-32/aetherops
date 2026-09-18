# services/security_scanner/app/scanner_engine.py
from typing import List, Dict
from app.schemas import SecurityScanRequest, SecurityScanResponse, SecurityFinding

def evaluate_security_posture(req: SecurityScanRequest) -> SecurityScanResponse:
    """
    Executes CIS AWS Foundations Benchmark checks and Zero-Trust IAM/KMS/WAF governance audits.
    """
    findings: List[SecurityFinding] = []
    score = 100

    # 1. Ingress Ports Check (CIS 4.1, 4.2)
    dangerous_ports = [22, 3389, 5432, 3306, 6379, 27017]
    bad_ingress = [p for p in req.open_ingress_ports if p in dangerous_ports]
    if bad_ingress:
        score -= 30
        findings.append(SecurityFinding(
            check_id="CIS-AWS-4.1",
            severity="CRITICAL",
            title=f"Management/Database Ports Exposed to Public Internet ({bad_ingress})",
            description="Direct ingress to administrative ports exposes infrastructure to brute-force and zero-day exploitation.",
            remediation="Close public ingress; route administrative access via AWS SSM Session Manager or VPN."
        ))
    else:
        findings.append(SecurityFinding(
            check_id="CIS-AWS-4.1",
            severity="PASS",
            title="Ingress Traffic Restricted to Standard Web Ports (80/443)",
            description="No administrative or database ports are exposed directly to the public perimeter.",
            remediation="None required."
        ))

    # 2. S3 Public Access Block (CIS 2.1.5)
    if req.public_s3_buckets:
        score -= 25
        findings.append(SecurityFinding(
            check_id="CIS-AWS-2.1.5",
            severity="CRITICAL",
            title="S3 Bucket Public Access Block Not Enforced",
            description="One or more S3 buckets have public read/write permissions enabled.",
            remediation="Apply aws_s3_account_public_access_block and enable SSE-KMS."
        ))
    else:
        findings.append(SecurityFinding(
            check_id="CIS-AWS-2.1.5",
            severity="PASS",
            title="S3 Public Access Block Enforced",
            description="All S3 storage resources enforce private bucket policies.",
            remediation="None required."
        ))

    # 3. KMS Encryption at Rest (CIS 2.8)
    if not req.kms_encryption_enabled:
        score -= 20
        findings.append(SecurityFinding(
            check_id="CIS-AWS-2.8",
            severity="HIGH",
            title="Customer-Managed KMS Encryption Not Configured",
            description="Workload relies on default cloud keys without envelope rotation or fine-grained key policies.",
            remediation="Provision aws_kms_key with enable_key_rotation=true."
        ))
    else:
        findings.append(SecurityFinding(
            check_id="CIS-AWS-2.8",
            severity="PASS",
            title="KMS Customer-Managed Envelope Encryption Enforced",
            description="Data volumes and database instances are encrypted with rotated customer keys.",
            remediation="None required."
        ))

    # 4. IAM Wildcard Permissions (CIS 1.16)
    if req.iam_wildcard_permissions:
        score -= 20
        findings.append(SecurityFinding(
            check_id="CIS-AWS-1.16",
            severity="HIGH",
            title="IAM Wildcard ('*') Permissions Detected in Policy",
            description="IAM roles grant unrestricted Action: '*' or Resource: '*', violating principle of least privilege.",
            remediation="Restrict IAM actions to specific API verbs and scoped ARNs."
        ))
    else:
        findings.append(SecurityFinding(
            check_id="CIS-AWS-1.16",
            severity="PASS",
            title="Least-Privilege Scoped IAM Policies Enforced",
            description="No wildcard administrator permissions granted to application service accounts.",
            remediation="None required."
        ))

    # 5. AWS WAF Layer 7 Protection
    if not req.waf_enabled:
        score -= 10
        findings.append(SecurityFinding(
            check_id="AETHER-SEC-01",
            severity="MEDIUM",
            title="AWS WAFv2 Not Attached to Ingress Balancer",
            description="Application endpoints lack Layer 7 rate-limiting and OWASP CRS filtering.",
            remediation="Attach AWS WAF WebACL to ALB or CloudFront distribution."
        ))
    else:
        findings.append(SecurityFinding(
            check_id="AETHER-SEC-01",
            severity="PASS",
            title="AWS WAFv2 Layer 7 Filtering Active",
            description="Traffic inspected against OWASP Top 10 exploits with automated IP throttling.",
            remediation="None required."
        ))

    final_score = max(0, min(100, score))
    passed = sum(1 for f in findings if f.severity == "PASS")
    failed = len(findings) - passed

    comp_status = {}
    for fw in req.target_frameworks:
        comp_status[fw] = "COMPLIANT" if final_score >= 80 else "NON_COMPLIANT"

    return SecurityScanResponse(
        status="SUCCESS",
        project_name=req.project_name,
        security_posture_score=final_score,
        total_checks_evaluated=len(findings),
        passed_count=passed,
        failed_count=failed,
        findings=findings,
        compliance_status=comp_status
    )
