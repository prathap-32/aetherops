// frontend/src/pages/DashboardPage.jsx
import React, { useState, useEffect } from 'react';
import Sidebar from '../components/layout/Sidebar';
import Navbar from '../components/layout/Navbar';
import AccountModal from '../components/layout/AccountModal';

// Module views
import DashboardOverview from '../modules/dashboard/DashboardOverview';
import ProjectEnvironmentView from '../modules/projects/ProjectEnvironmentView';
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
  '/app': 'dashboard',
  '/dashboard': 'dashboard',
  '/project-environment': 'project_environment',
  '/project_environment': 'project_environment',
  '/projects': 'project_environment',
  '/environments': 'project_environment',
  '/source-connection': 'source_cloud',
  '/source_connection': 'source_cloud',
  '/source-analysis': 'repo_analyzer',
  '/source_analysis': 'repo_analyzer',
  '/requirements': 'repo_analyzer',
  '/architecture': 'architecture_studio',
  '/architecture/designer': 'architecture_designer',
  '/architecture-designer': 'architecture_designer',
  '/architecture-studio': 'architecture_studio',
  '/architecture_studio': 'architecture_studio',
  '/risk-analysis': 'risk_analysis',
  '/risk_analysis': 'risk_analysis',
  '/architecture/validation': 'architecture_validation',
  '/architecture-validation': 'architecture_validation',
  '/security': 'architecture_validation',
  '/terraform': 'iac',
  '/iac': 'iac',
  '/execution': 'execution',
  '/deployment': 'deployments',
  '/deployments': 'deployments',
  '/cicd': 'cicd',
  '/monitoring': 'monitoring',
  '/optimization': 'optimization',
  '/audit': 'audit',
  '/documentation': 'docs',
  '/docs': 'docs',
  '/account': 'settings',
  '/settings': 'settings',
  '/admin': 'admin',
};

const VIEW_PATH_MAP = {
  dashboard: '/',
  app: '/',
  project_environment: '/project-environment',
  'project-environment': '/project-environment',
  projects: '/project-environment',
  environments: '/project-environment',
  source_cloud: '/source-connection',
  'source-connection': '/source-connection',
  'source_connection': '/source-connection',
  repo_analyzer: '/source-analysis',
  'source-analysis': '/source-analysis',
  'source_analysis': '/source-analysis',
  requirements: '/source-analysis',
  architecture_studio: '/architecture-studio',
  'architecture-studio': '/architecture-studio',
  architecture: '/architecture-studio',
  architecture_designer: '/architecture-designer',
  'architecture-designer': '/architecture-designer',
  'architecture/designer': '/architecture-designer',
  risk_analysis: '/risk-analysis',
  'risk-analysis': '/risk-analysis',
  architecture_validation: '/architecture/validation',
  'architecture/validation': '/architecture/validation',
  'architecture-validation': '/architecture/validation',
  security: '/security',
  iac: '/terraform',
  terraform: '/terraform',
  execution: '/execution',
  deployments: '/deployment',
  deployment: '/deployment',
  cicd: '/cicd',
  monitoring: '/monitoring',
  optimization: '/optimization',
  audit: '/audit',
  docs: '/documentation',
  documentation: '/documentation',
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

  const resolveViewKey = (keyOrPath) => {
    if (!keyOrPath || typeof keyOrPath !== 'string') return 'projects';
    const trimmed = keyOrPath.trim();
    if (trimmed.startsWith('/')) {
      return PATH_VIEW_MAP[trimmed] || trimmed.replace(/^\//, '');
    }
    if (PATH_VIEW_MAP[`/${trimmed}`]) {
      return PATH_VIEW_MAP[`/${trimmed}`];
    }
    return trimmed;
  };

  const handleOpenCreateProject = () => {
    setIsCreateProjectModalOpen(true);
    handleNavigate('projects', '/projects');
  };

  const handleNavigate = (viewKey, targetPathOrState, extraState) => {
    let resolvedKey = resolveViewKey(viewKey);
    let path = VIEW_PATH_MAP[resolvedKey] || VIEW_PATH_MAP[viewKey] || `/${viewKey}`;

    if (typeof targetPathOrState === 'string' && targetPathOrState.startsWith('/')) {
      path = targetPathOrState;
      if (PATH_VIEW_MAP[targetPathOrState]) {
        resolvedKey = PATH_VIEW_MAP[targetPathOrState];
      }
      if (extraState) {
        setNavState(extraState);
      }
    } else if (typeof targetPathOrState === 'object' && targetPathOrState !== null) {
      setNavState(targetPathOrState);
    }

    if (resolvedKey === 'admin' && !isAdmin) {
      alert('Access Restricted: The Admin Console is only accessible by platform administrators.');
      return;
    }

    try {
      window.history.pushState(null, '', path);
    } catch (e) {
      window.location.hash = `#${resolvedKey}`;
    }
    setActiveView(resolvedKey);
  };

  const renderActiveModule = () => {
    switch (activeView) {
      case 'dashboard':
      case 'app':
      case '/':
        return (
          <DashboardOverview
            onNavigate={handleNavigate}
            onOpenCreateProject={handleOpenCreateProject}
            onSelectProject={selectProject}
          />
        );
      case 'project_environment':
      case 'project-environment':
      case 'projects':
        return (
          <ProjectEnvironmentView
            onNavigate={handleNavigate}
            isCreateModalOpen={isCreateProjectModalOpen}
            onCloseCreateModal={() => setIsCreateProjectModalOpen(false)}
            onOpenCreateProject={handleOpenCreateProject}
            activeProject={activeProject}
            activeEnvironment={activeEnvironment}
            onSelectProject={selectProject}
            onSelectEnvironment={selectEnvironment}
            navState={navState}
            initialTab={navState?.tab || 'projects'}
          />
        );
      case 'environments':
        return (
          <ProjectEnvironmentView
            onNavigate={handleNavigate}
            isCreateModalOpen={isCreateProjectModalOpen}
            onCloseCreateModal={() => setIsCreateProjectModalOpen(false)}
            onOpenCreateProject={handleOpenCreateProject}
            activeProject={activeProject}
            activeEnvironment={activeEnvironment}
            onSelectProject={selectProject}
            onSelectEnvironment={selectEnvironment}
            navState={navState}
            initialTab="environments"
          />
        );
      case 'source_cloud':
      case 'source-connection':
      case 'source_connection':
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
      case 'source-analysis':
      case 'source_analysis':
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
      case 'architecture-studio':
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
      case 'architecture-designer':
      case 'architecture/designer':
      case 'designer':
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
      case 'risk-analysis':
      case 'risk':
        return (
          <RiskEngineView
            onNavigate={handleNavigate}
            activeProject={activeProject}
            activeEnvironment={activeEnvironment}
            user={user}
          />
        );
      case 'architecture_validation':
      case 'architecture/validation':
      case 'architecture-validation':
      case 'security':
      case 'validation':
        return (
          <ArchitectureValidationView
            onNavigate={handleNavigate}
            activeProject={activeProject}
            activeEnvironment={activeEnvironment}
            user={user}
          />
        );
      case 'iac':
      case 'terraform':
        return (
          <IacView
            onNavigate={handleNavigate}
            activeProject={activeProject}
            activeEnvironment={activeEnvironment}
            user={user}
          />
        );
      case 'execution':
      case 'approval':
        return (
          <ApprovalExecutionView
            onNavigate={handleNavigate}
            activeProject={activeProject}
            activeEnvironment={activeEnvironment}
            user={user}
          />
        );
      case 'deployments':
      case 'deployment':
        return (
          <DeploymentsView
            onNavigate={handleNavigate}
            activeProject={activeProject}
            activeEnvironment={activeEnvironment}
            user={user}
          />
        );
      case 'cicd':
      case 'cicd-pipeline':
        return <CicdView onNavigate={handleNavigate} />;
      case 'monitoring':
      case 'observability':
        return <MonitoringView onNavigate={handleNavigate} />;
      case 'optimization':
      case 'finops':
        return <OptimizationView onNavigate={handleNavigate} />;
      case 'audit':
      case 'history':
        return <AuditHistoryView onNavigate={handleNavigate} />;
      case 'admin':
      case 'admin_console':
        return isAdmin ? <AdminConsoleView onNavigate={handleNavigate} /> : <ProjectsView onNavigate={handleNavigate} />;
      case 'settings':
      case 'account':
        return <SettingsView onNavigate={handleNavigate} />;
      case 'docs':
      case 'documentation':
        return <DocsView onNavigate={handleNavigate} />;
      default:
        return (
          <DashboardOverview
            onNavigate={handleNavigate}
            onOpenCreateProject={handleOpenCreateProject}
            onSelectProject={selectProject}
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
        {/* Unified Top Navbar with Mobile Drawer Toggle and Context */}
        <Navbar
          activeView={activeView}
          onToggleMobileSidebar={() => setMobileSidebarOpen((prev) => !prev)}
          user={user}
          activeProject={activeProject}
          onOpenAccountModal={() => setIsAccountModalOpen(true)}
          onNavigate={handleNavigate}
        />

        {/* Dynamic Responsive Workspace Container */}
        <main className="flex-1 overflow-y-auto p-3.5 sm:p-5 md:p-6 lg:p-8">
          <div className="w-full max-w-7xl 2xl:max-w-[1600px] 3xl:max-w-[1800px] mx-auto">
            {renderActiveModule()}
          </div>
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
