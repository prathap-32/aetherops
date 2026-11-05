// frontend/src/components/layout/Sidebar.jsx
import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { formatAccountId } from '../../services/api';
import {
  LayoutDashboard,
  FolderKanban,
  Boxes,
  GitBranch,
  FileCode2,
  Network,
  Palette,
  ShieldAlert,
  CheckCircle2,
  Code2,
  CheckSquare,
  Rocket,
  GitFork,
  Activity,
  DollarSign,
  History,
  FileText,
  ShieldCheck,
  LogOut,
  Settings,
  ChevronDown,
  ChevronRight,
  X,
  Menu,
} from 'lucide-react';

const NAV_GROUPS = [
  {
    name: 'CORE WORKFLOW',
    items: [
      { id: 'dashboard', path: '/', label: 'Overview', icon: LayoutDashboard },
      { id: 'source_cloud', path: '/source-connection', label: '1. Connect AWS & Git', icon: GitBranch },
      { id: 'architecture_designer', path: '/architecture-designer', label: '2. Cloud Architecture', icon: Network },
      { id: 'iac', path: '/terraform', label: '3. Terraform Code', icon: Code2 },
      { id: 'execution', path: '/execution', label: '4. Plan & Approval', icon: CheckSquare },
      { id: 'deployments', path: '/deployment', label: '5. Deploy Infrastructure', icon: Rocket },
      { id: 'cicd', path: '/cicd', label: '6. CI/CD Pipelines', icon: GitFork },
      { id: 'monitoring', path: '/monitoring', label: '7. Live Monitoring', icon: Activity },
      { id: 'optimization', path: '/optimization', label: '8. FinOps Optimizer', icon: DollarSign },
    ],
  },
  {
    name: 'MANAGEMENT & WORKSPACES',
    items: [
      { id: 'projects', path: '/projects', label: 'Projects & Workspaces', icon: FolderKanban },
      { id: 'environments', path: '/environments', label: 'Environments', icon: Boxes },
      { id: 'security', path: '/security', label: 'Security & Compliance', icon: ShieldCheck },
      { id: 'audit', path: '/audit', label: 'Audit Log', icon: History },
      { id: 'docs', path: '/documentation', label: 'Documentation', icon: FileText },
      { id: 'settings', path: '/settings', label: 'Account Settings', icon: Settings },
    ],
  },
];

export default function Sidebar({
  activeView,
  activeItem,
  setActiveView,
  onNavigate,
  mobileOpen = false,
  setMobileOpen,
  onOpenAccountModal,
  onOpenAccount,
}) {
  const { user, isAdmin, logout } = useAuth();
  const currentView = activeView || activeItem || 'projects';
  const handleNavigation = setActiveView || onNavigate || (() => {});
  const handleOpenAccount = onOpenAccountModal || onOpenAccount || (() => {});

  // Collapsible category state (used when text is expanded)
  const [collapsedGroups, setCollapsedGroups] = useState({});

  const toggleGroup = (groupName) => {
    setCollapsedGroups((prev) => ({
      ...prev,
      [groupName]: !prev[groupName],
    }));
  };

  const navItemClick = (viewId, path) => {
    handleNavigation(viewId, path);
    // Auto-close full text overlay on mobile after clicking an item
    if (setMobileOpen) {
      setMobileOpen(false);
    }
  };

  const initials = (user?.username || 'AO').slice(0, 2).toUpperCase();

  return (
    <>
      {/* ─────────────────────────────────────────────────────────── */}
      {/* Backdrop overlay: visible on mobile when sidebar is expanded */}
      {/* ─────────────────────────────────────────────────────────── */}
      {mobileOpen && (
        <div
          className="fixed inset-0 bg-slate-900/40 z-30 lg:hidden backdrop-blur-xs transition-opacity duration-200"
          onClick={() => setMobileOpen && setMobileOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* ─────────────────────────────────────────────────────────── */}
      {/* Collapsed State: Icon-Only Rail (Always visible)           */}
      {/* ─────────────────────────────────────────────────────────── */}
      <aside
        className={`flex flex-col h-full justify-between select-none bg-white border-r border-slate-200/80 transition-all duration-200 shrink-0 z-20 ${
          mobileOpen ? 'hidden lg:flex w-16' : 'w-16'
        }`}
        aria-label="Compact Sidebar"
      >
        {/* Top: Compact Icon Logo */}
        <div>
          <div className="h-14 border-b border-slate-100 flex items-center justify-center">
            <button
              onClick={() => {
                if (setMobileOpen) setMobileOpen(true);
                else navItemClick('dashboard', '/');
              }}
              className="w-9 h-9 rounded-xl bg-[#1e40af] text-white flex items-center justify-center font-bold text-xs shadow-xs hover:bg-blue-800 transition cursor-pointer group select-none"
              title="Click to expand sidebar and show text"
              aria-label="Expand sidebar"
              onContextMenu={(e) => e.preventDefault()}
            >
              <img
                src="/static/logo/logo.png"
                alt="AetherOps"
                className="w-6 h-6 object-contain select-none pointer-events-none drop-shadow-xs"
                draggable={false}
                onContextMenu={(e) => e.preventDefault()}
                style={{ WebkitUserDrag: 'none', userSelect: 'none' }}
                width="24"
                height="24"
              />
            </button>
          </div>

          {/* Navigation Icon List */}
          <div className="px-2 py-3 space-y-2 overflow-y-auto max-h-[calc(100vh-130px)] no-scrollbar">
            {NAV_GROUPS.map((group, gIdx) => (
              <div key={group.name} className="space-y-1.5">
                {gIdx > 0 && <div className="h-px bg-slate-100 my-2 mx-1" />}
                {group.items.map((item) => {
                  const Icon = item.icon;
                  const isActive = currentView === item.id;
                  return (
                    <button
                      key={item.id}
                      onClick={() => navItemClick(item.id, item.path)}
                      className={`w-10 h-10 mx-auto rounded-xl flex items-center justify-center transition duration-150 cursor-pointer ${
                        isActive
                          ? 'bg-[#1e40af] text-white shadow-xs font-semibold'
                          : 'text-slate-400 hover:text-slate-800 hover:bg-slate-100'
                      }`}
                      title={item.label}
                      aria-label={item.label}
                    >
                      <Icon className="w-4 h-4 shrink-0" />
                    </button>
                  );
                })}
              </div>
            ))}

            {/* Admin Icon */}
            {isAdmin && (
              <div className="pt-2 border-t border-slate-100 mt-2">
                <button
                  onClick={() => navItemClick('admin', '/admin')}
                  className={`w-10 h-10 mx-auto rounded-xl flex items-center justify-center transition cursor-pointer ${
                    currentView === 'admin'
                      ? 'bg-blue-900 text-white shadow-xs font-semibold'
                      : 'text-blue-600 bg-blue-50/70 hover:bg-blue-100 border border-blue-200/60'
                  }`}
                  title="Admin Console (Privileged)"
                  aria-label="Admin Console"
                >
                  <ShieldCheck className="w-4 h-4 shrink-0" />
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Bottom User Avatar Icon & Settings (No Sign Out) */}
        <div className="p-2 border-t border-slate-100 bg-slate-50/70 flex flex-col items-center gap-2">
          <button
            onClick={handleOpenAccount}
            className="w-8 h-8 rounded-full bg-[#1e40af] text-white flex items-center justify-center font-bold font-mono text-xs shadow-xs hover:scale-105 transition cursor-pointer"
            title={`Account: ${user?.username || 'user'} (${formatAccountId(user?.account_id || '109283746519')})`}
            aria-label="Open Account Profile"
          >
            {initials}
          </button>
          <button
            onClick={() => navItemClick('settings', '/settings')}
            className={`p-1.5 rounded-lg transition shrink-0 cursor-pointer ${
              currentView === 'settings' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-slate-700 hover:bg-slate-200/60'
            }`}
            title="User & Credential Settings (AWS & GitHub)"
            aria-label="User & Credential Settings"
          >
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </aside>

      {/* ─────────────────────────────────────────────────────────── */}
      {/* Expanded State: Full Sidebar with Text                     */}
      {/* Visible on Mobile/Desktop when hamburger menu is toggled    */}
      {/* ─────────────────────────────────────────────────────────── */}
      {mobileOpen && (
        <aside
          className="fixed inset-y-0 left-0 z-40 w-64 bg-white border-r border-slate-200/80 shadow-2xl flex flex-col h-full justify-between select-none transition-all duration-200 ease-in-out shrink-0"
          aria-label="Expanded Navigation Sidebar"
        >
          {/* Top Header & Branding with 'X' Close Button */}
          <div>
            <div className="h-14 px-4 border-b border-slate-100 flex items-center justify-between">
              <div
                onClick={() => navItemClick('dashboard', '/')}
                className="cursor-pointer group flex items-center gap-2"
              >
                <picture>
                  <source srcSet="/static/logo/aetherops_transparent.webp" type="image/webp" />
                  <img
                    src="/static/logo/aetherops_transparent.png"
                    alt="AetherOps"
                    className="h-8 max-w-[170px] object-contain object-left transition-opacity group-hover:opacity-90"
                    width="170"
                    height="43"
                  />
                </picture>
              </div>

              {/* Close Button 'X' */}
              <button
                onClick={() => setMobileOpen && setMobileOpen(false)}
                className="p-1.5 text-slate-400 hover:text-slate-700 rounded-lg hover:bg-slate-100 cursor-pointer transition"
                aria-label="Close sidebar (show icons only)"
                title="Close (collapse to icons only)"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Scrollable Navigation Groups with Full Text Labels */}
            <div className="px-3 py-3 space-y-4 overflow-y-auto max-h-[calc(100vh-140px)]">
              {NAV_GROUPS.map((group) => {
                const isCollapsed = Boolean(collapsedGroups[group.name]);
                return (
                  <div key={group.name} className="space-y-1">
                    <div
                      onClick={() => toggleGroup(group.name)}
                      className="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1.5 flex items-center justify-between cursor-pointer hover:text-slate-600"
                    >
                      <span>{group.name}</span>
                      {isCollapsed ? (
                        <ChevronRight className="w-3 h-3" />
                      ) : (
                        <ChevronDown className="w-3 h-3" />
                      )}
                    </div>

                    {!isCollapsed && (
                      <div className="space-y-1">
                        {group.items.map((item) => {
                          const Icon = item.icon;
                          const isActive = currentView === item.id;
                          return (
                            <button
                              key={item.id}
                              onClick={() => navItemClick(item.id, item.path)}
                              className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-medium transition duration-150 text-left cursor-pointer ${
                                isActive
                                  ? 'bg-[#1e40af] text-white shadow-xs font-semibold'
                                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                              }`}
                            >
                              <div className="flex items-center gap-2.5 min-w-0">
                                <Icon
                                  className={`w-4 h-4 shrink-0 ${
                                    isActive ? 'text-white' : 'text-slate-400 group-hover:text-slate-600'
                                  }`}
                                />
                                <span className="truncate">{item.label}</span>
                              </div>
                            </button>
                          );
                        })}
                      </div>
                    )}
                  </div>
                );
              })}

              {/* Administration Section */}
              {isAdmin && (
                <div className="pt-2 border-t border-slate-100 mt-2 space-y-1">
                  <div className="px-3 text-[10px] font-bold uppercase tracking-wider text-blue-600 mb-1 flex items-center gap-1">
                    <span>ADMINISTRATION</span>
                  </div>
                  <button
                    onClick={() => navItemClick('admin', '/admin')}
                    className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-medium transition text-left cursor-pointer ${
                      currentView === 'admin'
                        ? 'bg-blue-900 text-white shadow-xs font-semibold'
                        : 'text-blue-950 bg-blue-50/70 hover:bg-blue-100/70 border border-blue-200/60'
                    }`}
                  >
                    <div className="flex items-center gap-2.5">
                      <ShieldCheck
                        className={`w-4 h-4 shrink-0 ${
                          currentView === 'admin' ? 'text-white' : 'text-blue-600'
                        }`}
                      />
                      <span className="truncate">Admin Console</span>
                    </div>
                    <span
                      className={`text-[9px] font-bold font-mono px-1.5 py-0.5 rounded uppercase ${
                        currentView === 'admin' ? 'bg-white/20 text-white' : 'bg-blue-100 text-[#1e40af]'
                      }`}
                    >
                      Privileged
                    </span>
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Expanded Bottom User Account Footer */}
          {/* Expanded Bottom User Account Footer with Settings Anchor */}
          <div className="p-3 border-t border-slate-100 bg-slate-50/70 flex items-center justify-between gap-2">
            <div
              onClick={handleOpenAccount}
              className="flex items-center gap-2.5 min-w-0 cursor-pointer p-1 rounded-lg hover:bg-slate-200/60 transition group flex-1"
              title="Click to manage account profile"
            >
              <div className="w-8 h-8 rounded-full bg-[#1e40af] text-white flex items-center justify-center font-bold font-mono text-xs shadow-xs group-hover:scale-105 transition shrink-0">
                {initials}
              </div>
              <div className="min-w-0 flex-1">
                <div className="text-xs font-bold text-slate-800 truncate">
                  {user?.username || 'developer'}
                </div>
                <div className="text-[10px] text-slate-500 truncate">
                  {user?.email || 'user@aetherops.cloud'}
                </div>
              </div>
            </div>

            <button
              onClick={() => navItemClick('settings', '/settings')}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition shrink-0 cursor-pointer flex items-center gap-1.5 shadow-xs ${
                currentView === 'settings'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-100'
              }`}
              title="Visit User Settings & Credential Manager"
            >
              <Settings className="w-3.5 h-3.5" />
              <span>Settings</span>
            </button>
          </div>
        </aside>
      )}
    </>
  );
}
