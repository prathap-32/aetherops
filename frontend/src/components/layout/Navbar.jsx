// frontend/src/components/layout/Navbar.jsx
import React from 'react';
import { Menu, Search, Plus, FolderKanban, Boxes, ExternalLink, Globe, ChevronDown } from 'lucide-react';

export default function Navbar({
  activeView,
  onOpenMobileSidebar,
  onOpenCreateProject,
  searchQuery,
  setSearchQuery,
  activeProject,
  activeEnvironment,
}) {
  const VIEW_TITLES = {
    dashboard: 'Platform Dashboard Overview',
    projects: 'Projects & Workspaces',
    environments: 'Target Environments Fleet',
    source_cloud: 'Source & Cloud Connection (Module 2)',
    repo_analyzer: 'Source Code Analyzer (Module 1 / 3)',
    architecture: 'AI Architecture Engine (Module 2)',
    architecture_designer: 'Architecture Designer Canvas',
    risk_analysis: 'Pre-Deployment Risk Engine',
    architecture_validation: 'Architecture Policy Validation',
    iac: 'Terraform / IaC Synthesizer (Module 3)',
    execution: 'Approval & Execution Gate',
    deployments: 'Application Deployment & Drift (Module 8)',
    cicd: 'CI/CD GitOps Pipeline (Module 6)',
    monitoring: 'Infrastructure Monitoring & APM (Module 7)',
    optimization: 'Continuous Risk & FinOps (Module 4)',
    audit: 'Audit & Operations History',
    docs: 'Documentation & System Blueprint',
    settings: 'Platform Settings',
    admin: 'Privileged Administration Console',
  };

  const currentTitle = VIEW_TITLES[activeView] || 'Console';

  return (
    <header className="sticky top-0 z-20 h-14 bg-white/95 backdrop-blur-md border-b border-slate-200/80 px-4 sm:px-6 flex items-center justify-between gap-4">
      {/* Left: Mobile hamburger & breadcrumbs */}
      <div className="flex items-center gap-3 min-w-0">
        <button
          onClick={onOpenMobileSidebar}
          className="lg:hidden p-1.5 -ml-1 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition cursor-pointer"
          aria-label="Toggle menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2 text-xs text-slate-500 truncate">
          <span className="font-semibold text-slate-900 tracking-tight">{currentTitle}</span>
          <span className="hidden sm:inline text-slate-300">/</span>

          {/* Active Project Context Badge */}
          <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 text-[11px] font-mono border border-slate-200/80">
            <FolderKanban className="w-3 h-3 text-blue-600" />
            <span className="font-bold text-slate-900 truncate max-w-[120px]">
              {activeProject?.name || 'All Projects'}
            </span>
          </div>

          {/* Active Environment Context Badge */}
          {activeEnvironment && (
            <div className="hidden md:flex items-center gap-1 px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 text-[10px] font-mono border border-indigo-200">
              <Boxes className="w-2.5 h-2.5" />
              <span>{activeEnvironment.name}</span>
            </div>
          )}

          {/* Default Region Badge */}
          <div className="hidden lg:flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 text-[10px] font-mono border border-slate-200/80">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>us-east-1 (N. Virginia)</span>
          </div>
        </div>
      </div>

      {/* Center / Right: Search & Actions */}
      <div className="flex items-center gap-2 sm:gap-3">
        {/* Search */}
        <div className="relative w-36 sm:w-60">
          <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search resources..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-8 pr-3 py-1.5 text-xs rounded-lg border border-slate-200 bg-slate-50 focus:bg-white text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-[#1e40af] focus:ring-1 focus:ring-[#1e40af] transition"
          />
        </div>

        {/* New Project Quick Action Button */}
        {onOpenCreateProject && (
          <button
            onClick={onOpenCreateProject}
            className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-[#1e40af] hover:bg-[#1d4ed8] text-white shadow-xs transition flex items-center gap-1.5 cursor-pointer shrink-0"
          >
            <Plus className="w-3.5 h-3.5" />
            <span className="hidden xs:inline">New Project</span>
          </button>
        )}
      </div>
    </header>
  );
}
