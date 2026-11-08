// frontend/src/modules/environments/EnvironmentsView.jsx
import React, { useState, useEffect } from 'react';
import {
  Layers,
  Plus,
  RefreshCw,
  Search,
  Filter,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Server,
  Globe,
  ExternalLink,
  ChevronRight,
  Shield,
  Trash2,
} from 'lucide-react';
import { projectsApi, formatAccountId } from '../../services/api';
import { AWS_REGIONS_39, TIER_TYPES_LIST } from '../../constants/awsRegions';
import { useAuth } from '../../context/AuthContext';

export default function EnvironmentsView({
  user: propUser,
  onNavigate,
  activeProject,
  activeEnvironment,
  onSelectEnvironment,
  navState,
}) {
  const { user: authUser } = useAuth();
  const user = propUser || authUser;
  const [projects, setProjects] = useState([]);
  const [environments, setEnvironments] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('ALL');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // New Environment Modal state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalProjectId, setModalProjectId] = useState('');
  const [envName, setEnvName] = useState('');
  const [envType, setEnvType] = useState('development');
  const [region, setRegion] = useState('us-east-1');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleDeleteEnv = async (env, e) => {
    if (e) e.stopPropagation();
    const envId = env.id || env.env_id;
    const name = env.name || env.env_name || 'this environment';
    if (!window.confirm(`Are you sure you want to delete environment "${name}"?`)) return;

    try {
      await projectsApi.deleteEnvironment(env.projectId, envId);
      await loadData();
    } catch (err) {
      alert(`Failed to delete environment: ${err.message || err}`);
    }
  };
  const targetProjectId = navState?.projectId || activeProject?.id || activeProject?.project_id || null;

  useEffect(() => {
    if (targetProjectId) {
      setSelectedProjectId(targetProjectId);
      setModalProjectId(targetProjectId);
    }
    if (navState?.autoOpenModal) {
      setIsModalOpen(true);
    }
  }, [navState, targetProjectId]);

  const loadData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const projList = await projectsApi.list();
      setProjects(projList);

      const defaultPid = targetProjectId || (projList.length > 0 ? (projList[0].id || projList[0].project_id) : '');
      if (defaultPid && !modalProjectId) {
        setModalProjectId(defaultPid);
      }
      if (targetProjectId) {
        setSelectedProjectId(targetProjectId);
      }

      // Fetch environments for all projects
      let allEnvs = [];
      for (const p of projList) {
        const pid = p.id || p.project_id;
        try {
          const envs = await projectsApi.listEnvironments(pid);
          const enriched = envs.map(e => ({
            ...e,
            projectName: p.name || p.project_name || 'Project ' + pid,
            projectId: pid,
          }));
          allEnvs = allEnvs.concat(enriched);
        } catch (e) {
          console.warn(`Failed to load envs for project ${pid}:`, e);
        }
      }
      setEnvironments(allEnvs);
    } catch (err) {
      console.error('Failed to load environments:', err);
      setError(err.message || 'Failed to fetch environments');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();

    const interval = setInterval(() => {
      if (!document.hidden) {
        loadData();
      }
    }, 6000);

    return () => clearInterval(interval);
  }, []);
  const handleCreateEnv = async (e) => {
    e.preventDefault();
    if (!modalProjectId || !envName.trim()) return;

    setIsSubmitting(true);
    try {
      const created = await projectsApi.createEnvironment(modalProjectId, {
        name: envName.trim(),
        env_type: envType.toLowerCase(),
        type: envType.toLowerCase(),
        aws_region: region.toLowerCase(),
        region: region.toLowerCase(),
        account_id: user?.account_id || null,
      });
      setIsModalOpen(false);
      setEnvName('');
      await loadData();

      const projObj = projects.find(p => (p.id || p.project_id) === modalProjectId) || activeProject;
      const enrichedEnv = {
        ...created,
        projectId: modalProjectId,
        projectName: projObj?.name || 'Project',
      };
      if (onSelectEnvironment) {
        onSelectEnvironment(enrichedEnv);
      }
    } catch (err) {
      alert(`Failed to create environment: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Filter logic
  const filteredEnvironments = environments.filter((env) => {
    const matchesProj = selectedProjectId === 'ALL' || env.projectId === selectedProjectId;
    const matchesType = filterType === 'ALL' || (env.type || env.env_type || '').toUpperCase() === filterType;
    const matchesSearch =
      (env.name || env.env_name || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
      (env.projectName || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
      (env.region || env.aws_region || '').toLowerCase().includes(searchQuery.toLowerCase());
    return matchesProj && matchesType && matchesSearch;
  });

  const getEnvBadgeColor = (type) => {
    const t = (type || '').toLowerCase();
    switch (t) {
      case 'prod':
      case 'production':
        return 'bg-rose-50 text-rose-700 border-rose-200';
      case 'staging':
      case 'stage':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'testing':
      case 'test':
        return 'bg-purple-50 text-purple-700 border-purple-200';
      case 'qa':
        return 'bg-indigo-50 text-indigo-700 border-indigo-200';
      case 'dr':
      case 'disaster_recovery':
        return 'bg-orange-50 text-orange-700 border-orange-200';
      case 'sandbox':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'dev':
      case 'development':
      default:
        return 'bg-blue-50 text-blue-700 border-blue-200';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Environment</h1>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={loadData}
            disabled={isLoading}
            className="p-2 text-slate-600 hover:text-slate-900 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition shadow-xs"
            title="Refresh environments"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
          <button
            onClick={() => setIsModalOpen(true)}
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg shadow-xs transition"
          >
            <Plus className="w-4 h-4" />
            New Environment
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-xs">
          <div className="flex items-center justify-between">
            <p className="text-xs font-medium uppercase tracking-wider text-slate-400">Total</p>
            <div className="p-2 rounded-lg bg-blue-50 text-blue-600">
              <Layers className="w-5 h-5" />
            </div>
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-2">{environments.length}</p>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-xs">
          <div className="flex items-center justify-between">
            <p className="text-xs font-medium uppercase tracking-wider text-slate-400">Dev &amp; Testing</p>
            <div className="p-2 rounded-lg bg-emerald-50 text-emerald-600">
              <Server className="w-5 h-5" />
            </div>
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-2">
            {environments.filter(e => ['DEV', 'DEVELOPMENT', 'TEST', 'TESTING', 'QA', 'SANDBOX'].includes((e.type || e.env_type || '').toUpperCase())).length}
          </p>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-xs">
          <div className="flex items-center justify-between">
            <p className="text-xs font-medium uppercase tracking-wider text-slate-400">Staging</p>
            <div className="p-2 rounded-lg bg-amber-50 text-amber-600">
              <Clock className="w-5 h-5" />
            </div>
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-2">
            {environments.filter(e => ['STAGE', 'STAGING'].includes((e.type || e.env_type || '').toUpperCase())).length}
          </p>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-xs">
          <div className="flex items-center justify-between">
            <p className="text-xs font-medium uppercase tracking-wider text-slate-400">Production</p>
            <div className="p-2 rounded-lg bg-rose-50 text-rose-600">
              <Shield className="w-5 h-5" />
            </div>
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-2">
            {environments.filter(e => ['PROD', 'PRODUCTION'].includes((e.type || e.env_type || '').toUpperCase())).length}
          </p>
        </div>
      </div>


      {/* Filter / Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs flex flex-col md:flex-row items-center gap-4 justify-between">
        <div className="flex items-center gap-3 w-full md:w-auto flex-1">
          <div className="relative w-full max-w-sm">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search environments, projects, regions..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
            />
          </div>

          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-400" />
            <select
              value={selectedProjectId}
              onChange={(e) => setSelectedProjectId(e.target.value)}
              className="text-sm bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
            >
              <option value="ALL">All Projects</option>
              {projects.map((p) => {
                const pid = p.id || p.project_id;
                return (
                  <option key={pid} value={pid}>
                    {p.name || p.project_name || pid}
                  </option>
                );
              })}
            </select>
          </div>
        </div>

        <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-lg w-full md:w-auto">
          {['ALL', 'DEV', 'STAGING', 'PROD'].map((type) => (
            <button
              key={type}
              onClick={() => setFilterType(type)}
              className={`px-3 py-1.5 text-xs font-semibold rounded-md transition ${
                filterType === type
                  ? 'bg-white text-slate-900 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      {/* Environments List */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        {isLoading ? (
          <div className="py-20 text-center">
            <RefreshCw className="w-8 h-8 text-blue-500 animate-spin mx-auto mb-3" />
            <p className="text-sm text-slate-500 font-medium">Scanning fleet environments...</p>
          </div>
        ) : error ? (
          <div className="py-12 text-center">
            <AlertTriangle className="w-10 h-10 text-rose-500 mx-auto mb-3" />
            <p className="text-sm text-rose-600 font-medium">{error}</p>
            <button
              onClick={loadData}
              className="mt-3 px-4 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-medium rounded-lg transition"
            >
              Try Again
            </button>
          </div>
        ) : filteredEnvironments.length === 0 ? (
          <div className="py-16 text-center">
            <div className="w-12 h-12 rounded-full bg-slate-100 text-slate-400 flex items-center justify-center mx-auto mb-3">
              <Layers className="w-6 h-6" />
            </div>
            <h3 className="text-base font-semibold text-slate-900">No environments found</h3>
            <p className="text-sm text-slate-500 mt-1 max-w-sm mx-auto">
              {searchQuery || filterType !== 'ALL' || selectedProjectId !== 'ALL'
                ? 'No environments match your current filters. Clear the search or selection to view all.'
                : 'Create an environment under one of your projects to begin provisioning AWS infrastructure.'}
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-xs font-medium rounded-lg hover:bg-blue-700 transition"
            >
              <Plus className="w-3.5 h-3.5" />
              Add Environment
            </button>
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {filteredEnvironments.map((env) => {
              const envId = env.id || env.env_id;
              const type = env.type || env.env_type || 'DEV';
              const name = env.name || env.env_name || 'Unnamed Environment';
              const reg = env.region || 'us-east-1';

              return (
                <div
                  key={envId}
                  className="p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-slate-50/70 transition"
                >
                  <div className="flex items-start gap-3.5">
                    <div className="w-10 h-10 rounded-lg bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600 shrink-0 mt-0.5">
                      <Server className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2.5">
                        <h4 className="text-sm font-semibold text-slate-900">{name}</h4>
                        <span
                          className={`text-[11px] font-semibold px-2 py-0.5 rounded-full border ${getEnvBadgeColor(
                            type
                          )}`}
                        >
                          {type.toUpperCase()}
                        </span>
                        <span className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                          <CheckCircle2 className="w-3 h-3 text-emerald-500" />
                          Ready
                        </span>
                      </div>
                      <div className="flex items-center gap-2 flex-wrap text-xs text-slate-500 mt-1">
                        <span className="font-medium text-slate-700">Project: {env.projectName}</span>
                        <span>•</span>
                        <span className="flex items-center gap-1 text-slate-600">
                          <Globe className="w-3.5 h-3.5 text-slate-400" />
                          {reg}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 self-end md:self-auto">
                    {onNavigate && (
                      <button
                        onClick={() => {
                          if (onSelectEnvironment) onSelectEnvironment(env);
                          onNavigate('source_cloud', '/source-connection', {
                            projectId: env.projectId,
                            environmentId: envId,
                            environment: env,
                          });
                        }}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-blue-600 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition cursor-pointer"
                      >
                        <span>Connect Cloud &amp; Git</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                      </button>
                    )}

                    <button
                      type="button"
                      onClick={(e) => handleDeleteEnv(env, e)}
                      className="p-1.5 text-slate-400 hover:text-rose-600 rounded transition cursor-pointer"
                      title="Delete Environment"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Create Environment Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs">
          <div className="bg-white rounded-2xl max-w-md w-full shadow-2xl border border-slate-200 p-6 animate-in fade-in zoom-in-95 duration-200">
            <h3 className="text-lg font-bold text-slate-900">New Environment</h3>

            <form onSubmit={handleCreateEnv} className="mt-5 space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                  Target Project
                </label>
                {projects.length === 0 ? (
                  <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-800 flex items-center justify-between">
                    <span>No projects found in this workspace yet.</span>
                    {onNavigate && (
                      <button
                        type="button"
                        onClick={() => { setIsModalOpen(false); onNavigate('projects', '/projects'); }}
                        className="font-bold underline ml-2 hover:text-amber-950"
                      >
                        Create Project First
                      </button>
                    )}
                  </div>
                ) : (
                  <select
                    value={modalProjectId}
                    onChange={(e) => setModalProjectId(e.target.value)}
                    className="w-full text-sm bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                    required
                  >
                    {projects.map((p) => {
                      const pid = p.id || p.project_id;
                      return (
                        <option key={pid} value={pid}>
                          {p.name || p.project_name || pid}
                        </option>
                      );
                    })}
                  </select>
                )}
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                  Environment Name
                </label>
                <input
                  type="text"
                  placeholder="e.g. production-us-east, staging-api, dev-cluster"
                  value={envName}
                  onChange={(e) => setEnvName(e.target.value)}
                  className="w-full text-sm bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                  required
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                    Tier Type ({TIER_TYPES_LIST.length})
                  </label>
                  <select
                    value={envType}
                    onChange={(e) => setEnvType(e.target.value)}
                    className="w-full text-sm bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                  >
                    {TIER_TYPES_LIST.map((t) => (
                      <option key={t.value} value={t.value}>
                        {t.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                    AWS Region (Total {AWS_REGIONS_39.length})
                  </label>
                  <select
                    value={region}
                    onChange={(e) => setRegion(e.target.value)}
                    className="w-full text-sm bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                  >
                    {AWS_REGIONS_39.map((r) => (
                      <option key={r.value} value={r.value}>
                        {r.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 text-xs font-semibold text-slate-600 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 text-xs font-semibold bg-blue-600 hover:bg-blue-700 text-white rounded-lg shadow-xs transition disabled:opacity-50 flex items-center gap-1.5"
                >
                  {isSubmitting ? (
                    <>
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                      Provisioning...
                    </>
                  ) : (
                    'Create Environment'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
