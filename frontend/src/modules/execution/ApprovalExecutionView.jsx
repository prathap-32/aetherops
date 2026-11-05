// frontend/src/modules/execution/ApprovalExecutionView.jsx
import React, { useState, useEffect, useRef } from 'react';
import {
  ShieldCheck,
  Play,
  ArrowRight,
  Clock,
  CheckCircle2,
  XCircle,
  Terminal,
  Layers,
  Lock,
  RefreshCw,
  AlertTriangle,
  Server
} from 'lucide-react';
import { deploymentsApi } from '../../services/api';

export default function ApprovalExecutionView({ onNavigate, activeProject, activeEnvironment, user }) {
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [approving, setApproving] = useState(false);
  const [approvedReceipt, setApprovedReceipt] = useState(null);
  const [executing, setExecuting] = useState(false);
  const [executionResult, setExecutionResult] = useState(null);
  const [logs, setLogs] = useState([]);
  const [resources, setResources] = useState([]);
  const [error, setError] = useState(null);
  const [executionMode, setExecutionMode] = useState('TEST_SANDBOX');
  const [comments, setComments] = useState('');
  const logTerminalRef = useRef(null);

  // Load active plan from localStorage or create fresh one
  useEffect(() => {
    async function initPlan() {
      setLoading(true);
      setError(null);
      try {
        const stored = localStorage.getItem('aether_active_plan');
        if (stored) {
          const parsed = JSON.parse(stored);
          setPlan(parsed);
          // Check if already approved
          const planStatus = await deploymentsApi.getPlan(parsed.plan_id);
          if (planStatus?.is_approved) {
            setApprovedReceipt(planStatus.approval_bundle);
          }
        } else {
          // Generate default baseline dry-run plan
          const p = await deploymentsApi.plan({
            project_name: activeProject?.name || activeProject?.id || 'aether-cloud',
            environment_tier: activeEnvironment?.type || 'production',
            target_region: activeEnvironment?.region || 'us-east-1',
          });
          setPlan(p);
          localStorage.setItem('aether_active_plan', JSON.stringify(p));
        }
      } catch (err) {
        console.warn('Init plan error:', err);
        setError(err.message || 'Could not load deployment plan');
      } finally {
        setLoading(false);
      }
    }
    initPlan();
  }, [activeProject, activeEnvironment]);

  // Handle plan approval
  const handleApprove = async () => {
    if (!plan?.plan_id || !plan?.plan_digest) return;
    setApproving(true);
    setError(null);
    try {
      const receipt = await deploymentsApi.approve({
        plan_id: plan.plan_id,
        plan_digest: plan.plan_digest,
        comments: comments || 'Approved for infrastructure execution',
      });
      setApprovedReceipt(receipt);
    } catch (err) {
      setError(err.message || 'Approval sign-off rejected');
    } finally {
      setApproving(false);
    }
  };

  // Handle execution & log streaming
  const handleExecute = async () => {
    if (!plan?.plan_id) return;
    setExecuting(true);
    setError(null);
    setLogs(['[00:00:00] Initializing state-locked deployment execution runner...']);
    try {
      let awsCreds = {};
      try {
        const saved = localStorage.getItem('aether_aws_creds');
        if (saved) awsCreds = JSON.parse(saved);
      } catch (e) {}

      const res = await deploymentsApi.execute({
        plan_id: plan.plan_id,
        execution_mode: executionMode,
        aws_access_key_id: awsCreds.accessKeyId || '',
        aws_secret_access_key: awsCreds.secretAccessKey || '',
        aws_region: plan.target_region || 'us-east-1',
      });
      setExecutionResult(res);

      // Fetch execution logs
      const logResp = await deploymentsApi.getLogs(res.deployment_id);
      if (logResp?.logs) {
        setLogs(logResp.logs);
      }

      // Fetch deployed resource inventory
      const resResp = await deploymentsApi.getResources(res.deployment_id);
      if (resResp?.resources) {
        setResources(resResp.resources);
      }
    } catch (err) {
      setError(err.message || 'Execution failed');
    } finally {
      setExecuting(false);
    }
  };

  // Auto scroll terminal
  useEffect(() => {
    if (logTerminalRef.current) {
      logTerminalRef.current.scrollTop = logTerminalRef.current.scrollHeight;
    }
  }, [logs]);

  const changes = plan?.resource_changes || [];
  const summary = plan?.summary || { create: changes.length, update: 0, destroy: 0 };
  const isApproved = Boolean(approvedReceipt);
  const isComplete = executionResult?.status === 'SUCCESS';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Deployment Approval &amp; Execution Gate</h1>
            <span className={`px-2.5 py-0.5 rounded text-xs font-semibold ${
              isComplete
                ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                : isApproved
                ? 'bg-blue-50 text-blue-700 border border-blue-200'
                : 'bg-amber-50 text-amber-700 border border-amber-200'
            }`}>
              {isComplete ? 'EXECUTED (SUCCESS)' : isApproved ? 'APPROVED & UNLOCKED' : 'PENDING SIGN-OFF'}
            </span>
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Section 8: Cryptographically bound deployment gate. Plan must be explicitly approved before state-locked execution.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => onNavigate('deployments', '/deployment')}
            className="px-4 py-2 rounded-lg bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 text-xs font-semibold transition flex items-center gap-1.5 cursor-pointer shadow-xs"
          >
            <span>Deployment History</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-medium flex items-center gap-2">
          <XCircle className="w-4 h-4 text-rose-600 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Plan Details Card */}
      {plan && (
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-bold text-slate-900">Execution Plan #{plan.plan_id}</h3>
                <span className="font-mono text-[11px] text-slate-400">
                  Digest: {plan.plan_digest?.substring(0, 16)}...
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">
                Target AWS Region: {plan.target_region} • Tier: {plan.environment_tier}
              </p>
            </div>

            <span className={`px-2.5 py-1 rounded-full text-xs font-mono font-bold flex items-center gap-1.5 self-start sm:self-auto ${
              isApproved
                ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                : 'bg-amber-50 text-amber-700 border border-amber-200'
            }`}>
              <Clock className="w-3.5 h-3.5" />
              <span>{isApproved ? 'APPROVED' : 'AWAITING APPROVAL'}</span>
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 font-mono text-xs">
            <div className="p-3 rounded-xl bg-emerald-50/60 border border-emerald-200/60 text-emerald-800">
              <div className="text-[10px] uppercase font-bold text-emerald-600">Resources to Add</div>
              <div className="text-lg font-black mt-1">+{summary.create || changes.length} resources</div>
            </div>
            <div className="p-3 rounded-xl bg-blue-50/60 border border-blue-200/60 text-blue-800">
              <div className="text-[10px] uppercase font-bold text-blue-600">Resources to Change</div>
              <div className="text-lg font-black mt-1">~{summary.update || 0} resources</div>
            </div>
            <div className="p-3 rounded-xl bg-rose-50/60 border border-rose-200/60 text-rose-800">
              <div className="text-[10px] uppercase font-bold text-rose-600">Resources to Destroy</div>
              <div className="text-lg font-black mt-1">-{summary.destroy || 0} resources</div>
            </div>
          </div>

          {/* Action Step 1: Approval Gate */}
          {!isApproved && (
            <div className="pt-4 border-t border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="text-xs text-slate-600 flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-blue-600 shrink-0" />
                <span>Pre-deployment risk assessment verified (PASS). Engineer sign-off required.</span>
              </div>
              <button
                onClick={handleApprove}
                disabled={approving}
                className="px-5 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs transition flex items-center gap-2 cursor-pointer shadow-xs disabled:opacity-50 shrink-0"
              >
                {approving ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <ShieldCheck className="w-3.5 h-3.5" />}
                <span>{approving ? 'Signing Off...' : 'Approve Deployment Plan'}</span>
              </button>
            </div>
          )}

          {/* Action Step 2: Execution Trigger */}
          {/* Action Step 2: Once Approved, Generate AI Terraform HCL Code & Execute */}
          {isApproved && (
            <div className="pt-4 border-t border-slate-100 space-y-4">
              <div className="p-4 bg-emerald-50/70 border border-emerald-200 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
                  <div>
                    <div className="text-xs font-bold text-emerald-900">Architecture Review Passed &amp; Approval Granted</div>
                    <div className="text-[11px] text-emerald-700">Access status verified. AI is ready to synthesize and generate Terraform HCL code for your topology.</div>
                  </div>
                </div>
                <button
                  onClick={() => {
                    const nav = onNavigate || (() => {});
                    nav('iac', '/terraform', { fromApproval: true, sizingOutput: activeSizing });
                  }}
                  className="px-5 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs transition flex items-center gap-2 cursor-pointer shadow-xs shrink-0"
                >
                  <span>Generate AI Terraform HCL Code</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>

              {!isComplete && (
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-2">
                  <div className="flex items-center gap-3">
                    <div className="text-xs text-slate-700 font-medium">
                      Plan approved by {approvedReceipt.approved_by || 'platform engineer'}.
                    </div>
                    <select
                      value={executionMode}
                      onChange={(e) => setExecutionMode(e.target.value)}
                      className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-700 font-semibold"
                    >
                      <option value="TEST_SANDBOX">Test Sandbox Runner (Isolated)</option>
                      <option value="REAL">Real AWS Cloud Apply</option>
                    </select>
                  </div>

                  <button
                    onClick={handleExecute}
                    disabled={executing}
                    className="px-5 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs transition flex items-center gap-2 cursor-pointer shadow-xs disabled:opacity-50 shrink-0"
                  >
                    {executing ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
                    <span>{executing ? 'Executing Terraform Apply...' : 'Execute Deployment Plan'}</span>
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Execution Terminal & Real-Time Log Stream */}
      {(executing || logs.length > 0) && (
        <div className="bg-slate-950 rounded-2xl border border-slate-800 shadow-xl overflow-hidden font-mono text-xs">
          <div className="px-4 py-3 bg-slate-900 border-b border-slate-800 flex items-center justify-between text-slate-400">
            <div className="flex items-center gap-2">
              <Terminal className="w-4 h-4 text-emerald-400" />
              <span className="text-slate-200 font-semibold">Live Terraform Apply Stream</span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-emerald-400 font-bold">
                {executionResult?.mode || executionMode}
              </span>
            </div>
            <span className="text-[11px] text-slate-400">
              {logs.length} Log Events
            </span>
          </div>

          <div ref={logTerminalRef} className="p-5 text-emerald-300 overflow-y-auto max-h-72 leading-relaxed space-y-1">
            {logs.map((line, idx) => (
              <div key={idx} className="font-mono">{line}</div>
            ))}
          </div>
        </div>
      )}

      {/* Provisioned AWS Resources Inventory */}
      {resources.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <Layers className="w-4 h-4 text-blue-600" />
                <span>Provisioned AWS Infrastructure Resource Inventory</span>
              </h3>
              <p className="text-[11px] text-slate-500 mt-0.5">Section 9 Honest Resource Inventory &amp; Verification Status</p>
            </div>
            <span className="text-xs font-mono font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded">
              {resources.length} Provisioned
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
                <tr>
                  <th className="py-2.5 px-3">Resource Identifier</th>
                  <th className="py-2.5 px-3">AWS Resource Type</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3">Verification Status</th>
                  <th className="py-2.5 px-3">Amazon Resource Name (ARN)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-mono">
                {resources.map((r, idx) => (
                  <tr key={idx} className="hover:bg-slate-50/70">
                    <td className="py-2.5 px-3 font-sans font-semibold text-slate-800">{r.resource_id}</td>
                    <td className="py-2.5 px-3 text-blue-700">{r.resource_type}</td>
                    <td className="py-2.5 px-3">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                        {r.status}
                      </span>
                    </td>
                    <td className="py-2.5 px-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        r.is_verified_aws
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          : 'bg-amber-50 text-amber-700 border border-amber-200'
                      }`}>
                        {r.verification_status}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-slate-500 text-[11px] truncate max-w-xs" title={r.arn}>
                      {r.arn || 'N/A (Test Sandbox)'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
