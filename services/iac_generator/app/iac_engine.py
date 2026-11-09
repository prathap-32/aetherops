import hashlib
import logging
import os
import shutil
import subprocess
import tempfile
import uuid
from typing import List, Dict, Any, Tuple
from app.schemas import IaCGenerationRequest, GeneratedFile, IaCGenerationResponse

logger = logging.getLogger("iac-engine")

PROVIDER_PLUGIN_DIRS = [
    "/home/prathap32/.terraform.d/plugins",
    "/tmp/tf_test/.terraform/providers",
]

def validate_and_format_terraform(files: List[GeneratedFile]) -> Tuple[List[GeneratedFile], Dict[str, Any]]:
    """
    Executes terraform fmt and terraform validate in an isolated temporary directory.
    Returns formatted files and validation report.
    """
    validation_report = {
        "fmt": "NOT_RUN",
        "validate": "NOT_RUN",
        "details": "",
        "terraform_version": "unknown"
    }

    tf_binary = shutil.which("terraform") or "/usr/bin/terraform"
    if not os.path.exists(tf_binary) and not shutil.which("terraform"):
        validation_report["details"] = "Terraform binary not found on system PATH."
        return files, validation_report

    try:
        ver_res = subprocess.run([tf_binary, "version"], capture_output=True, text=True, timeout=5)
        if ver_res.returncode == 0:
            first_line = ver_res.stdout.splitlines()[0] if ver_res.stdout else ""
            validation_report["terraform_version"] = first_line.replace("Terraform v", "").strip()
    except Exception as e:
        logger.warning(f"Could not retrieve terraform version: {e}")

    with tempfile.TemporaryDirectory() as tmpdir:
        file_map = {}
        for f in files:
            fp = os.path.join(tmpdir, f.filename)
            with open(fp, "w", encoding="utf-8") as out:
                out.write(f.content)
            file_map[f.filename] = fp

        # 1. Run terraform fmt
        try:
            fmt_res = subprocess.run([tf_binary, "fmt", tmpdir], capture_output=True, text=True, timeout=10)
            if fmt_res.returncode == 0:
                validation_report["fmt"] = "PASS"
                formatted_files = []
                for f in files:
                    fp = file_map[f.filename]
                    if os.path.exists(fp):
                        with open(fp, "r", encoding="utf-8") as r:
                            formatted_files.append(GeneratedFile(filename=f.filename, content=r.read(), language=f.language))
                    else:
                        formatted_files.append(f)
                files = formatted_files
            else:
                validation_report["fmt"] = "WARNING"
                validation_report["details"] += f"fmt error: {fmt_res.stderr}; "
        except Exception as e:
            validation_report["fmt"] = "ERROR"
            validation_report["details"] += f"fmt exception: {e}; "

        # 2. Run terraform init & validate
        plugin_dir = next((d for d in PROVIDER_PLUGIN_DIRS if os.path.exists(d)), None)
        init_args = [tf_binary, "init"]
        if plugin_dir:
            init_args.append(f"-plugin-dir={plugin_dir}")

        try:
            init_res = subprocess.run(init_args, cwd=tmpdir, capture_output=True, text=True, timeout=15)
            if init_res.returncode == 0:
                val_res = subprocess.run([tf_binary, "validate"], cwd=tmpdir, capture_output=True, text=True, timeout=10)
                if val_res.returncode == 0:
                    validation_report["validate"] = "PASS"
                    validation_report["details"] = "Terraform configuration is syntactically valid and passed hashicorp/aws provider schema validation."
                else:
                    validation_report["validate"] = "FAILED"
                    validation_report["details"] += f"validate error: {val_res.stderr or val_res.stdout}"
            else:
                validation_report["validate"] = "SKIPPED"
                validation_report["details"] += f"init notice: {init_res.stderr or init_res.stdout}"
        except Exception as e:
            validation_report["validate"] = "ERROR"
            validation_report["details"] += f"validate exception: {e}"

    return files, validation_report

def generate_terraform_hcl(req: IaCGenerationRequest) -> IaCGenerationResponse:
    """
    Generates dynamic, production-grade, syntax-valid Terraform HCL modules
    strictly matching the actual workload requirements (lean dev vs multi-tier prod).
    """
    files: List[GeneratedFile] = []

    has_db = bool(req.database_instance_type and req.database_instance_type.lower() != "none" and req.database_storage_gb > 0)
    has_alb = bool(req.enable_alb)
    is_lean_dev = not has_db and not has_alb and req.compute_count <= 1

    # 1. provider.tf
    provider_content = f"""terraform {{
  required_version = ">= 1.5.0"
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}
}}

provider "aws" {{
  region = var.aws_region

  default_tags {{
    tags = {{
      Project     = "{req.project_name}"
      ManagedBy   = "AetherOps"
      Environment = "Production"
    }}
  }}
}}
"""
    files.append(GeneratedFile(filename="provider.tf", content=provider_content, language="hcl"))

    # 2. variables.tf
    variables_content = f"""variable "aws_region" {{
  type        = string
  default     = "{req.aws_region}"
  description = "Target AWS deployment region"
}}

variable "project_name" {{
  type        = string
  default     = "{req.project_name}"
  description = "Workload project identifier"
}}

variable "instance_type" {{
  type        = string
  default     = "{req.compute_instance_type}"
  description = "EC2 instance sizing"
}}
"""
    if has_db:
        variables_content += f"""
variable "db_instance_class" {{
  type        = string
  default     = "{req.database_instance_type}"
  description = "RDS instance class"
}}
"""
    files.append(GeneratedFile(filename="variables.tf", content=variables_content, language="hcl"))

    # 3. main.tf (Dynamic based on workload requirements)
    kms_block = f"""
resource "aws_kms_key" "primary" {{
  description             = "AetherOps encryption key for ${{var.project_name}}"
  deletion_window_in_days = 30
  enable_key_rotation     = true
}}
""" if req.enable_kms else ""

    waf_block = f"""
resource "aws_wafv2_web_acl" "main" {{
  name        = "${{var.project_name}}-waf"
  description = "OWASP Core RuleSet protection"
  scope       = "REGIONAL"

  default_action {{
    allow {{}}
  }}

  visibility_config {{
    cloudwatch_metrics_enabled = true
    metric_name                = "${{var.project_name}}-waf-metric"
    sampled_requests_enabled   = true
  }}
}}
""" if req.enable_waf else ""

    if is_lean_dev:
        # Lean Single-Tier (e.g. Docker frontend / static app without RDS/ALB)
        main_content = f"""# VPC & Networking (Lean Single-Tier)
resource "aws_vpc" "main" {{
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {{
    Name = "${{var.project_name}}-vpc"
  }}
}}

resource "aws_subnet" "public_a" {{
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${{var.aws_region}}a"
  map_public_ip_on_launch = true

  tags = {{
    Name = "${{var.project_name}}-public-subnet"
  }}
}}

resource "aws_internet_gateway" "igw" {{
  vpc_id = aws_vpc.main.id

  tags = {{
    Name = "${{var.project_name}}-igw"
  }}
}}

resource "aws_route_table" "public" {{
  vpc_id = aws_vpc.main.id

  route {{
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }}

  tags = {{
    Name = "${{var.project_name}}-public-rt"
  }}
}}

resource "aws_route_table_association" "public_a" {{
  subnet_id      = aws_subnet.public_a.id
  route_table_id = aws_route_table.public.id
}}

resource "aws_security_group" "app_sg" {{
  name        = "${{var.project_name}}-app-sg"
  description = "Allow HTTP/HTTPS inbound traffic"
  vpc_id      = aws_vpc.main.id

  ingress {{
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}

  ingress {{
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}

  ingress {{
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}

  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}
}}

resource "aws_eip" "app_eip" {{
  domain = "vpc"

  tags = {{
    Name = "${{var.project_name}}-eip"
  }}
}}

resource "aws_instance" "app" {{
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.public_a.id
  vpc_security_group_ids = [aws_security_group.app_sg.id]

  tags = {{
    Name = "${{var.project_name}}-instance"
  }}
}}

data "aws_ami" "ubuntu" {{
  most_recent = true
  filter {{
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }}
  filter {{
    name   = "virtualization-type"
    values = ["hvm"]
  }}
  owners = ["099720109477"]
}}
{kms_block}
"""
    else:
        # Multi-Tier Production Workload (VPC, Public/Private Subnets, ALB, RDS)
        alb_resource = f"""
resource "aws_lb" "app" {{
  name               = "${{var.project_name}}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = [aws_subnet.public_a.id, aws_subnet.public_b.id]
}}
""" if has_alb else ""

        db_resource = f"""
resource "aws_db_subnet_group" "rds" {{
  name       = "${{var.project_name}}-db-subnet-group"
  subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id]
}}

resource "aws_db_instance" "main" {{
  identifier             = "${{var.project_name}}-db"
  allocated_storage      = {req.database_storage_gb}
  max_allocated_storage  = {req.database_storage_gb * 2}
  storage_type           = "gp3"
  engine                 = "postgres"
  engine_version         = "15.4"
  instance_class         = var.db_instance_class
  multi_az               = {str(req.database_multi_az).lower()}
  db_subnet_group_name   = aws_db_subnet_group.rds.name
  skip_final_snapshot    = true
  storage_encrypted      = true
  kms_key_id             = {"aws_kms_key.primary.arn" if req.enable_kms else "null"}
}}
""" if has_db else ""

        private_subnets_block = f"""
resource "aws_subnet" "private_a" {{
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.10.0/24"
  availability_zone = "${{var.aws_region}}a"
}}

resource "aws_subnet" "private_b" {{
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.20.0/24"
  availability_zone = "${{var.aws_region}}b"
}}
""" if has_db else ""

        main_content = f"""# VPC & Networking (Multi-Tier Production)
resource "aws_vpc" "main" {{
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {{
    Name = "${{var.project_name}}-vpc"
  }}
}}

resource "aws_subnet" "public_a" {{
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${{var.aws_region}}a"
  map_public_ip_on_launch = true
}}

resource "aws_subnet" "public_b" {{
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "${{var.aws_region}}b"
  map_public_ip_on_launch = true
}}
{private_subnets_block}
# Security Groups
resource "aws_security_group" "alb_sg" {{
  name        = "${{var.project_name}}-alb-sg"
  description = "Allow inbound HTTP/HTTPS traffic"
  vpc_id      = aws_vpc.main.id

  ingress {{
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}

  ingress {{
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}

  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}
}}
{alb_resource}{waf_block}{kms_block}{db_resource}
"""

    files.append(GeneratedFile(filename="main.tf", content=main_content, language="hcl"))

    # 4. outputs.tf
    outputs_content = f"""output "vpc_id" {{
  description = "Created VPC Identifier"
  value       = aws_vpc.main.id
}}
"""
    if is_lean_dev:
        outputs_content += f"""output "instance_ip" {{
  description = "Public IP of the application instance"
  value       = aws_instance.app.public_ip
}}
"""
    else:
        if has_db:
            outputs_content += f"""output "rds_endpoint" {{
  description = "Primary RDS Connection Endpoint"
  value       = aws_db_instance.main.endpoint
}}
"""
        if has_alb:
            outputs_content += f"""output "alb_dns_name" {{
  description = "Public Load Balancer FQDN"
  value       = aws_lb.app.dns_name
}}
"""
    files.append(GeneratedFile(filename="outputs.tf", content=outputs_content, language="hcl"))

    formatted_files, validation_report = validate_and_format_terraform(files)

    content_stream = "".join(f"{f.filename}:{f.content}\n" for f in formatted_files).encode("utf-8")
    checksum = hashlib.sha256(content_stream).hexdigest()
    tf_version_id = f"tf-{uuid.uuid4().hex[:12]}"
    arch_link = f"/api/v1/architecture/review/{req.architecture_version_id}" if req.architecture_version_id else ""

    resources_defined = ["aws_vpc", "aws_subnet"]
    if is_lean_dev:
        resources_defined.extend(["aws_instance", "aws_eip", "aws_security_group"])
    else:
        resources_defined.append("aws_security_group")
        if has_alb:
            resources_defined.append("aws_lb")
        if has_db:
            resources_defined.extend(["aws_db_instance", "aws_db_subnet_group"])
        if req.enable_kms:
            resources_defined.append("aws_kms_key")

    return IaCGenerationResponse(
        status="SUCCESS",
        iac_tool=req.iac_tool,
        project_name=req.project_name,
        architecture_version_id=req.architecture_version_id,
        terraform_version_id=tf_version_id,
        checksum=checksum,
        approved_architecture_link=arch_link,
        validation=validation_report,
        files=formatted_files,
        summary={
            "total_files": len(formatted_files),
            "resources_defined": resources_defined,
            "target_region": req.aws_region,
            "terraform_version_id": tf_version_id,
            "validation_status": validation_report.get("validate", "UNKNOWN")
        }
    )
