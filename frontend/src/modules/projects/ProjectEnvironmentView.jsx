// frontend/src/modules/projects/ProjectEnvironmentView.jsx
import React, { useState, useEffect } from 'react';
import {
  FolderKanban,
  Boxes,
  AlertCircle,
} from 'lucide-react';
import ProjectsView from './ProjectsView';
import EnvironmentsView from '../environments/EnvironmentsView';
import { projectsApi } from '../../services/api';
import { useAuth } from '../../context/AuthContext';

export default function ProjectEnvironmentView({
  onNavigate,
  activeProject,
  activeEnvironment,
  onSelectProject,
  onSelectEnvironment,
  navState,
  isCreateModalOpen,
  onCloseCreateModal,
  onOpenCreateProject,
  initialTab = 'projects',
}) {
  const [activeTab, setActiveTab] = useState(() => {
    if (navState?.tab) return navState.tab;
    return initialTab || 'projects';
  });

  const [internalNavState, setInternalNavState] = useState(navState || null);
  const [projectsList, setProjectsList] = useState([]);
  const [environmentsList, setEnvironmentsList] = useState([]);
  const { user } = useAuth();
  const [actionNotice, setActionNotice] = useState(null);
  const [lastSynced, setLastSynced] = useState(new Date());
  const [isSyncing, setIsSyncing] = useState(false);
  // Sync navState updates
  useEffect(() => {
    if (navState?.tab) {
      setActiveTab(navState.tab);
    }
    if (navState) {
      setInternalNavState(navState);
    }
  }, [navState]);

  // Load summary counts for tab badges and next-step validation
  const loadSummaryCounts = async () => {
    try {
      const pList = await projectsApi.list();
      const safePList = Array.isArray(pList) ? pList : [];
      setProjectsList(safePList);

      // Auto-select active project if none selected yet
      if (!activeProject && safePList.length > 0 && onSelectProject) {
        onSelectProject(safePList[0]);
      }

      // Load environments for active project
      const pid = activeProject?.id || activeProject?.project_id || (safePList.length > 0 ? (safePList[0].id || safePList[0].project_id) : null);
      if (pid) {
        try {
          const envs = await projectsApi.listEnvironments(pid);
          const safeEnvs = Array.isArray(envs) ? envs : [];
          setEnvironmentsList(safeEnvs);

          // Auto-select active environment if none selected yet
          if (!activeEnvironment && safeEnvs.length > 0 && onSelectEnvironment) {
            onSelectEnvironment({
              ...safeEnvs[0],
              projectId: pid,
              projectName: activeProject?.name || 'Project',
            });
          }
        } catch (e) {
          console.warn('Failed to fetch environments for summary:', e);
        }
      }
    } catch (e) {
      console.warn('Failed to load project summary:', e);
    }
  };

  useEffect(() => {
    loadSummaryCounts();
  }, [activeProject?.id, activeProject?.project_id]);

  // Real-time background sync polling every 6 seconds
  useEffect(() => {
    const syncTimer = setInterval(async () => {
      if (document.hidden) return;
      await loadSummaryCounts();
      setLastSynced(new Date());
    }, 6000);

    const handleFocus = async () => {
      setIsSyncing(true);
      await loadSummaryCounts();
      setLastSynced(new Date());
      setIsSyncing(false);
    };

    window.addEventListener('focus', handleFocus);
    return () => {
      clearInterval(syncTimer);
      window.removeEventListener('focus', handleFocus);
    };
  }, [activeProject?.id, activeProject?.project_id]);
  // Navigate to 2. Connect AWS & Git
  const handleProceedToConnect = (overrideEnv = null) => {
    const proj = activeProject || (projectsList.length > 0 ? projectsList[0] : null);
    const env = overrideEnv || activeEnvironment || (environmentsList.length > 0 ? environmentsList[0] : null);

    if (!proj) {
      setActionNotice({
        type: 'error',
        text: 'Please create or select a Project before proceeding to Connect AWS & Git.',
      });
      setActiveTab('projects');
      if (onOpenCreateProject) onOpenCreateProject();
      return;
    }

    if (!env) {
      setActionNotice({
        type: 'warning',
        text: `Please create an environment for project "${proj.name}" before proceeding.`,
      });
      setActiveTab('environments');
      setInternalNavState({
        projectId: proj.id || proj.project_id,
        project: proj,
        autoOpenModal: true,
      });
      return;
    }

    // Save context
    if (onSelectProject) onSelectProject(proj);
    if (onSelectEnvironment) onSelectEnvironment(env);

    // Transition to 2. Connect AWS & Git
    if (onNavigate) {
      onNavigate('source_cloud', '/source-connection', {
        projectId: proj.id || proj.project_id,
        environmentId: env.id || env.env_id,
        project: proj,
        environment: env,
      });
    }
  };

  // Intercept Projects navigation to keep inside Project & Environment
  const handleProjectsNavigate = (view, path, state) => {
    if (view === 'environments' || path === '/environments') {
      setActiveTab('environments');
      if (state) {
        setInternalNavState(state);
      }
      return;
    }
    if (view === 'source_cloud' || path === '/source-connection') {
      handleProceedToConnect(state?.environment || null);
      return;
    }
    if (onNavigate) {
      onNavigate(view, path, state);
    }
  };

  // Intercept Environments navigation
  const handleEnvironmentsNavigate = (view, path, state) => {
    if (view === 'projects' || path === '/projects') {
      setActiveTab('projects');
      if (state) {
        setInternalNavState(state);
      }
      return;
    }
    if (view === 'source_cloud' || path === '/source-connection') {
      handleProceedToConnect(state?.environment || null);
      return;
    }
    if (onNavigate) {
      onNavigate(view, path, state);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* Notice Alert if Next was clicked without prerequisite */}
      {actionNotice && (
        <div
          className={`p-3 rounded-xl border flex items-center justify-between text-xs font-medium animate-in fade-in duration-150 ${
            actionNotice.type === 'error'
              ? 'bg-rose-50 border-rose-200 text-rose-800'
              : 'bg-amber-50 border-amber-200 text-amber-800'
          }`}
        >
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{actionNotice.text}</span>
          </div>
          <button
            type="button"
            onClick={() => setActionNotice(null)}
            className="text-xs font-bold underline hover:opacity-80 ml-2"
          >
            Dismiss
          </button>
        </div>
      )}
      {/* ── Sleek Minimalist Tab Switcher (Projects & Environments) ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-200 pb-3">
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => {
              setActiveTab('projects');
              setActionNotice(null);
            }}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition flex items-center gap-2 cursor-pointer ${
              activeTab === 'projects'
                ? 'bg-blue-600 text-white shadow-xs'
                : 'bg-white hover:bg-slate-100 text-slate-600 border border-slate-200'
            }`}
          >
            <FolderKanban className="w-3.5 h-3.5" />
            <span>Projects &amp; Workspaces</span>
            {projectsList.length > 0 && (
              <span
                className={`px-1.5 py-0.5 rounded-full text-[10px] font-mono ${
                  activeTab === 'projects' ? 'bg-white/20 text-white' : 'bg-slate-100 text-slate-600'
                }`}
              >
                {projectsList.length}
              </span>
            )}
          </button>

          <button
            type="button"
            onClick={() => {
              setActiveTab('environments');
              setActionNotice(null);
            }}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition flex items-center gap-2 cursor-pointer ${
              activeTab === 'environments'
                ? 'bg-blue-600 text-white shadow-xs'
                : 'bg-white hover:bg-slate-100 text-slate-600 border border-slate-200'
            }`}
          >
            <Boxes className="w-3.5 h-3.5" />
            <span>Environments</span>
            {environmentsList.length > 0 && (
              <span
                className={`px-1.5 py-0.5 rounded-full text-[10px] font-mono ${
                  activeTab === 'environments' ? 'bg-white/20 text-white' : 'bg-slate-100 text-slate-600'
                }`}
              >
                {environmentsList.length}
              </span>
            )}
          </button>
        </div>

        {/* Minimal Context Badges */}
        {(activeProject || activeEnvironment) && (
          <div className="flex items-center gap-2 text-xs">
            {activeProject && (
              <span
                onClick={() => setActiveTab('projects')}
                className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-50 border border-slate-200 text-slate-700 font-medium cursor-pointer hover:bg-slate-100 transition"
                title={`Active Project: ${activeProject.name}`}
              >
                <FolderKanban className="w-3 h-3 text-blue-600" />
                <span className="font-semibold text-slate-800 truncate max-w-[150px]">{activeProject.name}</span>
              </span>
            )}
            {activeEnvironment && (
              <span
                onClick={() => setActiveTab('environments')}
                className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 font-medium cursor-pointer hover:bg-emerald-100/80 transition"
                title={`Active Environment: ${activeEnvironment.name}`}
              >
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                <span className="truncate max-w-[140px]">{activeEnvironment.name}</span>
                <span className="text-[10px] text-emerald-600 font-mono">({activeEnvironment.aws_region || activeEnvironment.region || 'us-east-1'})</span>
              </span>
            )}
          </div>
        )}
      </div>

      {/* ── Section Content ── */}
      <div>
        {activeTab === 'projects' ? (
          <ProjectsView
            user={user}
            onNavigate={handleProjectsNavigate}
            isCreateModalOpen={isCreateModalOpen}
            onCloseCreateModal={onCloseCreateModal}
            onOpenCreateProject={onOpenCreateProject}
            activeProject={activeProject}
            onSelectProject={(proj) => {
              if (onSelectProject) onSelectProject(proj);
              loadSummaryCounts();
            }}
          />
        ) : (
          <EnvironmentsView
            user={user}
            onNavigate={handleEnvironmentsNavigate}
            activeProject={activeProject}
            activeEnvironment={activeEnvironment}
            onSelectEnvironment={(env) => {
              if (onSelectEnvironment) onSelectEnvironment(env);
              loadSummaryCounts();
            }}
            navState={internalNavState}
          />
        )}
      </div>

    </div>
  );
}
