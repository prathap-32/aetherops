// frontend/src/modules/dashboard/components/AttentionPanel.jsx
import React from 'react';
import { AlertTriangle, ArrowRight } from 'lucide-react';

export default function AttentionPanel({ onNavigate }) {
  return (
    <div className="bg-rose-50 border border-rose-200 rounded-2xl p-6 text-rose-900 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-5">
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 rounded-xl bg-rose-100 text-rose-600 border border-rose-200 flex items-center justify-center shrink-0 mt-0.5">
          <AlertTriangle className="w-6 h-6" />
        </div>
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-rose-700 bg-rose-100 px-2.5 py-0.5 rounded-md border border-rose-200">
            Attention Required (L11)
          </span>
          <h3 className="text-lg font-bold text-rose-950 mt-1">
            Operational Failure Detected in Infrastructure Pipeline
          </h3>
          <p className="text-sm text-rose-800 mt-1 leading-relaxed">
            One or more deployment executions or risk validations encountered an error or state drift. Review logs and remediation steps immediately.
          </p>
        </div>
      </div>

      <button
        onClick={() => onNavigate('deployments', '/deployment')}
        className="px-5 py-3 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-semibold shadow-xs transition flex items-center justify-center gap-2 cursor-pointer shrink-0 min-h-[48px]"
      >
        <span>Remediate Issues</span>
        <ArrowRight className="w-4 h-4" />
      </button>
    </div>
  );
}
