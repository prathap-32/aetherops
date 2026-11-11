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
import StateInventoryView from '../modules/state_inventory/StateInventoryView';
import CicdView from '../modules/cicd/CicdView';
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
  '/approval-gate': 'approval_gate',
  '/state-inventory': 'state_inventory',
  '/deployment': 'deployments',
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
  approval_gate: '/approval-gate',
  'approval-gate': '/approval-gate',
  state_inventory: '/state-inventory',
  'state-inventory': '/state-inventory',
  deployments: '/deployment',
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
    const path = window.location.pathname;
    if (PATH_VIEW_MAP[path]) return PATH_VIEW_MAP[path];
    if (window.location.hash) {
      const cleanHash = window.location.hash.replace('#', '');
      if (PATH_VIEW_MAP['/' + cleanHash]) return PATH_VIEW_MAP['/' + cleanHash];
      if (PATH_VIEW_MAP[cleanHash]) return PATH_VIEW_MAP[cleanHash];
    }
    return 'dashboard';
  };

  const [activeView, setActiveView] = useState(getInitialView);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const [isAccountModalOpen, setIsAccountModalOpen] = useState(false);

  // Active Project & Environment State
  const [activeProject, setActiveProject] = useState(() => {
    try {
      const cached = localStorage.getItem('aether_active_project');
      return cached ? JSON.parse(cached) : null;
    } catch (e) {
      return null;
    }
  });

  const selectProject = (project) => {
    setActiveProject(project);
    try {
      if (project) {
        localStorage.setItem('aether_active_project', JSON.stringify(project));
      } else {
        localStorage.removeItem('aether_active_project');
      }
    } catch (e) {}
  };

  // Sync browser URL history on view change
  const handleNavigate = (viewId, customPath, extraState = {}) => {
    setActiveView(viewId);
    const targetPath = customPath || VIEW_PATH_MAP[viewId] || '/';
    try {
      if (window.location.pathname !== targetPath) {
        window.history.pushState({ viewId, ...extraState }, '', targetPath);
      }
    } catch (e) {}
  };

  useEffect(() => {
    const handlePopState = () => {
      const resolved = getInitialView();
      setActiveView(resolved);
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const renderActiveModule = () => {
    switch (activeView) {
      case 'project_environment':
      case 'projects':
      case 'environments':
        return (
          <ProjectEnvironmentView
            onNavigate={handleNavigate}
            activeProject={activeProject}
            onSelectProject={selectProject}
          />
        );
      case 'source_cloud':
        return <SourceCloudView onNavigate={handleNavigate} />;
      case 'repo_analyzer':
        return <RepoAnalyzerView onNavigate={handleNavigate} />;
      case 'architecture_studio':
        return <ArchitectureView onNavigate={handleNavigate} />;
      case 'architecture_designer':
        return <ArchitectureDesigner onNavigate={handleNavigate} />;
      case 'risk_analysis':
        return <RiskEngineView onNavigate={handleNavigate} />;
      case 'architecture_validation':
      case 'security':
        return <ArchitectureValidationView onNavigate={handleNavigate} />;
      case 'iac':
        return <IacView onNavigate={handleNavigate} />;
      case 'execution':
      case 'approval_gate':
        return <ApprovalExecutionView onNavigate={handleNavigate} />;
      case 'state_inventory':
        return <StateInventoryView onNavigate={handleNavigate} />;
      case 'deployments':
        return <DeploymentsView onNavigate={handleNavigate} />;
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
            onOpenCreateProject={handleCreateProjectClick = () => {}}
            onSelectProject={selectProject}
          />
        );
    }
  };

  return (
    <div className="flex flex-col h-screen bg-[#f8f9ff] text-slate-900 font-sans antialiased overflow-hidden">
      {/* 1. Global Full-Width Top Bar (Zone Top) */}
      <div className="w-full shrink-0 z-30">
        <Navbar
          activeView={activeView}
          onToggleMobileSidebar={() => setMobileSidebarOpen((prev) => !prev)}
          user={user}
          activeProject={activeProject}
          onOpenAccountModal={() => setIsAccountModalOpen(true)}
          onNavigate={handleNavigate}
        />
      </div>

      {/* 2. Below Top Bar: Three-Zone Layout Container */}
      <div className="flex flex-1 min-h-0 overflow-hidden w-full">
        {/* Zone A: Left Sidebar */}
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

        {/* Zone B: Main Dashboard Content Container */}
        <main className="flex-1 flex flex-col min-w-0 overflow-y-auto p-4 sm:p-6 lg:p-8 bg-[#f8f9ff]">
          <div className="w-full max-w-7xl 2xl:max-w-[1600px] 3xl:max-w-[1800px] mx-auto flex-1 flex flex-col">
            {renderActiveModule()}
          </div>
        </main>

        {/* Zone C: Right-Side Content Slot (Flex container when contextual panels are present) */}
      </div>

      {/* Account Profile Update Modal */}
      <AccountModal
        isOpen={isAccountModalOpen}
        onClose={() => setIsAccountModalOpen(false)}
        onNavigate={handleNavigate}
      />
    </div>
  );
}
