// frontend/src/modules/source_cloud/SourceCloudView.jsx
import React, { useState, useEffect, useRef } from 'react';
import {
  GitBranch,
  Cloud,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  FolderGit2,
  Layers,
  ChevronRight,
  ChevronDown,
  Search,
  Globe,
  Check,
  X,
  Plus,
  Trash2,
  LayoutGrid,
  List,
  Eye,
  EyeOff,
  ShieldCheck,
  Zap,
} from 'lucide-react';
import { projectsApi, connectionsApi, formatAccountId } from '../../services/api';
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
  const [inUseConnectionId, setInUseConnectionId] = useState(() => {
    try {
      return localStorage.getItem('aether_in_use_connection') || '';
    } catch {
      return '';
    }
  });

  // Modal & View Mode states
  const [isNewConnectionModalOpen, setIsNewConnectionModalOpen] = useState(false);
  const [newConnType, setNewConnType] = useState('git'); // 'git' | 'cloud'
  const [viewMode, setViewMode] = useState('grid'); // 'grid' | 'list'
  const [providerFilter, setProviderFilter] = useState('all'); // 'all' | 'git' | 'cloud'
  const [searchQuery, setSearchQuery] = useState('');

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

  // Submission & Loading state
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [statusMessage, setStatusMessage] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load initial projects & existing connections
  const loadInitialData = async () => {
    setIsLoading(true);
    try {
      const [projList, gitList, cloudList] = await Promise.all([
        projectsApi.list().catch(() => []),
        connectionsApi.listGit().catch(() => []),
        connectionsApi.listCloud().catch(() => []),
      ]);

      setProjects(projList);
      setGitConnections(gitList);
      setCloudConnections(cloudList);

      if (projList.length > 0 && !selectedProjectId) {
        const matched = targetProjectId && projList.find(p => (p.id || p.project_id) === targetProjectId);
        const firstId = matched ? (matched.id || matched.project_id) : (projList[0].id || projList[0].project_id);
        setSelectedProjectId(firstId);
      }

      // Default first connection as in-use if none explicitly set
      if (!inUseConnectionId && (gitList.length > 0 || cloudList.length > 0)) {
        const firstId = gitList[0]?.id || gitList[0]?.connection_id || cloudList[0]?.id || cloudList[0]?.cloud_id;
        if (firstId) {
          setInUseConnectionId(firstId);
          try {
            localStorage.setItem('aether_in_use_connection', firstId);
          } catch {}
        }
      }
    } catch (err) {
      console.error('Failed to load initial connections:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadInitialData();

    // Auto-refresh polling every 6 seconds
    const interval = setInterval(() => {
      if (!document.hidden) {
        loadInitialData();
      }
    }, 6000);

    return () => clearInterval(interval);
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

  // Listen for OAuth completion
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
      setBranches(['main', 'master', 'develop']);
      setSelectedBranch('main');
    }
  };

  const handleRepoChange = (e) => {
    const val = e.target.value;
    setSelectedRepo(val);
    loadBranchesForRepo(val, patToken.trim());
  };

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

  // Finalize new connection submission
  const handleFinalize = async (e) => {
    e.preventDefault();
    if (!selectedProjectId || !selectedEnvId) {
      alert('Please select both a Project and an Environment.');
      return;
    }

    setIsSubmitting(true);
    setStatusMessage(null);
    try {
      const payload = {
        project_id: selectedProjectId,
        environment_id: selectedEnvId,
        repo_url: selectedRepo ? (selectedRepo.startsWith('http') ? selectedRepo : `https://github.com/${selectedRepo}`) : 'https://github.com/aetherops/sample-repo',
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
      const newId = result.git_connection_id || result.cloud_connection_id || result.id;
      if (newId) {
        setInUseConnectionId(newId);
        try {
          localStorage.setItem('aether_in_use_connection', newId);
        } catch {}
      }

      setIsNewConnectionModalOpen(false);
      setStatusMessage({
        type: 'success',
        text: 'Successfully established and registered new connection!',
      });

      await loadInitialData();
    } catch (err) {
      setStatusMessage({ type: 'error', text: `Connection failed: ${err.message}` });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSetInUse = (connId, e) => {
    if (e) e.stopPropagation();
    setInUseConnectionId(connId);
    try {
      localStorage.setItem('aether_in_use_connection', connId);
    } catch {}
  };

  const handleDeleteConnection = async (conn, e) => {
    if (e) e.stopPropagation();
    const connId = conn.id || conn.connection_id;
    const isGit = conn.kind === 'git';
    const label = isGit
      ? (conn.repo_name || conn.repo_url || 'this repository')
      : (conn.account_id ? `AWS Account ${conn.account_id}` : 'this cloud connection');

    if (!window.confirm(`Are you sure you want to delete connection "${label}"?`)) return;

    try {
      if (isGit) {
        await connectionsApi.deleteGit(connId);
      } else {
        await connectionsApi.deleteCloud(connId);
      }
      if (inUseConnectionId === connId) {
        setInUseConnectionId('');
        try {
          localStorage.removeItem('aether_in_use_connection');
        } catch {}
      }
      await loadInitialData();
    } catch (err) {
      alert(`Failed to delete connection: ${err.message || err}`);
    }
  };

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

  // Build unified connection card objects
  const unifiedGit = gitConnections.map((g) => {
    const id = g.id || g.connection_id;
    const proj = projects.find((p) => (p.id || p.project_id) === g.project_id);
    return {
      ...g,
      id,
      kind: 'git',
      title: g.repo_name || (g.repo_url ? g.repo_url.replace('https://github.com/', '') : 'Git Repository'),
      provider: 'GitHub',
      projectName: proj?.name || g.project_id || 'Active Project',
      envIdentifier: g.environment_id || 'Dev',
      branch: g.branch || 'main',
      status: g.status || 'CONNECTED',
    };
  });

  const unifiedCloud = cloudConnections.map((c) => {
    const id = c.id || c.cloud_id;
    const proj = projects.find((p) => (p.id || p.project_id) === c.project_id);
    return {
      ...c,
      id,
      kind: 'cloud',
      title: c.account_id ? `AWS Account ${formatAccountId(c.account_id)}` : 'AWS IAM Cloud Provider',
      provider: 'AWS Cloud',
      projectName: proj?.name || c.project_id || 'Active Project',
      envIdentifier: c.environment_id || 'Production',
      region: c.aws_region || 'us-east-1',
      status: c.status || 'VERIFIED',
    };
  });

  const allConnections = [...unifiedGit, ...unifiedCloud];

  // Filtering
  const q = searchQuery.toLowerCase().trim();
  const filteredConnections = allConnections.filter((conn) => {
    const matchesProvider =
      providerFilter === 'all' ||
      (providerFilter === 'git' && conn.kind === 'git') ||
      (providerFilter === 'cloud' && conn.kind === 'cloud');

    const matchesQuery =
      !q ||
      conn.title?.toLowerCase().includes(q) ||
      conn.projectName?.toLowerCase().includes(q) ||
      conn.envIdentifier?.toLowerCase().includes(q) ||
      conn.branch?.toLowerCase().includes(q) ||
      conn.region?.toLowerCase().includes(q);

    return matchesProvider && matchesQuery;
  });

  const totalConnections = allConnections.length;
  const inUseCount = allConnections.filter((c) => c.id === inUseConnectionId).length || (totalConnections > 0 ? 1 : 0);

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* ── Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Connect Cloud &amp; Git</h1>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={loadInitialData}
            disabled={isLoading}
            className="p-2 text-slate-600 hover:text-slate-900 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 shadow-xs transition"
            title="Refresh connections"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
          <button
            type="button"
            onClick={() => setIsNewConnectionModalOpen(true)}
            className="px-3.5 py-2 rounded-lg bg-[#1e40af] hover:bg-[#1d4ed8] text-white text-xs font-semibold shadow-xs transition flex items-center gap-1.5 cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            <span>New Connection</span>
          </button>
        </div>
      </div>

      {statusMessage && (
        <div
          className={`p-3.5 rounded-xl border flex items-center justify-between text-xs font-medium animate-in fade-in duration-150 ${
            statusMessage.type === 'success'
              ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
              : 'bg-rose-50 border-rose-200 text-rose-800'
          }`}
        >
          <div className="flex items-center gap-2">
            {statusMessage.type === 'success' ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            ) : (
              <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
            )}
            <span>{statusMessage.text}</span>
          </div>
          <button
            onClick={() => setStatusMessage(null)}
            className="text-xs font-bold underline hover:opacity-80 ml-2 cursor-pointer"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* ── Summary KPI Cards (without descriptions) ── */}
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white border border-slate-200/90 rounded-2xl p-5 space-y-2 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Total</span>
            <div className="w-8 h-8 rounded-lg bg-blue-50 text-[#1e40af] flex items-center justify-center">
              <Layers className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold font-mono text-slate-900">{totalConnections}</span>
            <span className="text-xs text-slate-500 font-medium">connections</span>
          </div>
        </div>

        <div className="bg-white border border-slate-200/90 rounded-2xl p-5 space-y-2 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">In Use</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-700 flex items-center justify-center">
              <Zap className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold font-mono text-slate-900">{inUseCount}</span>
            <span className="text-xs text-slate-500 font-medium">active</span>
          </div>
        </div>

        <div className="bg-white border border-slate-200/90 rounded-2xl p-5 space-y-2 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">GitHub</span>
            <div className="w-8 h-8 rounded-lg bg-purple-50 text-purple-700 flex items-center justify-center">
              <FolderGit2 className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold font-mono text-slate-900">{gitConnections.length}</span>
            <span className="text-xs text-slate-500 font-medium">repos</span>
          </div>
        </div>

        <div className="bg-white border border-slate-200/90 rounded-2xl p-5 space-y-2 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">AWS</span>
            <div className="w-8 h-8 rounded-lg bg-amber-50 text-amber-700 flex items-center justify-center">
              <Cloud className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold font-mono text-slate-900">{cloudConnections.length}</span>
            <span className="text-xs text-slate-500 font-medium">accounts</span>
          </div>
        </div>
      </section>

      {/* ── Filter Toolbar ── */}
      <div className="bg-white border border-slate-200/80 rounded-xl p-3 flex flex-wrap items-center justify-between gap-3 shadow-xs">
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <span className="text-slate-400 font-medium text-[11px]">Provider:</span>
          <select
            value={providerFilter}
            onChange={(e) => setProviderFilter(e.target.value)}
            className="px-2.5 py-1.5 rounded-lg border border-slate-200 bg-slate-50 text-slate-700 font-medium focus:outline-none focus:border-[#1e40af]"
          >
            <option value="all">All Providers</option>
            <option value="git">GitHub</option>
            <option value="cloud">AWS Cloud</option>
          </select>
        </div>

        <div className="flex items-center gap-2 flex-1 max-w-sm justify-end">
          <div className="relative w-full">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search connections, repos, regions..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div className="flex bg-slate-100 p-0.5 rounded-lg border border-slate-200 shrink-0">
            <button
              type="button"
              onClick={() => setViewMode('grid')}
              className={`p-1.5 rounded-md transition ${viewMode === 'grid' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-400 hover:text-slate-700'}`}
              title="Grid View"
            >
              <LayoutGrid className="w-3.5 h-3.5" />
            </button>
            <button
              type="button"
              onClick={() => setViewMode('list')}
              className={`p-1.5 rounded-md transition ${viewMode === 'list' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-400 hover:text-slate-700'}`}
              title="List View"
            >
              <List className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* ── Connected Connections Cards Grid / List ── */}
      {filteredConnections.length === 0 ? (
        <div className="bg-white border border-slate-200/80 rounded-2xl p-12 text-center space-y-4 shadow-xs">
          <div className="w-12 h-12 rounded-2xl bg-blue-50 text-[#1e40af] flex items-center justify-center mx-auto">
            <GitBranch className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900">No connections configured yet</h3>
            <p className="text-xs text-slate-500 mt-1">
              Click &quot;New Connection&quot; above to link your GitHub repository and AWS cloud credentials.
            </p>
          </div>
          <button
            type="button"
            onClick={() => setIsNewConnectionModalOpen(true)}
            className="inline-flex items-center gap-1.5 px-4 py-2 bg-[#1e40af] hover:bg-[#1d4ed8] text-white text-xs font-semibold rounded-xl shadow-xs transition cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            <span>New Connection</span>
          </button>
        </div>
      ) : viewMode === 'grid' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {filteredConnections.map((conn) => {
            const isInUse = conn.id === inUseConnectionId;
            const isGit = conn.kind === 'git';

            return (
              <div
                key={conn.id}
                className={`bg-white border rounded-2xl p-5 shadow-xs hover:shadow-md transition flex flex-col justify-between space-y-4 ${
                  isInUse ? 'border-emerald-300 ring-1 ring-emerald-400/30' : 'border-slate-200/90 hover:border-blue-300'
                }`}
              >
                <div className="space-y-3">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2.5 min-w-0">
                      <div className={`w-9 h-9 rounded-xl flex items-center justify-center font-bold text-sm shrink-0 ${
                        isGit ? 'bg-purple-50 text-purple-700' : 'bg-amber-50 text-amber-700'
                      }`}>
                        {isGit ? <FolderGit2 className="w-4 h-4" /> : <Cloud className="w-4 h-4" />}
                      </div>
                      <div className="min-w-0">
                        <h3 className="text-sm font-bold text-slate-900 tracking-tight truncate">
                          {conn.title}
                        </h3>
                        <span className="text-[10px] font-mono text-slate-400 block truncate">
                          {conn.provider}
                        </span>
                      </div>
                    </div>

                    {/* Denotes In Use */}
                    {isInUse ? (
                      <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center gap-1.5 shrink-0">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                        In Use
                      </span>
                    ) : (
                      <button
                        type="button"
                        onClick={(e) => handleSetInUse(conn.id, e)}
                        className="text-[11px] font-medium text-slate-400 hover:text-slate-800 underline cursor-pointer shrink-0"
                        title="Set this connection as currently active"
                      >
                        Set In Use
                      </button>
                    )}
                  </div>

                  {/* Card Details */}
                  <div className="text-xs text-slate-500 space-y-1 bg-slate-50/70 p-3 rounded-xl border border-slate-100">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400 text-[11px]">Target Workspace:</span>
                      <strong className="text-slate-800 text-[11px] font-medium truncate max-w-[150px]">{conn.projectName}</strong>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400 text-[11px]">Environment:</span>
                      <span className="font-mono text-slate-700 text-[11px] font-medium">{conn.envIdentifier}</span>
                    </div>
                    {isGit ? (
                      <div className="flex items-center justify-between">
                        <span className="text-slate-400 text-[11px]">Branch:</span>
                        <span className="font-mono text-slate-700 text-[11px]">{conn.branch}</span>
                      </div>
                    ) : (
                      <div className="flex items-center justify-between">
                        <span className="text-slate-400 text-[11px]">AWS Region:</span>
                        <span className="font-mono text-slate-700 text-[11px]">{conn.region}</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Card Action Footer */}
                <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                  <div className="flex items-center gap-1.5">
                    {isGit && onNavigate && (
                      <button
                        type="button"
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
                        className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-semibold text-blue-600 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition cursor-pointer"
                      >
                        <span>Scan</span>
                        <ChevronRight className="w-3 h-3" />
                      </button>
                    )}
                    {isGit && (
                      <button
                        type="button"
                        onClick={() => handleViewSnapshot(conn.id)}
                        disabled={isLoadingSnapshot}
                        className="px-2.5 py-1 text-xs text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-lg transition cursor-pointer"
                      >
                        Snapshot
                      </button>
                    )}
                  </div>

                  <button
                    type="button"
                    onClick={(e) => handleDeleteConnection(conn, e)}
                    className="p-1 text-slate-400 hover:text-rose-600 rounded transition cursor-pointer"
                    title="Delete Connection"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="bg-white border border-slate-200/90 rounded-2xl overflow-hidden shadow-xs">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50/80 border-b border-slate-200/80 text-slate-500 font-semibold uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="px-5 py-3.5">Connection</th>
                  <th className="px-4 py-3.5">Provider</th>
                  <th className="px-4 py-3.5">Workspace</th>
                  <th className="px-4 py-3.5">Target</th>
                  <th className="px-4 py-3.5">Usage</th>
                  <th className="px-4 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredConnections.map((conn) => {
                  const isInUse = conn.id === inUseConnectionId;
                  const isGit = conn.kind === 'git';

                  return (
                    <tr key={conn.id} className="hover:bg-slate-50/70 transition">
                      <td className="px-5 py-3.5">
                        <div className="font-semibold text-slate-900">{conn.title}</div>
                      </td>
                      <td className="px-4 py-3.5">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                          isGit ? 'bg-purple-50 text-purple-700' : 'bg-amber-50 text-amber-700'
                        }`}>
                          {conn.provider}
                        </span>
                      </td>
                      <td className="px-4 py-3.5 text-slate-700">{conn.projectName}</td>
                      <td className="px-4 py-3.5 font-mono text-slate-600">
                        {isGit ? conn.branch : conn.region}
                      </td>
                      <td className="px-4 py-3.5">
                        {isInUse ? (
                          <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center gap-1 max-w-fit">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                            In Use
                          </span>
                        ) : (
                          <button
                            type="button"
                            onClick={(e) => handleSetInUse(conn.id, e)}
                            className="text-xs text-slate-400 hover:text-slate-800 underline cursor-pointer"
                          >
                            Set In Use
                          </button>
                        )}
                      </td>
                      <td className="px-4 py-3.5 text-right">
                        <button
                          type="button"
                          onClick={(e) => handleDeleteConnection(conn, e)}
                          className="p-1.5 text-slate-400 hover:text-rose-600 rounded transition cursor-pointer"
                          title="Delete Connection"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── New Connection Modal (Card-like Input Form) ── */}
      {isNewConnectionModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs">
          <div className="bg-white border border-slate-200 rounded-2xl w-full max-w-lg p-6 space-y-5 shadow-2xl animate-in fade-in zoom-in-95 duration-150 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-blue-50 text-[#1e40af] flex items-center justify-center font-bold text-base">
                  +
                </div>
                <h3 className="text-base font-bold text-slate-900">New Connection</h3>
              </div>
              <button
                type="button"
                onClick={() => setIsNewConnectionModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 p-1 rounded-md"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleFinalize} className="space-y-4">
              {/* Destination Selectors */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="block text-xs font-semibold text-slate-700">Project Workspace</label>
                  <select
                    value={selectedProjectId}
                    onChange={(e) => setSelectedProjectId(e.target.value)}
                    className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 bg-white focus:outline-none focus:border-[#1e40af]"
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

                <div className="space-y-1">
                  <label className="block text-xs font-semibold text-slate-700">Target Environment</label>
                  <select
                    value={selectedEnvId}
                    onChange={(e) => setSelectedEnvId(e.target.value)}
                    className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 bg-white focus:outline-none focus:border-[#1e40af]"
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

              {/* Provider Selection Tabs */}
              <div className="flex bg-slate-100 p-1 rounded-xl gap-1">
                <button
                  type="button"
                  onClick={() => setNewConnType('git')}
                  className={`flex-1 py-2 text-xs font-semibold rounded-lg transition flex items-center justify-center gap-1.5 ${
                    newConnType === 'git'
                      ? 'bg-white text-slate-900 shadow-xs'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  <FolderGit2 className="w-3.5 h-3.5 text-purple-600" />
                  <span>GitHub Repository</span>
                </button>
                <button
                  type="button"
                  onClick={() => setNewConnType('cloud')}
                  className={`flex-1 py-2 text-xs font-semibold rounded-lg transition flex items-center justify-center gap-1.5 ${
                    newConnType === 'cloud'
                      ? 'bg-white text-slate-900 shadow-xs'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  <Cloud className="w-3.5 h-3.5 text-amber-600" />
                  <span>AWS Cloud</span>
                </button>
              </div>

              {/* GitHub Card Form */}
              {newConnType === 'git' && (
                <div className="space-y-3.5 p-4 bg-slate-50/70 border border-slate-200 rounded-xl">
                  <div className="flex items-center gap-2 p-1 bg-slate-200/60 rounded-lg">
                    <button
                      type="button"
                      onClick={() => setAuthMethod('pat')}
                      className={`flex-1 py-1 text-xs font-semibold rounded-md transition ${
                        authMethod === 'pat' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600'
                      }`}
                    >
                      Personal Access Token (PAT)
                    </button>
                    <button
                      type="button"
                      onClick={() => setAuthMethod('oauth')}
                      className={`flex-1 py-1 text-xs font-semibold rounded-md transition ${
                        authMethod === 'oauth' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600'
                      }`}
                    >
                      GitHub OAuth
                    </button>
                  </div>

                  {githubUser && (
                    <div className="flex items-center justify-between p-2.5 bg-emerald-50 border border-emerald-200 rounded-lg text-xs text-emerald-900">
                      <div className="flex items-center gap-2">
                        <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                        <span className="font-semibold">@{githubUser.login || githubUser.name || 'connected'}</span>
                      </div>
                      <span className="text-[10px] font-mono text-emerald-700">{repos.length} repos loaded</span>
                    </div>
                  )}

                  {authMethod === 'pat' ? (
                    <div className="space-y-1">
                      <label className="block text-xs font-semibold text-slate-700">PAT Token</label>
                      <div className="flex gap-2">
                        <input
                          type="password"
                          placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
                          value={patToken}
                          onChange={(e) => setPatToken(e.target.value)}
                          className="flex-1 px-3 py-2 text-xs font-mono rounded-lg border border-slate-300 bg-white focus:outline-none focus:border-[#1e40af]"
                        />
                        <button
                          type="button"
                          onClick={handleVerifyPat}
                          disabled={isVerifyingPat || !patToken.trim()}
                          className="px-3 py-2 bg-slate-800 hover:bg-slate-900 text-white text-xs font-semibold rounded-lg transition disabled:opacity-50 shrink-0 cursor-pointer"
                        >
                          {isVerifyingPat ? <RefreshCw className="w-3 h-3 animate-spin" /> : 'Verify'}
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="p-3 bg-white rounded-lg border border-slate-200 text-center space-y-2">
                      <button
                        type="button"
                        onClick={handleConnectGitHubOAuth}
                        disabled={isConnectingOAuth}
                        className="inline-flex items-center gap-2 px-3.5 py-1.5 bg-slate-900 hover:bg-black text-white text-xs font-semibold rounded-lg shadow-2xs transition disabled:opacity-50 cursor-pointer"
                      >
                        {isConnectingOAuth ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <FolderGit2 className="w-3.5 h-3.5" />}
                        <span>{githubUser ? 'Reconnect OAuth' : 'Connect with GitHub OAuth'}</span>
                      </button>
                    </div>
                  )}

                  <div className="space-y-1">
                    <label className="block text-xs font-semibold text-slate-700">Repository</label>
                    {repos.length > 0 ? (
                      <select
                        value={selectedRepo}
                        onChange={handleRepoChange}
                        className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 bg-white focus:outline-none focus:border-[#1e40af]"
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
                        placeholder="e.g. organization/repository-name"
                        value={selectedRepo}
                        onChange={(e) => setSelectedRepo(e.target.value)}
                        className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 bg-white focus:outline-none focus:border-[#1e40af]"
                      />
                    )}
                  </div>

                  <div className="space-y-1">
                    <label className="block text-xs font-semibold text-slate-700">Default Branch</label>
                    {branches.length > 0 ? (
                      <select
                        value={selectedBranch}
                        onChange={(e) => setSelectedBranch(e.target.value)}
                        className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 bg-white focus:outline-none focus:border-[#1e40af]"
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
                        className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 bg-white focus:outline-none focus:border-[#1e40af]"
                      />
                    )}
                  </div>
                </div>
              )}

              {/* AWS Cloud Card Form */}
              {newConnType === 'cloud' && (
                <div className="space-y-3.5 p-4 bg-slate-50/70 border border-slate-200 rounded-xl">
                  <div className="space-y-1">
                    <label className="block text-xs font-semibold text-slate-700">AWS Access Key ID</label>
                    <input
                      type="text"
                      placeholder="AKIAIOSFODNN7EXAMPLE"
                      value={awsAccessKey}
                      onChange={(e) => setAwsAccessKey(e.target.value)}
                      className="w-full px-3 py-2 text-xs font-mono rounded-lg border border-slate-300 bg-white focus:outline-none focus:border-[#1e40af]"
                    />
                  </div>

                  <div className="space-y-1">
                    <label className="block text-xs font-semibold text-slate-700">AWS Secret Access Key</label>
                    <div className="relative">
                      <input
                        type={showSecretKey ? 'text' : 'password'}
                        placeholder="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
                        value={awsSecretKey}
                        onChange={(e) => setAwsSecretKey(e.target.value)}
                        className="w-full px-3 py-2 pr-9 text-xs font-mono rounded-lg border border-slate-300 bg-white focus:outline-none focus:border-[#1e40af]"
                      />
                      <button
                        type="button"
                        onClick={() => setShowSecretKey(!showSecretKey)}
                        className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                      >
                        {showSecretKey ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                      </button>
                    </div>
                  </div>

                  {/* Searchable 39 AWS Global Regions */}
                  <div className="space-y-1 relative" ref={regionDropdownRef}>
                    <label className="block text-xs font-semibold text-slate-700">Target Region</label>
                    <button
                      type="button"
                      onClick={() => setIsRegionDropdownOpen(!isRegionDropdownOpen)}
                      className="w-full text-left px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs flex items-center justify-between"
                    >
                      <div className="flex items-center gap-1.5 truncate">
                        <Globe className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                        <span className="font-mono font-semibold">{awsRegion}</span>
                        <span className="text-slate-500 truncate">({selectedRegionObj.label.replace(`${awsRegion} `, '').replace(/[()]/g, '')})</span>
                      </div>
                      <ChevronDown className={`w-3.5 h-3.5 text-slate-400 transition-transform ${isRegionDropdownOpen ? 'rotate-180' : ''}`} />
                    </button>

                    {isRegionDropdownOpen && (
                      <div className="absolute z-50 left-0 right-0 top-full mt-1 bg-white border border-slate-200 rounded-xl shadow-xl overflow-hidden max-w-full">
                        <div className="p-2 border-b border-slate-100 bg-slate-50">
                          <input
                            type="text"
                            autoFocus
                            placeholder="Search regions..."
                            value={regionSearch}
                            onChange={(e) => setRegionSearch(e.target.value)}
                            className="w-full px-2.5 py-1 text-xs border border-slate-200 rounded-md bg-white focus:outline-none"
                          />
                        </div>
                        <div className="max-h-48 overflow-y-auto divide-y divide-slate-100">
                          {filteredRegions.map((r) => (
                            <button
                              key={r.value}
                              type="button"
                              onClick={() => {
                                setAwsRegion(r.value);
                                setIsRegionDropdownOpen(false);
                                setRegionSearch('');
                              }}
                              className={`w-full text-left px-3 py-1.5 text-xs flex items-center justify-between hover:bg-blue-50/70 transition ${
                                r.value === awsRegion ? 'bg-blue-50 text-blue-900 font-semibold' : 'text-slate-700'
                              }`}
                            >
                              <span>{r.value} <span className="text-[10px] text-slate-400">({r.label})</span></span>
                              {r.value === awsRegion && <Check className="w-3.5 h-3.5 text-blue-600" />}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  <button
                    type="button"
                    onClick={handleValidateAws}
                    disabled={isValidatingAws || !awsAccessKey.trim() || !awsSecretKey.trim()}
                    className="w-full py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded-lg transition disabled:opacity-50 flex items-center justify-center gap-1.5 cursor-pointer"
                  >
                    {isValidatingAws ? <RefreshCw className="w-3 h-3 animate-spin" /> : <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />}
                    <span>{isValidatingAws ? 'Validating STS...' : 'Validate IAM Credentials'}</span>
                  </button>

                  {awsValidationResult && (
                    <div className={`p-2.5 rounded-lg text-xs border ${
                      awsValidationResult.is_valid !== false && !awsValidationResult.error
                        ? 'bg-emerald-50 text-emerald-900 border-emerald-200'
                        : 'bg-rose-50 text-rose-900 border-rose-200'
                    }`}>
                      {awsValidationResult.is_valid !== false && !awsValidationResult.error ? (
                        <span>✓ STS Validated · Account: <strong>{awsValidationResult.account_id}</strong></span>
                      ) : (
                        <span>✗ Validation failed: {awsValidationResult.error || 'Invalid credentials'}</span>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Modal Action Buttons */}
              <div className="pt-3 border-t border-slate-100 flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setIsNewConnectionModalOpen(false)}
                  className="px-4 py-2 text-xs font-medium rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 text-xs font-semibold rounded-lg bg-[#1e40af] hover:bg-[#1d4ed8] text-white shadow-xs transition disabled:opacity-50 flex items-center gap-1.5 cursor-pointer"
                >
                  {isSubmitting ? (
                    <>
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                      Connecting...
                    </>
                  ) : (
                    'Connect & Finalize'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── Snapshot Modal ── */}
      {selectedSnapshot && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs">
          <div className="bg-white rounded-2xl max-w-lg w-full shadow-2xl border border-slate-200 p-6 animate-in fade-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <h3 className="text-base font-bold text-slate-900">Repository Snapshot</h3>
              <button
                type="button"
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
                type="button"
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
