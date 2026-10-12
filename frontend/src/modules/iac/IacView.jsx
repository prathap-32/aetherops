// frontend/src/modules/iac/IacView.jsx
import React from 'react';
import { Terminal, Copy, Download, CheckCircle2, ShieldAlert } from 'lucide-react';

export default function IacView() {
  const terraformSnippet = `terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
  default_tags {
    tags = {
      Environment = "Production"
      ManagedBy   = "Aether-Cloud"
    }
  }
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.1.2"

  name = "aether-production-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = true
}`;

  return (
    <div className="space-y-6">
      <div className="pb-4 border-b border-slate-200">
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
            Module 5
          </span>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">IaC Generator (Terraform HCL)</h1>
        </div>
        <p className="text-sm text-slate-500 mt-1">
          Automated multi-tier infrastructure as code synthesis adhering to AWS Well-Architected Framework.
        </p>
      </div>

      <div className="bg-slate-950 rounded-xl border border-slate-800 shadow-xl overflow-hidden font-mono text-xs">
        <div className="p-3.5 bg-slate-900 border-b border-slate-800 flex items-center justify-between text-slate-400">
          <div className="flex items-center gap-2">
            <Terminal className="w-4 h-4 text-emerald-400" />
            <span className="text-slate-200 font-semibold">main.tf</span>
            <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-400">Terraform v1.5+</span>
          </div>
          <button
            onClick={() => {
              navigator.clipboard.writeText(terraformSnippet);
              alert('Copied Terraform configuration to clipboard!');
            }}
            className="flex items-center gap-1.5 px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-xs font-semibold transition"
          >
            <Copy className="w-3.5 h-3.5" />
            Copy Code
          </button>
        </div>
        <pre className="p-5 text-emerald-300 overflow-x-auto leading-relaxed">
          {terraformSnippet}
        </pre>
      </div>
    </div>
  );
}
