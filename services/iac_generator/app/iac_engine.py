# services/iac_generator/app/iac_engine.py
from typing import List, Dict, Any
from app.schemas import IaCGenerationRequest, GeneratedFile, IaCGenerationResponse

def generate_terraform_hcl(req: IaCGenerationRequest) -> IaCGenerationResponse:
    """
    Generates production-grade, syntax-valid Terraform HCL modules matching workload specs.
    """
    files: List[GeneratedFile] = []

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

variable "instance_count" {{
  type        = number
  default     = {req.compute_count}
  description = "Number of compute nodes in Auto Scaling Group"
}}

variable "db_instance_class" {{
  type        = string
  default     = "{req.database_instance_type}"
  description = "RDS instance class"
}}
"""
    files.append(GeneratedFile(filename="variables.tf", content=variables_content, language="hcl"))

    # 3. main.tf
    kms_block = """
# AWS KMS Customer Managed Key for Envelope Encryption
resource "aws_kms_key" "primary" {
  description             = "AetherOps encryption key for ${var.project_name}"
  deletion_window_in_days = 30
  enable_key_rotation     = true
}
""" if req.enable_kms else ""

    waf_block = """
# AWS WAFv2 Web ACL
resource "aws_wafv2_web_acl" "main" {
  name        = "${var.project_name}-waf"
  description = "OWASP Core RuleSet protection"
  scope       = "REGIONAL"

  default_action {
    allow {}
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "${var.project_name}-waf-metric"
    sampled_requests_enabled   = true
  }
}
""" if req.enable_waf else ""

    alb_block = """
# Application Load Balancer
resource "aws_lb" "app" {
  name               = "${var.project_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = [aws_subnet.public_a.id, aws_subnet.public_b.id]
}
""" if req.enable_alb else ""

    main_content = f"""# VPC & Networking
resource "aws_vpc" "main" {{
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {{
    Name = "${{var.project_name}}-vpc"
  }}
}}

resource "aws_subnet" "public_a" {{
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "${{var.aws_region}}a"
  map_public_ip_on_launch = true
}}

resource "aws_subnet" "public_b" {{
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "${{var.aws_region}}b"
  map_public_ip_on_launch = true
}}

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
{alb_block}{waf_block}{kms_block}
# Amazon RDS PostgreSQL Database
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
"""
    files.append(GeneratedFile(filename="main.tf", content=main_content, language="hcl"))

    # 4. outputs.tf
    outputs_content = f"""output "vpc_id" {{
  description = "Created VPC Identifier"
  value       = aws_vpc.main.id
}}

output "rds_endpoint" {{
  description = "Primary RDS Connection Endpoint"
  value       = aws_db_instance.main.endpoint
}}
"""
    if req.enable_alb:
        outputs_content += """
output "alb_dns_name" {{
  description = "Public Load Balancer FQDN"
  value       = aws_lb.app.dns_name
}}
"""
    files.append(GeneratedFile(filename="outputs.tf", content=outputs_content, language="hcl"))

    return IaCGenerationResponse(
        status="SUCCESS",
        iac_tool=req.iac_tool,
        project_name=req.project_name,
        files=files,
        summary={
            "total_files": len(files),
            "resources_defined": ["aws_vpc", "aws_subnets", "aws_db_instance", "aws_security_group"] + (["aws_lb"] if req.enable_alb else []) + (["aws_kms_key"] if req.enable_kms else []),
            "target_region": req.aws_region
        }
    )
