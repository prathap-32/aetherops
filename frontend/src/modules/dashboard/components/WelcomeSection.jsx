// frontend/src/modules/dashboard/components/WelcomeSection.jsx
import React from 'react';
import { ArrowRight } from 'lucide-react';

export default function WelcomeSection({ user, lifecycleState, primaryAction, onNavigate }) {
  const displayName = user?.username || 'Cloud Operator';

  let headingText = `Welcome back to AetherOps, ${displayName}`;
  let descriptionText = "Pick up where you left off and continue managing your projects.";
  let ctaLabel = primaryAction?.actionLabel || "View Projects";
  let targetView = primaryAction?.targetView || 'projects';
  let targetPath = primaryAction?.targetPath || '/project-environment';

  if (lifecycleState === 'STATE_A_NEW_USER') {
    headingText = `Welcome to AetherOps, ${displayName}`;
    descriptionText = "Let's get your workspace set up and ready for your first project.";
    ctaLabel = "Create Project";
    targetView = "projects";
    targetPath = "/project-environment";
  } else if (lifecycleState === 'STATE_B_CONNECTION_SETUP') {
    headingText = `Welcome back to AetherOps, ${displayName}`;
    descriptionText = "Your workspace is ready. Connect your source repository and cloud account to continue.";
    ctaLabel = "Connect Accounts";
    targetView = "source_cloud";
    targetPath = "/source-connection";
  } else if (lifecycleState === 'STATE_C_READY_FOR_ANALYSIS') {
    headingText = `Welcome back to AetherOps, ${displayName}`;
    descriptionText = "Your source and cloud connections are ready. Continue with source analysis.";
    ctaLabel = "Continue";
    targetView = "repo_analyzer";
    targetPath = "/source-analysis";
  }

  return (
    <div className="bg-gradient-to-r from-blue-900 via-indigo-900 to-slate-900 rounded-2xl p-6 sm:p-8 text-white shadow-xl relative overflow-hidden">
      <div className="absolute right-0 top-0 translate-x-8 -translate-y-8 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />
      
      <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
        <div className="space-y-2">
          <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            {headingText}
          </h2>
          <p className="text-slate-300 text-sm sm:text-base max-w-2xl leading-relaxed">
            {descriptionText}
          </p>
        </div>

        {primaryAction && (
          <div className="shrink-0">
            <button
              onClick={() => onNavigate(targetView, targetPath)}
              className="px-6 py-3.5 rounded-xl bg-[#ec7211] hover:bg-[#eb5f07] text-white font-semibold shadow-lg transition flex items-center gap-2.5 cursor-pointer min-h-[48px]"
            >
              <span>{ctaLabel}</span>
              <ArrowRight className="w-5 h-5" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
