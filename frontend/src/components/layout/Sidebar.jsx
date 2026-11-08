// frontend/src/components/layout/Sidebar.jsx
import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { formatAccountId } from '../../services/api';
import {
  LayoutDashboard,
  FolderKanban,
  GitBranch,
  FileCode2,
  Network,
  Code2,
  Rocket,
  Settings,
  ShieldCheck,
  ChevronDown,
  ChevronRight,
  X,
  PanelLeftClose,
  PanelLeftOpen,
} from 'lucide-react';

const NAV_GROUPS = [
  {
    name: 'CORE DEVOPS PIPELINE',
    items: [
      { id: 'dashboard', path: '/', label: 'Overview Dashboard', icon: LayoutDashboard },
      { id: 'project_environment', path: '/project-environment', label: 'Project and Environment', icon: FolderKanban },
      { id: 'source_cloud', path: '/source-connection', label: 'Connect Cloud and Git', icon: GitBranch },
      { id: 'repo_analyzer', path: '/source-analysis', label: 'Source Code Analyzer', icon: FileCode2 },
      { id: 'architecture_studio', path: '/architecture-studio', label: 'AI AWS Architecture', icon: Network },
      { id: 'iac', path: '/terraform', label: 'Terraform HCL Synthesis', icon: Code2 },
      { id: 'deployments', path: '/deployment', label: 'AI Dry-Run & Approval Gate', icon: Rocket },
      { id: 'audit', path: '/audit', label: 'Security & Session Audit', icon: ShieldCheck },
      { id: 'settings', path: '/settings', label: 'User & Credential Settings', icon: Settings },
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
  const { user, isAdmin } = useAuth();
  const currentView = activeView || activeItem || 'projects';
  const handleNavigation = setActiveView || onNavigate || (() => {});
  const handleOpenAccount = onOpenAccountModal || onOpenAccount || (() => {});

  const isItemActive = (itemId) => {
    if (currentView === itemId) return true;
    if (itemId === 'project_environment' && (currentView === 'projects' || currentView === 'environments')) return true;
    return false;
  };
  // Collapsible category state (used when text is expanded)
  const [collapsedGroups, setCollapsedGroups] = useState({});

  // Desktop sidebar expand/collapse state (saved across sessions)
  const [desktopExpanded, setDesktopExpanded] = useState(() => {
    try {
      return localStorage.getItem('aether_sidebar_desktop_expanded') === 'true';
    } catch (e) {
      return false;
    }
  });

  const toggleDesktopExpanded = () => {
    setDesktopExpanded((prev) => {
      const next = !prev;
      try {
        localStorage.setItem('aether_sidebar_desktop_expanded', String(next));
      } catch (e) {}
      return next;
    });
  };

  const toggleGroup = (groupName) => {
    setCollapsedGroups((prev) => ({
      ...prev,
      [groupName]: !prev[groupName],
    }));
  };

  const navItemClick = (viewId, path) => {
    handleNavigation(viewId, path);
    // Auto-close overlay on mobile after clicking an item
    if (setMobileOpen) {
      setMobileOpen(false);
    }
  };

  const initials = (user?.username || 'AO').slice(0, 2).toUpperCase();
  return (
    <>
      {/* ─────────────────────────────────────────────────────────── */}
      {/* 1. Mobile Backdrop Overlay (only on mobile when open)        */}
      {/* ─────────────────────────────────────────────────────────── */}
      {mobileOpen && (
        <div
          className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs z-40 lg:hidden transition-opacity duration-200"
          onClick={() => setMobileOpen && setMobileOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* ─────────────────────────────────────────────────────────── */}
      {/* 2. Desktop Sidebar (Hidden on mobile <1024px, Flex on lg+)  */}
      {/* ─────────────────────────────────────────────────────────── */}
      <aside
        className={`hidden lg:flex flex-col h-full justify-between select-none bg-white border-r border-slate-200/80 transition-all duration-200 shrink-0 z-20 ${
          desktopExpanded ? 'w-64' : 'w-16'
        }`}
        aria-label="Desktop Navigation Sidebar"
      >
        {desktopExpanded ? (
          /* Expanded Desktop Mode (w-64) */
          <div className="flex flex-col h-full justify-between">
            <div>
              {/* Header with full logo and collapse button */}
              <div className="h-14 px-4 border-b border-slate-100 flex items-center justify-between">
                <div
                  onClick={() => navItemClick('dashboard', '/')}
                  className="cursor-pointer group flex items-center gap-2 select-none"
                >
                  <img
                    src="/static/logo/aetherops_light_full.png"
                    alt="AetherOps"
                    className="h-8 max-w-[160px] w-auto object-contain object-left transition-opacity group-hover:opacity-90 select-none pointer-events-none"
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
                <button
                  type="button"
                  onClick={toggleDesktopExpanded}
                  className="p-1.5 text-slate-400 hover:text-slate-700 rounded-lg hover:bg-slate-100 cursor-pointer transition"
                  title="Collapse sidebar to icon-only"
                  aria-label="Collapse sidebar"
                >
                  <PanelLeftClose className="w-4 h-4" />
                </button>
              </div>

              {/* Full text nav items */}
              <div className="px-3 py-3 space-y-4 overflow-y-auto max-h-[calc(100vh-140px)] no-scrollbar">
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
                            const isActive = isItemActive(item.id);
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

                {/* Admin console button */}
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

            {/* Bottom account footer */}
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
                className={`px-2.5 py-1.5 rounded-lg text-xs font-semibold transition shrink-0 cursor-pointer flex items-center gap-1.5 ${
                  currentView === 'settings'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-100'
                }`}
                title="User & Credential Settings"
              >
                <Settings className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        ) : (
          /* Compact Desktop Mode (w-16) */
          <div className="flex flex-col h-full justify-between">
            <div>
              {/* Top Compact Icon Logo */}
              <div className="h-14 border-b border-slate-100 flex items-center justify-center">
                <button
                  type="button"
                  onClick={toggleDesktopExpanded}
                  className="w-10 h-10 rounded-xl hover:bg-slate-100 flex items-center justify-center transition cursor-pointer group select-none"
                  title="Click to expand sidebar"
                  aria-label="Expand sidebar"
                >
                  <img
                    src="/static/logo/aetherops_light_icon.png"
                    alt="AetherOps"
                    className="w-8 h-8 object-contain select-none pointer-events-none group-hover:scale-105 transition"
                    draggable={false}
                    onContextMenu={(e) => e.preventDefault()}
                    style={{
                      WebkitUserDrag: 'none',
                      userSelect: 'none',
                      WebkitTouchCallout: 'none',
                      pointerEvents: 'none',
                    }}
                    width="32"
                    height="32"
                  />
                </button>
              </div>

              {/* Navigation Icon List */}
              <div className="px-2 py-3 space-y-2 overflow-y-auto max-h-[calc(100vh-140px)] no-scrollbar">
                {NAV_GROUPS.map((group, gIdx) => (
                  <div key={group.name} className="space-y-1.5">
                    {gIdx > 0 && <div className="h-px bg-slate-100 my-2 mx-1" />}
                    {group.items.map((item) => {
                      const Icon = item.icon;
                      const isActive = isItemActive(item.id);
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

            {/* Bottom Actions in Compact Mode */}
            <div className="p-2 border-t border-slate-100 bg-slate-50/70 flex flex-col items-center gap-2">
              <button
                type="button"
                onClick={toggleDesktopExpanded}
                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 transition cursor-pointer"
                title="Expand sidebar"
                aria-label="Expand sidebar"
              >
                <PanelLeftOpen className="w-4 h-4" />
              </button>

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
                  currentView === 'settings'
                    ? 'bg-blue-600 text-white'
                    : 'text-slate-400 hover:text-slate-700 hover:bg-slate-200/60'
                }`}
                title="User & Credential Settings"
                aria-label="User & Credential Settings"
              >
                <Settings className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </aside>

      {/* ─────────────────────────────────────────────────────────── */}
      {/* 3. Mobile Off-Canvas Drawer (Slide-Out on Mobile <1024px)   */}
      {/* ─────────────────────────────────────────────────────────── */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-72 max-w-[85vw] bg-white border-r border-slate-200/80 shadow-2xl flex flex-col h-full justify-between select-none transform transition-transform duration-300 ease-in-out lg:hidden ${
          mobileOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
        aria-label="Mobile Navigation Drawer"
      >
        <div>
          {/* Header with full logo and close button */}
          <div className="h-14 px-4 border-b border-slate-100 flex items-center justify-between">
            <div
              onClick={() => navItemClick('dashboard', '/')}
              className="cursor-pointer group flex items-center gap-2 select-none"
            >
              <img
                src="/static/logo/aetherops_light_full.png"
                alt="AetherOps"
                className="h-8 max-w-[160px] w-auto object-contain object-left transition-opacity group-hover:opacity-90 select-none pointer-events-none"
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

            <button
              type="button"
              onClick={() => setMobileOpen && setMobileOpen(false)}
              className="p-2 text-slate-400 hover:text-slate-700 rounded-lg hover:bg-slate-100 cursor-pointer transition"
              aria-label="Close navigation"
              title="Close navigation"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Scrollable Navigation Groups */}
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
                        const isActive = isItemActive(item.id);
                        return (
                          <button
                            key={item.id}
                            onClick={() => navItemClick(item.id, item.path)}
                            className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium transition duration-150 text-left cursor-pointer ${
                              isActive
                                ? 'bg-[#1e40af] text-white shadow-xs font-semibold'
                                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100 active:bg-slate-200'
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

            {/* Mobile Admin Link */}
            {isAdmin && (
              <div className="pt-2 border-t border-slate-100 mt-2 space-y-1">
                <div className="px-3 text-[10px] font-bold uppercase tracking-wider text-blue-600 mb-1 flex items-center gap-1">
                  <span>ADMINISTRATION</span>
                </div>
                <button
                  onClick={() => navItemClick('admin', '/admin')}
                  className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium transition text-left cursor-pointer ${
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

        {/* Mobile User Profile Footer */}
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
            title="User Settings"
          >
            <Settings className="w-3.5 h-3.5" />
            <span>Settings</span>
          </button>
        </div>
      </aside>
    </>
  );
}
