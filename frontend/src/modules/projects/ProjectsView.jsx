// frontend/src/modules/projects/ProjectsView.jsx
import React, { useState, useEffect } from 'react';
import { projectsApi } from '../../services/api';
import {
  FolderKanban,
  Boxes,
  Globe,
  Plus,
  RefreshCw,
  Search,
  LayoutGrid,
  List,
  ExternalLink,
  Trash2,
  Layers,
  ArrowRight,
  Server,
} from 'lucide-react';

import { PROJECT_TYPES_LIST as PROJECT_TYPES } from '../../constants/awsRegions';


export default function ProjectsView({
  searchQuery,
  onOpenCreateProject: propOnOpenCreateProject,
  isCreateModalOpen: propIsCreateModalOpen,
  onCloseCreateModal: propOnCloseCreateModal,
  showToast,
  onSwitchView,
  onNavigate,
  activeProject,
  onSelectProject,
}) {
  const [internalModalOpen, setInternalModalOpen] = useState(false);
  const isCreateModalOpen = propIsCreateModalOpen !== undefined ? propIsCreateModalOpen : internalModalOpen;
  const onOpenCreateProject = propOnOpenCreateProject || (() => setInternalModalOpen(true));
  const onCloseCreateModal = () => {
    setInternalModalOpen(false);
    if (propOnCloseCreateModal) propOnCloseCreateModal();
  };

  const handleNavigate = onSwitchView || onNavigate;

  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [sortBy, setSortBy] = useState('date-desc');
  const [viewMode, setViewMode] = useState('grid'); // 'grid' | 'list'

  // Create Project Form State
  const [newName, setNewName] = useState('');
  const [newType, setNewType] = useState('web_application');
  const [newDesc, setNewDesc] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [createError, setCreateError] = useState('');

  const fetchProjects = async () => {
    setLoading(true);
    try {
      const data = await projectsApi.list();
      setProjects(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Failed to load projects:', err);
      if (showToast) showToast('Failed to load projects: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleCreateProject = async (e) => {
    e.preventDefault();
    if (!newName.trim()) return;

    setIsSubmitting(true);
    setCreateError('');

    try {
      const created = await projectsApi.create({
        name: newName.trim(),
        project_type: newType,
        description: newDesc.trim() || null,
      });

      setNewName('');
      setNewDesc('');
      setNewType('web_application');
      onCloseCreateModal();
      if (showToast) showToast(`Project "${newName.trim()}" created successfully! Opening environment setup...`);
      await fetchProjects();

      // Ensure active project is selected and navigate to Environment Creation step
      if (onSelectProject) {
        onSelectProject(created);
      }
      if (handleNavigate) {
        handleNavigate('environments', '/environments', {
          projectId: created.id || created.project_id,
          project: created,
          autoOpenModal: true,
        });
      }
    } catch (err) {
      setCreateError(err.message || 'Failed to create project');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteProject = async (id, name, e) => {
    e.stopPropagation();
    if (!window.confirm(`Are you sure you want to delete project "${name}"?`)) return;

    try {
      await projectsApi.delete(id);
      if (showToast) showToast(`Project "${name}" deleted.`);
      await fetchProjects();
    } catch (err) {
      if (showToast) showToast('Delete failed: ' + err.message);
    }
  };

  // Metrics
  const totalProjects = projects.length;
  let totalEnvs = 0;
  const regionsSet = new Set();
  projects.forEach((p) => {
    totalEnvs += p.environment_count || (p.environments ? p.environments.length : 0);
    (p.environments || []).forEach((env) => {
      if (env.aws_region) regionsSet.add(env.aws_region);
    });
  });

  // Filter & Search
  const q = (searchQuery || '').toLowerCase().trim();
  const filtered = projects.filter((p) => {
    const matchesQ =
      !q ||
      p.name?.toLowerCase().includes(q) ||
      p.description?.toLowerCase().includes(q) ||
      p.id?.toLowerCase().includes(q);
    const matchesType = filterType === 'all' || p.project_type === filterType;
    const matchesStatus = filterStatus === 'all' || p.status === filterStatus;
    return matchesQ && matchesType && matchesStatus;
  });

  // Sort
  filtered.sort((a, b) => {
    if (sortBy === 'date-desc') return new Date(b.created_at || 0) - new Date(a.created_at || 0);
    if (sortBy === 'date-asc') return new Date(a.created_at || 0) - new Date(b.created_at || 0);
    if (sortBy === 'name-asc') return (a.name || '').localeCompare(b.name || '');
    if (sortBy === 'envs-desc') return (b.environment_count || 0) - (a.environment_count || 0);
    return 0;
  });

  const getStatusBadge = (status) => {
    if (status === 'ACTIVE') {
      return (
        <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
          Active
        </span>
      );
    }
    if (status === 'ARCHIVED') {
      return (
        <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-semibold bg-slate-100 text-slate-600 border border-slate-200 flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-slate-400"></span>
          Archived
        </span>
      );
    }
    return (
      <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-semibold bg-blue-50 text-[#1e40af] border border-blue-200 flex items-center gap-1.5">
        <span className="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
        Ready
      </span>
    );
  };

  return (
    <div className="space-y-6">
      {/* Page Title & Top Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Projects</h1>
            <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded-md bg-blue-50 text-[#1e40af] border border-blue-100">
              {totalProjects} registered
            </span>
          </div>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Manage your autonomous cloud workspaces, target infrastructure, and container environments.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={fetchProjects}
            className="p-2 text-slate-600 hover:text-slate-900 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 shadow-xs transition"
            title="Refresh projects"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <button
            onClick={onOpenCreateProject}
            className="px-3.5 py-2 rounded-lg bg-[#1e40af] hover:bg-[#1d4ed8] text-white text-xs font-semibold shadow-xs transition flex items-center gap-1.5 cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            <span>New Project</span>
          </button>
        </div>
      </div>

      {/* Fleet KPI Metric Cards */}
      <section className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white border border-slate-200/90 rounded-2xl p-5 space-y-2 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Total Workspaces</span>
            <div className="w-8 h-8 rounded-lg bg-blue-50 text-[#1e40af] flex items-center justify-center">
              <FolderKanban className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold font-mono text-slate-900">{totalProjects}</span>
            <span className="text-xs text-slate-500 font-medium">projects</span>
          </div>
          <p className="text-xs text-slate-500">Applications configured in your tenant</p>
        </div>

        <div
          onClick={() => handleNavigate && handleNavigate('environments')}
          className="bg-white border border-slate-200/90 hover:border-blue-300 rounded-2xl p-5 space-y-2 shadow-xs cursor-pointer transition"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Target Environments</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-700 flex items-center justify-center">
              <Boxes className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold font-mono text-slate-900">{totalEnvs}</span>
            <span className="text-xs text-slate-500 font-medium">deployed fleets</span>
          </div>
          <p className="text-xs text-slate-500">Dev, Staging &amp; Production clusters</p>
        </div>

        <div className="bg-white border border-slate-200/90 rounded-2xl p-5 space-y-2 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">AWS Regions</span>
            <div className="w-8 h-8 rounded-lg bg-blue-50 text-[#1e40af] flex items-center justify-center">
              <Globe className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold font-mono text-slate-900">{regionsSet.size}</span>
            <span className="text-xs text-slate-500 font-medium">active regions</span>
          </div>
          <div className="flex flex-wrap gap-1">
            {Array.from(regionsSet).slice(0, 3).map((r) => (
              <span key={r} className="px-2 py-0.5 rounded text-xs font-mono bg-slate-100 text-slate-700 border border-slate-200">
                {r}
              </span>
            ))}
            {regionsSet.size === 0 && <span className="text-xs text-slate-400 italic">No regions bound</span>}
          </div>
        </div>
      </section>

      {/* Filter and View Controls Toolbar */}
      <div className="bg-white border border-slate-200/80 rounded-xl p-3 flex flex-wrap items-center justify-between gap-3 shadow-xs">
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <span className="text-slate-400 font-medium text-[11px]">Type:</span>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-2.5 py-1.5 rounded-lg border border-slate-200 bg-slate-50 text-slate-700 font-medium focus:outline-none focus:border-[#1e40af]"
          >
            <option value="all">All Types</option>
            <option value="web_application">Web App</option>
            <option value="api_service">API Service</option>
            <option value="microservices">Microservices</option>
            <option value="data_pipeline">Data Pipeline</option>
          </select>

          <span className="text-slate-400 font-medium text-[11px] ml-2">Status:</span>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-2.5 py-1.5 rounded-lg border border-slate-200 bg-slate-50 text-slate-700 font-medium focus:outline-none focus:border-[#1e40af]"
          >
            <option value="all">All Status</option>
            <option value="CREATED">CREATED</option>
            <option value="ACTIVE">ACTIVE</option>
            <option value="ARCHIVED">ARCHIVED</option>
          </select>
        </div>

        <div className="flex items-center gap-2">
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-2.5 py-1.5 text-xs rounded-lg border border-slate-200 bg-slate-50 text-slate-700 font-medium focus:outline-none focus:border-[#1e40af]"
          >
            <option value="date-desc">Newest First</option>
            <option value="date-asc">Oldest First</option>
            <option value="name-asc">Alphabetical</option>
            <option value="envs-desc">Most Environments</option>
          </select>

          <div className="flex bg-slate-100 p-0.5 rounded-lg border border-slate-200">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-1.5 rounded-md transition ${viewMode === 'grid' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-400 hover:text-slate-700'}`}
              title="Grid View"
            >
              <LayoutGrid className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-1.5 rounded-md transition ${viewMode === 'list' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-400 hover:text-slate-700'}`}
              title="List View"
            >
              <List className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Projects Grid / List View */}
      {filtered.length === 0 ? (
        <div className="bg-white border border-slate-200/80 rounded-2xl p-12 text-center space-y-4 shadow-xs">
          <div className="w-12 h-12 rounded-2xl bg-blue-50 text-[#1e40af] flex items-center justify-center mx-auto">
            <FolderKanban className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-slate-900">No Projects Found</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1">
              {q ? 'No projects match your search query.' : 'Create your first project workspace to start orchestrating cloud infrastructure.'}
            </p>
          </div>
          <button
            onClick={onOpenCreateProject}
            className="px-4 py-2 rounded-lg bg-[#1e40af] text-white text-xs font-semibold shadow-xs hover:bg-[#1d4ed8] transition inline-flex items-center gap-1.5"
          >
            <Plus className="w-4 h-4" />
            <span>Create Project</span>
          </button>
        </div>
      ) : viewMode === 'grid' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {filtered.map((project) => {
            const envCount = project.environment_count || (project.environments ? project.environments.length : 0);
            return (
              <div
                key={project.id}
                className="bg-white border border-slate-200/90 hover:border-blue-300 rounded-2xl p-5 shadow-xs hover:shadow-md transition flex flex-col justify-between group space-y-4"
              >
                <div
                  className="space-y-3 cursor-pointer"
                  onClick={() => {
                    if (onSelectProject) onSelectProject(project);
                    if (handleNavigate) {
                      handleNavigate('environments', '/environments', {
                        projectId: project.id,
                        project: project,
                      });
                    }
                  }}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2.5 min-w-0">
                      <div className="w-9 h-9 rounded-xl bg-blue-50 text-[#1e40af] flex items-center justify-center font-bold text-sm shrink-0">
                        {project.project_type === 'api_service' ? '⚡' : project.project_type === 'microservices' ? '🧩' : '🌐'}
                      </div>
                      <div className="min-w-0">
                        <h3 className="text-sm font-bold text-slate-900 tracking-tight truncate group-hover:text-[#1e40af] transition">
                          {project.name}
                        </h3>
                        <span className="text-[10px] font-mono text-slate-400 truncate block">
                          owner: {project.owner}
                        </span>
                      </div>
                    </div>
                    {getStatusBadge(project.status)}
                  </div>

                  <p className="text-xs text-slate-500 line-clamp-2 min-h-[32px]">
                    {project.description || 'No project description configured.'}
                  </p>
                </div>

                <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-mono text-[10px] font-semibold">
                      {envCount} {envCount === 1 ? 'env' : 'envs'}
                    </span>
                    <span className="text-[10px] font-mono uppercase text-slate-400">
                      {project.project_type?.replace('_', ' ')}
                    </span>
                  </div>

                  <div className="flex items-center gap-1.5">
                    <button
                      onClick={() => {
                        if (onSelectProject) onSelectProject(project);
                        if (handleNavigate) {
                          handleNavigate('environments', '/environments', {
                            projectId: project.id,
                            project: project,
                          });
                        }
                      }}
                      className="p-1 text-slate-400 hover:text-blue-600 rounded transition cursor-pointer"
                      title="Manage Environments"
                    >
                      <ArrowRight className="w-4 h-4" />
                    </button>
                    <button
                      onClick={(e) => handleDeleteProject(project.id, project.name, e)}
                      className="p-1 text-slate-400 hover:text-rose-600 rounded transition"
                      title="Delete Project"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="bg-white border border-slate-200/90 rounded-2xl overflow-hidden shadow-xs">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50/80 border-b border-slate-200/80 text-slate-500 font-semibold uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="px-5 py-3.5">Project Workspace</th>
                  <th className="px-4 py-3.5">Type</th>
                  <th className="px-4 py-3.5">Status</th>
                  <th className="px-4 py-3.5">Environments</th>
                  <th className="px-4 py-3.5">Created</th>
                  <th className="px-4 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filtered.map((project) => (
                  <tr
                    key={project.id}
                    onClick={() => {
                      if (onSelectProject) onSelectProject(project);
                      if (handleNavigate) {
                        handleNavigate('environments', '/environments', {
                          projectId: project.id,
                          project: project,
                        });
                      }
                    }}
                    className="hover:bg-slate-50/70 transition cursor-pointer"
                  >
                    <td className="px-5 py-3.5">
                      <div className="font-semibold text-slate-900">{project.name}</div>
                      <div className="text-[10px] font-mono text-slate-400">owner: {project.owner}</div>
                    </td>
                    <td className="px-4 py-3.5 font-mono text-slate-600">
                      {project.project_type?.replace('_', ' ')}
                    </td>
                    <td className="px-4 py-3.5">{getStatusBadge(project.status)}</td>
                    <td className="px-4 py-3.5">
                      <span className="font-mono font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700 text-[10px]">
                        {project.environment_count || 0} fleets
                      </span>
                    </td>
                    <td className="px-4 py-3.5 text-slate-500 font-mono text-[11px]">
                      {project.created_at ? new Date(project.created_at).toLocaleDateString() : '—'}
                    </td>
                    <td className="px-4 py-3.5 text-right">
                      <button
                        onClick={(e) => handleDeleteProject(project.id, project.name, e)}
                        className="p-1.5 text-slate-400 hover:text-rose-600 rounded transition"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* New Project Modal */}
      {isCreateModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs">
          <div className="bg-white border border-slate-200 rounded-2xl w-full max-w-md p-6 space-y-5 shadow-2xl animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-blue-50 text-[#1e40af] flex items-center justify-center font-bold text-base">
                  +
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-900">New Project</h3>
                  <p className="text-[11px] text-slate-500">Configure your application workspace</p>
                </div>
              </div>
              <button
                onClick={onCloseCreateModal}
                className="text-slate-400 hover:text-slate-600 p-1 rounded-md"
              >
                ×
              </button>
            </div>

            {createError && (
              <div className="p-2.5 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-xs font-medium">
                {createError}
              </div>
            )}

            <form onSubmit={handleCreateProject} className="space-y-4">
              <div className="space-y-1">
                <label className="block text-xs font-semibold text-slate-700">
                  Project Name <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. fooddelivery-api"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  className="w-full px-3 py-2 text-xs font-mono rounded-lg border border-slate-300 focus:outline-none focus:border-[#1e40af] focus:ring-1 focus:ring-[#1e40af]"
                />
              </div>

              <div className="space-y-1.5">
                <label className="block text-xs font-semibold text-slate-700">
                  Project Type <span className="text-slate-400 font-normal">({PROJECT_TYPES.length} available types)</span>
                </label>
                <div className="grid grid-cols-2 gap-2 max-h-48 overflow-y-auto pr-1">
                  {PROJECT_TYPES.map((t) => (
                    <button
                      key={t.value}
                      type="button"
                      onClick={() => setNewType(t.value)}
                      title={t.desc}
                      className={`flex items-center gap-2 p-2 rounded-xl text-xs font-semibold border transition text-left ${
                        newType === t.value
                          ? 'border-[#1e40af] bg-blue-50/70 text-[#1e40af] shadow-xs ring-1 ring-blue-500/30'
                          : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300 hover:bg-slate-50/50'
                      }`}
                    >
                      <span className="text-base shrink-0">{t.icon}</span>
                      <div className="truncate">
                        <div className="truncate">{t.label}</div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              <div className="space-y-1">
                <label className="block text-xs font-semibold text-slate-700">Description</label>
                <textarea
                  rows={2}
                  placeholder="Optional brief description of services..."
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:outline-none focus:border-[#1e40af] focus:ring-1 focus:ring-[#1e40af]"
                />
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={onCloseCreateModal}
                  className="px-4 py-2 text-xs font-medium rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 text-xs font-semibold rounded-lg bg-[#1e40af] hover:bg-[#1d4ed8] text-white shadow-xs transition disabled:opacity-50"
                >
                  {isSubmitting ? 'Creating...' : 'Create Project'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
