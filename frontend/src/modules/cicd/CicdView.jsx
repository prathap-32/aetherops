// frontend/src/modules/cicd/CicdView.jsx
import React, { useState } from 'react';
import { CheckCircle2, Copy, FileCode, ArrowRight } from 'lucide-react';

export default function CicdView({ onNavigate }) {
  const [copied, setCopied] = useState(false);

  const samplePipeline = `name: AetherOps CI/CD GitOps Pipeline
on:
  push:
    branches: [ "main", "staging" ]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: AetherOps AST Repo Scanner
        run: |
          curl -s https://api.aetherops.cloud/api/v1/repo/scan
      - name: Terraform Format & Validate
        run: |
          terraform fmt -check
          terraform validate
  deploy:
    needs: validate
    runs-on: ubuntu-latest
    steps:
      - name: Apply Plan via Cloud Deployer
        run: |
          curl -X POST https://api.aetherops.cloud/api/v1/deploy`;

  const copyToClipboard = () => {
    navigator.clipboard.writeText(samplePipeline);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">CI/CD GitOps Pipeline</h1>
            <span className="px-2.5 py-0.5 rounded text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200">
              GitHub Actions
            </span>
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Automated pipeline generation for GitHub Actions, GitLab CI, and AWS CodePipeline.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => onNavigate('monitoring', '/monitoring')}
            className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold transition flex items-center gap-1.5 cursor-pointer shadow-xs"
          >
            <span>Observability</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Pipeline Preview Card */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="p-4 border-b border-slate-100 bg-slate-50/70 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileCode className="w-4 h-4 text-indigo-600" />
            <span className="font-mono text-xs font-bold text-slate-800">.github/workflows/aetherops-gitops.yml</span>
          </div>
          <button
            onClick={copyToClipboard}
            className="px-3 py-1 rounded-lg text-xs font-semibold bg-white border border-slate-200 text-slate-700 hover:bg-slate-100 transition flex items-center gap-1.5 cursor-pointer"
          >
            {copied ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? 'Copied!' : 'Copy Workflow'}</span>
          </button>
        </div>
        <div className="p-5 bg-slate-950 font-mono text-xs text-slate-300 overflow-x-auto">
          <pre>{samplePipeline}</pre>
        </div>
      </div>
    </div>
  );
}
