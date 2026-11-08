// frontend/src/components/layout/Navbar.jsx
import React from 'react';
import { Menu } from 'lucide-react';
import { formatAccountId } from '../../services/api';

export default function Navbar({
  activeView,
  onToggleMobileSidebar,
  user,
  activeProject,
  onOpenAccountModal,
  onNavigate,
}) {
  const VIEW_TITLES = {
    dashboard: 'Platform Dashboard',
    project_environment: 'Project and Environment',
    projects: 'Projects',
    environments: 'Environment',
    source_cloud: 'Connect Cloud and Git',
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
    audit: 'Security & Session Audit',
    docs: 'Platform Documentation',
    settings: 'Platform Settings',
    admin: 'Administration Console',
  };

  const currentTitle = VIEW_TITLES[activeView] || 'Console';

  const initials = (user?.username || 'AO').slice(0, 2).toUpperCase();

  return (
    <header className="sticky top-0 z-20 h-14 bg-white/95 backdrop-blur-md border-b border-slate-200/80 px-3.5 sm:px-6 flex items-center justify-between min-w-0 transition-colors">
      {/* Left: Hamburger (Mobile) + Brand/Page Title */}
      <div className="flex items-center gap-2.5 sm:gap-3.5 min-w-0">
        {/* Mobile Hamburger Toggle Button */}
        <button
          type="button"
          onClick={onToggleMobileSidebar}
          className="lg:hidden p-2 -ml-1 text-slate-600 hover:text-slate-900 rounded-lg hover:bg-slate-100 transition cursor-pointer flex items-center justify-center shrink-0"
          aria-label="Open Navigation Menu"
          title="Toggle Navigation Menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Mobile Brand Icon (Anti-download protected) */}
        <div
          className="lg:hidden flex items-center shrink-0 select-none pointer-events-none"
          onContextMenu={(e) => e.preventDefault()}
        >
          <img
            src="/static/logo/aetherops_light_icon.png"
            alt="AetherOps"
            className="w-6 h-6 object-contain select-none pointer-events-none"
            draggable={false}
            onContextMenu={(e) => e.preventDefault()}
            style={{
              WebkitUserDrag: 'none',
              userSelect: 'none',
              WebkitTouchCallout: 'none',
              pointerEvents: 'none',
            }}
            width="24"
            height="24"
          />
        </div>

        {/* View Title */}
        <div className="flex items-center gap-2 min-w-0">
          <span className="font-bold text-slate-900 tracking-tight text-sm sm:text-base truncate">
            {currentTitle}
          </span>

        </div>
      </div>

      {/* Right: Quick Account Info & Actions */}
      <div className="flex items-center gap-2 sm:gap-3 shrink-0">
        {/* Account ID Badge */}
        {user?.account_id && (
          <div
            className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-50 border border-slate-200/80 text-slate-600 text-[11px] font-mono shadow-2xs"
            title={`Account: ${formatAccountId(user.account_id)}`}
          >
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
            <span className="font-semibold text-slate-700">
              {formatAccountId(user.account_id)}
            </span>
          </div>
        )}

        {/* User Role Tag (Desktop/PC) */}
        {user?.role && (
          <span className="hidden lg:inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-slate-100 text-slate-600 border border-slate-200">
            {user.role}
          </span>
        )}

        {/* User Profile Avatar Button */}
        <button
          type="button"
          onClick={onOpenAccountModal}
          className="w-8 h-8 rounded-full bg-[#1e40af] hover:bg-[#1d4ed8] text-white flex items-center justify-center font-bold font-mono text-xs shadow-xs hover:scale-105 transition cursor-pointer shrink-0"
          title={`Logged in as ${user?.username || 'User'} — click to edit profile`}
          aria-label="User Account Profile"
        >
          {initials}
        </button>
      </div>
    </header>
  );
}
