// frontend/src/modules/dashboard/components/WelcomeSection.jsx
import React from 'react';
import { Sparkles, ArrowRight } from 'lucide-react';

export default function WelcomeSection({ lifecycleState, primaryAction, onNavigate }) {
  return (
    <div className="bg-gradient-to-r from-blue-900 via-indigo-900 to-slate-900 rounded-2xl p-6 sm:p-8 text-white shadow-xl relative overflow-hidden">
      <div className="absolute right-0 top-0 translate-x-8 -translate-y-8 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />
      
      <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-500/20 border border-blue-400/30 text-blue-200 text-xs sm:text-sm font-semibold">
            <Sparkles className="w-4 h-4 text-amber-400" />
            <span>Workspace Lifecycle: {lifecycleState.replace(/_/g, ' ')}</span>
          </div>
        </div>

        {primaryAction && (
          <div className="shrink-0">
            <button
              onClick={() => onNavigate(primaryAction.targetView, primaryAction.targetPath)}
              className="px-6 py-3.5 rounded-xl bg-[#ec7211] hover:bg-[#eb5f07] text-white font-semibold shadow-lg transition flex items-center gap-2.5 cursor-pointer min-h-[48px]"
            >
              <span>{primaryAction.actionLabel}</span>
              <ArrowRight className="w-5 h-5" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
