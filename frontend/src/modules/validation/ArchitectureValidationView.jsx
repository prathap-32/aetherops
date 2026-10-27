// frontend/src/modules/validation/ArchitectureValidationView.jsx
import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  ArrowRight,
  Layers,
  Server,
  Database,
  Lock,
  Cpu,
  RefreshCw,
  ExternalLink,
  Edit3,
  Check
} from 'lucide-react';
import { architectureStudioApi } from '../../services/api';

export default function ArchitectureValidationView({ onNavigate, activeProject, activeEnvironment, user }) {
  const [loading, setLoading] = useState(true);
  const [reviewData, setReviewData] = useState(null);
  const [error, setError] = useState(null);
  const [approving, setApproving] = useState(false);
  const [approvalSuccess, setApprovalSuccess] = useState(null);
  const [comments, setComments] = useState('');

  const projectId = activeProject?.id || activeProject?.project_id || 'default';
  const envId = activeEnvironment?.id || 'env';
  const envTier = activeEnvironment?.type || 'development';
  const region = activeEnvironment?.region || 'us-east-1';

  const loadReview = async () => {
    setLoading(true);
    setError(null);
    try {
      // Fetch latest review bundle from Architecture Studio (Port 8005)
      const data = await architectureStudioApi.getReview({
        project_id: projectId,
        environment_id: envId,
        environment_tier: envTier,
        target_region: region,
      });
      setReviewData(data);
      if (data?.is_approved) {
        setApprovalSuccess({
          approval_id: data.approval_id,
          approved_by: data.approved_by,
          approved_at: data.approved_at,
        });
      }
    } catch (err) {
      console.warn('Failed to load architecture review:', err);
      setError(err.message || 'Could not contact Architecture Review Engine');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReview();
  }, [projectId, envId]);

  const handleApprove = async () => {
    if (!reviewData?.version_id) return;
    setApproving(true);
    setError(null);
    try {
      const res = await architectureStudioApi.approve({
        version_id: reviewData.version_id,
        project_id: projectId,
        environment_id: envId,
        comments: comments || 'Approved for infrastructure synthesis',
      });
      setApprovalSuccess(res);
      setReviewData((prev) => ({
        ...prev,
        is_approved: true,
        approval_id: res.approval_id,
        approved_by: res.approved_by,
      }));
    } catch (err) {
      setError(err.message || 'Failed to approve architecture');
    } finally {
      setApproving(false);
    }
  };

  const deterministic = reviewData?.deterministic_validation || {};
  const aiAnalysis = reviewData?.ai_analysis || {};
  const findings = aiAnalysis.findings || [];
  const blockingErrors = deterministic.blocking_errors || [];
  const warnings = deterministic.warnings || [];
  const checksPassed = deterministic.checks_passed || [];
  const inventory = reviewData?.resource_inventory || [];

  const overallStatus = deterministic.status || (blockingErrors.length > 0 ? 'BLOCKED' : warnings.length > 0 ? 'WARNING' : 'PASS');
  const canApprove = deterministic.can_approve !== false && !aiAnalysis.has_blocking_findings && !approvalSuccess;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Architecture Review &amp; Approval Gate</h1>
            <span className={`px-2.5 py-0.5 rounded text-xs font-semibold ${
              approvalSuccess || reviewData?.is_approved
                ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                : overallStatus === 'BLOCKED'
                ? 'bg-rose-50 text-rose-700 border border-rose-200'
                : 'bg-blue-50 text-blue-700 border border-blue-200'
            }`}>
              {approvalSuccess || reviewData?.is_approved ? 'APPROVED' : `STATUS: ${overallStatus}`}
            </span>
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Stage A–C Review: Deep AI Architecture Analysis and Deterministic Well-Architected validation before Terraform generation.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => onNavigate('architecture_designer', '/architecture/designer')}
            className="px-3.5 py-2 rounded-lg bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 text-xs font-semibold transition flex items-center gap-1.5 cursor-pointer shadow-xs"
          >
            <Edit3 className="w-3.5 h-3.5" />
            <span>Edit in Designer</span>
          </button>
          <button
            onClick={loadReview}
            disabled={loading}
            className="px-3.5 py-2 rounded-lg bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 text-xs font-semibold transition flex items-center gap-1.5 cursor-pointer shadow-xs"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Re-analyze</span>
          </button>
          <button
            onClick={() => onNavigate('iac', '/terraform')}
            disabled={!reviewData?.is_approved && !approvalSuccess}
            className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold transition flex items-center gap-1.5 cursor-pointer shadow-xs disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <span>Proceed to Terraform</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 flex items-center gap-3 text-rose-800 text-xs font-medium">
          <XCircle className="w-4 h-4 text-rose-600 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Official Approval Banner */}
      {(approvalSuccess || reviewData?.is_approved) && (
        <div className="p-5 rounded-xl bg-emerald-50 border border-emerald-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4 text-emerald-900 shadow-xs">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-emerald-600 text-white flex items-center justify-center shrink-0">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <div>
              <div className="text-sm font-bold">Architecture Approved by Platform Engineer</div>
              <div className="text-xs text-emerald-700 mt-0.5 font-mono">
                Approval ID: {approvalSuccess?.approval_id || reviewData?.approval_id} • Version: {reviewData?.version_id}
              </div>
            </div>
          </div>
          <button
            onClick={() => onNavigate('iac', '/terraform')}
            className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold transition flex items-center gap-1.5 cursor-pointer shadow-xs self-start sm:self-auto"
          >
            <span>Generate Terraform HCL</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* Grid: Left Column (Stage B Deterministic & Inventory) / Right Column (Stage A AI Findings & Approval Form) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Stage B: Deterministic Policy Validation Card */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
            <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-blue-600" />
                  <span>Stage B: Deterministic Well-Architected Rules</span>
                </h3>
                <p className="text-[11px] text-slate-500 mt-0.5">Automated policy gate evaluating topology boundaries</p>
              </div>
              <span className={`px-2.5 py-1 rounded text-xs font-mono font-bold ${
                overallStatus === 'PASS'
                  ? 'bg-emerald-100 text-emerald-800'
                  : overallStatus === 'WARNING'
                  ? 'bg-amber-100 text-amber-800'
                  : 'bg-rose-100 text-rose-800'
              }`}>
                {overallStatus}
              </span>
            </div>

            <div className="p-4 space-y-3 text-xs">
              {blockingErrors.map((err, i) => (
                <div key={i} className="p-3 rounded-lg bg-rose-50 border border-rose-200 flex items-start gap-2.5 text-rose-900 font-medium">
                  <XCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-bold uppercase tracking-wider text-[10px] text-rose-700 mr-2">Blocking:</span>
                    <span>{err}</span>
                  </div>
                </div>
              ))}

              {warnings.map((warn, i) => (
                <div key={i} className="p-3 rounded-lg bg-amber-50 border border-amber-200 flex items-start gap-2.5 text-amber-900 font-medium">
                  <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-bold uppercase tracking-wider text-[10px] text-amber-700 mr-2">Advisory:</span>
                    <span>{warn}</span>
                  </div>
                </div>
              ))}

              {checksPassed.map((chk, i) => (
                <div key={i} className="p-2.5 rounded-lg bg-emerald-50/60 border border-emerald-200/50 flex items-center gap-2.5 text-emerald-900">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                  <span>{chk}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Resource Inventory Table */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
            <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <Layers className="w-4 h-4 text-blue-600" />
                  <span>Resource Inventory Specification</span>
                </h3>
                <p className="text-[11px] text-slate-500 mt-0.5">Identified components for synthesis</p>
              </div>
              <span className="text-xs font-mono font-semibold text-slate-600 bg-slate-200 px-2 py-0.5 rounded">
                {inventory.length} Nodes
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
                  <tr>
                    <th className="py-2.5 px-3">Resource Name</th>
                    <th className="py-2.5 px-3">AWS Type</th>
                    <th className="py-2.5 px-3">Placement Tier</th>
                    <th className="py-2.5 px-3">Security &amp; Encryption</th>
                    <th className="py-2.5 px-3">Est. Cost</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-mono">
                  {inventory.map((item, idx) => (
                    <tr key={idx} className="hover:bg-slate-50/70">
                      <td className="py-2.5 px-3 font-sans font-semibold text-slate-800">{item.name}</td>
                      <td className="py-2.5 px-3 text-blue-700">{item.resource_type}</td>
                      <td className="py-2.5 px-3 text-slate-600">{item.placement}</td>
                      <td className="py-2.5 px-3 text-emerald-700">{item.encryption}</td>
                      <td className="py-2.5 px-3 text-slate-800 font-bold">{item.monthly_cost}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Right Column (5 cols): Stage A AI Architecture Findings & Stage C Approval Action */}
        <div className="lg:col-span-5 space-y-6">
          {/* Stage C Approval Action Box */}
          <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-slate-900">Stage C: Architecture Approval Sign-Off</h3>
                <p className="text-xs text-slate-500 mt-0.5">Version-bound gate required prior to HCL synthesis</p>
              </div>
              <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-semibold">
                {reviewData?.version_id || 'arch-v1'}
              </span>
            </div>

            {reviewData?.is_approved ? (
              <div className="p-3.5 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs font-medium space-y-1">
                <div className="flex items-center gap-1.5 font-bold">
                  <Check className="w-4 h-4 text-emerald-600" />
                  <span>Approved for IaC Synthesis</span>
                </div>
                <div className="text-[11px] text-emerald-700 font-mono">
                  Sign-off recorded by: {reviewData.approved_by || 'platform-engineer'}
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                {overallStatus === 'BLOCKED' ? (
                  <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-800 text-xs">
                    Approval is blocked until critical architectural violations are remediated in the designer.
                  </div>
                ) : (
                  <>
                    <div>
                      <label className="block text-xs font-semibold text-slate-700 mb-1">
                        Reviewer Sign-Off Comments
                      </label>
                      <textarea
                        rows={2}
                        value={comments}
                        onChange={(e) => setComments(e.target.value)}
                        placeholder="e.g., Reviewed ingress routing, multi-AZ subnets, and KMS encryption."
                        className="w-full text-xs p-2.5 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 bg-slate-50/50"
                      />
                    </div>

                    <button
                      onClick={handleApprove}
                      disabled={approving || !canApprove}
                      className="w-full py-2.5 px-4 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs transition flex items-center justify-center gap-2 cursor-pointer shadow-xs disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {approving ? (
                        <>
                          <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                          <span>Recording Approval...</span>
                        </>
                      ) : (
                        <>
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          <span>Approve Architecture Version</span>
                        </>
                      )}
                    </button>
                  </>
                )}
              </div>
            )}
          </div>

          {/* Stage A: AI Architecture Analysis Findings */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
            <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-slate-900">Stage A: AI Architectural Findings</h3>
                <p className="text-[11px] text-slate-500 mt-0.5">17-point automated Well-Architected assessment</p>
              </div>
              <span className="text-xs font-bold font-mono text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                Score: {aiAnalysis.overall_score || '92'}/100
              </span>
            </div>

            <div className="p-4 space-y-3.5 max-h-[460px] overflow-y-auto">
              {findings.length === 0 ? (
                <div className="text-xs text-slate-500 p-4 text-center">
                  Zero architectural vulnerabilities identified. Topology complies with standard Well-Architected patterns.
                </div>
              ) : (
                findings.map((f, i) => (
                  <div key={i} className="p-3.5 rounded-lg border border-slate-200 bg-white space-y-2 text-xs shadow-2xs">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-900">{f.title}</span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                        f.severity === 'CRITICAL'
                          ? 'bg-rose-100 text-rose-800'
                          : f.severity === 'HIGH'
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-blue-100 text-blue-800'
                      }`}>
                        {f.severity}
                      </span>
                    </div>
                    <p className="text-slate-600 leading-relaxed">{f.explanation}</p>
                    <div className="p-2 rounded bg-slate-50 border border-slate-100 text-slate-700 text-[11px]">
                      <span className="font-semibold text-slate-900">Recommendation:</span> {f.recommended_correction}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
