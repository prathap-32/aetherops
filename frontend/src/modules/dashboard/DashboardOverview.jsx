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
  Calendar,
  Layers,
  CheckCircle2,
  RefreshCw,
  Server,
} from 'lucide-react';
import {
  projectsApi,
  connectionsApi,
  deploymentsApi,
  dashboardApi,
} from '../../services/api';
import { useAuth } from '../../context/AuthContext';

export default function DashboardOverview({ onNavigate, onOpenCreateProject, onSelectProject }) {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [projectSearchQuery, setProjectSearchQuery] = useState('');

  const [projectsState, setProjectsState] = useState({ status: 'loading', data: [], error: null });
  const [environmentsState, setEnvironmentsState] = useState({ status: 'loading', data: [], error: null });
  const [connectionsState, setConnectionsState] = useState({ status: 'loading', git: [], cloud: [], error: null });

  const handleCreateProjectClick = () => {
    if (onOpenCreateProject) {
      onOpenCreateProject();
    } else if (onNavigate) {
      onNavigate('projects', '/projects');
    }
  };

  const fetchDashboardData = useCallback(async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true);
    else setLoading(true);

    try {
      const [projRes, gitRes, cloudRes] = await Promise.allSettled([
        projectsApi.list(),
        connectionsApi.listGit(),
        connectionsApi.listCloud(),
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

  // AWS regions in use from actual environments
  const activeAwsRegions = useMemo(() => {
    const regions = new Set();
    environmentsState.data.forEach((env) => {
      if (env.aws_region) regions.add(env.aws_region);
    });
    return Array.from(regions);
  }, [environmentsState.data]);

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
      onNavigate('projects', '/projects', { activeProjectId: project.id });
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-5 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
              Workspace Overview
            </h1>
            {refreshing && <RefreshCw className="w-4 h-4 animate-spin text-blue-600" />}
          </div>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Manage your cloud projects, target environments, and deployed AWS infrastructure.
          </p>
        </div>

        <div className="flex items-center gap-2.5 shrink-0">
          <button
            onClick={() => fetchDashboardData(true)}
            className="px-3.5 py-2 bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 text-xs font-semibold rounded-xl shadow-2xs transition flex items-center gap-1.5 cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin text-blue-600' : 'text-slate-400'}`} />
            <span>Refresh</span>
          </button>

          <button
            onClick={handleCreateProjectClick}
            className="px-4 py-2 bg-[#1e40af] hover:bg-[#1d4ed8] text-white text-xs font-bold rounded-xl shadow-xs transition flex items-center gap-2 cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            <span>New Project</span>
          </button>
        </div>
      </div>

      {/* Summary Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Projects */}
        <div
          onClick={() => onNavigate('projects', '/projects')}
          className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs hover:shadow-md transition cursor-pointer group"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">Total Projects</span>
            <div className="w-9 h-9 rounded-xl bg-blue-50 text-blue-700 flex items-center justify-center group-hover:scale-105 transition">
              <FolderKanban className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-slate-900">{projectsCount}</div>
            <div className="text-[11px] text-slate-500 mt-0.5">Isolated tenant workspaces</div>
          </div>
        </div>

        {/* Active Environments */}
        <div
          onClick={() => onNavigate('environments', '/environments')}
          className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs hover:shadow-md transition cursor-pointer group"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">Active Environments</span>
            <div className="w-9 h-9 rounded-xl bg-indigo-50 text-indigo-700 flex items-center justify-center group-hover:scale-105 transition">
              <Boxes className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-slate-900">{environmentsCount}</div>
            <div className="text-[11px] text-slate-500 mt-0.5">Dev, Staging &amp; Production</div>
          </div>
        </div>

        {/* AWS Regions in Use */}
        <div
          onClick={() => onNavigate('source_cloud', '/source-connection')}
          className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs hover:shadow-md transition cursor-pointer group"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">AWS Regions in Use</span>
            <div className="w-9 h-9 rounded-xl bg-cyan-50 text-cyan-700 flex items-center justify-center group-hover:scale-105 transition">
              <Globe className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-slate-900">{activeAwsRegions.length}</div>
            <div className="text-[11px] text-slate-500 mt-0.5">
              {activeAwsRegions.length > 0 ? activeAwsRegions.join(', ') : 'No regions attached'}
            </div>
          </div>
        </div>

        {/* Connected Cloud & Git */}
        <div
          onClick={() => onNavigate('source_cloud', '/source-connection')}
          className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs hover:shadow-md transition cursor-pointer group"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">Connected Accounts</span>
            <div className="w-9 h-9 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center group-hover:scale-105 transition">
              <GitBranch className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-slate-900">
              {connectionsState.git.length + connectionsState.cloud.length}
            </div>
            <div className="text-[11px] text-slate-500 mt-0.5">GitHub repos &amp; AWS IAM roles</div>
          </div>
        </div>
      </div>

      {/* Project Cards Section */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="p-5 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-slate-50/50">
          <div>
            <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <FolderKanban className="w-4 h-4 text-[#1e40af]" />
              <span>Project Workspaces ({projectsCount})</span>
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Configured project boundaries, type classifications, and environment counts.
            </p>
          </div>

          <div className="flex items-center gap-2.5 w-full sm:w-auto">
            <div className="relative flex-1 sm:w-64">
              <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="Search projects by name or type..."
                value={projectSearchQuery}
                onChange={(e) => setProjectSearchQuery(e.target.value)}
                className="w-full pl-8 pr-3 py-1.5 text-xs rounded-xl border border-slate-200 bg-white focus:outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600 font-medium"
              />
            </div>
          </div>
        </div>

        {loading ? (
          <div className="p-12 text-center text-xs text-slate-500">Loading project workspaces...</div>
        ) : filteredProjects.length === 0 ? (
          <div className="p-12 text-center space-y-3">
            <FolderKanban className="w-10 h-10 text-slate-300 mx-auto" />
            <div className="text-sm font-bold text-slate-800">No project workspaces found</div>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              Get started by creating your first AetherOps project workspace to deploy cloud infrastructure.
            </p>
            <button
              onClick={handleCreateProjectClick}
              className="px-4 py-2 bg-[#1e40af] hover:bg-[#1d4ed8] text-white text-xs font-bold rounded-xl shadow-xs transition inline-flex items-center gap-2 cursor-pointer mt-2"
            >
              <Plus className="w-4 h-4" />
              <span>New Project</span>
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-5 bg-slate-50/30">
            {filteredProjects.map((project) => {
              const pEnvs = environmentsState.data.filter((e) => e.project_id === (project.id || project.project_id));
              const createdDate = project.created_at
                ? new Date(project.created_at).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' })
                : 'Recently';

              return (
                <div
                  key={project.id || project.project_id}
                  className="bg-white rounded-2xl border border-slate-200/80 p-5 shadow-2xs hover:shadow-md transition flex flex-col justify-between gap-4 group"
                >
                  <div className="space-y-3">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <span className="text-[10px] font-bold font-mono px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200 uppercase">
                          {project.project_type || 'web_application'}
                        </span>
                        <h4 className="text-base font-bold text-slate-900 mt-2 group-hover:text-blue-600 transition">
                          {project.name}
                        </h4>
                      </div>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        (project.status || 'CREATED') === 'ACTIVE'
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          : 'bg-slate-100 text-slate-700 border border-slate-200'
                      }`}>
                        {project.status || 'CREATED'}
                      </span>
                    </div>

                    <p className="text-xs text-slate-500 line-clamp-2 leading-relaxed">
                      {project.description || 'No description provided for this cloud project workspace.'}
                    </p>
                  </div>

                  <div className="pt-3 border-t border-slate-100 space-y-3">
                    <div className="flex items-center justify-between text-xs text-slate-500">
                      <div className="flex items-center gap-1.5 font-medium">
                        <Boxes className="w-3.5 h-3.5 text-indigo-600" />
                        <span>{pEnvs.length} Environments</span>
                      </div>
                      <div className="flex items-center gap-1.5 text-[11px] text-slate-400">
                        <Calendar className="w-3.5 h-3.5" />
                        <span>{createdDate}</span>
                      </div>
                    </div>

                    <button
                      onClick={() => handleOpenProject(project)}
                      className="w-full py-2 bg-slate-900 hover:bg-[#1e40af] text-white text-xs font-semibold rounded-xl shadow-xs transition flex items-center justify-center gap-2 cursor-pointer"
                    >
                      <span>Open Project</span>
                      <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
