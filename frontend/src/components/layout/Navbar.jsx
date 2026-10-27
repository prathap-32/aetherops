// frontend/src/components/layout/Navbar.jsx
import React, { useState } from 'react';
import { Menu, Search, Plus, FolderKanban, Boxes, Key, Copy, Check, User } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { formatAccountId } from '../../services/api';

export default function Navbar({
  activeView,
  onOpenMobileSidebar,
  onOpenCreateProject,
  searchQuery,
  setSearchQuery,
  activeProject,
  activeEnvironment,
  onOpenAccountModal,
  onOpenAccount,
}) {
  const { user, isAdmin } = useAuth();
  const [copiedAccount, setCopiedAccount] = useState(false);
  const handleOpenAccount = onOpenAccountModal || onOpenAccount || (() => {});
  const initials = (user?.username || 'AO').slice(0, 2).toUpperCase();

  const copyAccountId = () => {
    const acc = user?.account_id || '109283746519';
    if (navigator.clipboard) {
      navigator.clipboard.writeText(acc);
      setCopiedAccount(true);
      setTimeout(() => setCopiedAccount(false), 2000);
    }
  };

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
          <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 text-[10px] font-mono border border-slate-200/80">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>us-east-1 (N. Virginia)</span>
          </div>
        </div>
      </div>

      {/* Center / Right: AWS Account ID Showcase, Search & Actions */}
      <div className="flex items-center gap-2 sm:gap-3">
        {/* Prominent AWS Account ID Showcase */}
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-amber-50/90 text-amber-900 text-xs font-mono border border-amber-200/90 shadow-xs">
          <Key className="w-3.5 h-3.5 text-amber-600 shrink-0" />
          <span className="font-semibold text-amber-950 hidden xs:inline">Account:</span>
          <span className="font-bold text-amber-900">
            {formatAccountId(user?.account_id || '109283746519')}
          </span>
          <button
            onClick={copyAccountId}
            title={copiedAccount ? 'Copied Account ID!' : 'Copy AWS Account ID'}
            className="p-1 hover:bg-amber-100 rounded text-amber-700 transition cursor-pointer"
          >
            {copiedAccount ? (
              <Check className="w-3.5 h-3.5 text-emerald-600" />
            ) : (
              <Copy className="w-3.5 h-3.5 text-amber-700 hover:text-amber-900" />
            )}
          </button>
        </div>

        {/* Search */}
        <div className="relative w-32 sm:w-48 lg:w-56">
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
            <span className="hidden sm:inline">New Project</span>
          </button>
        )}

        {/* Top-Right Corner Account Page & Profile Access Button */}
        <button
          onClick={handleOpenAccount}
          title={`Account: ${user?.username || 'user'} (${formatAccountId(user?.account_id || '109283746519')}) - Click to access Account settings`}
          className="flex items-center gap-2 pl-1.5 pr-2.5 py-1 rounded-xl bg-slate-100 hover:bg-slate-200/80 border border-slate-200/90 transition group cursor-pointer text-left shrink-0 shadow-xs"
          aria-label="Open Account Profile & Settings"
        >
          <div className="w-7 h-7 rounded-lg bg-[#1e40af] text-white flex items-center justify-center font-bold font-mono text-xs shadow-xs group-hover:scale-105 transition">
            {initials}
          </div>
          <div className="hidden sm:block text-left leading-tight">
            <div className="text-xs font-bold text-slate-800 flex items-center gap-1.5">
              <span>{user?.username || 'User'}</span>
              <span
                className={`px-1.5 py-0.2 rounded text-[9px] font-mono font-bold uppercase border ${
                  isAdmin
                    ? 'bg-amber-100 text-amber-900 border-amber-300'
                    : 'bg-emerald-100 text-emerald-900 border-emerald-300'
                }`}
              >
                {user?.role || 'USER'}
              </span>
            </div>
            <div className="text-[10px] font-mono text-slate-500">
              Account
            </div>
          </div>
          <User className="w-3.5 h-3.5 text-slate-400 group-hover:text-slate-600 sm:hidden" />
        </button>
      </div>
    </header>
  );
}
