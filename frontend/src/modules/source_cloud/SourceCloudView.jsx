// frontend/src/modules/source_cloud/SourceCloudView.jsx
import React, { useState, useEffect, useRef } from 'react';
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
  ChevronDown,
  Database,
  Cpu,
  Lock,
  Eye,
  EyeOff,
  Sparkles,
  Search,
  Globe,
  Check,
  X
} from 'lucide-react';
import { projectsApi, connectionsApi } from '../../services/api';
import { AWS_REGIONS_39 } from '../../constants/awsRegions';

export default function SourceCloudView({
  onNavigate,
  activeProject,
  activeEnvironment,
  navState,
}) {
  const targetProjectId = navState?.projectId || activeProject?.id || activeProject?.project_id || '';
  const targetEnvId = navState?.environmentId || activeEnvironment?.id || activeEnvironment?.env_id || '';

  // Data states
  const [projects, setProjects] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState(targetProjectId);
  const [environments, setEnvironments] = useState([]);
  const [selectedEnvId, setSelectedEnvId] = useState(targetEnvId);

  // Active connections
  const [gitConnections, setGitConnections] = useState([]);
  const [cloudConnections, setCloudConnections] = useState([]);
  const [selectedSnapshot, setSelectedSnapshot] = useState(null);
  const [isLoadingSnapshot, setIsLoadingSnapshot] = useState(false);

  // GitHub form state
  const [authMethod, setAuthMethod] = useState('pat'); // 'pat' | 'oauth'
  const [patToken, setPatToken] = useState('');
  const [isVerifyingPat, setIsVerifyingPat] = useState(false);
  const [isConnectingOAuth, setIsConnectingOAuth] = useState(false);
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

  // AWS 39-Region Searchable Dropdown state
  const [regionSearch, setRegionSearch] = useState('');
  const [isRegionDropdownOpen, setIsRegionDropdownOpen] = useState(false);
  const regionDropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (regionDropdownRef.current && !regionDropdownRef.current.contains(e.target)) {
        setIsRegionDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const filteredRegions = AWS_REGIONS_39.filter((r) => {
    if (!regionSearch.trim()) return true;
    const q = regionSearch.toLowerCase();
    return (
      r.value.toLowerCase().includes(q) ||
      r.label.toLowerCase().includes(q) ||
      (r.group && r.group.toLowerCase().includes(q))
    );
  });

  const selectedRegionObj = AWS_REGIONS_39.find((r) => r.value === awsRegion) || {
    value: awsRegion,
    label: `${awsRegion} (Global)`,
    group: 'AWS Global'
  };

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
        const matched = targetProjectId && projList.find(p => (p.id || p.project_id) === targetProjectId);
        const firstId = matched ? (matched.id || matched.project_id) : (projList[0].id || projList[0].project_id);
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
          const matchedEnv = targetEnvId && envList.find(e => (e.id || e.env_id) === targetEnvId);
          setSelectedEnvId(matchedEnv ? (matchedEnv.id || matchedEnv.env_id) : (envList[0].id || envList[0].env_id));
        } else {
          setSelectedEnvId('');
        }
      } catch (err) {
        console.warn('Failed to load project environments:', err);
      }
    }
    loadEnvs();
  }, [selectedProjectId, targetEnvId]);

  // Reusable repository loader
  const loadUserRepos = async (token) => {
    try {
      const repoData = await connectionsApi.getRepos(token);
      const repoList = Array.isArray(repoData) ? repoData : (repoData.repos || repoData.repositories || []);
      setRepos(repoList);
      if (repoList.length > 0) {
        const first = repoList[0].full_name || repoList[0].name;
        setSelectedRepo(first);
        loadBranchesForRepo(first, token);
      }
      return repoList;
    } catch (err) {
      console.warn('Failed to load repositories:', err);
      return [];
    }
  };

  // Listen for OAuth completion from popup or URL parameters
  useEffect(() => {
    const handleOAuthMessage = async (event) => {
      if (event.data && event.data.type === 'GITHUB_CONNECTION_SUCCESS') {
        setIsConnectingOAuth(false);
        const token = event.data.access_token || event.data.token;
        const user = event.data.user;
        if (token) {
          setPatToken(token);
          const ghUserObj = user || { login: 'developer' };
          setGithubUser(ghUserObj);
          setAuthMethod('oauth');
          setStatusMessage({
            type: 'success',
            text: `Successfully connected GitHub account @${ghUserObj.login || 'developer'} via OAuth!`,
          });
          await loadUserRepos(token);
        }
      }
    };

    window.addEventListener('message', handleOAuthMessage);

    // Also check URL parameters if redirected in full page
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('github_connected') === '1' && urlParams.get('gh_token')) {
      const token = urlParams.get('gh_token');
      const userLogin = urlParams.get('gh_user') || 'Connected User';
      setPatToken(token);
      setGithubUser({ login: userLogin });
      setAuthMethod('oauth');
      setStatusMessage({
        type: 'success',
        text: `Connected GitHub account: @${userLogin} via OAuth.`,
      });
      loadUserRepos(token);
      window.history.replaceState({}, document.title, window.location.pathname);
    }

    return () => window.removeEventListener('message', handleOAuthMessage);
  }, []);

  // Handle GitHub OAuth Popup
  const handleConnectGitHubOAuth = () => {
    setIsConnectingOAuth(true);
    setStatusMessage(null);
    const width = 600;
    const height = 700;
    const left = Math.max(0, (window.screen.width - width) / 2);
    const top = Math.max(0, (window.screen.height - height) / 2);
    window.open(
      '/api/v1/connections/github/login',
      'AetherOpsGitHubConnection',
      `width=${width},height=${height},top=${top},left=${left},scrollbars=yes,status=yes`
    );
  };

  // Handle PAT verification
  const handleVerifyPat = async () => {
    if (!patToken.trim()) return;
    setIsVerifyingPat(true);
    setStatusMessage(null);
    try {
      const res = await connectionsApi.verifyPat(patToken.trim());
      const userObj = res.user || {
        login: res.username || 'Authorized User',
        name: res.name || res.username,
        avatar_url: res.avatar_url,
      };
      setGithubUser(userObj);
      await loadUserRepos(patToken.trim());
      setStatusMessage({ type: 'success', text: `Verified GitHub account: @${res.username || userObj.login || 'Connected'}` });
    } catch (err) {
      const msg = err?.message || (typeof err === 'string' ? err : 'PAT verification failed');
      setStatusMessage({ type: 'error', text: `GitHub PAT Error: ${msg}` });
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
        access_key_id: awsAccessKey.trim(),
        secret_access_key: awsSecretKey.trim(),
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
        pat_token: patToken.trim() || 'mock-token',
        access_token: patToken.trim() || 'mock-token',
        access_key_id: awsAccessKey.trim() || 'AKIAIOSFODNN7EXAMPLE',
        secret_access_key: awsSecretKey.trim() || 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
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
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Source &amp; Cloud Connection</h1>
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Securely link Git repositories, verify IAM credentials, and configure target AWS cloud deployment providers.
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
              <span className="w-6 h-6 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-xs">
                1
              </span>
              Target Project &amp; Environment
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
                <span className="w-6 h-6 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-xs">
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

              {/* Connected GitHub Account Badge */}
              {githubUser && (
                <div className="flex items-center justify-between p-3 bg-emerald-50/80 border border-emerald-200/90 rounded-xl text-xs text-emerald-900 shadow-2xs">
                  <div className="flex items-center gap-2.5">
                    {githubUser.avatar_url ? (
                      <img src={githubUser.avatar_url} alt="" className="w-5 h-5 rounded-full border border-emerald-300" />
                    ) : (
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                    )}
                    <div>
                      <span className="font-semibold text-emerald-950">@{githubUser.login || githubUser.name || 'user'}</span>
                      <span className="text-[11px] text-emerald-700 ml-1.5">
                        {repos.length > 0 ? `(${repos.length} repositories loaded)` : '(Connected)'}
                      </span>
                    </div>
                  </div>
                  <span className="text-[10px] font-bold uppercase tracking-wider bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-md border border-emerald-200">
                    {authMethod === 'oauth' ? 'OAuth 2.0' : 'PAT'}
                  </span>
                </div>
              )}

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
                      className="px-3.5 py-2 bg-slate-800 hover:bg-slate-900 text-white text-xs font-semibold rounded-lg transition disabled:opacity-50 shrink-0 cursor-pointer"
                    >
                      {isVerifyingPat ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : 'Verify'}
                    </button>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1">
                    Requires repo or public_repo scopes to read repository metadata.
                  </p>
                </div>
              ) : (
                <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 text-center space-y-3">
                  <p className="text-xs text-slate-600">
                    Authorize AetherOps to securely read your GitHub repositories without generating manual access tokens.
                  </p>
                  <button
                    type="button"
                    onClick={handleConnectGitHubOAuth}
                    disabled={isConnectingOAuth}
                    className="inline-flex items-center gap-2 px-4 py-2 bg-slate-900 hover:bg-black text-white text-xs font-semibold rounded-lg shadow-2xs transition disabled:opacity-50 cursor-pointer"
                  >
                    {isConnectingOAuth ? (
                      <RefreshCw className="w-4 h-4 animate-spin" />
                    ) : (
                      <FolderGit2 className="w-4 h-4" />
                    )}
                    {isConnectingOAuth ? 'Connecting to GitHub...' : (githubUser && authMethod === 'oauth' ? 'Reconnect GitHub Account' : 'Connect with GitHub OAuth')}
                  </button>
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
                <span className="w-6 h-6 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-xs">
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

              {/* AWS Region Selector (Searchable across all 39 Global Regions) */}
              <div className="relative" ref={regionDropdownRef}>
                <div className="flex items-center justify-between mb-1">
                  <label className="block text-xs font-medium text-slate-600">
                    AWS Region ({AWS_REGIONS_39.length} Global Regions)
                  </label>
                  <span className="text-[10px] text-blue-600 font-medium">
                    {selectedRegionObj.group}
                  </span>
                </div>

                {/* Dropdown trigger button */}
                <button
                  type="button"
                  onClick={() => setIsRegionDropdownOpen(!isRegionDropdownOpen)}
                  className="w-full text-left text-sm bg-slate-50 hover:bg-slate-100/80 border border-slate-200 rounded-lg p-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 flex items-center justify-between transition"
                >
                  <div className="flex items-center gap-2 truncate">
                    <Globe className="w-4 h-4 text-blue-600 shrink-0" />
                    <span className="font-mono text-xs font-semibold text-slate-900">{awsRegion}</span>
                    <span className="text-slate-500 text-xs truncate">
                      · {selectedRegionObj.label.replace(`${awsRegion} `, '').replace(/[()]/g, '')}
                    </span>
                  </div>
                  <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform duration-200 shrink-0 ${isRegionDropdownOpen ? 'rotate-180' : ''}`} />
                </button>

                {/* Searchable Dropdown Popup */}
                {isRegionDropdownOpen && (
                  <div className="absolute z-50 left-0 right-0 top-full mt-1.5 bg-white border border-slate-200 rounded-xl shadow-xl overflow-hidden animate-in fade-in slide-in-from-top-1 duration-150 max-w-full">
                    <div className="p-2 border-b border-slate-100 bg-slate-50/80">
                      <div className="relative">
                        <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
                        <input
                          type="text"
                          autoFocus
                          placeholder="Search 39 regions (e.g. ap-south-1, Mumbai, us-east-1)..."
                          value={regionSearch}
                          onChange={(e) => setRegionSearch(e.target.value)}
                          className="w-full pl-8 pr-7 py-1.5 text-xs bg-white border border-slate-200 rounded-md text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                        />
                        {regionSearch && (
                          <button
                            type="button"
                            onClick={() => setRegionSearch('')}
                            className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                          >
                            <X className="w-3.5 h-3.5" />
                          </button>
                        )}
                      </div>
                      <div className="flex items-center justify-between mt-1 px-1 text-[10px] text-slate-400">
                        <span>Select deployment region</span>
                        <span>{filteredRegions.length} matches</span>
                      </div>
                    </div>

                    <div className="max-h-56 overflow-y-auto divide-y divide-slate-100">
                      {filteredRegions.length === 0 ? (
                        <div className="p-4 text-center text-xs text-slate-400">
                          No AWS regions found matching "{regionSearch}"
                        </div>
                      ) : (
                        filteredRegions.map((region) => {
                          const isSelected = region.value === awsRegion;
                          return (
                            <button
                              key={region.value}
                              type="button"
                              onClick={() => {
                                setAwsRegion(region.value);
                                setIsRegionDropdownOpen(false);
                                setRegionSearch('');
                              }}
                              className={`w-full text-left px-3 py-2 text-xs flex items-center justify-between hover:bg-blue-50/70 transition ${
                                isSelected ? 'bg-blue-50 font-medium text-blue-900' : 'text-slate-700'
                              }`}
                            >
                              <div className="flex flex-col min-w-0 pr-2">
                                <div className="flex items-center gap-1.5">
                                  <span className="font-mono font-semibold text-slate-900">{region.value}</span>
                                  <span className="text-[9px] px-1.5 py-0.2 rounded bg-slate-100 text-slate-600 font-sans">
                                    {region.group}
                                  </span>
                                </div>
                                <span className="text-[11px] text-slate-500 truncate mt-0.5">{region.label}</span>
                              </div>
                              {isSelected && <Check className="w-4 h-4 text-blue-600 shrink-0" />}
                            </button>
                          );
                        })
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Validate IAM Action */}
              <div>
                <button
                  type="button"
                  onClick={handleValidateAws}
                  disabled={isValidatingAws || !awsAccessKey.trim() || !awsSecretKey.trim()}
                  className="w-full py-2.5 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded-lg transition disabled:opacity-50 flex items-center justify-center gap-2 shadow-xs"
                >
                  {isValidatingAws ? (
                    <>
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                      Validating STS ({awsRegion})...
                    </>
                  ) : (
                    <>
                      <ShieldCheck className="w-4 h-4 text-emerald-400" />
                      Validate IAM Credentials (AWS STS)
                    </>
                  )}
                </button>
              </div>

              {awsValidationResult && (
                <div
                  className={`p-3 rounded-lg text-xs border ${
                    awsValidationResult.is_valid !== false && !awsValidationResult.error
                      ? 'bg-emerald-50 text-emerald-900 border-emerald-200'
                      : 'bg-rose-50 text-rose-900 border-rose-200'
                  }`}
                >
                  {awsValidationResult.is_valid !== false && !awsValidationResult.error ? (
                    <div className="space-y-1">
                      <div className="flex items-center gap-2 font-medium">
                        <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                        <span>AWS STS Validated · Account ID: <strong className="font-mono">{awsValidationResult.account_id}</strong></span>
                      </div>
                      <div className="pl-6 text-xs text-emerald-700 font-mono break-all">
                        Caller ARN: {awsValidationResult.arn || 'arn:aws:iam::' + awsValidationResult.account_id + ':root'}
                      </div>
                      <div className="pl-6 text-xs text-emerald-600">
                        Region: <span className="font-mono font-semibold">{awsValidationResult.region || awsRegion}</span>
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-start gap-2">
                      <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
                      <div>
                        <div className="font-semibold text-rose-800">AWS Validation Failed</div>
                        <div className="text-xs text-rose-700 mt-0.5">{awsValidationResult.error || 'Authentication error'}</div>
                      </div>
                    </div>
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
                        onClick={() => {
                          onNavigate('repo_analyzer', '/source-analysis', {
                            projectId: conn.project_id || selectedProjectId,
                            environmentId: conn.environment_id || selectedEnvId,
                            repoPath: conn.repo_name || conn.repo_url,
                            branch: conn.branch || 'main',
                            activeProject,
                            activeEnvironment,
                          });
                        }}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-blue-600 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition cursor-pointer"
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
