// frontend/src/modules/risk/RiskEngineView.jsx
import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  DollarSign,
  CheckCircle2,
  XCircle,
  ArrowRight,
  RefreshCw,
  Layers,
  FileCode,
  Activity,
  Clock,
  Lock,
  Server,
  ChevronDown,
  ChevronUp,
  Info,
  Check,
  X,
  Play
} from 'lucide-react';
import { dryRunApi, architectureStudioApi, approvalApi, finopsApi } from '../../services/api';

const ANALYSIS_STAGES = [
  'Architecture Validation',
  'Cost Analysis',
  'Security Assessment',
  'Reliability Assessment',
  'Performance Assessment',
  'Operations Assessment',
  'Sustainability Assessment',
  'Risk Calculation',
  'Final Assessment',
];

export default function RiskEngineView({ onNavigate, activeProject, activeEnvironment, navState, user }) {
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisStageIndex, setAnalysisStageIndex] = useState(0);
  const [versions, setVersions] = useState([]);
  const [selectedVersionId, setSelectedVersionId] = useState('');
  const [planData, setPlanData] = useState(null);
  const [error, setError] = useState(null);
  
  // Filtering & UI state
  const [selectedSeverityFilter, setSelectedSeverityFilter] = useState('ALL');
  const [selectedCategoryFilter, setSelectedCategoryFilter] = useState('ALL');
  const [expandedFindings, setExpandedFindings] = useState({});
  const [dismissedFindings, setDismissedFindings] = useState(new Set());
  const [appliedRecommendations, setAppliedRecommendations] = useState(new Set());
  
  // Approval state
  const [approving, setApproving] = useState(false);
  const [rejecting, setRejecting] = useState(false);
  const [approvedReceipt, setApprovedReceipt] = useState(null);
  const [rejectedStatus, setRejectedStatus] = useState(false);
  const [comments, setComments] = useState('');
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  
  // Architecture change tracking
  const [isOutdated, setIsOutdated] = useState(false);
  const [lastAnalyzedVersionId, setLastAnalyzedVersionId] = useState(null);

  const hasProject = Boolean(activeProject?.id || activeProject?.project_id || activeProject?.name);
  const hasEnvironment = Boolean(activeEnvironment?.id || activeEnvironment?.env_id || activeEnvironment?.type || activeEnvironment?.name);
  const hasArchitecture = versions.length > 0 && Boolean(selectedVersionId);

  const projectName = activeProject?.name || activeProject?.id || '';
  const envTier = activeEnvironment?.type || activeEnvironment?.env_type || '';
  const region = activeEnvironment?.region || activeEnvironment?.aws_region || 'us-east-1';

  // 1. Fetch available architecture versions on mount or project change
  useEffect(() => {
    async function loadVersions() {
      if (!hasProject || !hasEnvironment) {
        setVersions([]);
        setSelectedVersionId('');
        return;
      }
      try {
        const res = await architectureStudioApi.listVersions(activeProject?.id || activeProject?.project_id, activeEnvironment?.id || activeEnvironment?.env_id);
        const list = res?.versions || (Array.isArray(res) ? res : []);
        setVersions(list);
        if (list.length > 0) {
          const latest = list[list.length - 1];
          setSelectedVersionId(latest.version_id);
        }
      } catch (err) {
        console.warn('Failed to load architecture versions:', err);
      }
    }
    loadVersions();
  }, [activeProject, activeEnvironment]);

  // Track if architecture version changed after analysis
  useEffect(() => {
    if (lastAnalyzedVersionId && selectedVersionId && lastAnalyzedVersionId !== selectedVersionId) {
      setIsOutdated(true);
    }
  }, [selectedVersionId, lastAnalyzedVersionId]);

  // 2. Run Pre-Deployment Analysis with stage animation
  const runAnalysis = async () => {
    setAnalyzing(true);
    setLoading(true);
    setError(null);
    setAnalysisStageIndex(0);

    // Simulate progressive stage advancement for visual user feedback
    const stageInterval = setInterval(() => {
      setAnalysisStageIndex((prev) => {
        if (prev < ANALYSIS_STAGES.length - 1) {
          return prev + 1;
        }
        return prev;
      });
    }, 250);

    try {
      let archVersionId = selectedVersionId || null;
      if (!archVersionId && versions.length > 0) {
        archVersionId = versions[versions.length - 1].version_id;
      }

      const planResp = await dryRunApi.analyze({
        project_name: projectName,
        environment_tier: envTier,
        target_region: region,
        architecture_version_id: archVersionId,
        iac_files: navState?.iacData?.files || null,
        terraform_version_id: navState?.iacData?.terraform_version_id || null,
      });

      clearInterval(stageInterval);
      setAnalysisStageIndex(ANALYSIS_STAGES.length - 1);
      
      // Brief pause to show completion of final stage
      await new Promise((r) => setTimeout(r, 400));

      setPlanData(planResp);
      setLastAnalyzedVersionId(archVersionId);
      setIsOutdated(false);
      setApprovedReceipt(null);
      setRejectedStatus(false);

      // Cache active plan for downstream modules
      try {
        localStorage.setItem('aether_active_plan', JSON.stringify(planResp));
      } catch (e) {}
    } catch (err) {
      clearInterval(stageInterval);
      setError(err.message || 'Pre-deployment analysis execution failed');
    } finally {
      setAnalyzing(false);
      setLoading(false);
    }
  };

  // Run analysis automatically on initial load when versions are available or project/env changes
  useEffect(() => {
    if (selectedVersionId) {
      runAnalysis();
    }
  }, [selectedVersionId]);

  // Handle Recommendation Apply
  const handleApplyRecommendation = async (findingId) => {
    try {
      // Simulate or call backend remediation
      setAppliedRecommendations((prev) => new Set([...prev, findingId]));
      setIsOutdated(true); // Plan updated, re-analysis required
    } catch (err) {
      setError(err.message || 'Failed to apply recommendation');
    }
  };

  // Handle Recommendation Dismiss
  const handleDismissRecommendation = (findingId) => {
    setDismissedFindings((prev) => new Set([...prev, findingId]));
  };

  // Handle Plan Approval
  const handleApprovePlan = async () => {
    if (!planData?.plan_id || !planData?.plan_digest) return;
    setApproving(true);
    setError(null);
    try {
      const receipt = await approvalApi.approve({
        plan_id: planData.plan_id,
        plan_digest: planData.plan_digest,
        comments: comments || 'Approved for infrastructure execution',
      });
      setApprovedReceipt(receipt);
      setShowConfirmModal(false);
    } catch (err) {
      setError(err.message || 'Approval sign-off rejected');
    } finally {
      setApproving(false);
    }
  };

  // Handle Plan Rejection
  const handleRejectPlan = () => {
    setRejectedStatus(true);
    setApprovedReceipt(null);
    setShowConfirmModal(false);
  };

  const risk = planData?.risk_assessment || {};
  const status = risk.status || 'PASS';
  const rawFindings = risk.findings || [];
  const findings = rawFindings.filter((f) => !dismissedFindings.has(f.id));
  const scores = risk.scores || {};
  const changes = planData?.resource_changes || [];
  const summary = planData?.summary || { create: changes.length, update: 0, destroy: 0 };

  // Filter findings by severity and category
  const filteredFindings = findings.filter((f) => {
    if (selectedSeverityFilter !== 'ALL' && f.severity?.toUpperCase() !== selectedSeverityFilter) {
      return false;
    }
    if (selectedCategoryFilter !== 'ALL' && f.category?.toUpperCase() !== selectedCategoryFilter.toUpperCase()) {
      return false;
    }
    return true;
  });

  const criticalCount = findings.filter((f) => f.severity === 'CRITICAL').length;
  const highCount = findings.filter((f) => f.severity === 'HIGH').length;
  const mediumCount = findings.filter((f) => f.severity === 'MEDIUM').length;
  const lowCount = findings.filter((f) => f.severity === 'LOW').length;

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {!hasProject ? (
        <>
          <div className="flex items-center justify-between pb-4 border-b border-slate-200">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Pre-Deployment Dry Run &amp; Risk Engine</h1>
          </div>
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-12 text-center max-w-xl mx-auto space-y-4 my-12">
            <div className="w-16 h-16 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center mx-auto border border-amber-200 shadow-sm">
              <ShieldAlert className="w-8 h-8" />
            </div>
            <h3 className="text-base font-bold text-slate-900">Select a project to begin pre-deployment analysis.</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Pre-deployment risk assessment, cost projection, Well-Architected validation, and approval gates require an active project context. No default project or template data is loaded.
            </p>
            <button
              onClick={() => onNavigate && onNavigate('projects', '/projects')}
              className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold transition shadow-md shadow-blue-500/20 inline-flex items-center gap-2 cursor-pointer"
            >
              <span>Select or Create Project</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </>
      ) : !hasEnvironment ? (
        <>
          <div className="flex items-center justify-between pb-4 border-b border-slate-200">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Pre-Deployment Dry Run &amp; Risk Engine</h1>
          </div>
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-12 text-center max-w-xl mx-auto space-y-4 my-12">
            <div className="w-16 h-16 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center mx-auto border border-blue-200 shadow-sm">
              <Layers className="w-8 h-8" />
            </div>
            <h3 className="text-base font-bold text-slate-900">Select an environment for project "{activeProject?.name || activeProject?.id}".</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Pre-deployment analysis requires an environment (e.g. production, staging, development) to evaluate target region and tier compliance rules.
            </p>
            <button
              onClick={() => onNavigate && onNavigate('environments', '/environments', { projectId: activeProject?.id || activeProject?.project_id })}
              className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold transition shadow-md shadow-blue-500/20 inline-flex items-center gap-2 cursor-pointer"
            >
              <span>Select Environment</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </>
      ) : !hasArchitecture ? (
        <>
          <div className="flex items-center justify-between pb-4 border-b border-slate-200">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Pre-Deployment Dry Run &amp; Risk Engine</h1>
          </div>
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-12 text-center max-w-xl mx-auto space-y-4 my-12">
            <div className="w-16 h-16 rounded-2xl bg-purple-50 text-purple-600 flex items-center justify-center mx-auto border border-purple-200 shadow-sm">
              <FileCode className="w-8 h-8" />
            </div>
            <h3 className="text-base font-bold text-slate-900">No architecture version found for {activeProject?.name || 'Project'} ({activeEnvironment?.name || activeEnvironment?.type || 'Environment'}).</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Generate or select an architecture topology and IaC configuration in the Architecture Designer before running pre-deployment risk analysis.
            </p>
            <button
              onClick={() => onNavigate && onNavigate('designer', '/architecture-designer')}
              className="px-5 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-700 text-white text-xs font-bold transition shadow-md shadow-purple-500/20 inline-flex items-center gap-2 cursor-pointer"
            >
              <span>Open Architecture Designer</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </>
      ) : (
        <>
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Pre-Deployment Dry Run &amp; Risk Engine</h1>
            <span className={`px-2.5 py-0.5 rounded text-xs font-semibold ${
              status === 'PASS'
                ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                : status === 'WARNING'
                ? 'bg-amber-50 text-amber-700 border border-amber-200'
                : 'bg-rose-50 text-rose-700 border border-rose-200'
            }`}>
              {status}
            </span>
            {isOutdated && (
              <span className="px-2.5 py-0.5 rounded text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-300 flex items-center gap-1">
                <AlertTriangle className="w-3 h-3" /> Re-Analysis Required
              </span>
            )}
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Project: <strong className="text-slate-700">{projectName}</strong> | Environment: <strong className="text-slate-700">{envTier}</strong> ({region})
          </p>
        </div>

        <div className="flex items-center gap-2">
          {versions.length > 0 && (
            <div className="flex items-center gap-1.5 bg-white border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs">
              <span className="text-slate-400 font-medium">Version:</span>
              <select
                value={selectedVersionId}
                onChange={(e) => setSelectedVersionId(e.target.value)}
                className="bg-transparent font-semibold text-slate-800 focus:outline-none cursor-pointer"
              >
                {versions.map((v) => (
                  <option key={v.version_id} value={v.version_id}>
                    {v.version_id} ({v.status || 'DRAFT'})
                  </option>
                ))}
              </select>
            </div>
          )}

          <button
            onClick={() => onNavigate('designer', '/architecture-designer')}
            className="px-3.5 py-2 rounded-lg bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 text-xs font-semibold transition flex items-center gap-1.5 cursor-pointer shadow-xs"
          >
            <Layers className="w-3.5 h-3.5 text-blue-600" />
            <span>View Architecture</span>
          </button>

          <button
            onClick={runAnalysis}
            disabled={analyzing}
            className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold transition flex items-center gap-1.5 cursor-pointer shadow-xs disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${analyzing ? 'animate-spin' : ''}`} />
            <span>{analyzing ? 'Running Analysis...' : 'Start Analysis'}</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-medium flex items-center gap-2">
          <XCircle className="w-4 h-4 text-rose-600 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Section 2 — Analysis Progress Experience (Visible while analyzing) */}
      {analyzing && (
        <div className="bg-white rounded-xl border border-blue-200 p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <Activity className="w-4 h-4 text-blue-600 animate-pulse" />
              <span>Executing Pre-Deployment Analysis Pipeline</span>
            </h3>
            <span className="text-xs font-mono font-semibold text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
              Stage {analysisStageIndex + 1} of {ANALYSIS_STAGES.length}
            </span>
          </div>

          <div className="space-y-2">
            <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
              <div
                className="bg-blue-600 h-2 transition-all duration-300 rounded-full"
                style={{ width: `${((analysisStageIndex + 1) / ANALYSIS_STAGES.length) * 100}%` }}
              />
            </div>
            <div className="flex justify-between text-[11px] font-medium text-slate-500">
              <span className="text-blue-700 font-bold">{ANALYSIS_STAGES[analysisStageIndex]}</span>
              <span>{Math.round(((analysisStageIndex + 1) / ANALYSIS_STAGES.length) * 100)}% Complete</span>
            </div>
          </div>

          <div className="grid grid-cols-3 sm:grid-cols-5 gap-2 pt-2">
            {ANALYSIS_STAGES.map((stageName, idx) => {
              const isCompleted = idx < analysisStageIndex;
              const isCurrent = idx === analysisStageIndex;
              return (
                <div
                  key={idx}
                  className={`p-2 rounded-lg border text-[11px] flex items-center gap-1.5 transition ${
                    isCompleted
                      ? 'bg-emerald-50/50 border-emerald-200 text-emerald-800'
                      : isCurrent
                      ? 'bg-blue-50 border-blue-300 text-blue-900 font-semibold shadow-2xs'
                      : 'bg-slate-50 border-slate-200 text-slate-400'
                  }`}
                >
                  {isCompleted ? (
                    <Check className="w-3 h-3 text-emerald-600 shrink-0" />
                  ) : isCurrent ? (
                    <RefreshCw className="w-3 h-3 text-blue-600 animate-spin shrink-0" />
                  ) : (
                    <div className="w-3 h-3 rounded-full border border-slate-300 shrink-0" />
                  )}
                  <span className="truncate">{stageName}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Section 1 — Architecture Context Card */}
      {planData && (
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 text-xs">
          <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs">
            <div className="text-slate-400 font-medium text-[11px]">Selected Architecture</div>
            <div className="text-slate-900 font-bold mt-1 truncate">{planData.plan_id}</div>
          </div>
          <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs">
            <div className="text-slate-400 font-medium text-[11px]">Cryptographic Plan Digest</div>
            <div className="text-slate-900 font-bold font-mono mt-1 truncate" title={planData.plan_digest}>
              {planData.plan_digest?.substring(0, 16)}...
            </div>
          </div>
          <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs">
            <div className="text-slate-400 font-medium text-[11px]">Cloud Region &amp; Tier</div>
            <div className="text-slate-900 font-bold mt-1">
              AWS {planData.target_region} ({planData.environment_tier})
            </div>
          </div>
          <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs">
            <div className="text-slate-400 font-medium text-[11px]">Planned Mutations</div>
            <div className="flex items-center gap-2 mt-1 font-mono font-bold">
              <span className="text-emerald-600">+{summary.create || changes.length}</span>
              <span className="text-blue-600">~{summary.update || 0}</span>
              <span className="text-rose-600">-{summary.destroy || 0}</span>
            </div>
          </div>
        </div>
      )}

      {/* Section 3 — Overall Risk Summary Card */}
      {planData && (
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div>
              <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-blue-600" />
                <span>Overall Risk Assessment Summary</span>
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">Automated evaluation across infrastructure compliance and resilience rules</p>
            </div>
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 rounded text-xs font-mono font-bold bg-slate-100 text-slate-800 border border-slate-200">
                {risk.evaluated_rules_count || 18} Rules Evaluated
              </span>
              <span className={`px-2.5 py-0.5 rounded text-xs font-bold ${
                status === 'PASS' ? 'bg-emerald-100 text-emerald-800' : status === 'WARNING' ? 'bg-amber-100 text-amber-800' : 'bg-rose-100 text-rose-800'
              }`}>
                {status}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-6 gap-3 text-center">
            <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
              <div className="text-[11px] text-slate-500 font-medium">Total Findings</div>
              <div className="text-lg font-bold text-slate-900 mt-1">{findings.length}</div>
            </div>
            <div className="p-3 rounded-lg bg-rose-50/60 border border-rose-200">
              <div className="text-[11px] text-rose-700 font-medium">Critical Findings</div>
              <div className="text-lg font-bold text-rose-700 mt-1">{criticalCount}</div>
            </div>
            <div className="p-3 rounded-lg bg-amber-50/60 border border-amber-200">
              <div className="text-[11px] text-amber-700 font-medium">High / Warnings</div>
              <div className="text-lg font-bold text-amber-700 mt-1">{highCount}</div>
            </div>
            <div className="p-3 rounded-lg bg-blue-50/60 border border-blue-200">
              <div className="text-[11px] text-blue-700 font-medium">Medium Issues</div>
              <div className="text-lg font-bold text-blue-700 mt-1">{mediumCount}</div>
            </div>
            <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
              <div className="text-[11px] text-slate-600 font-medium">Low Priority</div>
              <div className="text-lg font-bold text-slate-700 mt-1">{lowCount}</div>
            </div>
            <div className="p-3 rounded-lg bg-emerald-50/60 border border-emerald-200">
              <div className="text-[11px] text-emerald-700 font-medium">Passed Checks</div>
              <div className="text-lg font-bold text-emerald-700 mt-1">100%</div>
            </div>
          </div>
        </div>
      )}

      {/* Section 4 — Six Risk Category Cards */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <Layers className="w-4 h-4 text-blue-600" />
            <span>Six Risk &amp; Well-Architected Pillars</span>
          </h3>
          <span className="text-xs text-slate-500">Click any pillar to filter findings</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {[
            {
              id: 'SECURITY',
              name: '1. Security',
              score: scores.security_risk || '100/100 (OPTIMAL)',
              findings: findings.filter(f => f.category?.toUpperCase() === 'SECURITY'),
            },
            {
              id: 'SPOF',
              name: '2. Reliability & SPOF',
              score: scores.reliability_spof || '100/100 (OPTIMAL)',
              findings: findings.filter(f => f.category?.toUpperCase() === 'SPOF' || f.category?.toUpperCase() === 'RELIABILITY'),
            },
            {
              id: 'FINOPS',
              name: '3. Cost / FinOps',
              score: scores.cost_efficiency || '100/100 (OPTIMAL)',
              findings: findings.filter(f => f.category?.toUpperCase() === 'FINOPS'),
            },
            {
              id: 'PERFORMANCE',
              name: '4. Performance',
              score: scores.performance_efficiency || '100/100 (OPTIMAL)',
              findings: findings.filter(f => f.category?.toUpperCase() === 'PERFORMANCE'),
            },
            {
              id: 'OPERATIONS',
              name: '5. Operations',
              score: scores.operational_excellence || '100/100 (OPTIMAL)',
              findings: findings.filter(f => f.category?.toUpperCase() === 'OPERATIONS'),
            },
            {
              id: 'SUSTAINABILITY',
              name: '6. Sustainability',
              score: scores.sustainability_impact || '100/100 (OPTIMAL)',
              findings: findings.filter(f => f.category?.toUpperCase() === 'SUSTAINABILITY'),
            },
          ].map((cat) => {
            const catFindingsCount = cat.findings.length;
            const isSelected = selectedCategoryFilter === cat.id;
            const catStatus = cat.findings.some(f => f.severity === 'CRITICAL') ? 'CRITICAL' : cat.findings.some(f => f.severity === 'HIGH' || f.severity === 'MEDIUM') ? 'WARNING' : 'PASS';
            const dynamicDesc = catFindingsCount > 0 
              ? cat.findings.map(f => f.title).join('; ') 
              : `All automated checks passed for ${cat.name}. No configuration findings detected.`;
            return (
              <div
                key={cat.id}
                onClick={() => setSelectedCategoryFilter(isSelected ? 'ALL' : cat.id)}
                className={`p-4 rounded-xl border transition cursor-pointer space-y-2 ${
                  isSelected
                    ? 'bg-blue-50/80 border-blue-400 ring-1 ring-blue-400 shadow-xs'
                    : 'bg-white hover:bg-slate-50/80 border-slate-200 shadow-2xs'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-800 text-xs">{cat.name}</span>
                  <span className="font-mono font-bold text-emerald-700 text-xs">{cat.score}</span>
                </div>
                <p className="text-[11px] text-slate-500 line-clamp-2">{dynamicDesc}</p>
                <div className="flex items-center justify-between pt-1 border-t border-slate-100 text-[11px]">
                  <span className="text-slate-600 font-medium">
                    {catFindingsCount} {catFindingsCount === 1 ? 'finding' : 'findings'}
                  </span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                    catStatus === 'PASS' ? 'bg-emerald-50 text-emerald-700' : catStatus === 'WARNING' ? 'bg-amber-50 text-amber-700' : 'bg-rose-50 text-rose-700'
                  }`}>
                    {catStatus}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
      {/* Section — Cost & FinOps Analysis */}
      {planData?.cost_summary && (
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div>
              <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <DollarSign className="w-4 h-4 text-emerald-600" />
                <span>Infrastructure Cost &amp; FinOps Analysis</span>
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">{planData.cost_summary.pricing_assumptions}</p>
            </div>
            <div className="text-right">
              <div className="text-[11px] text-slate-400 font-medium">Estimated Monthly Spend</div>
              <div className="text-lg font-bold font-mono text-slate-900">
                ${planData.cost_summary.total_estimated_monthly_usd?.toFixed(2) || '0.00'} / mo
              </div>
            </div>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-xs">
            {Object.entries(planData.cost_summary.breakdown || {}).map(([cat, cost]) => (
              <div key={cat} className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                <div className="text-[11px] text-slate-500 font-medium uppercase">{cat}</div>
                <div className="text-sm font-bold font-mono text-slate-800 mt-1">${cost.toFixed(2)} / mo</div>
              </div>
            ))}
          </div>

          {planData.cost_summary.unavailable_pricing?.length > 0 && (
            <div className="p-3 rounded-lg bg-amber-50 border border-amber-200 text-xs text-amber-800">
              <strong>Unavailable Pricing:</strong> Explicit pricing not found in AWS catalog for: {planData.cost_summary.unavailable_pricing.join(', ')}. Estimated with default baseline.
            </div>
          )}
        </div>
      )}

      {/* Section — Complexity Assessment */}
      {planData?.complexity_assessment && (
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs space-y-3">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div>
              <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <Activity className="w-4 h-4 text-blue-600" />
                <span>Architecture Complexity &amp; Operational Assessment</span>
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">{planData.complexity_assessment.operational_considerations}</p>
            </div>
            <span className={`px-2.5 py-0.5 rounded text-xs font-bold ${
              planData.complexity_assessment.complexity_level === 'HIGH' ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'
            }`}>
              Complexity: {planData.complexity_assessment.complexity_level}
            </span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-2 gap-3 text-xs">
            <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
              <span className="text-slate-500">Resource Count:</span> <strong className="text-slate-800 font-mono">{planData.complexity_assessment.resource_count} resources</strong>
            </div>
            <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
              <span className="text-slate-500">Service Diversity:</span> <strong className="text-slate-800 font-mono">{planData.complexity_assessment.service_diversity} distinct AWS services</strong>
            </div>
          </div>
        </div>
      )}

      {/* Section 5 — Findings Interface */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-3 border-b border-slate-100">
          <div>
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-blue-600" />
              <span>Detected Findings &amp; Risk Items</span>
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">Filter by severity or expand items to inspect technical evidence</p>
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((sev) => (
              <button
                key={sev}
                onClick={() => setSelectedSeverityFilter(sev)}
                className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition cursor-pointer ${
                  selectedSeverityFilter === sev
                    ? 'bg-blue-600 text-white shadow-2xs'
                    : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
                }`}
              >
                {sev}
              </button>
            ))}
          </div>
        </div>

        {filteredFindings.length === 0 ? (
          <div className="p-8 text-center text-slate-500 text-xs">
            <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto mb-2" />
            <p className="font-semibold text-slate-700">No findings match the current filter criteria.</p>
            <p className="text-[11px] text-slate-400 mt-1">Your architecture meets all automated pre-deployment thresholds.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {filteredFindings.map((finding) => {
              const isExpanded = Boolean(expandedFindings[finding.id]);
              const isApplied = appliedRecommendations.has(finding.id);
              return (
                <div key={finding.id} className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 space-y-3">
                  <div className="flex items-start justify-between gap-4">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          finding.severity === 'CRITICAL' ? 'bg-rose-100 text-rose-800' :
                          finding.severity === 'HIGH' ? 'bg-amber-100 text-amber-800' : 'bg-blue-100 text-blue-800'
                        }`}>
                          {finding.severity}
                        </span>
                        <span className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-slate-200 text-slate-700">
                          {finding.category}
                        </span>
                        <span className="font-mono text-[11px] text-slate-500">{finding.id}</span>
                      </div>
                      <h4 className="text-xs font-bold text-slate-900">{finding.title}</h4>
                      <p className="text-xs text-slate-600">{finding.explanation}</p>
                    </div>

                    <div className="flex items-center gap-2 shrink-0">
                      <button
                        onClick={() => handleApplyRecommendation(finding.id)}
                        disabled={isApplied}
                        className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer ${
                          isApplied
                            ? 'bg-emerald-100 text-emerald-800 cursor-default'
                            : 'bg-blue-600 hover:bg-blue-700 text-white shadow-2xs'
                        }`}
                      >
                        {isApplied ? 'Applied' : 'Apply Fix'}
                      </button>
                      <button
                        onClick={() => handleDismissRecommendation(finding.id)}
                        className="px-2.5 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-600 text-xs transition cursor-pointer"
                        title="Dismiss Finding"
                      >
                        Dismiss
                      </button>
                      <button
                        onClick={() => setExpandedFindings((prev) => ({ ...prev, [finding.id]: !isExpanded }))}
                        className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-600 transition cursor-pointer"
                      >
                        {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>

                  {isExpanded && (
                    <div className="p-3 rounded-lg bg-white border border-slate-200 text-[11px] font-mono space-y-1.5 text-slate-700">
                      <div><strong className="text-slate-900 font-sans">Affected Resource:</strong> {finding.affected_resource || 'Cluster wide / Terraform root'}</div>
                      <div><strong className="text-slate-900 font-sans">Compliance Standard:</strong> AWS Well-Architected Framework &amp; Zero-Trust Baseline</div>
                      <div><strong className="text-slate-900 font-sans">Recommended Action:</strong> {finding.recommendation || 'Apply recommended module patch or update configuration variable.'}</div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Section 6 — Resource Changes Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <Layers className="w-4 h-4 text-blue-600" />
              <span>Dry Run Proposed AWS Resource Changes</span>
            </h3>
            <p className="text-[11px] text-slate-500 mt-0.5">Exact infrastructure mutations that will occur upon approval</p>
          </div>
          <span className="text-xs font-mono font-semibold text-slate-600 bg-slate-200 px-2 py-0.5 rounded">
            {changes.length} Resources Planned
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
              <tr>
                <th className="py-2.5 px-3">Action</th>
                <th className="py-2.5 px-3">Resource Identifier</th>
                <th className="py-2.5 px-3">Terraform Resource Type</th>
                <th className="py-2.5 px-3">Key Attributes</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-mono">
              {changes.map((rc, idx) => (
                <tr key={idx} className="hover:bg-slate-50/70">
                  <td className="py-2.5 px-3">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                      {rc.symbol || '+'} {rc.action || 'CREATE'}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 font-sans font-semibold text-slate-800">{rc.resource_id}</td>
                  <td className="py-2.5 px-3 text-blue-700">{rc.resource_type}</td>
                  <td className="py-2.5 px-3 text-slate-600 font-sans text-[11px]">
                    {Object.entries(rc.details || {}).map(([k, v]) => `${k}=${v}`).join(', ') || 'Standard baseline'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Section 7 — Unified Approval Interface */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div>
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <span>Unified Approval Gate &amp; Execution Authorization</span>
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">Cryptographically bind plan digest, record approver identity, and authorize Cloud Deployment</p>
          </div>
          <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold ${
            approvedReceipt ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' :
            rejectedStatus ? 'bg-rose-50 text-rose-700 border border-rose-200' :
            isOutdated ? 'bg-amber-50 text-amber-700 border border-amber-200' : 'bg-blue-50 text-blue-700 border border-blue-200'
          }`}>
            {approvedReceipt ? 'APPROVED & AUTHORIZED' : rejectedStatus ? 'PLAN REJECTED' : isOutdated ? 'STALENESS DETECTED' : 'READY FOR APPROVAL'}
          </span>
        </div>

        {approvedReceipt ? (
          <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-emerald-900 font-bold text-xs">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>Infrastructure Plan Successfully Approved</span>
              </div>
              <span className="font-mono text-[11px] text-emerald-700">ID: {approvedReceipt.approval_id}</span>
            </div>
            <p className="text-xs text-emerald-800">
              Approved by <strong className="font-semibold">{approvedReceipt.approved_by || user?.username || 'admin'}</strong> at {new Date((approvedReceipt.approved_at || Date.now() / 1000) * 1000).toLocaleString()}. Valid execution authorization generated for Cloud Deployment.
            </p>
            <div className="flex items-center justify-end pt-2">
              <button
                onClick={() => onNavigate('deployments', '/deployment')}
                className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold transition flex items-center gap-1.5 cursor-pointer shadow-xs"
              >
                <span>Continue to Cloud Deployment</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        ) : rejectedStatus ? (
          <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 space-y-2">
            <div className="flex items-center gap-2 text-rose-900 font-bold text-xs">
              <XCircle className="w-4 h-4 text-rose-600" />
              <span>Infrastructure Plan Rejected</span>
            </div>
            <p className="text-xs text-rose-800">
              This deployment plan has been rejected. Modify the architecture version or run a new dry-run analysis to proceed.
            </p>
            <button
              onClick={runAnalysis}
              className="px-3 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-700 text-white text-xs font-semibold transition cursor-pointer"
            >
              Run New Analysis
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {isOutdated && (
              <div className="p-3 rounded-lg bg-amber-50 border border-amber-200 text-amber-800 text-xs font-medium flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
                <span>Architecture has been modified since last analysis. Re-analysis is required before approval.</span>
              </div>
            )}

            <label className="block text-xs font-semibold text-slate-700">
              Approval Sign-off Comments / Review Notes
            </label>
            <textarea
              value={comments}
              onChange={(e) => setComments(e.target.value)}
              placeholder="Enter compliance sign-off notes, release justification, or security verification remarks..."
              className="w-full p-3 rounded-lg border border-slate-200 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={2}
            />

            <div className="flex items-center justify-between pt-2">
              <span className="text-[11px] text-slate-500 font-mono">
                Plan Digest: {planData?.plan_digest ? `${planData.plan_digest.substring(0, 16)}...` : 'N/A'}
              </span>
              <div className="flex items-center gap-2">
                <button
                  onClick={handleRejectPlan}
                  className="px-4 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition cursor-pointer"
                >
                  Reject Plan
                </button>
                <button
                  onClick={() => setShowConfirmModal(true)}
                  disabled={approving || !planData || status === 'BLOCKED' || isOutdated}
                  className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold transition flex items-center gap-1.5 cursor-pointer shadow-xs disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  <ShieldCheck className={`w-3.5 h-3.5 ${approving ? 'animate-spin' : ''}`} />
                  <span>Approve Plan &amp; Authorize Deployment</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Confirmation Modal before approval */}
      {showConfirmModal && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl border border-slate-200 max-w-md w-full p-6 space-y-4 shadow-xl">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-emerald-600" />
                <span>Confirm Infrastructure Approval</span>
              </h3>
              <button
                onClick={() => setShowConfirmModal(false)}
                className="text-slate-400 hover:text-slate-600 cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="text-xs text-slate-600 space-y-2">
              <p>You are about to cryptographically sign and approve plan <strong className="font-mono text-slate-900">{planData?.plan_id}</strong>.</p>
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 space-y-1 font-mono text-[11px]">
                <div><span className="text-slate-400">Project:</span> {projectName}</div>
                <div><span className="text-slate-400">Environment:</span> {envTier} ({region})</div>
                <div><span className="text-slate-400">Digest:</span> {planData?.plan_digest?.substring(0, 24)}...</div>
                <div><span className="text-slate-400">Mutations:</span> +{changes.length} resources</div>
              </div>
              <p className="text-[11px] text-slate-500">This action generates a verified execution authorization for Cloud Deployment.</p>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => setShowConfirmModal(false)}
                className="px-4 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={handleApprovePlan}
                disabled={approving}
                className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold transition flex items-center gap-1.5 cursor-pointer shadow-xs"
              >
                {approving ? 'Signing...' : 'Confirm & Approve'}
              </button>
            </div>
          </div>
        </div>
      )}
        </>
      )}
    </div>
  );

}
