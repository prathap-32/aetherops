// frontend/src/pages/DashboardPage.jsx
import React, { useState, useEffect } from 'react';
import Sidebar from '../components/layout/Sidebar';
import Navbar from '../components/layout/Navbar';
import AccountModal from '../components/layout/AccountModal';

// Module views
import DashboardOverview from '../modules/dashboard/DashboardOverview';
import ProjectsView from '../modules/projects/ProjectsView';
import EnvironmentsView from '../modules/environments/EnvironmentsView';
import SourceCloudView from '../modules/source_cloud/SourceCloudView';
import RepoAnalyzerView from '../modules/repo_analyzer/RepoAnalyzerView';
import ArchitectureView from '../modules/architecture/ArchitectureView';
import ArchitectureDesigner from '../modules/designer/ArchitectureDesigner';
import RiskEngineView from '../modules/risk/RiskEngineView';
import ArchitectureValidationView from '../modules/validation/ArchitectureValidationView';
import IacView from '../modules/iac/IacView';
import ApprovalExecutionView from '../modules/execution/ApprovalExecutionView';
import DeploymentsView from '../modules/deployments/DeploymentsView';
import CicdView from '../modules/cicd/CicdView';
import MonitoringView from '../modules/monitoring/MonitoringView';
import OptimizationView from '../modules/optimization/OptimizationView';
import AuditHistoryView from '../modules/audit/AuditHistoryView';
import AdminConsoleView from '../modules/admin/AdminConsoleView';
import SettingsView from '../modules/settings/SettingsView';
import DocsView from '../modules/docs/DocsView';

import { useAuth } from '../context/AuthContext';

// Path-to-View mapping for clean URLs
const PATH_VIEW_MAP = {
  '/': 'dashboard',
  '/dashboard': 'dashboard',
  '/projects': 'projects',
  '/environments': 'environments',
  '/source-connection': 'source_cloud',
  '/source-analysis': 'repo_analyzer',
  '/requirements': 'repo_analyzer',
  '/architecture': 'architecture_studio',
  '/architecture/designer': 'architecture_designer',
  '/architecture-designer': 'architecture_designer',
  '/architecture-studio': 'architecture_studio',
  '/risk-analysis': 'risk_analysis',
  '/architecture/validation': 'architecture_validation',
  '/security': 'security',
  '/terraform': 'iac',
  '/execution': 'execution',
  '/deployment': 'deployments',
  '/cicd': 'cicd',
  '/monitoring': 'monitoring',
  '/optimization': 'optimization',
  '/audit': 'audit',
  '/documentation': 'docs',
  '/account': 'settings',
  '/settings': 'settings',
  '/admin': 'admin',
};

const VIEW_PATH_MAP = {
  dashboard: '/',
  projects: '/projects',
  environments: '/environments',
  source_cloud: '/source-connection',
  repo_analyzer: '/source-analysis',
  architecture_studio: '/architecture-studio',
  architecture: '/architecture-studio',
  architecture_designer: '/architecture-designer',
  risk_analysis: '/risk-analysis',
  architecture_validation: '/architecture/validation',
  security: '/security',
  iac: '/terraform',
  execution: '/execution',
  deployments: '/deployment',
  cicd: '/cicd',
  monitoring: '/monitoring',
  optimization: '/optimization',
  audit: '/audit',
  docs: '/documentation',
  account: '/account',
  settings: '/settings',
  admin: '/admin',
};

export default function DashboardPage() {
  const { user, isAdmin } = useAuth();

  // Resolve initial view from window.location.pathname or hash
  const getInitialView = () => {
    const pathname = window.location.pathname.replace(/\/$/, '') || '/';
    if (PATH_VIEW_MAP[pathname]) {
      return PATH_VIEW_MAP[pathname];
    }
    const hash = window.location.hash.replace('#', '');
    if (hash && VIEW_PATH_MAP[hash]) {
      return hash;
    }
    return 'projects';
  };

  const [activeView, setActiveView] = useState(getInitialView);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const [isAccountModalOpen, setIsAccountModalOpen] = useState(() => {
    return typeof window !== 'undefined' && window.location.pathname.startsWith('/account');
  });
  const [isCreateProjectModalOpen, setIsCreateProjectModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Active Project & Environment Context
  const [activeProject, setActiveProject] = useState(() => {
    try {
      const saved = localStorage.getItem('aether_active_project');
      return saved ? JSON.parse(saved) : null;
    } catch (e) {
      return null;
    }
  });

  const [activeEnvironment, setActiveEnvironment] = useState(() => {
    try {
      const saved = localStorage.getItem('aether_active_env');
      return saved ? JSON.parse(saved) : null;
    } catch (e) {
      return null;
    }
  });

  const selectProject = (proj) => {
    setActiveProject(proj);
    try {
      if (proj) localStorage.setItem('aether_active_project', JSON.stringify(proj));
      else localStorage.removeItem('aether_active_project');
    } catch (e) {}
  };

  const selectEnvironment = (env) => {
    setActiveEnvironment(env);
    try {
      if (env) localStorage.setItem('aether_active_env', JSON.stringify(env));
      else localStorage.removeItem('aether_active_env');
    } catch (e) {}
  };

  // Sync state with browser navigation (popstate & hashchange)
  useEffect(() => {
    const handleLocationChange = () => {
      const pathname = window.location.pathname.replace(/\/$/, '') || '/';
      const resolvedView = PATH_VIEW_MAP[pathname] || window.location.hash.replace('#', '');
      if (pathname === '/account' || resolvedView === 'account') {
        setIsAccountModalOpen(true);
      }
      if (resolvedView) {
        if (resolvedView === 'admin' && !isAdmin) {
          window.history.pushState(null, '', '/projects');
          setActiveView('projects');
        } else {
          setActiveView(resolvedView);
        }
      }
    };

    window.addEventListener('popstate', handleLocationChange);
    window.addEventListener('hashchange', handleLocationChange);
    return () => {
      window.removeEventListener('popstate', handleLocationChange);
      window.removeEventListener('hashchange', handleLocationChange);
    };
  }, [isAdmin]);

  const [navState, setNavState] = useState(null);

  const handleNavigate = (viewKey, targetPathOrState, extraState) => {
    if (viewKey === 'admin' && !isAdmin) {
      alert('Access Restricted: The Admin Console is only accessible by platform administrators.');
      return;
    }
    let path = VIEW_PATH_MAP[viewKey] || `/${viewKey}`;
    if (typeof targetPathOrState === 'string' && targetPathOrState.startsWith('/')) {
      path = targetPathOrState;
      if (extraState) {
        setNavState(extraState);
      }
    } else if (typeof targetPathOrState === 'object' && targetPathOrState !== null) {
      setNavState(targetPathOrState);
    }
    try {
      window.history.pushState(null, '', path);
    } catch (e) {
      window.location.hash = `#${viewKey}`;
    }
    setActiveView(viewKey);
  };

  const renderActiveModule = () => {
    switch (activeView) {
      case 'dashboard':
        return (
          <DashboardOverview
            onNavigate={handleNavigate}
            onOpenCreateProject={() => setIsCreateProjectModalOpen(true)}
          />
        );
      case 'projects':
        return (
          <ProjectsView
            onNavigate={handleNavigate}
            searchQuery={searchQuery}
            isCreateModalOpen={isCreateProjectModalOpen}
            onCloseCreateModal={() => setIsCreateProjectModalOpen(false)}
            onOpenCreateProject={() => setIsCreateProjectModalOpen(true)}
            activeProject={activeProject}
            onSelectProject={selectProject}
          />
        );
      case 'environments':
        return (
          <EnvironmentsView
            onNavigate={handleNavigate}
            activeProject={activeProject}
            activeEnvironment={activeEnvironment}
            onSelectEnvironment={selectEnvironment}
            navState={navState}
          />
        );
      case 'source_cloud':
        return (
          <SourceCloudView
            onNavigate={handleNavigate}
            activeProject={activeProject}
            activeEnvironment={activeEnvironment}
            navState={navState}
          />
        );
      case 'repo_analyzer':
      case 'requirements':
        return (
          <RepoAnalyzerView
            onNavigate={handleNavigate}
            activeProject={activeProject}
            activeEnvironment={activeEnvironment}
            navState={navState}
          />
        );
      case 'architecture_studio':
      case 'architecture':
        return (
          <ArchitectureView
            onNavigate={handleNavigate}
            activeProject={activeProject}
            activeEnvironment={activeEnvironment}
            navState={navState}
            user={user}
          />
        );
      case 'architecture_designer':
        return (
          <ArchitectureDesigner
            onNavigate={handleNavigate}
            activeProject={activeProject}
            activeEnvironment={activeEnvironment}
            navState={navState}
            user={user}
          />
        );
      case 'risk_analysis':
        return (
          <RiskEngineView
            onNavigate={handleNavigate}
            activeProject={activeProject}
            activeEnvironment={activeEnvironment}
            user={user}
          />
        );
      case 'architecture_validation':
      case 'security':
        return (
          <ArchitectureValidationView
            onNavigate={handleNavigate}
            activeProject={activeProject}
            activeEnvironment={activeEnvironment}
            user={user}
          />
        );
      case 'iac':
        return (
          <IacView
            onNavigate={handleNavigate}
            activeProject={activeProject}
            activeEnvironment={activeEnvironment}
            user={user}
          />
        );
      case 'execution':
        return (
          <ApprovalExecutionView
            onNavigate={handleNavigate}
            activeProject={activeProject}
            activeEnvironment={activeEnvironment}
            user={user}
          />
        );
      case 'deployments':
        return (
          <DeploymentsView
            onNavigate={handleNavigate}
            activeProject={activeProject}
            activeEnvironment={activeEnvironment}
            user={user}
          />
        );
      case 'cicd':
        return <CicdView onNavigate={handleNavigate} />;
      case 'monitoring':
        return <MonitoringView onNavigate={handleNavigate} />;
      case 'optimization':
        return <OptimizationView onNavigate={handleNavigate} />;
      case 'audit':
        return <AuditHistoryView onNavigate={handleNavigate} />;
      case 'admin':
        return isAdmin ? <AdminConsoleView onNavigate={handleNavigate} /> : <ProjectsView onNavigate={handleNavigate} />;
      case 'settings':
        return <SettingsView onNavigate={handleNavigate} />;
      case 'docs':
        return <DocsView onNavigate={handleNavigate} />;
      default:
        return (
          <DashboardOverview
            onNavigate={handleNavigate}
            onOpenCreateProject={() => setIsCreateProjectModalOpen(true)}
          />
        );
    }
  };

  return (
    <div className="flex h-screen bg-[#f8f9ff] text-slate-900 font-sans antialiased overflow-hidden">
      {/* Unified Global Sidebar */}
      <Sidebar
        activeView={activeView}
        activeItem={activeView}
        setActiveView={handleNavigate}
        onNavigate={handleNavigate}
        mobileOpen={mobileSidebarOpen}
        setMobileOpen={setMobileSidebarOpen}
        onOpenAccountModal={() => setIsAccountModalOpen(true)}
        onOpenAccount={() => setIsAccountModalOpen(true)}
      />

      {/* Main Orchestrator Workspace */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Unified Top Navbar */}
        <Navbar
          activeView={activeView}
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
          onOpenMobileSidebar={() => setMobileSidebarOpen((prev) => !prev)}
          onOpenCreateProject={() => {
            handleNavigate('projects', '/projects');
            setIsCreateProjectModalOpen(true);
          }}
          onOpenAccountModal={() => setIsAccountModalOpen(true)}
          onOpenAccount={() => setIsAccountModalOpen(true)}
          activeProject={activeProject}
          activeEnvironment={activeEnvironment}
        />

        {/* Dynamic Workspace Container */}
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 md:p-8">
          <div className="max-w-7xl mx-auto">{renderActiveModule()}</div>
        </main>
      </div>

      {/* Account Profile Update Modal (Dynamic updates in DB & Dashboard) */}
      <AccountModal
        isOpen={isAccountModalOpen}
        onClose={() => setIsAccountModalOpen(false)}
      />
    </div>
  );
}
