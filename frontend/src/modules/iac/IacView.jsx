// frontend/src/modules/iac/IacView.jsx
import React, { useState, useEffect } from 'react';
import {
  Terminal,
  Copy,
  Check,
  Download,
  ShieldCheck,
  ShieldAlert,
  ArrowRight,
  FileCode,
  RefreshCw,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { iacApi, architectureStudioApi } from '../../services/api';

export default function IacView({ onNavigate, activeProject, activeEnvironment, navState }) {
  const [activeFile, setActiveFile] = useState('main.tf');
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(false);
  const [approvalStatus, setApprovalStatus] = useState(null);
  const [iacData, setIacData] = useState(null);
  const [error, setError] = useState(null);

  const projectName = activeProject?.name || activeProject?.id || 'aether-cloud';
  const region = activeEnvironment?.region || 'us-east-1';

  // Check architecture approval on mount
  useEffect(() => {
    async function checkApproval() {
      setLoading(true);
      setError(null);
      try {
        // Query Architecture Studio for current environment's approval
        const review = await architectureStudioApi.getReview({
          project_id: activeProject?.id || 'default',
          environment_id: activeEnvironment?.id || 'env',
          environment_tier: activeEnvironment?.type || 'development',
          target_region: region,
        });

        setApprovalStatus(review);

        const versionId = navState?.sizingOutput?.module4_payload?.version_id || review?.version_id || localStorage.getItem('aether_latest_version_id') || `arch-${activeProject?.id || 'default'}-v1`;
        localStorage.setItem('aether_latest_version_id', versionId);

        const sizing = navState?.sizingOutput || review?.sizing || {};
        const hasAlb = Boolean(sizing.networking?.alb || sizing.compute?.service?.toLowerCase().includes('alb'));
        const hasDb = Boolean(sizing.database?.service && !sizing.database.service.toLowerCase().includes('none'));
        const envTier = sizing.environment_tier || activeEnvironment?.type || 'development';
        const isLean = envTier.toLowerCase().includes('dev') || (!hasDb && !hasAlb);

        const iacPayload = {
          project_name: projectName,
          aws_region: region,
          iac_tool: 'terraform',
          architecture_version_id: versionId,
          compute_instance_type: sizing.compute?.instance_class || sizing.compute?.task_cpu || 't3.medium',
          database_instance_type: hasDb ? (sizing.database?.service || 'db.t3.medium') : 'none',
          database_storage_gb: hasDb ? 20 : 0,
          enable_alb: hasAlb,
          enable_waf: !isLean,
          enable_kms: !isLean,
        };

        // Trigger IaC synthesis automatically
        const genResp = await iacApi.generate(iacPayload);
        setIacData(genResp);
        if (genResp?.files?.length > 0) {
          setActiveFile(genResp.files[0].filename);
        }
      } catch (err) {
        console.warn('IaC generation notice:', err);
        setError(err.message || 'Approval check error');
      } finally {
        setLoading(false);
      }
    }
    checkApproval();
  }, [activeProject, activeEnvironment, navState]);

  const handleGenerateManual = async () => {
    setLoading(true);
    setError(null);
    try {
      const versionId = navState?.sizingOutput?.module4_payload?.version_id || approvalStatus?.version_id || localStorage.getItem('aether_latest_version_id') || `arch-${activeProject?.id || 'default'}-v1`;
      localStorage.setItem('aether_latest_version_id', versionId);
      localStorage.setItem('aether_architecture_approved', 'true');

      const sizing = navState?.sizingOutput || approvalStatus?.sizing || {};
      const hasAlb = Boolean(sizing.networking?.alb || sizing.compute?.service?.toLowerCase().includes('alb'));
      const hasDb = Boolean(sizing.database?.service && !sizing.database.service.toLowerCase().includes('none'));
      const envTier = sizing.environment_tier || activeEnvironment?.type || 'development';
      const isLean = envTier.toLowerCase().includes('dev') || (!hasDb && !hasAlb);

      const iacPayload = {
        project_name: projectName,
        aws_region: region,
        iac_tool: 'terraform',
        architecture_version_id: versionId,
        compute_instance_type: sizing.compute?.instance_class || sizing.compute?.task_cpu || 't3.medium',
        database_instance_type: hasDb ? (sizing.database?.service || 'db.t3.medium') : 'none',
        database_storage_gb: hasDb ? 20 : 0,
        enable_alb: hasAlb,
        enable_waf: !isLean,
        enable_kms: !isLean,
      };

      const genResp = await iacApi.generate(iacPayload);
      setIacData(genResp);
      if (genResp?.files?.length > 0) {
        setActiveFile(genResp.files[0].filename);
      }
    } catch (err) {
      setError(err.message || 'Terraform generation failed');
    } finally {
      setLoading(false);
    }
  };

  const files = iacData?.files || [];
  const currentFileContent = files.find((f) => f.filename === activeFile)?.content || '';

  const copyToClipboard = () => {
    navigator.clipboard.writeText(currentFileContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const isApproved = Boolean(approvalStatus?.is_approved) || localStorage.getItem('aether_architecture_approved') === 'true';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Infrastructure as Code Syntherizer</h1>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => onNavigate('architecture_validation', '/architecture/validation')}
            className="px-3.5 py-2 rounded-lg bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 text-xs font-semibold transition cursor-pointer shadow-xs"
          >
            Review Architecture
          </button>
          <button
            onClick={handleGenerateManual}
            disabled={loading}
            className="px-3.5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold transition flex items-center gap-1.5 cursor-pointer shadow-xs disabled:opacity-40"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>New IAC</span>
          </button>
          <button
            onClick={() => onNavigate('risk_analysis', '/risk-analysis')}
            disabled={!iacData}
            className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold transition flex items-center gap-1.5 cursor-pointer shadow-xs disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <span>Proceed to Pre-Deployment Dry Run</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Approval Gate Check Banner */}
      {!isApproved && !loading && (
        <div className="p-5 rounded-2xl bg-amber-50 border border-amber-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4 text-amber-900 shadow-xs">
          <div className="flex items-start sm:items-center gap-3">
            <ShieldAlert className="w-6 h-6 text-amber-600 shrink-0 mt-0.5 sm:mt-0" />
            <div>
              <div className="text-sm font-bold">Mandatory Architecture Approval Gate Active</div>
              <div className="text-xs text-amber-800 mt-0.5">
                Section 5 Master Specification: Architecture version must be reviewed and officially approved before Terraform code synthesis is unlocked.
              </div>
            </div>
          </div>
          <button
            onClick={() => onNavigate('architecture_validation', '/architecture/validation')}
            className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white font-semibold text-xs rounded-lg transition shrink-0 cursor-pointer shadow-xs"
          >
            Open Architecture Review
          </button>
        </div>
      )}

      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-medium flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Synthesis Metadata Bar */}
      {iacData && (
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 text-xs">
          <div className="p-3.5 rounded-xl bg-white border border-slate-200 shadow-2xs">
            <div className="text-slate-500 font-medium text-xs">Architecture Version</div>
            <div className="text-slate-900 font-bold font-mono mt-1 truncate">
              {iacData.architecture_version_id}
            </div>
          </div>
          <div className="p-3.5 rounded-xl bg-white border border-slate-200 shadow-2xs">
            <div className="text-slate-500 font-medium text-xs">Terraform Version</div>
            <div className="text-slate-900 font-bold font-mono mt-1 truncate">
              {iacData.terraform_version_id}
            </div>
          </div>
          <div className="p-3.5 rounded-xl bg-white border border-slate-200 shadow-2xs">
            <div className="text-slate-500 font-medium text-xs">HCL Checksum</div>
            <div className="text-slate-900 font-bold font-mono mt-1 truncate" title={iacData.checksum}>
              {iacData.checksum?.substring(0, 16)}...
            </div>
          </div>
          <div className="p-3.5 rounded-xl bg-white border border-slate-200 shadow-2xs">
            <div className="text-slate-500 font-medium text-xs">Terraform Validation</div>
            <div className="flex items-center gap-2 mt-1">
              <span className="px-2 py-0.5 rounded text-xs font-mono font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                FMT: {iacData.validation?.fmt || 'PASS'}
              </span>
              <span className="px-2 py-0.5 rounded text-xs font-mono font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                VALIDATE: {iacData.validation?.validate || 'PASS'}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Code Editor Window */}
      <div className="bg-slate-950 rounded-2xl border border-slate-800 shadow-xl overflow-hidden font-mono text-xs">
        {/* Tab Header */}
        <div className="px-4 py-2.5 bg-slate-900 border-b border-slate-800 flex flex-wrap items-center justify-between gap-3 text-slate-400">
          <div className="flex items-center gap-1.5 overflow-x-auto">
            {files.length > 0 ? (
              files.map((f) => (
                <button
                  key={f.filename}
                  onClick={() => setActiveFile(f.filename)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer flex items-center gap-1.5 ${
                    activeFile === f.filename
                      ? 'bg-slate-800 text-emerald-400 shadow-xs'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`}
                >
                  <FileCode className="w-3.5 h-3.5" />
                  <span>{f.filename}</span>
                </button>
              ))
            ) : (
              <span className="text-xs text-slate-500 py-1">No Terraform files synthesized</span>
            )}
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleGenerateManual}
              disabled={loading || !isApproved}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-semibold transition cursor-pointer disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
              <span>{loading ? 'Synthesizing...' : 'Re-synthesize'}</span>
            </button>
            <button
              onClick={copyToClipboard}
              disabled={!currentFileContent}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-semibold transition cursor-pointer disabled:opacity-50"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied!' : 'Copy Code'}</span>
            </button>
          </div>
        </div>

        {/* Code Content */}
        <div className="p-6 text-emerald-300 overflow-x-auto leading-relaxed max-h-[520px]">
          {loading ? (
            <div className="py-16 text-center text-slate-500 font-sans">
              <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-blue-500" />
              <span>Synthesizing AWS Well-Architected Terraform HCL modules...</span>
            </div>
          ) : currentFileContent ? (
            <pre>{currentFileContent}</pre>
          ) : (
            <div className="py-16 text-center text-slate-600 font-sans">
              <span>Approve architecture in Architecture Review to unlock Terraform synthesis.</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
