// frontend/src/modules/validation/ArchitectureValidationView.jsx
import React, { useState } from 'react';
import { CheckCircle2, ShieldCheck, AlertCircle, FileCheck, ArrowRight } from 'lucide-react';

export default function ArchitectureValidationView({ onNavigate }) {
  const checks = [
    { rule: 'CIS-1.1: Root Account MFA Active', status: 'PASS', severity: 'HIGH', category: 'IAM' },
    { rule: 'CIS-2.2: VPC Flow Logs Enabled', status: 'PASS', severity: 'MEDIUM', category: 'Networking' },
    { rule: 'CIS-2.4: Subnet CIDR Non-Overlapping', status: 'PASS', severity: 'CRITICAL', category: 'Networking' },
    { rule: 'CIS-3.1: KMS Customer Managed Keys Enforced', status: 'PASS', severity: 'HIGH', category: 'Storage' },
    { rule: 'CIS-4.1: Security Group 0.0.0.0/0 Ingress Restricted', status: 'PASS', severity: 'CRITICAL', category: 'Security' },
    { rule: 'CIS-5.3: RDS Storage Encrypted at Rest', status: 'PASS', severity: 'HIGH', category: 'Database' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
              MODULE // VALIDATION
            </span>
            <span className="text-xs text-slate-400 font-mono">CIS AWS Foundations &amp; Compliance</span>
          </div>
          <h1 className="text-xl font-bold text-slate-900 mt-1">Architecture Validation Engine</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Automated compliance scanning against CIS benchmarks and AWS security best practices.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => onNavigate('iac', '/terraform')}
            className="px-3.5 py-2 rounded-xl bg-[#1e40af] hover:bg-blue-700 text-white text-xs font-semibold transition flex items-center gap-1.5 cursor-pointer"
          >
            <span>Proceed to Terraform</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Validation Checklist */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="p-5 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900">Pre-Synthesis Policy Checks</h3>
            <p className="text-[11px] text-slate-500">All rules evaluated before HCL synthesis is approved</p>
          </div>
          <span className="px-2.5 py-1 rounded-full text-xs font-mono font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
            6 / 6 PASSED
          </span>
        </div>

        <div className="divide-y divide-slate-100">
          {checks.map((c, idx) => (
            <div key={idx} className="p-4 flex items-center justify-between hover:bg-slate-50/60 transition">
              <div className="flex items-center gap-3">
                <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                <div>
                  <div className="text-xs font-bold text-slate-800">{c.rule}</div>
                  <div className="text-[10px] text-slate-500 font-mono mt-0.5">Category: {c.category}</div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-bold">
                  {c.severity}
                </span>
                <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">
                  {c.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
