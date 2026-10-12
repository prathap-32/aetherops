// frontend/src/modules/execution/ApprovalExecutionView.jsx
import React, { useState } from 'react';
import { CheckSquare, AlertTriangle, ShieldCheck, Play, ArrowRight, Clock } from 'lucide-react';

export default function ApprovalExecutionView({ onNavigate }) {
  const [approved, setApproved] = useState(false);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-blue-50 text-blue-700 border border-blue-200">
              MODULE // EXECUTION
            </span>
            <span className="text-xs text-slate-400 font-mono">Infrastructure Execution &amp; Gate</span>
          </div>
          <h1 className="text-xl font-bold text-slate-900 mt-1">Approval &amp; Execution Gate</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Cryptographically signed gate requiring explicit approval before applying infrastructure changes.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => onNavigate('deployments', '/deployment')}
            className="px-3.5 py-2 rounded-xl bg-[#1e40af] hover:bg-blue-700 text-white text-xs font-semibold transition flex items-center gap-1.5 cursor-pointer"
          >
            <span>Live Deployments</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Execution Plan Card */}
      <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-xs space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900">Execution Plan #PLN-2026-094</h3>
            <p className="text-xs text-slate-500">Target AWS Region: us-east-1 // VPC: 10.0.0.0/16</p>
          </div>
          <span className="px-2.5 py-1 rounded-full text-xs font-mono font-bold bg-amber-50 text-amber-700 border border-amber-200 flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5" />
            <span>PENDING SIGN-OFF</span>
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 font-mono text-xs">
          <div className="p-3 rounded-xl bg-emerald-50/60 border border-emerald-200/60 text-emerald-800">
            <div className="text-[10px] uppercase font-bold text-emerald-600">Resources to Add</div>
            <div className="text-lg font-black mt-1">+14 resources</div>
          </div>
          <div className="p-3 rounded-xl bg-blue-50/60 border border-blue-200/60 text-blue-800">
            <div className="text-[10px] uppercase font-bold text-blue-600">Resources to Change</div>
            <div className="text-lg font-black mt-1">~0 resources</div>
          </div>
          <div className="p-3 rounded-xl bg-rose-50/60 border border-rose-200/60 text-rose-800">
            <div className="text-[10px] uppercase font-bold text-rose-600">Resources to Destroy</div>
            <div className="text-lg font-black mt-1">-0 resources</div>
          </div>
        </div>

        <div className="pt-4 border-t border-slate-100 flex items-center justify-between">
          <div className="text-xs text-slate-600 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span>All CIS Security &amp; FinOps guardrails verified.</span>
          </div>
          <button
            onClick={() => {
              setApproved(true);
              alert('Execution gate approved! Initiating deployment plan with Cloud Deployer (Port 8008)...');
              onNavigate('deployments', '/deployment');
            }}
            className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs transition flex items-center gap-2 cursor-pointer shadow-lg shadow-emerald-600/20"
          >
            <Play className="w-3.5 h-3.5" />
            <span>Approve &amp; Execute</span>
          </button>
        </div>
      </div>
    </div>
  );
}
