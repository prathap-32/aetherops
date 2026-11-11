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
  return (
    <header className="sticky top-0 z-20 h-16 lg:h-18 bg-white/95 backdrop-blur-md border-b border-slate-200/80 px-4 sm:px-8 flex items-center justify-between min-w-0 transition-colors shadow-2xs">
      {/* Left: Hamburger (Mobile) + Global Brand Logo */}
      <div className="flex items-center gap-3 sm:gap-4 min-w-0">
        {/* Mobile Hamburger Toggle Button */}
        <button
          type="button"
          onClick={onToggleMobileSidebar}
          className="lg:hidden p-2.5 -ml-1 text-slate-700 hover:text-slate-900 rounded-xl hover:bg-slate-100 transition cursor-pointer flex items-center justify-center shrink-0 min-h-[44px] min-w-[44px]"
          aria-label="Open Navigation Menu"
          title="Toggle Navigation Menu"
        >
          <Menu className="w-6 h-6" />
        </button>

        {/* Global Brand Logo (Logo contains text; anti-download protected) */}
        <div
          className="flex items-center shrink-0 select-none cursor-pointer"
          onClick={() => onNavigate && onNavigate('dashboard', '/')}
          title="AetherOps Cloud Platform"
          onContextMenu={(e) => e.preventDefault()}
        >
          <img
            src="/static/logo/aetherops_light_transparent.webp"
            alt="AetherOps Logo"
            className="h-9 max-w-[160px] w-auto object-contain object-left select-none pointer-events-none"
            draggable={false}
            onContextMenu={(e) => e.preventDefault()}
            style={{
              WebkitUserDrag: 'none',
              userSelect: 'none',
              WebkitTouchCallout: 'none',
              pointerEvents: 'none',
            }}
          />
        </div>

        {activeProject && (
          <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-blue-50 border border-blue-200/85 text-blue-900 text-sm font-medium ml-2">
            <span className="w-2 h-2 rounded-full bg-blue-600" />
            <span className="truncate max-w-[180px]">{activeProject.name}</span>
          </div>
        )}
      </div>

      {/* Right: Quick Account Info & Actions */}
      <div className="flex items-center gap-3 sm:gap-4 shrink-0">
        {user?.account_id && (
          <div
            className="hidden sm:flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-slate-50 border border-slate-200/80 text-slate-700 text-sm font-mono shadow-2xs"
            title={`Account: ${formatAccountId(user.account_id)}`}
          >
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="font-medium text-slate-800">
              {formatAccountId(user.account_id)}
            </span>
          </div>
        )}

        {user?.role && (
          <span className="hidden lg:inline-flex items-center px-2.5 py-1 rounded-md text-xs font-semibold uppercase tracking-wider bg-slate-100 text-slate-700 border border-slate-200">
            {user.role}
          </span>
        )}

        {/* Account Profile Trigger Button */}
        <button
          type="button"
          onClick={onOpenAccountModal}
          className="flex items-center gap-2.5 p-1.5 rounded-xl hover:bg-slate-100 transition cursor-pointer min-h-[44px]"
          title="Account Profile & Sessions"
        >
          <div className="w-10 h-10 rounded-full bg-[#1e40af] text-white flex items-center justify-center font-bold font-mono text-sm shadow-xs shrink-0">
            {user?.username ? user.username.slice(0, 2).toUpperCase() : 'AO'}
          </div>
        </button>
      </div>
    </header>
  );
}
