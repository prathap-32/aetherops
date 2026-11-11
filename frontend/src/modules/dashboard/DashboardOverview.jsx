// frontend/src/modules/dashboard/DashboardOverview.jsx
import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  FolderKanban,
  Boxes,
  GitBranch,
  Rocket,
  ArrowRight,
  Plus,
  Search,
  Globe,
  RefreshCw,
} from 'lucide-react';
import {
  projectsApi,
  connectionsApi,
  deploymentsApi,
} from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import { resolveLifecycleState, getNextBestAction } from './components/lifecycleEngine';
import WelcomeSection from './components/WelcomeSection';
import NextActionPanel from './components/NextActionPanel';
import AttentionPanel from './components/AttentionPanel';

export default function DashboardOverview({ onNavigate, onOpenCreateProject, onSelectProject }) {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [projectSearchQuery, setProjectSearchQuery] = useState('');

  const [projectsState, setProjectsState] = useState({ status: 'loading', data: [], error: null });
  const [environmentsState, setEnvironmentsState] = useState({ status: 'loading', data: [], error: null });
  const [connectionsState, setConnectionsState] = useState({ status: 'loading', git: [], cloud: [], error: null });
  const [deploymentsState, setDeploymentsState] = useState({ status: 'loading', data: [], error: null });

  const handleCreateProjectClick = () => {
    if (onOpenCreateProject) {
      onOpenCreateProject();
    } else if (onNavigate) {
      onNavigate('projects', '/project-environment');
    }
  };

  const fetchDashboardData = useCallback(async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true);
    else setLoading(true);

    try {
      const [projRes, gitRes, cloudRes, depRes] = await Promise.allSettled([
        projectsApi.list(),
        connectionsApi.listGit(),
        connectionsApi.listCloud(),
        deploymentsApi.list ? deploymentsApi.list() : Promise.resolve([]),
      ]);

      let loadedProjects = [];
      if (projRes.status === 'fulfilled') {
        loadedProjects = Array.isArray(projRes.value) ? projRes.value : [];
        setProjectsState({ status: 'success', data: loadedProjects, error: null });
      } else {
        setProjectsState({ status: 'error', data: [], error: projRes.reason?.message || 'Failed to load projects' });
      }

      if (loadedProjects.length > 0) {
        try {
          const envPromises = loadedProjects.map((p) =>
            projectsApi.listEnvironments(p.id || p.project_id).catch(() => [])
          );
          const envResults = await Promise.all(envPromises);
          const flattenedEnvs = envResults.flat().filter(Boolean);
          setEnvironmentsState({ status: 'success', data: flattenedEnvs, error: null });
        } catch (envErr) {
          setEnvironmentsState({ status: 'error', data: [], error: envErr.message });
        }
      } else {
        setEnvironmentsState({ status: 'success', data: [], error: null });
      }

      const gitData = gitRes.status === 'fulfilled' && Array.isArray(gitRes.value) ? gitRes.value : [];
      const cloudData = cloudRes.status === 'fulfilled' && Array.isArray(cloudRes.value) ? cloudRes.value : [];
      setConnectionsState({
        status: 'success',
        git: gitData,
        cloud: cloudData,
        error: null,
      });

      const depData = depRes.status === 'fulfilled' && Array.isArray(depRes.value) ? depRes.value : [];
      setDeploymentsState({ status: 'success', data: depData, error: null });

    } catch (err) {
      console.warn('Dashboard fetch error:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  const projectsCount = projectsState.data.length;
  const environmentsCount = environmentsState.data.length;

  const activeAwsRegions = useMemo(() => {
    const regions = new Set();
    environmentsState.data.forEach((env) => {
      if (env.aws_region) regions.add(env.aws_region);
    });
    return Array.from(regions);
  }, [environmentsState.data]);

  // Resolve Lifecycle State & Next Best Action with user onboarding context
  const lifecycleState = useMemo(() => {
    return resolveLifecycleState({
      user,
      projects: projectsState.data,
      environments: environmentsState.data,
      connections: connectionsState,
      deployments: deploymentsState.data,
    });
  }, [user, projectsState.data, environmentsState.data, connectionsState, deploymentsState.data]);

  const primaryAction = useMemo(() => {
    return getNextBestAction(lifecycleState, {
      projects: projectsState.data,
      environments: environmentsState.data,
      connections: connectionsState,
    });
  }, [lifecycleState, projectsState.data, environmentsState.data, connectionsState]);

  const filteredProjects = useMemo(() => {
    const q = projectSearchQuery.toLowerCase().trim();
    if (!q) return projectsState.data;
    return projectsState.data.filter(
      (p) =>
        String(p.name || '').toLowerCase().includes(q) ||
        String(p.description || '').toLowerCase().includes(q) ||
        String(p.project_type || '').toLowerCase().includes(q)
    );
  }, [projectsState.data, projectSearchQuery]);

  const handleOpenProject = (project) => {
    if (onSelectProject) {
      onSelectProject(project);
    }
    if (onNavigate) {
      onNavigate('projects', '/project-environment', { activeProjectId: project.id });
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-200">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
              Platform Dashboard
            </h1>
            {refreshing && <RefreshCw className="w-5 h-5 animate-spin text-blue-600" />}
          </div>
          <p className="text-sm sm:text-base text-slate-600 mt-1.5 leading-relaxed">
            Manage your cloud projects, target environments, and deployed AWS infrastructure.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <button
            onClick={() => fetchDashboardData(true)}
            className="px-4 py-2.5 bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 text-sm font-medium rounded-xl shadow-2xs transition flex items-center gap-2 cursor-pointer min-h-[48px]"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin text-blue-600' : 'text-slate-400'}`} />
            <span>Refresh</span>
          </button>

          <button
            onClick={handleCreateProjectClick}
            className="px-5 py-2.5 bg-[#1e40af] hover:bg-[#1d4ed8] text-white text-sm font-semibold rounded-xl shadow-xs transition flex items-center gap-2 cursor-pointer min-h-[48px]"
          >
            <Plus className="w-5 h-5" />
            <span>New Project</span>
          </button>
        </div>
      </div>

      {/* Lifecycle-Driven Welcome Banner */}
      <WelcomeSection
        user={user}
        lifecycleState={lifecycleState}
        primaryAction={primaryAction}
        onNavigate={onNavigate}
      />

      {/* Conditional Attention Panel for L11 */}
      {lifecycleState === 'L11_ATTENTION_REQUIRED' && (
        <AttentionPanel onNavigate={onNavigate} />
      )}

      {/* Next Best Action Panel */}
      <NextActionPanel primaryAction={primaryAction} onNavigate={onNavigate} />

      {/* Summary Metric Cards (Scaled KPI 36-42px values) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* Total Projects */}
        <div
          onClick={() => onNavigate('projects', '/project-environment')}
          className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs hover:shadow-md transition cursor-pointer group"
        >
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-slate-600">Total Projects</span>
            <div className="w-11 h-11 rounded-xl bg-blue-50 text-blue-700 flex items-center justify-center group-hover:scale-105 transition">
              <FolderKanban className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4">
            <div className="text-4xl font-bold text-slate-900 tracking-tight">{projectsCount}</div>
            <div className="text-xs text-slate-500 mt-1">Isolated tenant workspaces</div>
          </div>
        </div>

        {/* Active Environments */}
        <div
          onClick={() => onNavigate('environments', '/project-environment')}
          className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs hover:shadow-md transition cursor-pointer group"
        >
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-slate-600">Active Environments</span>
            <div className="w-11 h-11 rounded-xl bg-indigo-50 text-indigo-700 flex items-center justify-center group-hover:scale-105 transition">
              <Boxes className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4">
            <div className="text-4xl font-bold text-slate-900 tracking-tight">{environmentsCount}</div>
            <div className="text-xs text-slate-500 mt-1">Dev, Staging &amp; Production</div>
          </div>
        </div>

        {/* AWS Regions in Use */}
        <div
          onClick={() => onNavigate('source_cloud', '/source-connection')}
          className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs hover:shadow-md transition cursor-pointer group"
        >
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-slate-600">AWS Regions in Use</span>
            <div className="w-11 h-11 rounded-xl bg-cyan-50 text-cyan-700 flex items-center justify-center group-hover:scale-105 transition">
              <Globe className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4">
            <div className="text-4xl font-bold text-slate-900 tracking-tight">{activeAwsRegions.length}</div>
            <div className="text-xs text-slate-500 mt-1 truncate">
              {activeAwsRegions.length > 0 ? activeAwsRegions.join(', ') : 'No regions attached'}
            </div>
          </div>
        </div>

        {/* Connected Cloud & Git */}
        <div
          onClick={() => onNavigate('source_cloud', '/source-connection')}
          className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs hover:shadow-md transition cursor-pointer group"
        >
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-slate-600">Connected Accounts</span>
            <div className="w-11 h-11 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center group-hover:scale-105 transition">
              <GitBranch className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4">
            <div className="text-4xl font-bold text-slate-900 tracking-tight">
              {connectionsState.git.length + connectionsState.cloud.length}
            </div>
            <div className="text-xs text-slate-500 mt-1">GitHub repos &amp; AWS IAM roles</div>
          </div>
        </div>
      </div>

      {/* Project Cards Section */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="p-6 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-50/50">
          <div>
            <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2.5">
              <FolderKanban className="w-5 h-5 text-[#1e40af]" />
              <span>Project Workspaces ({projectsCount})</span>
            </h3>
            <p className="text-sm text-slate-600 mt-0.5">
              Configured project boundaries, type classifications, and environment counts.
            </p>
          </div>

          <div className="flex items-center gap-3 w-full sm:w-auto">
            <div className="relative flex-1 sm:w-72">
              <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="Search projects by name or type..."
                value={projectSearchQuery}
                onChange={(e) => setProjectSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 text-sm rounded-xl border border-slate-200 bg-white focus:outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600 font-medium min-h-[48px]"
              />
            </div>
          </div>
        </div>

        <div className="p-6">
          {projectsState.status === 'loading' ? (
            <div className="py-12 text-center text-slate-500 text-sm">
              Loading project workspaces...
            </div>
          ) : filteredProjects.length === 0 ? (
            <div className="py-12 text-center space-y-3">
              <p className="text-slate-600 text-sm font-medium">No project workspaces found.</p>
              <button
                onClick={handleCreateProjectClick}
                className="px-4 py-2 bg-blue-600 text-white rounded-xl text-sm font-semibold hover:bg-blue-700 transition"
              >
                Create First Project
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {filteredProjects.map((proj) => (
                <div
                  key={proj.id || proj.project_id}
                  onClick={() => handleOpenProject(proj)}
                  className="p-5 rounded-xl border border-slate-200 hover:border-blue-500 hover:shadow-md transition cursor-pointer bg-white group flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-start justify-between gap-2">
                      <h4 className="font-bold text-slate-900 group-hover:text-blue-600 transition text-base">
                        {proj.name}
                      </h4>
                      <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200 shrink-0">
                        {proj.project_type || 'Standard'}
                      </span>
                    </div>
                    <p className="text-slate-600 text-sm mt-2 line-clamp-2">
                      {proj.description || 'No description provided for this tenant project.'}
                    </p>
                  </div>

                  <div className="mt-5 pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500 font-medium">
                    <span>ID: {proj.id || proj.project_id}</span>
                    <span className="text-blue-600 group-hover:translate-x-1 transition flex items-center gap-1 font-semibold">
                      <span>Open</span>
                      <ArrowRight className="w-4 h-4" />
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
