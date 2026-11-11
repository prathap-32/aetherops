// frontend/src/modules/dashboard/components/NextActionPanel.jsx
import React from 'react';
import { Target, ArrowRight, CheckCircle2 } from 'lucide-react';

export default function NextActionPanel({ primaryAction, onNavigate }) {
  if (!primaryAction) return null;

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 p-6 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-5">
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 rounded-xl bg-amber-50 text-amber-600 border border-amber-200 flex items-center justify-center shrink-0 mt-0.5">
          <Target className="w-6 h-6" />
        </div>
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-amber-700 bg-amber-50 px-2.5 py-0.5 rounded-md border border-amber-200">
            Next Best Action
          </span>
          <h3 className="text-lg font-bold text-slate-900 mt-1">
            {primaryAction.title}
          </h3>
          <p className="text-sm text-slate-600 mt-1 leading-relaxed">
            {primaryAction.description}
          </p>
        </div>
      </div>

      <button
        onClick={() => onNavigate(primaryAction.targetView, primaryAction.targetPath)}
        className="px-5 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold shadow-xs transition flex items-center justify-center gap-2 cursor-pointer shrink-0 min-h-[48px]"
      >
        <span>{primaryAction.actionLabel}</span>
        <ArrowRight className="w-4 h-4" />
      </button>
    </div>
  );
}
