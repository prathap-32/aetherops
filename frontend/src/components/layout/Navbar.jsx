// frontend/src/components/layout/Navbar.jsx
import React from 'react';
import { Menu } from 'lucide-react';

export default function Navbar({
  activeView,
  onOpenMobileSidebar,
}) {
  const VIEW_TITLES = {
    dashboard: 'Platform Dashboard',
    projects: 'Projects & Workspaces',
    environments: 'Target Environments Fleet',
    source_cloud: 'Source & Cloud Connection',
    repo_analyzer: 'Source Code Analyzer',
    architecture: 'Cloud Architecture Studio',
    architecture_studio: 'Cloud Architecture Studio',
    architecture_designer: 'Architecture Designer',
    risk_analysis: 'Pre-Deployment Risk Engine',
    architecture_validation: 'Architecture Validation',
    security: 'Architecture Validation',
    iac: 'Infrastructure as Code Synthesizer',
    execution: 'Approval & Execution Gate',
    deployments: 'Application Deployments & Drift',
    cicd: 'CI/CD GitOps Pipeline',
    monitoring: 'Infrastructure Monitoring & APM',
    optimization: 'Continuous Risk & FinOps',
    audit: 'Audit & Operations History',
    docs: 'Platform Documentation',
    settings: 'Platform Settings',
    admin: 'Administration Console',
  };

  const currentTitle = VIEW_TITLES[activeView] || 'Console';

  return (
    <header className="sticky top-0 z-20 h-14 bg-white/95 backdrop-blur-md border-b border-slate-200/80 px-4 sm:px-6 flex items-center justify-between gap-4">
      {/* Left: Mobile hamburger & Module Title only */}
      <div className="flex items-center gap-3 min-w-0">
        <button
          onClick={onOpenMobileSidebar}
          className="p-1.5 -ml-1 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition cursor-pointer"
          aria-label="Toggle sidebar menu"
          title="Toggle sidebar menu (Expand text / Show icons only)"
        >
          <Menu className="w-5 h-5" />
        </button>

        <span className="font-bold text-slate-900 tracking-tight text-sm sm:text-base truncate">
          {currentTitle}
        </span>
      </div>
    </header>
  );
}
