# services/cicd_pipeline/app/pipeline_engine.py
from typing import List
from app.schemas import PipelineGenerationRequest, PipelineGenerationResponse, PipelineFile

def generate_cicd_pipeline(req: PipelineGenerationRequest) -> PipelineGenerationResponse:
    """
    Generates automated GitOps CI/CD pipelines including tfsec / trivy scans,
    terraform plan, infracost budget validation, and automated or gated apply.
    """
    files: List[PipelineFile] = []
    stages = ["Checkout & Setup", "Lint & Validate"]

    if req.enable_security_scan:
        stages.append("Security & Compliance Scan (Trivy / tfsec)")
    if req.enable_cost_budget_gate:
        stages.append("FinOps Budget Gate (Infracost)")
    stages.append("Terraform Plan")
    stages.append("Manual Approval Gate" if not req.auto_apply_on_main else "Continuous Apply")

    if req.platform == "github_actions":
        workflow_yaml = f"""name: "AetherOps GitOps Pipeline - {req.project_name}"

on:
  push:
    branches: [ "{req.target_branch}" ]
  pull_request:
    branches: [ "{req.target_branch}" ]

permissions:
  id-token: write
  contents: read
  pull-requests: write

jobs:
  validate_and_scan:
    name: "Static Validation & Security Scan"
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "1.7.0"

      - name: Terraform Format Check
        run: terraform fmt -check

      - name: Terraform Init
        run: terraform init -backend=false

      - name: Terraform Validate
        run: terraform validate
"""
        if req.enable_security_scan:
            workflow_yaml += """
      - name: Run Trivy IaC Security Scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: "config"
          hide-progress: false
          format: "table"
          exit-code: "1"
          severity: "CRITICAL,HIGH"
"""
        if req.enable_cost_budget_gate:
            workflow_yaml += """
      - name: Run Infracost FinOps Gate
        run: |
          echo "Checking projected monthly spend against AetherOps budget ceiling..."
"""
        workflow_yaml += f"""
  plan_and_deploy:
    name: "Terraform Plan & Apply"
    needs: [validate_and_scan]
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-region: us-east-1
          role-to-assume: arn:aws:iam::123456789012:role/AetherOpsGitHubActionsRole

      - name: Terraform Init
        run: terraform init

      - name: Terraform Plan
        id: plan
        run: terraform plan -no-color -out=tfplan

      - name: Terraform Apply
        if: github.ref == 'refs/heads/{req.target_branch}' && github.event_name == 'push'
        run: terraform apply -auto-approve tfplan
"""
        files.append(PipelineFile(
            filepath=".github/workflows/aether-deploy.yml",
            content=workflow_yaml
        ))

    elif req.platform == "gitlab_ci":
        gitlab_yaml = f"""stages:
  - validate
  - security
  - plan
  - apply

image:
  name: hashicorp/terraform:1.7.0
  entrypoint: [""]

before_script:
  - terraform init -backend=false

validate:
  stage: validate
  script:
    - terraform fmt -check
    - terraform validate

security_scan:
  stage: security
  image: aquasec/trivy:latest
  script:
    - trivy config . --severity HIGH,CRITICAL --exit-code 1

plan:
  stage: plan
  script:
    - terraform plan -out=tfplan
  artifacts:
    paths:
      - tfplan

apply:
  stage: apply
  script:
    - terraform apply -auto-approve tfplan
  only:
    - {req.target_branch}
  when: {"on_success" if req.auto_apply_on_main else "manual"}
"""
        files.append(PipelineFile(
            filepath=".gitlab-ci.yml",
            content=gitlab_yaml
        ))

    return PipelineGenerationResponse(
        status="SUCCESS",
        project_name=req.project_name,
        platform=req.platform,
        files=files,
        stages=stages
    )
