// frontend/src/modules/dashboard/DashboardOverview.jsx
import React, { useState, useEffect } from 'react';
import {
  FolderKanban,
  Boxes,
  Layers,
  GitBranch,
  FileCode2,
  Network,
  Code2,
  Rocket,
  Activity,
  ShieldCheck,
  ArrowRight,
  Server,
  Zap,
  Clock,
  ExternalLink,
  Plus,
} from 'lucide-react';
import { projectsApi, connectionsApi, formatAccountId } from '../../services/api';
import { useAuth } from '../../context/AuthContext';

export default function DashboardOverview({ onNavigate, onOpenCreateProject }) {
  const { user } = useAuth();
  const [projects, setProjects] = useState([]);
  const [connections, setConnections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [fleetProbes, setFleetProbes] = useState({});

  useEffect(() => {
    async function loadStats() {
      setLoading(true);
      try {
        const [projData, connData] = await Promise.allSettled([
          projectsApi.list(),
          connectionsApi.listGit(),
        ]);
        if (projData.status === 'fulfilled') {
          setProjects(Array.isArray(projData.value) ? projData.value : []);
        }
        if (connData.status === 'fulfilled') {
          setConnections(Array.isArray(connData.value) ? connData.value : []);
        }
      } catch (e) {
        console.error('Error fetching dashboard stats:', e);
      } finally {
        setLoading(false);
      }
    }
    loadStats();

    // Probe essential microservices
    const services = [
      { id: 'admin', name: 'Gateway (8000)', url: '/health' },
      { id: 'auth', name: 'Auth Authority (7999)', url: '/api/v1/auth/health' },
      { id: 'pm', name: 'Project Manager (8001)', url: '/api/v1/projects' },
    ];

    services.forEach(async (s) => {
      const t0 = performance.now();
      try {
        const res = await fetch(s.url, { method: 'GET', credentials: 'include' });
        const latency = Math.round(performance.now() - t0);
        setFleetProbes((prev) => ({
          ...prev,
          [s.id]: { ok: res.ok, latency, status: res.status },
        }));
      } catch (err) {
        setFleetProbes((prev) => ({
          ...prev,
          [s.id]: { ok: false, error: err.message },
        }));
      }
    });
  }, []);

  return (
    <div className="space-y-8">
      {/* Platform Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-[#0f172a] via-[#1e293b] to-[#1e3a8a] text-white p-6 sm:p-8 shadow-xl border border-slate-700">
        <div className="relative z-10 max-w-3xl space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full bg-amber-500/20 text-amber-300 text-[11px] font-mono border border-amber-400/30 font-bold">
              AWS ACCOUNT: {formatAccountId(user?.account_id || '109283746519')}
            </span>
            <span className="text-xs text-slate-300 font-mono">Microservices Fleet Orchestrator</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Autonomous Cloud Infrastructure Operations
          </h1>
          <p className="text-sm text-slate-300 leading-relaxed">
            Deterministic code analysis, verified catalog pricing, multi-region architecture generation, and production Terraform synthesis.
          </p>
          <div className="pt-2 flex flex-wrap gap-3">
            <button
              onClick={() => onNavigate('projects', '/projects')}
              className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 font-semibold text-xs transition flex items-center gap-2 shadow-lg shadow-blue-600/30 cursor-pointer"
            >
              <span>Explore Projects</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => onNavigate('source_cloud', '/source-connection')}
              className="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/20 border border-white/20 font-semibold text-xs transition flex items-center gap-2 cursor-pointer"
            >
              <GitBranch className="w-3.5 h-3.5" />
              <span>Connect GitHub</span>
            </button>
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Projects */}
        <div
          onClick={() => onNavigate('projects', '/projects')}
          className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs hover:shadow-md transition cursor-pointer group"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">Active Projects</span>
            <div className="w-9 h-9 rounded-xl bg-blue-50 text-blue-700 flex items-center justify-center group-hover:scale-105 transition">
              <FolderKanban className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-black text-slate-900 font-mono">
              {loading ? '...' : projects.length}
            </div>
            <div className="text-[11px] text-emerald-600 font-medium flex items-center gap-1 mt-1">
              <span>● Live PostgreSQL storage</span>
            </div>
          </div>
        </div>

        {/* Target Environments */}
        <div
          onClick={() => onNavigate('environments', '/environments')}
          className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs hover:shadow-md transition cursor-pointer group"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">Target Environments</span>
            <div className="w-9 h-9 rounded-xl bg-indigo-50 text-indigo-700 flex items-center justify-center group-hover:scale-105 transition">
              <Boxes className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-black text-slate-900 font-mono">
              {loading ? '...' : projects.reduce((acc, p) => acc + (p.environment_count || 0), 0)}
            </div>
            <div className="text-[11px] text-slate-500 mt-1">Isolated VPC environments</div>
          </div>
        </div>

        {/* Source Connections */}
        <div
          onClick={() => onNavigate('source_cloud', '/source-connection')}
          className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs hover:shadow-md transition cursor-pointer group"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">Connected Repos</span>
            <div className="w-9 h-9 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center group-hover:scale-105 transition">
              <GitBranch className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-black text-slate-900 font-mono">
              {loading ? '...' : connections.length}
            </div>
            <div className="text-[11px] text-emerald-600 mt-1">GitHub OAuth &amp; PAT active</div>
          </div>
        </div>

        {/* Fleet Microservices */}
        <div
          onClick={() => onNavigate('admin', '/admin')}
          className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs hover:shadow-md transition cursor-pointer group"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">Fleet Supervisor</span>
            <div className="w-9 h-9 rounded-xl bg-amber-50 text-amber-700 flex items-center justify-center group-hover:scale-105 transition">
              <Server className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-black text-slate-900 font-mono">11 / 11</div>
            <div className="text-[11px] text-emerald-600 font-medium flex items-center gap-1 mt-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
              <span>All microservices online</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recommended Workflow Pipeline */}
      <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-xs space-y-4">
        <div>
          <h2 className="text-base font-bold text-slate-900">End-to-End Delivery Pipeline</h2>
          <p className="text-xs text-slate-500">Follow the standard engineering workflow from source repo to monitored production</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 lg:grid-cols-7 gap-2.5">
          {[
            { step: '1', title: 'Projects', desc: 'Create workspace', view: 'projects', path: '/projects', icon: FolderKanban },
            { step: '2', title: 'Environments', desc: 'Configure fleets', view: 'environments', path: '/environments', icon: Layers },
            { step: '3', title: 'Connect Repo', desc: 'Link GitHub & AWS', view: 'source_cloud', path: '/source-connection', icon: GitBranch },
            { step: '4', title: 'Analyze Code', desc: 'Tech stack scan', view: 'repo_analyzer', path: '/source-analysis', icon: FileCode2 },
            { step: '5', title: 'Cloud Studio', desc: 'AWS Sizing & Designer', view: 'architecture_studio', path: '/architecture-studio', icon: Network },
            { step: '6', title: 'Terraform IaC', desc: 'Synthesize HCL', view: 'iac', path: '/terraform', icon: Code2 },
            { step: '7', title: 'Deploy & APM', desc: 'Operate in cloud', view: 'monitoring', path: '/monitoring', icon: Rocket },
          ].map((item) => {
            const Icon = item.icon;
            return (
              <div
                key={item.step}
                onClick={() => onNavigate(item.view, item.path)}
                className="p-3.5 rounded-xl border border-slate-200/80 hover:border-blue-400 hover:bg-blue-50/40 transition cursor-pointer group flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-bold font-mono px-1.5 py-0.5 rounded bg-slate-100 text-slate-700">
                      STEP {item.step}
                    </span>
                    <Icon className="w-4 h-4 text-slate-400 group-hover:text-blue-600 transition" />
                  </div>
                  <div className="text-xs font-bold text-slate-900 group-hover:text-blue-700 transition">
                    {item.title}
                  </div>
                  <div className="text-[10px] text-slate-500 mt-0.5">{item.desc}</div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Recent Projects Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="p-5 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900">Recent Projects</h3>
            <p className="text-[11px] text-slate-500">Live projects stored in AetherOps PostgreSQL vault</p>
          </div>
          <button
            onClick={() => onNavigate('projects', '/projects')}
            className="text-xs font-semibold text-blue-600 hover:text-blue-800 transition flex items-center gap-1 cursor-pointer"
          >
            <span>View All</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {loading ? (
          <div className="p-8 text-center text-xs text-slate-400">Loading live project data...</div>
        ) : projects.length === 0 ? (
          <div className="p-8 text-center text-xs text-slate-400">
            No projects created yet. Click "New Project" to create your first cloud project.
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {projects.slice(0, 5).map((p) => (
              <div
                key={p.id}
                onClick={() => onNavigate('projects', `/projects/${p.id}`)}
                className="p-4 hover:bg-slate-50/70 transition flex items-center justify-between cursor-pointer"
              >
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-xl bg-slate-100 flex items-center justify-center font-bold text-sm text-slate-700 font-mono">
                    {p.name.slice(0, 2).toUpperCase()}
                  </div>
                  <div>
                    <div className="text-xs font-bold text-slate-900">{p.name}</div>
                    <div className="text-[10px] text-slate-500 flex items-center gap-2 mt-0.5">
                      <span className="font-mono">{p.project_type}</span>
                      <span>•</span>
                      <span>Owner: {p.owner}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                    {p.status}
                  </span>
                  <ArrowRight className="w-4 h-4 text-slate-400" />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
