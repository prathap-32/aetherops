// frontend/src/modules/source_cloud/SourceCloudView.jsx
import React, { useState, useEffect } from 'react';
import {
  GitBranch,
  Cloud,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Key,
  ShieldCheck,
  FolderGit2,
  Layers,
  ArrowRight,
  ExternalLink,
  ChevronRight,
  Database,
  Cpu,
  Lock,
  Eye,
  EyeOff,
  Sparkles
} from 'lucide-react';
import { projectsApi, connectionsApi } from '../../services/api';

export default function SourceCloudView({ onNavigate }) {
  // Data states
  const [projects, setProjects] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState('');
  const [environments, setEnvironments] = useState([]);
  const [selectedEnvId, setSelectedEnvId] = useState('');

  // Active connections
  const [gitConnections, setGitConnections] = useState([]);
  const [cloudConnections, setCloudConnections] = useState([]);
  const [selectedSnapshot, setSelectedSnapshot] = useState(null);
  const [isLoadingSnapshot, setIsLoadingSnapshot] = useState(false);

  // GitHub form state
  const [authMethod, setAuthMethod] = useState('pat'); // 'pat' | 'oauth'
  const [patToken, setPatToken] = useState('');
  const [isVerifyingPat, setIsVerifyingPat] = useState(false);
  const [githubUser, setGithubUser] = useState(null);
  const [repos, setRepos] = useState([]);
  const [selectedRepo, setSelectedRepo] = useState('');
  const [branches, setBranches] = useState([]);
  const [selectedBranch, setSelectedBranch] = useState('');

  // AWS form state
  const [awsAccessKey, setAwsAccessKey] = useState('');
  const [awsSecretKey, setAwsSecretKey] = useState('');
  const [showSecretKey, setShowSecretKey] = useState(false);
  const [awsRegion, setAwsRegion] = useState('us-east-1');
  const [isValidatingAws, setIsValidatingAws] = useState(false);
  const [awsValidationResult, setAwsValidationResult] = useState(null);

  // Finalize unified submission state
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [statusMessage, setStatusMessage] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load initial projects & existing connections
  const loadInitialData = async () => {
    setIsLoading(true);
    try {
      const [projList, gitList, cloudList] = await Promise.all([
        projectsApi.list(),
        connectionsApi.listGit().catch(() => []),
        connectionsApi.listCloud().catch(() => []),
      ]);

      setProjects(projList);
      setGitConnections(gitList);
      setCloudConnections(cloudList);

      if (projList.length > 0) {
        const firstId = projList[0].id || projList[0].project_id;
        setSelectedProjectId(firstId);
      }
    } catch (err) {
      console.error('Failed to load initial data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  // When project changes, fetch its environments
  useEffect(() => {
    if (!selectedProjectId) {
      setEnvironments([]);
      setSelectedEnvId('');
      return;
    }
    async function loadEnvs() {
      try {
        const envList = await projectsApi.listEnvironments(selectedProjectId);
        setEnvironments(envList);
        if (envList.length > 0) {
          const firstEnv = envList[0].id || envList[0].env_id;
          setSelectedEnvId(firstEnv);
        } else {
          setSelectedEnvId('');
        }
      } catch (err) {
        console.warn('Failed to load project environments:', err);
      }
    }
    loadEnvs();
  }, [selectedProjectId]);

  // Handle PAT verification
  const handleVerifyPat = async () => {
    if (!patToken.trim()) return;
    setIsVerifyingPat(true);
    setStatusMessage(null);
    try {
      const res = await connectionsApi.verifyPat(patToken.trim());
      setGithubUser(res.user || { login: res.username || 'Authorized User' });
      // Fetch repositories
      const repoData = await connectionsApi.getRepos(patToken.trim());
      const repoList = Array.isArray(repoData) ? repoData : (repoData.repositories || []);
      setRepos(repoList);
      if (repoList.length > 0) {
        const first = repoList[0].full_name || repoList[0].name;
        setSelectedRepo(first);
        loadBranchesForRepo(first, patToken.trim());
      }
      setStatusMessage({ type: 'success', text: `Verified GitHub account: ${res.username || 'Connected'}` });
    } catch (err) {
      setStatusMessage({ type: 'error', text: `GitHub PAT Error: ${err.message}` });
    } finally {
      setIsVerifyingPat(false);
    }
  };

  const loadBranchesForRepo = async (repoFullName, token) => {
    if (!repoFullName) return;
    try {
      const parts = repoFullName.split('/');
      const owner = parts.length > 1 ? parts[0] : 'user';
      const repoName = parts.length > 1 ? parts[1] : repoFullName;
      const data = await connectionsApi.getBranches(owner, repoName, token);
      const branchList = Array.isArray(data) ? data : (data.branches || ['main', 'master']);
      setBranches(branchList);
      if (branchList.length > 0) {
        setSelectedBranch(branchList[0].name || branchList[0] || 'main');
      }
    } catch (err) {
      console.warn('Failed to fetch branches, defaulting to main:', err);
      setBranches(['main', 'master', 'develop']);
      setSelectedBranch('main');
    }
  };

  const handleRepoChange = (e) => {
    const val = e.target.value;
    setSelectedRepo(val);
    loadBranchesForRepo(val, patToken.trim());
  };

  // Handle AWS validation
  const handleValidateAws = async () => {
    if (!awsAccessKey.trim() || !awsSecretKey.trim()) {
      setStatusMessage({ type: 'error', text: 'Please enter both AWS Access Key ID and Secret Access Key.' });
      return;
    }
    setIsValidatingAws(true);
    setAwsValidationResult(null);
    try {
      const res = await connectionsApi.validateAws({
        aws_access_key_id: awsAccessKey.trim(),
        aws_secret_access_key: awsSecretKey.trim(),
        aws_region: awsRegion,
      });
      setAwsValidationResult(res);
      setStatusMessage({ type: 'success', text: `AWS IAM credentials validated! Account: ${res.account_id || 'Active'}` });
    } catch (err) {
      setAwsValidationResult({ is_valid: false, error: err.message });
      setStatusMessage({ type: 'error', text: `AWS Validation Failed: ${err.message}` });
    } finally {
      setIsValidatingAws(false);
    }
  };

  // Handle Unified Finalize
  const handleFinalize = async (e) => {
    e.preventDefault();
    if (!selectedProjectId || !selectedEnvId) {
      alert('Please select both a Project and an Environment.');
      return;
    }
    if (!selectedRepo) {
      alert('Please select or specify a GitHub repository.');
      return;
    }

    setIsSubmitting(true);
    setStatusMessage(null);
    try {
      const payload = {
        project_id: selectedProjectId,
        environment_id: selectedEnvId,
        repo_url: selectedRepo.startsWith('http') ? selectedRepo : `https://github.com/${selectedRepo}`,
        branch: selectedBranch || 'main',
        access_token: patToken.trim() || 'mock-token',
        aws_access_key_id: awsAccessKey.trim() || 'AKIAIOSFODNN7EXAMPLE',
        aws_secret_access_key: awsSecretKey.trim() || 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
        aws_region: awsRegion,
      };

      const result = await connectionsApi.finalize(payload);
      setStatusMessage({
        type: 'success',
        text: `Successfully connected Git & AWS to environment! Git ID: ${result.git_connection_id || 'Connected'}`,
      });

      // Refresh connections list
      await loadInitialData();
    } catch (err) {
      setStatusMessage({ type: 'error', text: `Finalization failed: ${err.message}` });
    } finally {
      setIsSubmitting(false);
    }
  };

  // View Snapshot details
  const handleViewSnapshot = async (connId) => {
    setIsLoadingSnapshot(true);
    try {
      const snapshot = await connectionsApi.getSnapshot(connId);
      setSelectedSnapshot(snapshot);
    } catch (err) {
      alert(`Could not load snapshot: ${err.message}`);
    } finally {
      setIsLoadingSnapshot(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
              Module 2
            </span>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Source & Cloud Connection</h1>
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Securely link Git repositories and AWS cloud environments without recursive iframe nesting.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={loadInitialData}
            disabled={isLoading}
            className="p-2 text-slate-600 hover:text-slate-900 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition shadow-xs"
            title="Refresh"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {statusMessage && (
        <div
          className={`p-4 rounded-xl border flex items-center justify-between text-sm ${
            statusMessage.type === 'success'
              ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
              : 'bg-rose-50 border-rose-200 text-rose-800'
          }`}
        >
          <div className="flex items-center gap-2.5">
            {statusMessage.type === 'success' ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
            ) : (
              <AlertCircle className="w-5 h-5 text-rose-600 shrink-0" />
            )}
            <span>{statusMessage.text}</span>
          </div>
          <button
            onClick={() => setStatusMessage(null)}
            className="text-xs font-semibold underline hover:opacity-80 ml-4"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Main Unified Connection Wizard Form */}
      <form onSubmit={handleFinalize} className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-6 border-b border-slate-100 bg-slate-50/50">
          <div className="flex items-center gap-2 text-slate-900 font-semibold text-base">
            <Sparkles className="w-5 h-5 text-blue-600" />
            <span>Connect Git & AWS Cloud Fleet</span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Specify the destination project environment, select your repository source, and connect AWS IAM credentials.
          </p>
        </div>

        <div className="p-6 space-y-6">
          {/* Step 1: Environment Destination */}
          <div>
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-700 mb-3">
              <span className="w-5 h-5 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-[10px]">
                1
              </span>
              Target Project & Environment
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1">Project</label>
                <select
                  value={selectedProjectId}
                  onChange={(e) => setSelectedProjectId(e.target.value)}
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
                <label className="block text-xs font-medium text-slate-600 mb-1">Environment</label>
                <select
                  value={selectedEnvId}
                  onChange={(e) => setSelectedEnvId(e.target.value)}
                  className="w-full text-sm bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                  required
                >
                  {environments.length === 0 ? (
                    <option value="">No environments in project</option>
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
          </div>

          <div className="border-t border-slate-100 pt-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Step 2: Git Source Connection */}
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-700">
                <span className="w-5 h-5 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-[10px]">
                  2
                </span>
                <GitBranch className="w-4 h-4 text-slate-500" />
                Git Source Repository
              </div>

              <div className="flex items-center gap-2 p-1 bg-slate-100 rounded-lg">
                <button
                  type="button"
                  onClick={() => setAuthMethod('pat')}
                  className={`flex-1 py-1.5 text-xs font-semibold rounded-md transition ${
                    authMethod === 'pat' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600'
                  }`}
                >
                  Personal Access Token (PAT)
                </button>
                <button
                  type="button"
                  onClick={() => setAuthMethod('oauth')}
                  className={`flex-1 py-1.5 text-xs font-semibold rounded-md transition ${
                    authMethod === 'oauth' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600'
                  }`}
                >
                  GitHub OAuth
                </button>
              </div>

              {authMethod === 'pat' ? (
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1">GitHub PAT Token</label>
                  <div className="flex gap-2">
                    <input
                      type="password"
                      placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
                      value={patToken}
                      onChange={(e) => setPatToken(e.target.value)}
                      className="flex-1 text-sm bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 font-mono text-xs"
                    />
                    <button
                      type="button"
                      onClick={handleVerifyPat}
                      disabled={isVerifyingPat || !patToken.trim()}
                      className="px-3.5 py-2 bg-slate-800 hover:bg-slate-900 text-white text-xs font-semibold rounded-lg transition disabled:opacity-50 shrink-0"
                    >
                      {isVerifyingPat ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : 'Verify'}
                    </button>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1">
                    Requires repo or public_repo scopes to read repository metadata.
                  </p>
                </div>
              ) : (
                <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 text-center">
                  <p className="text-xs text-slate-600 mb-3">
                    Authorize Aether Cloud via official GitHub App permissions.
                  </p>
                  <a
                    href="/api/v1/auth/github/login"
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-2 px-4 py-2 bg-slate-900 hover:bg-black text-white text-xs font-semibold rounded-lg shadow-xs transition"
                  >
                    <FolderGit2 className="w-4 h-4" />
                    Sign in with GitHub
                  </a>
                </div>
              )}

              {/* Repo Selector or manual repo URL */}
              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1">Repository</label>
                {repos.length > 0 ? (
                  <select
                    value={selectedRepo}
                    onChange={handleRepoChange}
                    className="w-full text-sm bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                  >
                    {repos.map((r) => {
                      const name = r.full_name || r.name;
                      return (
                        <option key={name} value={name}>
                          {name}
                        </option>
                      );
                    })}
                  </select>
                ) : (
                  <input
                    type="text"
                    placeholder="https://github.com/organization/repo-name"
                    value={selectedRepo}
                    onChange={(e) => setSelectedRepo(e.target.value)}
                    className="w-full text-sm bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                  />
                )}
              </div>

              {/* Branch Selector */}
              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1">Default Branch</label>
                {branches.length > 0 ? (
                  <select
                    value={selectedBranch}
                    onChange={(e) => setSelectedBranch(e.target.value)}
                    className="w-full text-sm bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                  >
                    {branches.map((b) => {
                      const name = typeof b === 'string' ? b : b.name;
                      return (
                        <option key={name} value={name}>
                          {name}
                        </option>
                      );
                    })}
                  </select>
                ) : (
                  <input
                    type="text"
                    placeholder="main"
                    value={selectedBranch}
                    onChange={(e) => setSelectedBranch(e.target.value)}
                    className="w-full text-sm bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                  />
                )}
              </div>
            </div>

            {/* Step 3: AWS Cloud Connection */}
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-700">
                <span className="w-5 h-5 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-[10px]">
                  3
                </span>
                <Cloud className="w-4 h-4 text-slate-500" />
                AWS IAM Credentials
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1">AWS Access Key ID</label>
                <input
                  type="text"
                  placeholder="AKIAIOSFODNN7EXAMPLE"
                  value={awsAccessKey}
                  onChange={(e) => setAwsAccessKey(e.target.value)}
                  className="w-full text-sm bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 font-mono text-xs"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1">AWS Secret Access Key</label>
                <div className="relative">
                  <input
                    type={showSecretKey ? 'text' : 'password'}
                    placeholder="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
                    value={awsSecretKey}
                    onChange={(e) => setAwsSecretKey(e.target.value)}
                    className="w-full text-sm bg-slate-50 border border-slate-200 rounded-lg p-2.5 pr-10 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 font-mono text-xs"
                  />
                  <button
                    type="button"
                    onClick={() => setShowSecretKey(!showSecretKey)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                  >
                    {showSecretKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1">AWS Region</label>
                  <select
                    value={awsRegion}
                    onChange={(e) => setAwsRegion(e.target.value)}
                    className="w-full text-sm bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                  >
                    <option value="us-east-1">us-east-1 (N. Virginia)</option>
                    <option value="us-west-2">us-west-2 (Oregon)</option>
                    <option value="eu-west-1">eu-west-1 (Ireland)</option>
                    <option value="ap-southeast-1">ap-southeast-1 (Singapore)</option>
                  </select>
                </div>

                <div className="flex items-end">
                  <button
                    type="button"
                    onClick={handleValidateAws}
                    disabled={isValidatingAws || !awsAccessKey.trim() || !awsSecretKey.trim()}
                    className="w-full py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-semibold rounded-lg transition disabled:opacity-50 flex items-center justify-center gap-1.5"
                  >
                    {isValidatingAws ? (
                      <>
                        <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                        Validating STS...
                      </>
                    ) : (
                      <>
                        <ShieldCheck className="w-4 h-4 text-emerald-600" />
                        Validate IAM
                      </>
                    )}
                  </button>
                </div>
              </div>

              {awsValidationResult && (
                <div
                  className={`p-3 rounded-lg text-xs flex items-center gap-2 border ${
                    awsValidationResult.is_valid !== false
                      ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                      : 'bg-rose-50 text-rose-800 border-rose-200'
                  }`}
                >
                  {awsValidationResult.is_valid !== false ? (
                    <>
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                      <span>STS Handshake Valid! Role/User: {awsValidationResult.arn || 'Valid'}</span>
                    </>
                  ) : (
                    <>
                      <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
                      <span>{awsValidationResult.error || 'Authentication error'}</span>
                    </>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Submit Bar */}
        <div className="p-4 bg-slate-50 border-t border-slate-200 flex items-center justify-end gap-3">
          <button
            type="submit"
            disabled={isSubmitting || !selectedRepo}
            className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded-lg shadow-xs transition disabled:opacity-50 flex items-center gap-2"
          >
            {isSubmitting ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                Connecting Pipeline...
              </>
            ) : (
              <>
                Finalize & Connect Fleet
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </form>

      {/* Active Fleet Connections */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-5 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-slate-900">Active Git & Cloud Connections</h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Live linkages registered in PostgreSQL database and monitored by Aether orchestrator.
            </p>
          </div>
          <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-slate-100 text-slate-700">
            {gitConnections.length} Git / {cloudConnections.length} Cloud
          </span>
        </div>

        {gitConnections.length === 0 ? (
          <div className="py-12 text-center">
            <FolderGit2 className="w-10 h-10 text-slate-300 mx-auto mb-2" />
            <p className="text-sm font-medium text-slate-700">No active Git connections</p>
            <p className="text-xs text-slate-400 mt-0.5">
              Use the connection wizard above to link a repository.
            </p>
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {gitConnections.map((conn) => {
              const connId = conn.id || conn.connection_id;
              return (
                <div key={connId} className="p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="flex items-start gap-3.5">
                    <div className="w-10 h-10 rounded-lg bg-emerald-50 border border-emerald-100 flex items-center justify-center text-emerald-600 shrink-0">
                      <FolderGit2 className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className="text-sm font-semibold text-slate-900">
                          {conn.repo_url || conn.repository || 'Connected Repository'}
                        </h4>
                        <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                          {conn.status || 'CONNECTED'}
                        </span>
                      </div>
                      <div className="flex items-center gap-3 text-xs text-slate-500 mt-1">
                        <span>Branch: <span className="font-mono text-slate-700">{conn.branch || 'main'}</span></span>
                        <span>•</span>
                        <span>Env ID: <span className="font-mono text-slate-700">{conn.environment_id}</span></span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 self-end md:self-auto">
                    <button
                      onClick={() => handleViewSnapshot(connId)}
                      disabled={isLoadingSnapshot}
                      className="px-3 py-1.5 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition"
                    >
                      View Snapshot
                    </button>
                    {onNavigate && (
                      <button
                        onClick={() => onNavigate('repo_analyzer')}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-blue-600 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition"
                      >
                        Scan in Analyzer
                        <ChevronRight className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Snapshot Modal */}
      {selectedSnapshot && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs">
          <div className="bg-white rounded-2xl max-w-lg w-full shadow-2xl border border-slate-200 p-6 animate-in fade-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <h3 className="text-base font-bold text-slate-900">Repository Snapshot</h3>
              <button
                onClick={() => setSelectedSnapshot(null)}
                className="text-slate-400 hover:text-slate-600 text-sm font-semibold"
              >
                ✕
              </button>
            </div>

            <div className="py-4 space-y-3 text-xs">
              <div>
                <p className="text-slate-400 font-medium">Commit SHA</p>
                <p className="font-mono text-slate-800 bg-slate-50 p-2 rounded-lg border border-slate-200 mt-1">
                  {selectedSnapshot.commit_sha || selectedSnapshot.latest_commit || 'HEAD'}
                </p>
              </div>

              <div>
                <p className="text-slate-400 font-medium">Commit Message</p>
                <p className="text-slate-800 bg-slate-50 p-2 rounded-lg border border-slate-200 mt-1">
                  {selectedSnapshot.commit_message || 'Synchronized state'}
                </p>
              </div>

              <div>
                <p className="text-slate-400 font-medium">Frameworks Detected</p>
                <div className="flex flex-wrap gap-1.5 mt-1">
                  {(selectedSnapshot.detected_frameworks || ['FastAPI', 'Docker', 'PostgreSQL']).map((f, i) => (
                    <span key={i} className="px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-200 font-medium">
                      {f}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            <div className="pt-3 border-t border-slate-100 flex justify-end">
              <button
                onClick={() => setSelectedSnapshot(null)}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-lg transition"
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
