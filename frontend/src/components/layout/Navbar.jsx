// frontend/src/components/layout/Navbar.jsx
import React from 'react';

export default function Navbar({ activeView }) {
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
    <header className="sticky top-0 z-20 h-14 bg-white/95 backdrop-blur-md border-b border-slate-200/80 px-4 sm:px-6 flex items-center min-w-0">
      <span className="font-bold text-slate-900 tracking-tight text-sm sm:text-base truncate">
        {currentTitle}
      </span>
    </header>
  );
}
