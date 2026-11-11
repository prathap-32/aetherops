// frontend/src/modules/repo_analyzer/RepoAnalyzerView.jsx
import React, { useState, useEffect } from 'react';
import {
  Cpu,
  Search,
  Zap,
  CheckCircle2,
  AlertCircle,
  AlertTriangle,
  Server,
  Database,
  ArrowRight,
  RefreshCw,
  Sliders,
  DollarSign,
  Layers,
  Sparkles,
  FileCode,
  HardDrive,
  Check,
  Edit3,
  ShieldCheck,
  Globe,
  Boxes,
  FolderKanban,
  GitBranch,
  ExternalLink,
  ChevronDown
} from 'lucide-react';
import { repoAnalyzerApi, projectsApi, connectionsApi } from '../../services/api';
import { AWS_REGIONS_39 } from '../../constants/awsRegions';
import { formatAiProvider } from '../../utils/formatters';

export default function RepoAnalyzerView({
  onNavigate,
  activeProject,
  activeEnvironment,
  navState,
}) {
  const targetProjectId = navState?.projectId || activeProject?.id || activeProject?.project_id || '';
  const targetEnvId = navState?.environmentId || activeEnvironment?.id || activeEnvironment?.env_id || '';

  // Navigation & Project Context
  const [projects, setProjects] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState(targetProjectId);
  const [environments, setEnvironments] = useState([]);
  const [selectedEnvId, setSelectedEnvId] = useState(targetEnvId);
  const [selectedEnvTier, setSelectedEnvTier] = useState('development');
  const [connectedGit, setConnectedGit] = useState(null);

  // Form Parameters
  const [repoPath, setRepoPath] = useState(navState?.repoPath || '.');
  const [targetRegion, setTargetRegion] = useState('us-east-1');
  const [trafficScale, setTrafficScale] = useState('MODERATE');
  const [budgetTier, setBudgetTier] = useState('STANDARD');

  // State Pipeline: 1 = Initial, 2 = Ready & Scanned, 3 = Accepted & Sized
  const [workflowStep, setWorkflowStep] = useState(1);
  const [isScanning, setIsScanning] = useState(false);
  const [isSizing, setIsSizing] = useState(false);
  const [statusMessage, setStatusMessage] = useState(null);

  // Scan & Report Results
  const [readinessResult, setReadinessResult] = useState(null);
  const [scanReport, setScanReport] = useState(null);
  const [editableKeyValue, setEditableKeyValue] = useState([]);

  // Final Sizing Output
  const [sizingOutput, setSizingOutput] = useState(null);

  // Editable AWS Services State for Step 3
  const [editedComputeService, setEditedComputeService] = useState('Amazon EC2 (Docker Runtime)');
  const [editedInstanceType, setEditedInstanceType] = useState('t4g.micro');
  const [editedMinCapacity, setEditedMinCapacity] = useState(1);
  const [editedAlbEnabled, setEditedAlbEnabled] = useState(false);
  const [editedDatabaseService, setEditedDatabaseService] = useState('None');
  const [editedCacheService, setEditedCacheService] = useState('None');
  const [editedCdnEnabled, setEditedCdnEnabled] = useState(false);
  const [isRecalculating, setIsRecalculating] = useState(false);

  // Load connected projects and environments
  useEffect(() => {
    async function loadData() {
      try {
        const [projList, gitList] = await Promise.all([
          projectsApi.list().catch(() => []),
          connectionsApi.listGit().catch(() => []),
        ]);
        setProjects(projList);
        if (projList.length > 0) {
          const matched = targetProjectId && projList.find(p => (p.id || p.project_id) === targetProjectId);
          const activeProjObj = matched || projList[0];
          const pid = activeProjObj.id || activeProjObj.project_id;
          setSelectedProjectId(pid);
          loadEnvironments(pid, gitList);
        }
      } catch (err) {
        console.error('Failed to load initial context:', err);
      }
    }
    loadData();
  }, [targetProjectId]);

  const loadEnvironments = async (projectId, gitList = []) => {
    try {
      const envList = await projectsApi.listEnvironments(projectId);
      setEnvironments(envList);
      if (envList.length > 0) {
        const matchedEnv = targetEnvId && envList.find(e => (e.id || e.env_id) === targetEnvId);
        const activeEnvObj = matchedEnv || envList[0];
        const eid = activeEnvObj.id || activeEnvObj.env_id;
        setSelectedEnvId(eid);
        setSelectedEnvTier(activeEnvObj.type || activeEnvObj.env_type || 'development');

        // Check if there is an existing git connection for this env
        const matchGit = gitList.find(
          (g) => (g.project_id === projectId && g.environment_id === eid) || g.project_id === projectId
        );
        if (matchGit) {
          setConnectedGit(matchGit);
          if (!navState?.repoPath) {
            if (matchGit.repo_name) {
              setRepoPath(matchGit.repo_name);
            } else if (matchGit.repo_url) {
              setRepoPath(matchGit.repo_url);
            }
          }
        }
      }
    } catch (err) {
      console.warn('Failed to load environments:', err);
    }
  };

  const handleProjectChange = (e) => {
    const pid = e.target.value;
    setSelectedProjectId(pid);
    loadEnvironments(pid);
  };

  const handleEnvChange = (e) => {
    const eid = e.target.value;
    setSelectedEnvId(eid);
    const found = environments.find((env) => (env.id || env.env_id) === eid);
    if (found) {
      setSelectedEnvTier(found.type || found.env_type || 'development');
    }
  };

  // Step 1: Universal Codebase Scan with AST Readiness Check
  const handleUniversalScan = async (e) => {
    if (e) e.preventDefault();
    if (!repoPath.trim()) return;

    setIsScanning(true);
    setStatusMessage(null);
    setReadinessResult(null);
    setScanReport(null);
    setSizingOutput(null);

    try {
      // 1. Check Readiness
      const readiness = await repoAnalyzerApi.checkReadiness({
        repo_path: repoPath.trim(),
        project_id: selectedProjectId,
        environment_id: selectedEnvId,
        branch: connectedGit?.branch || 'main',
      });
      setReadinessResult(readiness);

      if (!readiness.is_analyzable) {
        setStatusMessage({
          type: 'error',
          text: readiness.message || 'Repository cannot be analyzed. Missing manifests or code files.',
        });
        setIsScanning(false);
        return;
      }

      // 2. Run Universal Scan & Generate Key:Value Report
      const report = await repoAnalyzerApi.scanReport({
        repo_path: repoPath.trim(),
        project_id: selectedProjectId,
        environment_id: selectedEnvId,
        environment_tier: selectedEnvTier,
        target_region: targetRegion,
        branch: connectedGit?.branch || 'main',
      });

      setScanReport(report);
      setEditableKeyValue(report.key_value_report || []);
      setWorkflowStep(2);
      setStatusMessage({
        type: 'success',
        text: `Codebase scanned successfully! Found ${report.frameworks?.length || 0} frameworks and ${report.languages?.length || 0} runtimes. Please review and verify below.`,
      });
    } catch (err) {
      console.error('Scan error:', err);
      setStatusMessage({
        type: 'error',
        text: err.message || 'Universal codebase scan failed. Please verify the target path.',
      });
    } finally {
      setIsScanning(false);
    }
  };

  // Handle User Editing Key:Value item
  const handleValueChange = (index, newValue) => {
    setEditableKeyValue((prev) => {
      const copy = [...prev];
      copy[index] = { ...copy[index], value: newValue };
      return copy;
    });
  };

  // Step 2: User Verifies & Accepts Specification -> Triggers Environment-Aware Sizing
  const handleAcceptAndSize = async () => {
    setIsSizing(true);
    setStatusMessage(null);

    try {
      // Build verified spec dictionary from user-approved Key:Value pairs
      const verifiedSpec = {};
      editableKeyValue.forEach((item) => {
        verifiedSpec[item.key] = item.value;
      });

      // Include base detected parameters
      if (scanReport?.summary_dict) {
        Object.assign(verifiedSpec, scanReport.summary_dict, verifiedSpec);
      }

      const res = await repoAnalyzerApi.acceptAndSize({
        repo_path: repoPath.trim(),
        project_id: selectedProjectId,
        environment_id: selectedEnvId,
        environment_tier: selectedEnvTier,
        target_region: targetRegion,
        budget_tier: budgetTier,
        traffic_scale: trafficScale,
        verified_spec: verifiedSpec,
      });

      setSizingOutput(res);
      // Cache sizing in localStorage for Cloud Architecture Studio & Designer
      try {
        localStorage.setItem('aether_latest_sizing', JSON.stringify(res));
        const userKey = 'user';
        const projectKey = selectedProjectId || 'default';
        localStorage.setItem(`aether_sizing_${userKey}_${projectKey}`, JSON.stringify(res));
      } catch (e) {
        console.warn('Could not cache sizing in localStorage', e);
      }

      // Initialize editable fields from sizing response
      setEditedComputeService(res.compute?.service || 'Amazon EC2 (Docker Runtime)');
      setEditedInstanceType(res.compute?.instance_class || (res.compute?.service?.includes('ECS') ? '0.25 vCPU / 0.5 GB' : 't4g.micro'));
      setEditedMinCapacity(res.compute?.min_capacity || 1);
      setEditedAlbEnabled(Boolean(res.networking?.alb));
      setEditedDatabaseService(res.database?.service || 'None');
      setEditedCacheService(res.cache?.service || 'None');
      setEditedCdnEnabled(Boolean(res.frontend_hosting));

      setWorkflowStep(3);
      setStatusMessage({
        type: 'success',
        text: `Tech stack confirmed! Generating AWS recommendations for ${selectedEnvTier.toUpperCase()}. Forwarding to Cloud Architecture Studio...`,
      });

      // Userflow: "after analyse of aws service recommendation want to in cloud architecture studio , after click verify then it shows that"
      if (onNavigate) {
        setTimeout(() => {
          onNavigate('architecture_studio', '/architecture-studio', {
            sizingOutput: res,
            scanReport,
            editableKeyValue,
            selectedProjectId,
            selectedEnvId,
            selectedEnvTier,
            targetRegion,
            trafficScale,
            budgetTier,
            repoPath,
            activeProject,
            activeEnvironment,
            fromAnalyzer: true,
          });
        }, 300);
      }
    } catch (err) {
      console.error('Sizing error:', err);
      setStatusMessage({
        type: 'error',
        text: err.message || 'Failed to size AWS infrastructure.',
      });
    } finally {
      setIsSizing(false);
    }
  };

  // Step 3 Customizer: User modifies AWS services and triggers re-analysis
  const handleRecalculateSizing = async () => {
    setIsRecalculating(true);
    setStatusMessage(null);

    try {
      const res = await repoAnalyzerApi.recalculateSizing({
        environment_tier: selectedEnvTier,
        target_region: targetRegion,
        compute_service: editedComputeService,
        instance_type: editedInstanceType,
        min_capacity: Number(editedMinCapacity),
        max_capacity: Number(editedMinCapacity),
        multi_az: selectedEnvTier === 'production',
        alb_enabled: editedAlbEnabled,
        waf_enabled: selectedEnvTier === 'production',
        database_service: editedDatabaseService,
        cache_service: editedCacheService,
        cdn_enabled: editedCdnEnabled,
        verified_spec: sizingOutput?.verified_spec_applied || {},
      });

      setSizingOutput(res);
      setStatusMessage({
        type: 'success',
        text: `Architecture re-analyzed! Updated monthly estimate is $${res.monthly_cost_estimate_usd?.total_estimated_monthly_usd || '0.00'}/month.`,
      });
    } catch (err) {
      console.error('Recalculation error:', err);
      setStatusMessage({
        type: 'error',
        text: err.message || 'Failed to recalculate architecture.',
      });
    } finally {
      setIsRecalculating(false);
    }
  };

  // Step 3: Forward to Module 4 (Cloud Architecture Studio)
  const handleProceedToModule4 = () => {
    try {
      localStorage.setItem('aether_latest_sizing', JSON.stringify(sizingOutput));
    } catch (e) {
      console.warn('Could not cache sizing in localStorage', e);
    }

    if (onNavigate) {
      onNavigate('architecture_studio', '/architecture-studio', {
        sizingOutput,
        scanReport,
        editableKeyValue,
        selectedProjectId,
        selectedEnvId,
        selectedEnvTier,
        targetRegion,
        trafficScale,
        budgetTier,
        repoPath,
        activeProject,
        activeEnvironment,
        fromAnalyzer: true,
      });
    }
  };

  return (
    <div className="space-y-6">
      {/* Module Header */}
      <div className="pb-4 border-b border-slate-200">
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
          Source Code Analyzer
        </h1>
      </div>

      {/* Global Status Message */}
      {statusMessage && (
        <div
          className={`p-3.5 rounded-xl text-xs flex items-center gap-2.5 border ${
            statusMessage.type === 'success'
              ? 'bg-emerald-50 text-emerald-900 border-emerald-200'
              : 'bg-rose-50 text-rose-900 border-rose-200'
          }`}
        >
          {statusMessage.type === 'success' ? (
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          ) : (
            <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
          )}
          <span>{statusMessage.text}</span>
        </div>
      )}

      {/* STEP 1: Repository & Environment Context Card */}
      <form onSubmit={handleUniversalScan} className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-4 bg-slate-50/70 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-700">
            <span className="w-5 h-5 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-[10px]">
              1
            </span>
            Target Project Environment &amp; Codebase Source
          </div>
          {connectedGit && (
            <div className="flex items-center gap-1.5 text-xs text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
              <GitBranch className="w-3.5 h-3.5" />
              <span>Connected: {connectedGit.repo_name || connectedGit.repo_url}</span>
            </div>
          )}
        </div>

        <div className="p-6 space-y-5">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Target Project</label>
              <select
                value={selectedProjectId}
                onChange={handleProjectChange}
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
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Target Environment Tier</label>
              <select
                value={selectedEnvId}
                onChange={handleEnvChange}
                className="w-full text-sm bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                required
              >
                {environments.length === 0 ? (
                  <option value="">No environments found</option>
                ) : (
                  environments.map((env) => {
                    const eid = env.id || env.env_id;
                    return (
                      <option key={eid} value={eid}>
                        {env.name || env.env_name || eid} ({env.type || env.env_type || 'DEV'})
                      </option>
                    );
                  })
                )}
              </select>
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="block text-xs font-medium text-slate-600">
                Repository Target (Remote GitHub or Local Workspace)
              </label>
              {connectedGit && (
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => setRepoPath(connectedGit.repo_name || connectedGit.repo_url)}
                    className="text-[11px] text-blue-600 hover:text-blue-800 font-medium flex items-center gap-1 underline"
                  >
                    Use Connected: {connectedGit.repo_name || 'GitHub'}
                  </button>
                  <span className="text-slate-300">|</span>
                  <button
                    type="button"
                    onClick={() => setRepoPath('.')}
                    className="text-[11px] text-slate-500 hover:text-slate-700 font-medium underline"
                  >
                    Local Workspace (.)
                  </button>
                </div>
              )}
            </div>
            <div className="relative">
              <FileCode className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={repoPath}
                onChange={(e) => setRepoPath(e.target.value)}
                placeholder="e.g. prathap-32/Docker_webApp_analogClock, https://github.com/... or ."
                className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-xs font-mono text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                required
              />
            </div>
            {readinessResult?.inspection_mode && (
              <div className="mt-1.5 text-right text-slate-400 font-mono text-[10px]">
                Mode: {readinessResult.inspection_mode}
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">AWS Target Region</label>
              <select
                value={targetRegion}
                onChange={(e) => setTargetRegion(e.target.value)}
                className="w-full text-xs bg-slate-50 border border-slate-200 rounded-lg p-2 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 font-mono"
              >
                {AWS_REGIONS_39.map((r) => (
                  <option key={r.value} value={r.value}>
                    {r.value} ({r.group})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Projected Traffic Profile</label>
              <select
                value={trafficScale}
                onChange={(e) => setTrafficScale(e.target.value)}
                className="w-full text-xs bg-slate-50 border border-slate-200 rounded-lg p-2 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
              >
                <option value="LOW">Low (Dev / Internal Testing)</option>
                <option value="MODERATE">Moderate (Standard Web Traffic)</option>
                <option value="HIGH">High (Scale-out Production)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Budget Allocation Tier</label>
              <select
                value={budgetTier}
                onChange={(e) => setBudgetTier(e.target.value)}
                className="w-full text-xs bg-slate-50 border border-slate-200 rounded-lg p-2 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
              >
                <option value="LOW">Frugal / Lean (Cost Minimized)</option>
                <option value="STANDARD">Standard Production</option>
                <option value="ENTERPRISE">High Performance / Resilient</option>
              </select>
            </div>
          </div>
        </div>

        <div className="p-4 bg-slate-50 border-t border-slate-200 flex items-center justify-end">
          <button
            type="submit"
            disabled={isScanning || !repoPath.trim()}
            className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg shadow-xs transition disabled:opacity-50 flex items-center gap-2"
          >
            {isScanning ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                Scanning Codebase &amp; Manifests...
              </>
            ) : (
              <>
                <Search className="w-3.5 h-3.5" />
                Analyze Codebase
              </>
            )}
          </button>
        </div>
      </form>

      {/* STEP 2: Detected Tech Stack & Configuration */}
      {workflowStep >= 2 && scanReport && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden animate-in fade-in space-y-0">
          <div className="p-5 bg-slate-50/80 border-b border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <div className="flex items-center gap-2">
                <span className="w-5 h-5 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center text-[10px] font-bold">
                  2
                </span>
                <h3 className="text-sm font-bold text-slate-900">
                  Review Detected Tech Stack &amp; Configuration
                </h3>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-[11px] font-semibold px-2.5 py-1 rounded-md bg-blue-50 text-blue-800 border border-blue-200">
                Environment: {selectedEnvTier.toUpperCase()}
              </span>
            </div>
          </div>
          {/* Factual Repository Intelligence & Source Overview (Zero AI) */}
          <div className="p-5 bg-gradient-to-br from-slate-900 via-slate-800 to-indigo-950 text-white border-b border-slate-700">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 mb-3">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-white/10 flex items-center justify-center text-white shrink-0">
                  <FolderKanban className="w-5 h-5 text-indigo-400" />
                </div>
                <div>
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-mono text-sm font-bold text-white">
                      {scanReport.repo_metadata?.full_name || scanReport.repo_name}
                    </span>
                    {scanReport.repo_metadata?.html_url && (
                      <a
                        href={scanReport.repo_metadata.html_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-xs text-indigo-300 hover:text-white flex items-center gap-1 underline"
                      >
                        GitHub <ExternalLink className="w-3 h-3" />
                      </a>
                    )}
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-white/10 text-slate-300 capitalize">
                      {scanReport.repo_metadata?.visibility || (scanReport.is_remote ? 'Remote' : 'Local')}
                    </span>
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-blue-500/20 text-blue-300 border border-blue-400/30">
                      branch: {scanReport.repo_metadata?.default_branch || 'main'}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Commit & Manifest Diagnostics */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 pt-3 border-t border-slate-700/60 text-xs">
              {scanReport.repo_metadata?.latest_commit && (
                <div className="bg-white/5 rounded-lg p-2.5 border border-white/5">
                  <div className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold flex items-center gap-1.5 mb-1">
                    <GitBranch className="w-3 h-3 text-indigo-400" />
                    Latest Commit
                  </div>
                  <div className="font-mono text-[11px] text-indigo-300 flex items-center gap-1.5 truncate">
                    <span className="px-1.5 py-0.2 rounded bg-indigo-900/60 text-indigo-200 border border-indigo-700/50">
                      {scanReport.repo_metadata.latest_commit.short_sha || 'HEAD'}
                    </span>
                    <span className="truncate text-slate-200" title={scanReport.repo_metadata.latest_commit.message}>
                      {scanReport.repo_metadata.latest_commit.message}
                    </span>
                  </div>
                  <div className="text-[10px] text-slate-400 mt-0.5">
                    by {scanReport.repo_metadata.latest_commit.author}
                  </div>
                </div>
              )}

              <div className="bg-white/5 rounded-lg p-2.5 border border-white/5">
                <div className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold flex items-center gap-1.5 mb-1">
                  <Boxes className="w-3 h-3 text-emerald-400" />
                  Inspected Manifests
                </div>
                <div className="flex items-center gap-1.5 flex-wrap">
                  {scanReport.inspected_manifests && scanReport.inspected_manifests.length > 0 ? (
                    scanReport.inspected_manifests.map((m) => (
                      <span key={m} className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-950/70 text-emerald-300 border border-emerald-700/50">
                        ✓ {m}
                      </span>
                    ))
                  ) : (
                    <span className="text-[11px] text-slate-400 font-mono">No standard manifests</span>
                  )}
                </div>
              </div>

              {scanReport.commit_sha && (
                <div className="bg-white/5 rounded-lg p-2.5 border border-white/5">
                  <div className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold mb-1">
                    Analyzed Revision
                  </div>
                  <code className="text-[11px] text-slate-200 break-all">{scanReport.commit_sha}</code>
                </div>
              )}

              {scanReport.profile_completeness === "PARTIAL" && (
                <div className="rounded-lg p-2.5 border border-amber-700/50 bg-amber-950/20 text-amber-200 text-[11px]">
                  Preliminary profile: this scan currently covers repository manifests and configuration. It is not yet a complete dependency graph or architecture inventory.
                </div>
              )}

              {scanReport.truncated_manifests && (
                <div className="rounded-lg p-2.5 border border-amber-700/50 bg-amber-950/20 text-amber-200 text-[11px]">
                  Manifest inspection was limited to {scanReport.manifest_limit} of {scanReport.manifest_count} candidate files. Treat this profile as partial coverage.
                </div>
              )}

              <div className="bg-white/5 rounded-lg p-2.5 border border-white/5">
                <div className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold flex items-center gap-1.5 mb-1">
                  <HardDrive className="w-3 h-3 text-cyan-400" />
                  Repository Storage
                </div>
                <div className="text-slate-200 font-mono text-[11px]">
                  {scanReport.repo_metadata?.size_kb ? `${scanReport.repo_metadata.size_kb} KB` : 'Dynamic Workspace'}
                  {scanReport.repo_metadata?.license && scanReport.repo_metadata.license !== 'None' && (
                    <span className="ml-2 text-slate-400 font-sans">({scanReport.repo_metadata.license})</span>
                  )}
                </div>
              </div>
            </div>

            {/* Language Breakdown Stacked Bar */}
            {scanReport.languages_breakdown && scanReport.languages_breakdown.length > 0 && (
              <div className="mt-4 pt-3 border-t border-slate-700/60">
                <div className="text-[11px] text-slate-300 mb-1.5 font-medium">
                  Language Composition
                </div>
                <div className="w-full h-2.5 rounded-full bg-slate-700 overflow-hidden flex shadow-inner">
                  {scanReport.languages_breakdown.map((l) => (
                    <div
                      key={l.name}
                      style={{ width: `${l.percentage}%`, backgroundColor: l.color || '#8b949e' }}
                      title={`${l.name}: ${l.percentage}% (${(l.bytes / 1024).toFixed(1)} KB)`}
                      className="h-full first:rounded-l-full last:rounded-r-full transition-all duration-300 hover:brightness-125"
                    />
                  ))}
                </div>
                <div className="flex items-center gap-3 flex-wrap mt-2 text-[10px]">
                  {scanReport.languages_breakdown.map((l) => (
                    <div key={l.name} className="flex items-center gap-1.5">
                      <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: l.color || '#8b949e' }} />
                      <span className="text-slate-200 font-medium">{l.name}</span>
                      <span className="text-slate-400 font-mono">{l.percentage}%</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Key:Value Specification Table */}
          <div className="divide-y divide-slate-100">
            {editableKeyValue.map((item, idx) => (
              <div key={item.key} className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-slate-50/50 transition">
                <div className="sm:w-1/3">
                  <span className="text-xs font-semibold text-slate-800">{item.label}</span>
                </div>

                <div className="sm:w-2/3 flex items-center gap-3">
                  {item.options && item.options.length > 0 ? (
                    <select
                      value={item.value}
                      onChange={(e) => handleValueChange(idx, e.target.value)}
                      className="w-full text-xs bg-white border border-slate-200 rounded-lg p-2 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 font-medium"
                    >
                      {item.options.map((opt) => (
                        <option key={opt} value={opt}>
                          {opt}
                        </option>
                      ))}
                    </select>
                  ) : item.editable ? (
                    <div className="relative w-full">
                      <input
                        type="text"
                        value={item.value}
                        onChange={(e) => handleValueChange(idx, e.target.value)}
                        className="w-full text-xs bg-white border border-slate-200 rounded-lg py-2 pl-3 pr-8 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 font-mono"
                      />
                      <Edit3 className="w-3.5 h-3.5 text-slate-400 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                    </div>
                  ) : (
                    <span className="text-xs font-semibold text-slate-900 bg-slate-100 px-3 py-1.5 rounded-lg border border-slate-200 font-mono">
                      {item.value}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Acceptance Action Bar */}
          <div className="p-4 bg-slate-50 border-t border-slate-200 flex flex-col sm:flex-row sm:items-center justify-end gap-3">
            <button
              type="button"
              onClick={handleAcceptAndSize}
              disabled={isSizing}
              className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold rounded-lg shadow-xs transition disabled:opacity-50 flex items-center justify-center gap-2 cursor-pointer"
            >
              {isSizing ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  Generating AWS Architecture...
                </>
              ) : (
                <>
                  <Check className="w-4 h-4" />
                  Confirm Stack &amp; Open Architecture Studio ➔
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* STEP 3: AWS Architecture Blueprint & Editable Service Customizer */}
      {workflowStep === 3 && sizingOutput && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden animate-in fade-in space-y-6 p-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-100">
            <div>
              <div className="flex items-center gap-2">
                <span className="w-5 h-5 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center text-[10px] font-bold">
                  3
                </span>
                <h3 className="text-lg font-bold text-slate-900">
                  Recommended AWS Infrastructure &amp; Service Configuration
                </h3>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="text-right">
                <span className="text-[10px] uppercase font-bold text-slate-400 block">Total Estimated Cost</span>
                <span className="text-2xl font-bold text-slate-900">
                  ${sizingOutput.monthly_cost_estimate_usd?.total_estimated_monthly_usd || '0.00'}
                  <span className="text-xs font-normal text-slate-500"> / month</span>
                </span>
              </div>
              <span className="text-xs font-semibold px-2.5 py-1 rounded-md bg-blue-50 text-blue-700 border border-blue-200">
                {formatAiProvider(sizingOutput.ai_provider)}
              </span>
            </div>
          </div>

          {/* Interactive AWS Service Customizer Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* 1. Compute Fleet Card */}
            <div className="p-4 rounded-xl border border-blue-200 bg-blue-50/20 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs font-bold text-blue-900">
                  <Server className="w-4 h-4 text-blue-600" />
                  Compute Fleet
                </div>
                <span className="text-[10px] font-semibold text-blue-700 bg-blue-100/60 px-2 py-0.5 rounded">
                  ${sizingOutput.compute?.monthly_cost || 0}/mo
                </span>
              </div>

              <div className="space-y-2 text-xs">
                <div>
                  <label className="text-slate-500 block mb-1">Compute Service</label>
                  <select
                    value={editedComputeService}
                    onChange={(e) => {
                      const val = e.target.value;
                      setEditedComputeService(val);
                      if (val.includes('EC2')) setEditedInstanceType('t4g.micro');
                      else if (val.includes('ECS')) setEditedInstanceType('0.25 vCPU / 0.5 GB');
                    }}
                    className="w-full bg-white border border-slate-200 rounded-lg p-2 text-slate-800 font-medium"
                  >
                    <option value="Amazon EC2 (Docker Runtime)">Amazon EC2 (Docker Runtime)</option>
                    <option value="AWS ECS Fargate">AWS ECS Fargate (Serverless Container)</option>
                    <option value="AWS Lambda">AWS Lambda (Serverless Function)</option>
                  </select>
                </div>

                <div>
                  <label className="text-slate-500 block mb-1">Instance / Task Sizing</label>
                  <select
                    value={editedInstanceType}
                    onChange={(e) => setEditedInstanceType(e.target.value)}
                    className="w-full bg-white border border-slate-200 rounded-lg p-2 text-slate-800 font-medium font-mono"
                  >
                    {editedComputeService.includes('EC2') ? (
                      <>
                        <option value="t4g.nano">t4g.nano (2 vCPU, 0.5 GB) — $3.06/mo</option>
                        <option value="t4g.micro">t4g.micro (2 vCPU, 1 GB) — $6.12/mo (Free Tier)</option>
                        <option value="t4g.small">t4g.small (2 vCPU, 2 GB) — $12.24/mo</option>
                        <option value="t3.micro">t3.micro (2 vCPU, 1 GB x86) — $7.60/mo</option>
                        <option value="t3.medium">t3.medium (2 vCPU, 4 GB x86) — $30.40/mo</option>
                      </>
                    ) : editedComputeService.includes('ECS') ? (
                      <>
                        <option value="0.25 vCPU / 0.5 GB">0.25 vCPU / 0.5 GB RAM — $12.80/mo</option>
                        <option value="0.5 vCPU / 1 GB">0.5 vCPU / 1 GB RAM — $25.60/mo</option>
                        <option value="1 vCPU / 2 GB">1 vCPU / 2 GB RAM — $51.20/mo</option>
                        <option value="2 vCPU / 4 GB">2 vCPU / 4 GB RAM — $102.40/mo</option>
                      </>
                    ) : (
                      <option value="Serverless">Serverless 512 MB — $1.50/mo</option>
                    )}
                  </select>
                </div>

                <div className="flex items-center justify-between pt-1">
                  <span className="text-slate-500">Instance Count:</span>
                  <select
                    value={editedMinCapacity}
                    onChange={(e) => setEditedMinCapacity(Number(e.target.value))}
                    className="bg-white border border-slate-200 rounded-lg px-2 py-1 text-slate-800 font-medium"
                  >
                    <option value={1}>1 Instance</option>
                    <option value={2}>2 Instances (Dual-AZ)</option>
                    <option value={3}>3 Instances (HA Fleet)</option>
                  </select>
                </div>
              </div>
            </div>

            {/* 2. Networking & Ingress Card */}
            <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs font-bold text-slate-900">
                  <Globe className="w-4 h-4 text-slate-600" />
                  Networking &amp; Ingress
                </div>
                <span className="text-[10px] font-semibold text-slate-700 bg-slate-200/60 px-2 py-0.5 rounded">
                  ${sizingOutput.networking?.monthly_cost || 0}/mo
                </span>
              </div>

              <div className="space-y-2 text-xs">
                <div>
                  <label className="text-slate-500 block mb-1">Ingress Mode</label>
                  <select
                    value={editedAlbEnabled ? 'alb' : 'eip'}
                    onChange={(e) => setEditedAlbEnabled(e.target.value === 'alb')}
                    className="w-full bg-white border border-slate-200 rounded-lg p-2 text-slate-800 font-medium"
                  >
                    <option value="eip">Direct Elastic IP (No ALB) — $0.00/mo (Recommended in DEV)</option>
                    <option value="alb">Application Load Balancer (ALB) — $16.50/mo</option>
                  </select>
                </div>


              </div>
            </div>

            {/* 3. Database Layer Card */}
            <div className="p-4 rounded-xl border border-indigo-200 bg-indigo-50/20 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs font-bold text-indigo-900">
                  <Database className="w-4 h-4 text-indigo-600" />
                  Data Layer
                </div>
                <span className="text-[10px] font-semibold text-indigo-700 bg-indigo-100/60 px-2 py-0.5 rounded">
                  ${sizingOutput.database?.monthly_cost || 0}/mo
                </span>
              </div>

              <div className="space-y-2 text-xs">
                <div>
                  <label className="text-slate-500 block mb-1">Database Service</label>
                  <select
                    value={editedDatabaseService}
                    onChange={(e) => setEditedDatabaseService(e.target.value)}
                    className="w-full bg-white border border-slate-200 rounded-lg p-2 text-slate-800 font-medium"
                  >
                    <option value="None">None / Local SQLite ($0.00/mo)</option>
                    <option value="Amazon RDS PostgreSQL (db.t4g.micro)">Amazon RDS PostgreSQL (db.t4g.micro) — $8.60/mo</option>
                    <option value="Amazon RDS PostgreSQL (db.t4g.small)">Amazon RDS PostgreSQL (db.t4g.small) — $17.20/mo</option>
                    <option value="Amazon Aurora Serverless v2">Amazon Aurora Serverless v2 — $48.00/mo</option>
                  </select>
                </div>

              </div>
            </div>

            {/* 4. Cache Service Card */}
            <div className="p-4 rounded-xl border border-purple-200 bg-purple-50/20 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs font-bold text-purple-900">
                  <Zap className="w-4 h-4 text-purple-600" />
                  In-Memory Cache
                </div>
                <span className="text-[10px] font-semibold text-purple-700 bg-purple-100/60 px-2 py-0.5 rounded">
                  ${sizingOutput.cache?.monthly_cost || 0}/mo
                </span>
              </div>

              <div className="space-y-2 text-xs">
                <div>
                  <label className="text-slate-500 block mb-1">Cache Service</label>
                  <select
                    value={editedCacheService}
                    onChange={(e) => setEditedCacheService(e.target.value)}
                    className="w-full bg-white border border-slate-200 rounded-lg p-2 text-slate-800 font-medium"
                  >
                    <option value="None">None ($0.00/mo)</option>
                    <option value="Amazon ElastiCache Redis (cache.t4g.micro)">Amazon ElastiCache Redis (cache.t4g.micro) — $13.20/mo</option>
                    <option value="Amazon ElastiCache Redis (cache.t4g.small)">Amazon ElastiCache Redis (cache.t4g.small) — $36.40/mo</option>
                  </select>
                </div>
              </div>
            </div>

            {/* 5. Static Assets & CDN Card */}
            <div className="p-4 rounded-xl border border-amber-200 bg-amber-50/20 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs font-bold text-amber-900">
                  <Layers className="w-4 h-4 text-amber-600" />
                  Frontend &amp; CDN
                </div>
                <span className="text-[10px] font-semibold text-amber-700 bg-amber-100/60 px-2 py-0.5 rounded">
                  ${sizingOutput.frontend_hosting?.monthly_cost || 0}/mo
                </span>
              </div>

              <div className="space-y-2 text-xs">
                <div>
                  <label className="text-slate-500 block mb-1">CDN Distribution</label>
                  <select
                    value={editedCdnEnabled ? 'cdn' : 'none'}
                    onChange={(e) => setEditedCdnEnabled(e.target.value === 'cdn')}
                    className="w-full bg-white border border-slate-200 rounded-lg p-2 text-slate-800 font-medium"
                  >
                    <option value="none">None ($0.00/mo)</option>
                    <option value="cdn">Amazon CloudFront + S3 Origin — $1.80/mo</option>
                  </select>
                </div>
              </div>
            </div>

            {/* 6. Quick Cost Breakdown Summary */}
            <div className="p-4 rounded-xl border border-slate-200 bg-white space-y-2">
              <div className="text-xs font-bold text-slate-900 border-b border-slate-100 pb-1.5 flex items-center justify-between">
                <span>Cost Item Breakdown</span>
                <span className="text-emerald-700 font-bold">${sizingOutput.monthly_cost_estimate_usd?.total_estimated_monthly_usd || 0}/mo</span>
              </div>
              <div className="space-y-1 text-xs text-slate-600">
                <div className="flex justify-between"><span>Compute:</span> <strong className="font-mono">${sizingOutput.monthly_cost_estimate_usd?.compute || 0}/mo</strong></div>
                <div className="flex justify-between"><span>Networking:</span> <strong className="font-mono">${sizingOutput.monthly_cost_estimate_usd?.networking || 0}/mo</strong></div>
                <div className="flex justify-between"><span>Database:</span> <strong className="font-mono">${sizingOutput.monthly_cost_estimate_usd?.database || 0}/mo</strong></div>
                <div className="flex justify-between"><span>Cache:</span> <strong className="font-mono">${sizingOutput.monthly_cost_estimate_usd?.cache || 0}/mo</strong></div>
                <div className="flex justify-between"><span>CDN / Storage:</span> <strong className="font-mono">${sizingOutput.monthly_cost_estimate_usd?.frontend || 0}/mo</strong></div>
              </div>
            </div>
          </div>

          {/* Compatibility Analysis Notes */}
          {sizingOutput.compatibility_notes && sizingOutput.compatibility_notes.length > 0 && (
            <div className="p-4 rounded-xl bg-blue-50/60 border border-blue-200 space-y-2">
              <div className="flex items-center gap-2 text-xs font-bold text-blue-900">
                <ShieldCheck className="w-4 h-4 text-blue-600" />
                Architectural Compatibility &amp; Analysis
              </div>
              <ul className="list-disc list-inside text-xs text-blue-800 space-y-1">
                {sizingOutput.compatibility_notes.map((note, idx) => (
                  <li key={idx}>{note}</li>
                ))}
              </ul>
            </div>
          )}

          {/* FinOps Optimizations List */}
          {sizingOutput.finops_optimizations && sizingOutput.finops_optimizations.length > 0 && (
            <div className="p-4 rounded-xl bg-amber-50/60 border border-amber-200 space-y-2">
              <div className="flex items-center gap-2 text-xs font-bold text-amber-900">
                <DollarSign className="w-4 h-4 text-amber-600" />
                FinOps Cost Optimizations Applied
              </div>
              <ul className="list-disc list-inside text-xs text-amber-800 space-y-1">
                {sizingOutput.finops_optimizations.map((tip, idx) => (
                  <li key={idx}>{tip}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Bottom Dual Action Bar */}
          <div className="pt-4 border-t border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            {/* Button 1: Analyze & Recalculate What the User Edited */}
            <button
              type="button"
              onClick={handleRecalculateSizing}
              disabled={isRecalculating}
              className="px-5 py-2.5 bg-slate-800 hover:bg-slate-900 text-white text-xs font-semibold rounded-lg shadow-xs transition disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {isRecalculating ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  Recalculating Architecture...
                </>
              ) : (
                <>
                  <RefreshCw className="w-3.5 h-3.5" />
                  Recalculate Architecture
                </>
              )}
            </button>

            {/* Button 2: Proceed to Cloud Architecture Studio */}
            <button
              type="button"
              onClick={handleProceedToModule4}
              className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg shadow-xs transition flex items-center justify-center gap-2"
            >
              <span>Proceed to Cloud Architecture Studio</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
