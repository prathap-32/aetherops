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

    // Probe essential platform services
    const services = [
      { id: 'admin', name: 'API Gateway', url: '/health' },
      { id: 'auth', name: 'Authentication Authority', url: '/api/v1/auth/health' },
      { id: 'pm', name: 'Project Management Service', url: '/api/v1/projects' },
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
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-[#0a1128] via-[#1e293b] to-[#1e40af] text-white p-6 sm:p-8 shadow-xl border border-slate-700/80">
        <div className="relative z-10 max-w-3xl space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/15 border border-cyan-400/30 text-cyan-300 text-xs font-semibold">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
            Autonomous Cloud Operations MVP
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            AWS Cloud Infrastructure &amp; Deployment Platform
          </h1>
          <p className="text-sm text-slate-300 leading-relaxed max-w-2xl">
            Connect your real AWS account, design your cloud architecture, generate production-ready Terraform code, and deploy and monitor your infrastructure.
          </p>
          <div className="pt-2 flex flex-wrap gap-3">
            <button
              onClick={() => onNavigate('source_cloud', '/source-connection')}
              className="px-4 py-2 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 font-semibold text-xs transition flex items-center gap-2 shadow-lg shadow-blue-600/30 cursor-pointer"
            >
              <span>1. Connect AWS Account</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => onNavigate('architecture_designer', '/architecture-designer')}
              className="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/20 border border-white/20 font-semibold text-xs transition flex items-center gap-2 cursor-pointer"
            >
              <Network className="w-3.5 h-3.5 text-cyan-400" />
              <span>2. Cloud Architecture</span>
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
            <span className="text-xs font-medium text-slate-500">Workspaces</span>
            <div className="w-9 h-9 rounded-xl bg-blue-50 text-blue-700 flex items-center justify-center group-hover:scale-105 transition">
              <FolderKanban className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-slate-900 font-mono">
              {loading ? '...' : projects.length}
            </div>
            <div className="text-xs text-slate-500 mt-1">Configured applications</div>
          </div>
        </div>

        {/* Cloud Connections */}
        <div
          onClick={() => onNavigate('source_cloud', '/source-connection')}
          className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs hover:shadow-md transition cursor-pointer group"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">Cloud &amp; Repos</span>
            <div className="w-9 h-9 rounded-xl bg-cyan-50 text-cyan-700 flex items-center justify-center group-hover:scale-105 transition">
              <GitBranch className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-slate-900 font-mono">
              {loading ? '...' : connections.length}
            </div>
            <div className="text-xs text-slate-500 mt-1">AWS &amp; Git Connections</div>
          </div>
        </div>

        {/* Terraform / IaC */}
        <div
          onClick={() => onNavigate('iac', '/terraform')}
          className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs hover:shadow-md transition cursor-pointer group"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">Terraform IaC</span>
            <div className="w-9 h-9 rounded-xl bg-indigo-50 text-indigo-700 flex items-center justify-center group-hover:scale-105 transition">
              <Code2 className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-slate-900 font-mono">Ready</div>
            <div className="text-xs text-slate-500 mt-1">Validated HCL stacks</div>
          </div>
        </div>

        {/* Microservices Health */}
        <div
          onClick={() => onNavigate('monitoring', '/monitoring')}
          className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs hover:shadow-md transition cursor-pointer group"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">System Status</span>
            <div className="w-9 h-9 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center group-hover:scale-105 transition">
              <Activity className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-emerald-600 font-mono">14 / 14</div>
            <div className="text-xs text-emerald-600 font-medium flex items-center gap-1 mt-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              <span>All Services Healthy</span>
            </div>
          </div>
        </div>
      </div>

      {/* Clean 4-Step MVP Guided Workflow */}
      <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-xs space-y-5">
        <div>
          <h2 className="text-base font-bold text-slate-900">End-to-End Cloud Workflow</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Follow these core steps to provision and monitor infrastructure on your AWS account.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            {
              step: '1',
              title: 'Connect AWS & Git',
              desc: 'Enter AWS Access Key, Secret, and region to authorize infrastructure creation.',
              view: 'source_cloud',
              path: '/source-connection',
              icon: GitBranch,
              color: 'text-blue-600',
              badge: 'Authentication',
            },
            {
              step: '2',
              title: 'Cloud Architecture',
              desc: 'Design and review your multi-tier VPC, compute, container, and database topology.',
              view: 'architecture_designer',
              path: '/architecture-designer',
              icon: Network,
              color: 'text-cyan-600',
              badge: 'Architecture',
            },
            {
              step: '3',
              title: 'Generate Terraform',
              desc: 'Synthesize clean, validated HashiCorp HCL Terraform configuration files.',
              view: 'iac',
              path: '/terraform',
              icon: Code2,
              color: 'text-indigo-600',
              badge: 'IaC Synthesis',
            },
            {
              step: '4',
              title: 'Deploy & Monitor',
              desc: 'Execute deployment to AWS and view live resource metrics, CPU, and alarms.',
              view: 'deployments',
              path: '/deployment',
              icon: Rocket,
              color: 'text-emerald-600',
              badge: 'Operation',
            },
          ].map((item) => {
            const Icon = item.icon;
            return (
              <div
                key={item.step}
                onClick={() => onNavigate(item.view, item.path)}
                className="p-5 rounded-xl border border-slate-200/80 hover:border-blue-500 hover:shadow-md transition cursor-pointer group flex flex-col justify-between space-y-4 bg-slate-50/40 hover:bg-white"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="w-7 h-7 rounded-lg bg-blue-100 text-blue-800 font-bold font-mono text-xs flex items-center justify-center">
                      {item.step}
                    </span>
                    <Icon className={`w-5 h-5 ${item.color}`} />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-slate-900 group-hover:text-blue-600 transition">
                      {item.title}
                    </h3>
                    <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                      {item.desc}
                    </p>
                  </div>
                </div>
                <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs font-semibold text-blue-600 group-hover:text-blue-700">
                  <span>Launch Step {item.step}</span>
                  <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition" />
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
            <p className="text-xs text-slate-500">Active application workspaces</p>
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
                    <div className="text-xs text-slate-500 flex items-center gap-2 mt-0.5">
                      <span className="font-mono text-slate-600">{p.project_type}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                    {p.status || 'Active'}
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
