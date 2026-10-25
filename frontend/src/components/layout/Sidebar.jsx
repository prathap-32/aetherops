// frontend/src/components/layout/Sidebar.jsx
import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { formatAccountId } from '../../services/api';
import {
  LayoutDashboard,
  FolderKanban,
  Boxes,
  Cpu,
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
  User as UserIcon,
  ChevronDown,
  ChevronRight,
  X,
  Settings,
} from 'lucide-react';

export default function Sidebar({
  activeView,
  activeItem,
  setActiveView,
  onNavigate,
  mobileOpen,
  setMobileOpen,
  onOpenAccountModal,
  onOpenAccount,
}) {
  const { user, isAdmin, logout } = useAuth();
  const currentView = activeView || activeItem || 'projects';
  const handleNavigation = setActiveView || onNavigate || (() => {});
  const handleOpenAccount = onOpenAccountModal || onOpenAccount || (() => {});

  // Collapsible category state
  const [collapsedGroups, setCollapsedGroups] = useState({});

  const toggleGroup = (groupName) => {
    setCollapsedGroups((prev) => ({
      ...prev,
      [groupName]: !prev[groupName],
    }));
  };

  const navItemClick = (viewId, path) => {
    handleNavigation(viewId, path);
    if (setMobileOpen) setMobileOpen(false);
  };

  const navItemClass = (viewId) => {
    const isActive = currentView === viewId;
    return `w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-medium transition duration-150 text-left cursor-pointer ${
      isActive
        ? 'bg-[#1e40af] text-white shadow-xs font-semibold'
        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
    }`;
  };

  const iconClass = (viewId) => {
    const isActive = currentView === viewId;
    return `w-4 h-4 shrink-0 ${isActive ? 'text-white' : 'text-slate-400 group-hover:text-slate-600'}`;
  };

  const initials = (user?.username || 'AO').slice(0, 2).toUpperCase();

  return (
    <div className="flex flex-col h-full justify-between select-none bg-white border-r border-slate-200/80 w-64 shrink-0">
      {/* Top Header & Branding */}
      <div>
        <div className="p-4 border-b border-slate-100">
          <div className="flex items-center justify-between">
            <div
              onClick={() => navItemClick('dashboard', '/')}
              className="cursor-pointer group flex items-center"
            >
              <img
                src="/static/logo/aetherops_light.png"
                alt="AetherOps"
                className="h-8 max-w-[190px] object-contain object-left transition-opacity group-hover:opacity-90"
              />
            </div>

            {setMobileOpen && (
              <button
                onClick={() => setMobileOpen(false)}
                className="lg:hidden p-1.5 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 cursor-pointer"
                aria-label="Close sidebar"
              >
                <X className="w-5 h-5" />
              </button>
            )}
          </div>
        </div>

        {/* Scrollable Navigation Groups */}
        <div className="px-3 py-3 space-y-4 overflow-y-auto max-h-[calc(100vh-140px)]">
          {/* GROUP 1: WORKSPACE */}
          <div className="space-y-1">
            <div
              onClick={() => toggleGroup('WORKSPACE')}
              className="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1.5 flex items-center justify-between cursor-pointer hover:text-slate-600"
            >
              <span>WORKSPACE</span>
              {collapsedGroups['WORKSPACE'] ? (
                <ChevronRight className="w-3 h-3" />
              ) : (
                <ChevronDown className="w-3 h-3" />
              )}
            </div>
            {!collapsedGroups['WORKSPACE'] && (
              <>
                <button
                  onClick={() => navItemClick('dashboard', '/')}
                  className={navItemClass('dashboard')}
                >
                  <div className="flex items-center gap-2.5">
                    <LayoutDashboard className={iconClass('dashboard')} />
                    <span>Dashboard</span>
                  </div>
                </button>
                <button
                  onClick={() => navItemClick('projects', '/projects')}
                  className={navItemClass('projects')}
                >
                  <div className="flex items-center gap-2.5">
                    <FolderKanban className={iconClass('projects')} />
                    <span>Projects</span>
                  </div>
                </button>
                <button
                  onClick={() => navItemClick('environments', '/environments')}
                  className={navItemClass('environments')}
                >
                  <div className="flex items-center gap-2.5">
                    <Boxes className={iconClass('environments')} />
                    <span>Environments</span>
                  </div>
                </button>
              </>
            )}
          </div>

          {/* GROUP 2: BUILD */}
          <div className="space-y-1">
            <div
              onClick={() => toggleGroup('BUILD')}
              className="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1.5 flex items-center justify-between cursor-pointer hover:text-slate-600"
            >
              <span>BUILD</span>
              {collapsedGroups['BUILD'] ? (
                <ChevronRight className="w-3 h-3" />
              ) : (
                <ChevronDown className="w-3 h-3" />
              )}
            </div>
            {!collapsedGroups['BUILD'] && (
              <>
                <button
                  onClick={() => navItemClick('source_cloud', '/source-connection')}
                  className={navItemClass('source_cloud')}
                >
                  <div className="flex items-center gap-2.5">
                    <GitBranch className={iconClass('source_cloud')} />
                    <span>Source &amp; Cloud Connection</span>
                  </div>
                </button>
                <button
                  onClick={() => navItemClick('repo_analyzer', '/source-analysis')}
                  className={navItemClass('repo_analyzer')}
                >
                  <div className="flex items-center gap-2.5">
                    <FileCode2 className={iconClass('repo_analyzer')} />
                    <span>Source Code Analyzer</span>
                  </div>
                  <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-violet-100 text-violet-800 border border-violet-200">
                    M3
                  </span>
                </button>
                <button
                  onClick={() => navItemClick('architecture_studio', '/architecture-studio')}
                  className={navItemClass('architecture_studio')}
                >
                  <div className="flex items-center gap-2.5">
                    <Palette className={iconClass('architecture_studio')} />
                    <span>Cloud Architecture Studio</span>
                  </div>
                  <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-sky-100 text-sky-800 border border-sky-200">
                    M4
                  </span>
                </button>
                <button
                  onClick={() => navItemClick('architecture_designer', '/architecture-designer')}
                  className={navItemClass('architecture_designer')}
                >
                  <div className="flex items-center gap-2.5">
                    <Network className={iconClass('architecture_designer')} />
                    <span>Architecture Designer</span>
                  </div>
                  <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800 border border-emerald-200">
                    Canvas
                  </span>
                </button>
                <button
                  onClick={() => navItemClick('risk_analysis', '/risk-analysis')}
                  className={navItemClass('risk_analysis')}
                >
                  <div className="flex items-center gap-2.5">
                    <ShieldAlert className={iconClass('risk_analysis')} />
                    <span>Pre-Deployment Risk Engine</span>
                  </div>
                </button>
                <button
                  onClick={() => navItemClick('architecture_validation', '/architecture/validation')}
                  className={navItemClass('architecture_validation')}
                >
                  <div className="flex items-center gap-2.5">
                    <CheckCircle2 className={iconClass('architecture_validation')} />
                    <span>Architecture Validation</span>
                  </div>
                </button>
                <button
                  onClick={() => navItemClick('security', '/security')}
                  className={navItemClass('security')}
                >
                  <div className="flex items-center gap-2.5">
                    <ShieldCheck className={iconClass('security')} />
                    <span>Security &amp; Compliance</span>
                  </div>
                </button>
              </>
            )}
          </div>

          {/* GROUP 3: DEPLOY */}
          <div className="space-y-1">
            <div
              onClick={() => toggleGroup('DEPLOY')}
              className="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1.5 flex items-center justify-between cursor-pointer hover:text-slate-600"
            >
              <span>DEPLOY</span>
              {collapsedGroups['DEPLOY'] ? (
                <ChevronRight className="w-3 h-3" />
              ) : (
                <ChevronDown className="w-3 h-3" />
              )}
            </div>
            {!collapsedGroups['DEPLOY'] && (
              <>
                <button
                  onClick={() => navItemClick('iac', '/terraform')}
                  className={navItemClass('iac')}
                >
                  <div className="flex items-center gap-2.5">
                    <Code2 className={iconClass('iac')} />
                    <span>Terraform / IaC Generator</span>
                  </div>
                </button>
                <button
                  onClick={() => navItemClick('execution', '/execution')}
                  className={navItemClass('execution')}
                >
                  <div className="flex items-center gap-2.5">
                    <CheckSquare className={iconClass('execution')} />
                    <span>Approval &amp; Execution</span>
                  </div>
                </button>
                <button
                  onClick={() => navItemClick('deployments', '/deployment')}
                  className={navItemClass('deployments')}
                >
                  <div className="flex items-center gap-2.5">
                    <Rocket className={iconClass('deployments')} />
                    <span>Application Deployment</span>
                  </div>
                </button>
                <button
                  onClick={() => navItemClick('cicd', '/cicd')}
                  className={navItemClass('cicd')}
                >
                  <div className="flex items-center gap-2.5">
                    <GitFork className={iconClass('cicd')} />
                    <span>CI/CD Integration</span>
                  </div>
                </button>
              </>
            )}
          </div>

          {/* GROUP 4: OPERATE */}
          <div className="space-y-1">
            <div
              onClick={() => toggleGroup('OPERATE')}
              className="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1.5 flex items-center justify-between cursor-pointer hover:text-slate-600"
            >
              <span>OPERATE</span>
              {collapsedGroups['OPERATE'] ? (
                <ChevronRight className="w-3 h-3" />
              ) : (
                <ChevronDown className="w-3 h-3" />
              )}
            </div>
            {!collapsedGroups['OPERATE'] && (
              <>
                <button
                  onClick={() => navItemClick('monitoring', '/monitoring')}
                  className={navItemClass('monitoring')}
                >
                  <div className="flex items-center gap-2.5">
                    <Activity className={iconClass('monitoring')} />
                    <span>Infrastructure Monitoring</span>
                  </div>
                </button>
                <button
                  onClick={() => navItemClick('optimization', '/optimization')}
                  className={navItemClass('optimization')}
                >
                  <div className="flex items-center gap-2.5">
                    <DollarSign className={iconClass('optimization')} />
                    <span>Continuous Risk &amp; Optimization</span>
                  </div>
                </button>
              </>
            )}
          </div>

          {/* GROUP 5: MANAGE */}
          <div className="space-y-1">
            <div
              onClick={() => toggleGroup('MANAGE')}
              className="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1.5 flex items-center justify-between cursor-pointer hover:text-slate-600"
            >
              <span>MANAGE</span>
              {collapsedGroups['MANAGE'] ? (
                <ChevronRight className="w-3 h-3" />
              ) : (
                <ChevronDown className="w-3 h-3" />
              )}
            </div>
            {!collapsedGroups['MANAGE'] && (
              <>
                <button
                  onClick={() => navItemClick('audit', '/audit')}
                  className={navItemClass('audit')}
                >
                  <div className="flex items-center gap-2.5">
                    <History className={iconClass('audit')} />
                    <span>Audit &amp; History</span>
                  </div>
                </button>
                <button
                  onClick={() => navItemClick('docs', '/documentation')}
                  className={navItemClass('docs')}
                >
                  <div className="flex items-center gap-2.5">
                    <FileText className={iconClass('docs')} />
                    <span>Documentation &amp; Evidence</span>
                  </div>
                </button>
              </>
            )}
          </div>

          {/* GROUP 6: ADMINISTRATION (Privileged - strictly visible to Admin users only) */}
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
                    className={`w-4 h-4 ${currentView === 'admin' ? 'text-white' : 'text-blue-600'}`}
                  />
                  <span>Admin Console</span>
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

      {/* Bottom User Account Footer (Clickable to edit username in DB) */}
      <div className="p-3 border-t border-slate-100 bg-slate-50/70 flex items-center justify-between gap-2">
        <div
          onClick={handleOpenAccount}
          className="flex items-center gap-2.5 min-w-0 cursor-pointer p-1 rounded-lg hover:bg-slate-200/60 transition group flex-1"
          title="Click to manage account profile"
        >
          <div className="w-8 h-8 rounded-full bg-[#1e40af] text-white flex items-center justify-center font-bold font-mono text-xs shadow-xs group-hover:scale-105 transition">
            {initials}
          </div>
          <div className="min-w-0 flex-1">
            <div className="text-xs font-bold text-slate-800 truncate flex items-center gap-1">
              <span className="truncate">{user?.username || 'developer'}</span>
            </div>
            <div className="text-[10px] text-slate-500 truncate">{user?.email || 'user@aetherops.cloud'}</div>
            <div className="text-[10px] font-mono font-semibold text-amber-700 truncate">
              AWS: {formatAccountId(user?.account_id || '109283746519')}
            </div>
          </div>
        </div>

        <button
          onClick={logout}
          className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition shrink-0 cursor-pointer"
          title="Sign Out"
        >
          <LogOut className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
