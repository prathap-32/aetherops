// frontend/src/modules/deployments/DeploymentsView.jsx
import React, { useState, useEffect } from 'react';
import {
  Rocket,
  GitCommit,
  CheckCircle2,
  XCircle,
  RefreshCw,
  Clock,
  Layers,
  Terminal,
  ArrowRight,
  ShieldCheck,
  AlertTriangle,
  Play
} from 'lucide-react';
import { deploymentsApi } from '../../services/api';

export default function DeploymentsView({ onNavigate, activeProject, activeEnvironment }) {
  const [deployments, setDeployments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedDep, setSelectedDep] = useState(null);
  const [depLogs, setDepLogs] = useState([]);
  const [depResources, setDepResources] = useState([]);
  const [inspectModalOpen, setInspectModalOpen] = useState(false);
  const [inspectLoading, setInspectLoading] = useState(false);

  const projectName = activeProject?.name || activeProject?.id;

  const fetchDeployments = async () => {
    setLoading(true);
    setError(null);
    try {
      const resp = await deploymentsApi.list(projectName);
      if (resp?.deployments) {
        setDeployments(resp.deployments);
      }
    } catch (err) {
      console.warn('Fetch deployments error:', err);
      setError(err.message || 'Could not retrieve deployments');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDeployments();
  }, [projectName]);

  const handleInspectDeployment = async (dep) => {
    setSelectedDep(dep);
    setInspectModalOpen(true);
    setInspectLoading(true);
    try {
      const [logsRes, resRes] = await Promise.all([
        deploymentsApi.getLogs(dep.deployment_id).catch(() => ({ logs: [] })),
        deploymentsApi.getResources(dep.deployment_id).catch(() => ({ resources: [] })),
      ]);
      setDepLogs(logsRes?.logs || []);
      setDepResources(resRes?.resources || []);
    } catch (e) {
      console.warn('Inspect deployment notice:', e);
    } finally {
      setInspectLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Cloud Deployments &amp; State Inventory</h1>
            <span className="px-2.5 py-0.5 rounded text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
              Module 8 &amp; 9: Live Operations
            </span>
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Verified cloud infrastructure mutations, real-time apply logs, and continuous state drift auditing.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={fetchDeployments}
            disabled={loading}
            className="px-3.5 py-2 rounded-lg bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 text-xs font-semibold transition flex items-center gap-1.5 cursor-pointer shadow-xs"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
          <button
            onClick={() => onNavigate('execution', '/execution')}
            className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold transition flex items-center gap-1.5 cursor-pointer shadow-xs"
          >
            <Play className="w-3.5 h-3.5" />
            <span>New Deployment</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-medium flex items-center gap-2">
          <XCircle className="w-4 h-4 text-rose-600 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Deployments List Card */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-5 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900">Recorded Deployment Runs</h3>
            <p className="text-xs text-slate-500 mt-0.5">Retrieved from AetherOps Cloud Deployer Engine (Port 8011)</p>
          </div>
          <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200">
            {deployments.length} Runs Recorded
          </span>
        </div>

        {loading ? (
          <div className="py-16 text-center text-slate-500 text-xs">
            <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-blue-500" />
            <span>Loading deployment records...</span>
          </div>
        ) : deployments.length === 0 ? (
          <div className="py-16 text-center text-slate-500 space-y-3">
            <Rocket className="w-8 h-8 mx-auto text-slate-300" />
            <div className="text-xs font-medium">No deployment runs recorded yet for this project.</div>
            <button
              onClick={() => onNavigate('execution', '/execution')}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold cursor-pointer shadow-xs"
            >
              Start First Deployment
            </button>
          </div>
        ) : (
          <div className="divide-y divide-slate-100 text-xs">
            {deployments.map((d) => (
              <div
                key={d.deployment_id}
                onClick={() => handleInspectDeployment(d)}
                className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-slate-50 transition cursor-pointer"
              >
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center font-bold shrink-0">
                    <Rocket className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-slate-900 font-mono">{d.deployment_id}</span>
                      <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${
                        d.status === 'SUCCESS'
                          ? 'text-emerald-700 bg-emerald-50 border-emerald-200'
                          : d.status === 'CANCELLED'
                          ? 'text-amber-700 bg-amber-50 border-amber-200'
                          : 'text-rose-700 bg-rose-50 border-rose-200'
                      }`}>
                        {d.status}
                      </span>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                        {d.mode || 'TEST_SANDBOX'}
                      </span>
                    </div>
                    <p className="text-slate-500 mt-0.5">
                      Target: AWS {d.target_region} • {d.resources_count || 0} resources • Approved by {d.approved_by || 'engineer'}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3 self-end sm:self-auto text-slate-400 font-medium">
                  <span>{d.execution_time_seconds ? `${d.execution_time_seconds}s` : 'Completed'}</span>
                  <span className="text-blue-600 font-semibold flex items-center gap-1 hover:underline">
                    <span>Inspect</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Deployment Inspection Modal */}
      {inspectModalOpen && selectedDep && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-3xl w-full border border-slate-200 shadow-xl overflow-hidden flex flex-col max-h-[85vh] animate-in fade-in">
            {/* Modal Header */}
            <div className="p-4 bg-slate-900 text-white flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Rocket className="w-4 h-4 text-blue-400" />
                <h3 className="text-sm font-bold font-mono">Deployment #{selectedDep.deployment_id}</h3>
                <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-emerald-400 font-mono">
                  {selectedDep.status}
                </span>
              </div>
              <button
                onClick={() => setInspectModalOpen(false)}
                className="text-slate-400 hover:text-white text-xs font-semibold cursor-pointer"
              >
                ✕ Close
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-5 overflow-y-auto space-y-5 text-xs">
              {inspectLoading ? (
                <div className="py-12 text-center text-slate-500">
                  <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-blue-500" />
                  <span>Loading deployment telemetry...</span>
                </div>
              ) : (
                <>
                  {/* Metadata */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
                      <div className="text-slate-400 text-[10px] font-semibold">PLAN ID</div>
                      <div className="font-mono text-slate-800 mt-0.5 truncate">{selectedDep.plan_id || 'N/A'}</div>
                    </div>
                    <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
                      <div className="text-slate-400 text-[10px] font-semibold">REGION</div>
                      <div className="font-mono text-slate-800 mt-0.5">{selectedDep.target_region}</div>
                    </div>
                    <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
                      <div className="text-slate-400 text-[10px] font-semibold">MODE</div>
                      <div className="font-mono text-slate-800 mt-0.5">{selectedDep.mode || 'TEST_SANDBOX'}</div>
                    </div>
                    <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
                      <div className="text-slate-400 text-[10px] font-semibold">DURATION</div>
                      <div className="font-mono text-slate-800 mt-0.5">{selectedDep.execution_time_seconds || '0.4'}s</div>
                    </div>
                  </div>

                  {/* Provisioned Resources */}
                  <div className="space-y-2">
                    <h4 className="font-bold text-slate-900 flex items-center gap-1.5">
                      <Layers className="w-4 h-4 text-blue-600" />
                      <span>Provisioned Cloud Resources ({depResources.length})</span>
                    </h4>
                    <div className="border border-slate-200 rounded-xl overflow-hidden">
                      <table className="w-full text-left text-xs">
                        <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
                          <tr>
                            <th className="py-2 px-3">Resource ID</th>
                            <th className="py-2 px-3">Type</th>
                            <th className="py-2 px-3">Status</th>
                            <th className="py-2 px-3">Verification</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100 font-mono text-[11px]">
                          {depResources.map((r, i) => (
                            <tr key={i} className="hover:bg-slate-50/70">
                              <td className="py-2 px-3 font-semibold text-slate-800">{r.resource_id}</td>
                              <td className="py-2 px-3 text-blue-700">{r.resource_type}</td>
                              <td className="py-2 px-3 text-emerald-700 font-bold">{r.status}</td>
                              <td className="py-2 px-3 text-slate-500">{r.verification_status}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>

                  {/* Execution Logs Terminal */}
                  <div className="space-y-2">
                    <h4 className="font-bold text-slate-900 flex items-center gap-1.5">
                      <Terminal className="w-4 h-4 text-emerald-600" />
                      <span>Execution Logs ({depLogs.length} Lines)</span>
                    </h4>
                    <div className="p-4 bg-slate-950 rounded-xl text-emerald-400 font-mono text-xs max-h-48 overflow-y-auto leading-relaxed space-y-0.5">
                      {depLogs.map((l, idx) => (
                        <div key={idx}>{l}</div>
                      ))}
                    </div>
                  </div>
                </>
              )}
            </div>

            {/* Modal Footer */}
            <div className="p-4 bg-slate-50 border-t border-slate-200 flex justify-end">
              <button
                onClick={() => setInspectModalOpen(false)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-900 text-white rounded-lg text-xs font-semibold cursor-pointer"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
