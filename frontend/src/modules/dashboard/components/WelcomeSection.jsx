// frontend/src/modules/dashboard/components/WelcomeSection.jsx
import React, { useEffect } from 'react';
import { Sparkles, ArrowRight } from 'lucide-react';

export default function WelcomeSection({ user, lifecycleState, primaryAction, onNavigate }) {
  const isFirstTimeUser = lifecycleState === 'L00_FIRST_VISIT' || (user && user.has_seen_welcome === 0);

  useEffect(() => {
    if (isFirstTimeUser) {
      // Acknowledge welcome state on server so returning visits display "Welcome back"
      fetch('/api/v1/auth/ack-welcome', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
      }).catch(() => {});
    }
  }, [isFirstTimeUser]);

  return (
    <div className="bg-gradient-to-r from-blue-900 via-indigo-900 to-slate-900 rounded-2xl p-6 sm:p-8 text-white shadow-xl relative overflow-hidden">
      <div className="absolute right-0 top-0 translate-x-8 -translate-y-8 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />
      
      <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/20 border border-blue-400/30 text-blue-200 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            <span>Workspace Lifecycle: {lifecycleState.replace(/_/g, ' ')}</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            {isFirstTimeUser ? `Welcome to AetherOps, ${user?.username || 'Cloud Operator'}` : `Welcome back, ${user?.username || 'Cloud Operator'}`}
          </h2>
          <p className="text-slate-300 text-sm sm:text-base max-w-2xl leading-relaxed">
            AetherOps is continuously monitoring your multi-cloud workspace boundaries, IAM security posture, and Terraform synthesis pipelines.
          </p>
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
