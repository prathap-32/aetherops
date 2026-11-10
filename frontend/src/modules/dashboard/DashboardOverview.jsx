// frontend/src/modules/dashboard/DashboardOverview.jsx
import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  FolderKanban,
  Boxes,
  GitBranch,
  FileCode2,
  Network,
  Rocket,
  Activity,
  ShieldAlert,
  ArrowRight,
  Server,
  Clock,
  Plus,
  CheckCircle2,
  AlertTriangle,
  Sparkles,
  RefreshCw,
  Search,
  Smartphone,
  Laptop,
  Tablet,
  Globe,
  Key,
  Copy,
  Check,
  LogIn,
  LogOut,
  ShieldCheck,
  User,
  Mail,
  Shield,
  KeyRound,
  Trash2,
  Edit3,
  Save,
} from 'lucide-react';
import {
  projectsApi,
  connectionsApi,
  deploymentsApi,
  dashboardApi,
  authApi,
  formatAccountId,
} from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import WidgetCustomizerModal from './WidgetCustomizerModal';

const DEFAULT_PREFERENCES = {
  widget_order: [
    'getting_started',
    'recommendations',
    'attention_required',
    'overview_metrics',
    'recent_projects',
    'environments_summary',
    'deployments_overview',
    'system_health',
    'recent_activity',
  ],
  widget_visibility: {
    getting_started: true,
    recommendations: true,
    attention_required: true,
    overview_metrics: true,
    recent_projects: true,
    environments_summary: true,
    deployments_overview: true,
    system_health: true,
    recent_activity: true,
  },
  widget_sizes: {
    getting_started: 'full',
    recommendations: 'full',
    attention_required: 'full',
    overview_metrics: 'full',
    recent_projects: 'full',
    environments_summary: 'half',
    deployments_overview: 'half',
    system_health: 'half',
    recent_activity: 'half',
  },
  pinned_widgets: [],
};

export default function DashboardOverview({ onNavigate, onOpenCreateProject, onSelectProject }) {
  const { user, isAdmin, updateProfile } = useAuth();
  const userKey = user?.uuid || user?.username || 'user';
  const storageKey = `aether_dashboard_prefs_${userKey}`;

  const handleCreateProjectClick = () => {
    if (onOpenCreateProject) {
      onOpenCreateProject();
    } else if (onNavigate) {
      onNavigate('projects', '/projects');
    }
  };
  // ── 1. Data States with Explicit Availability/Error Distinction ──
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [isCustomizerOpen, setIsCustomizerOpen] = useState(false);
  const [projectSearchQuery, setProjectSearchQuery] = useState('');

  // Primary Data Sources
  const [projectsState, setProjectsState] = useState({ status: 'loading', data: [], error: null });
  const [environmentsState, setEnvironmentsState] = useState({ status: 'loading', data: [], error: null });
  const [connectionsState, setConnectionsState] = useState({ status: 'loading', git: [], cloud: [], error: null });
  const [deploymentsState, setDeploymentsState] = useState({ status: 'loading', data: [], error: null });
  const [fleetProbes, setFleetProbes] = useState({});
  const [dashboardSummary, setDashboardSummary] = useState(null);


  // ── Profile & Account State (Dashboard Direct View) ──
  const [newUsername, setNewUsername] = useState(user?.username || '');
  const [isSavingProfile, setIsSavingProfile] = useState(false);
  const [profileMsg, setProfileMsg] = useState(null);
  const [copiedAcc, setCopiedAcc] = useState(false);

  // ── Login Sessions & Audit State (Real-Time Device Tracking) ──
  const [sessionsData, setSessionsData] = useState({
    active_count: 0,
    past_count: 0,
    current_session_id: null,
    active_sessions: [],
    past_sessions: [],
    audit_logs: [],
  });
  const [loadingSessions, setLoadingSessions] = useState(true);
  const [refreshingSessions, setRefreshingSessions] = useState(false);
  const [revokingId, setRevokingId] = useState(null);
  const [revokingOthers, setRevokingOthers] = useState(false);
  const [sessionStatusMsg, setSessionStatusMsg] = useState(null);
  const [auditSearchQuery, setAuditSearchQuery] = useState('');
  const [auditEventFilter, setAuditEventFilter] = useState('ALL');

  const fetchSessions = useCallback(async (isSilent = false) => {
    if (!isSilent) setLoadingSessions(true);
    else setRefreshingSessions(true);
    try {
      const res = await authApi.getSessions();
      if (res && res.status === 'SUCCESS') {
        setSessionsData(res);
      }
    } catch (err) {
      console.warn('Failed to load user sessions on dashboard:', err);
    } finally {
      setLoadingSessions(false);
      setRefreshingSessions(false);
    }
  }, []);

  useEffect(() => {
    fetchSessions();
    const interval = setInterval(() => {
      fetchSessions(true);
    }, 8000); // 8-second auto-poll for multi-device real-time sync
    return () => clearInterval(interval);
  }, [fetchSessions]);

  const handleRevokeSession = async (sessionId, deviceLabel) => {
    if (!window.confirm(`Log out and revoke session on ${deviceLabel}?`)) return;
    setRevokingId(sessionId);
    setSessionStatusMsg(null);
    try {
      await authApi.revokeSession(sessionId);
      setSessionStatusMsg({ type: 'success', text: `Logged out session on ${deviceLabel}` });
      await fetchSessions(true);
    } catch (err) {
      setSessionStatusMsg({ type: 'error', text: err.message || 'Failed to revoke session' });
    } finally {
      setRevokingId(null);
    }
  };

  const handleRevokeAllOthers = async () => {
    if (!window.confirm('Log out all other devices? Only this current device will stay logged in.')) return;
    setRevokingOthers(true);
    setSessionStatusMsg(null);
    try {
      const res = await authApi.revokeOtherSessions();
      setSessionStatusMsg({ type: 'success', text: res.message || 'All other devices logged out' });
      await fetchSessions(true);
    } catch (err) {
      setSessionStatusMsg({ type: 'error', text: err.message || 'Failed to revoke other devices' });
    } finally {
      setRevokingOthers(false);
    }
  };

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    if (!newUsername.trim()) return;
    setIsSavingProfile(true);
    setProfileMsg(null);
    try {
      await updateProfile(newUsername.trim());
      setProfileMsg({ type: 'success', text: `Handle updated to @${newUsername.trim()}` });
      setTimeout(() => setProfileMsg(null), 3000);
    } catch (err) {
      setProfileMsg({ type: 'error', text: err.message || 'Failed to update handle' });
    } finally {
      setIsSavingProfile(false);
    }
  };

  const copyAccountId = () => {
    const acc = user?.account_id || '109283746519';
    if (navigator.clipboard) {
      navigator.clipboard.writeText(acc);
      setCopiedAcc(true);
      setTimeout(() => setCopiedAcc(false), 2000);
    }
  };

  const renderDeviceIcon = (deviceType) => {
    const type = String(deviceType || '').toLowerCase();
    if (type.includes('mobile') || type.includes('phone') || type.includes('android') || type.includes('ios')) {
      return <Smartphone className="w-5 h-5 text-indigo-600" />;
    }
    if (type.includes('tablet')) {
      return <Tablet className="w-5 h-5 text-amber-600" />;
    }
    return <Laptop className="w-5 h-5 text-blue-600" />;
  };

  const formatSessionTime = (isoStr) => {
    if (!isoStr) return '—';
    try {
      const d = new Date(isoStr);
      return d.toLocaleString([], {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true,
      });
    } catch {
      return isoStr;
    }
  };

  const formatSessionTimeAgo = (isoStr) => {
    if (!isoStr) return 'Active now';
    try {
      const diffMs = Date.now() - new Date(isoStr).getTime();
      const diffSec = Math.floor(diffMs / 1000);
      if (diffSec < 45) return 'Active now';
      const diffMin = Math.floor(diffSec / 60);
      if (diffMin < 60) return `${diffMin}m ago`;
      const diffHr = Math.floor(diffMin / 60);
      if (diffHr < 24) return `${diffHr}h ago`;
      const diffDays = Math.floor(diffHr / 24);
      return `${diffDays}d ago`;
    } catch {
      return 'Recently';
    }
  };

  const filteredAuditLogs = (sessionsData.audit_logs || []).filter((item) => {
    if (auditEventFilter !== 'ALL' && item.event_type !== auditEventFilter) return false;
    if (auditSearchQuery.trim()) {
      const q = auditSearchQuery.toLowerCase();
      const matchDevice = String(item.device_info || '').toLowerCase().includes(q);
      const matchIp = String(item.ip_address || '').toLowerCase().includes(q);
      const matchDetails = String(item.details || '').toLowerCase().includes(q);
      const matchEvent = String(item.event_type || '').toLowerCase().includes(q);
      return matchDevice || matchIp || matchDetails || matchEvent;
    }
    return true;
  });
  // User Preferences State
  const [preferences, setPreferences] = useState(() => {
    try {
      const saved = localStorage.getItem(storageKey);
      if (saved) return JSON.parse(saved);
    } catch (e) {}
    return DEFAULT_PREFERENCES;
  });

  // ── 2. Data Fetching & Aggregation Engine ──
  const fetchAllDashboardData = useCallback(async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true);
    else setLoading(true);

    try {
      const [
        projRes,
        gitConnRes,
        cloudConnRes,
        deployRes,
        summaryRes,
        prefRes,
      ] = await Promise.allSettled([
        projectsApi.list(),
        connectionsApi.listGit(),
        connectionsApi.listCloud(),
        deploymentsApi.list(),
        dashboardApi.getSummary(),
        dashboardApi.getPreferences(),
      ]);

      // Projects
      let loadedProjects = [];
      if (projRes.status === 'fulfilled') {
        loadedProjects = Array.isArray(projRes.value) ? projRes.value : [];
        setProjectsState({ status: 'success', data: loadedProjects, error: null });
      } else {
        setProjectsState({ status: 'error', data: [], error: projRes.reason?.message || 'Failed to load projects' });
      }

      // Environments across projects
      if (loadedProjects.length > 0) {
        try {
          const envPromises = loadedProjects.map((p) =>
            projectsApi.listEnvironments(p.id || p.project_id).catch(() => [])
          );
          const envResults = await Promise.all(envPromises);
          const flattenedEnvs = envResults.flat().filter(Boolean);
          setEnvironmentsState({ status: 'success', data: flattenedEnvs, error: null });
        } catch (envErr) {
          setEnvironmentsState({ status: 'error', data: [], error: envErr.message });
        }
      } else {
        setEnvironmentsState({ status: 'success', data: [], error: null });
      }

      // Connections
      const gitData = gitConnRes.status === 'fulfilled' && Array.isArray(gitConnRes.value) ? gitConnRes.value : [];
      const cloudData = cloudConnRes.status === 'fulfilled' && Array.isArray(cloudConnRes.value) ? cloudConnRes.value : [];
      setConnectionsState({
        status: gitConnRes.status === 'fulfilled' || cloudConnRes.status === 'fulfilled' ? 'success' : 'error',
        git: gitData,
        cloud: cloudData,
        error: gitConnRes.status === 'rejected' ? gitConnRes.reason?.message : null,
      });

      // Deployments (Explicit error vs empty distinction)
      if (deployRes.status === 'fulfilled') {
        const deployList = Array.isArray(deployRes.value)
          ? deployRes.value
          : (deployRes.value?.deployments || []);
        setDeploymentsState({ status: 'success', data: deployList, error: null });
      } else {
        // Did not fail silently: record the unavailable state
        setDeploymentsState({
          status: 'unavailable',
          data: [],
          error: deployRes.reason?.message || 'Deployments telemetry service offline',
        });
      }

      // Backend Summary & Analytics
      if (summaryRes.status === 'fulfilled') {
        setDashboardSummary(summaryRes.value);
      }

      // Backend Preferences (fallback to localStorage if unreachable)
      if (prefRes.status === 'fulfilled' && prefRes.value?.widget_order) {
        setPreferences(prefRes.value);
        try {
          localStorage.setItem(storageKey, JSON.stringify(prefRes.value));
        } catch (e) {}
      }
    } catch (globalErr) {
      console.warn('Dashboard data aggregation notice:', globalErr);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }

    // Probe essential platform services
    const services = [
      { code: 'gateway', name: 'Gateway', port: 8000, ping: '/health' },
      { code: 'projects', name: 'Project & Workspace Manager', port: 8001, ping: '/health' },
      { code: 'connections', name: 'Source & Cloud Broker', port: 8002, ping: '/health' },
      { code: 'analyzer', name: 'AST Codebase Analyzer', port: 8003, ping: '/health' },
      { code: 'architecture', name: 'Cloud Architecture Studio', port: 8005, ping: '/health' },
      { code: 'deployer', name: 'Cloud Deployer & Drift Engine', port: 8011, ping: '/health' },
    ];

    services.forEach(async (s) => {
      const startTime = performance.now();
      try {
        const res = await fetch(`http://localhost:${s.port}${s.ping}`, { method: 'GET', mode: 'cors' });
        const latency = Math.round(performance.now() - startTime);
        setFleetProbes((prev) => ({
          ...prev,
          [s.code]: { status: res.ok ? 'ONLINE' : 'DEGRADED', latency },
        }));
      } catch (err) {
        setFleetProbes((prev) => ({
          ...prev,
          [s.code]: { status: 'OFFLINE', latency: 0 },
        }));
      }
    });
  }, [userKey, storageKey]);

  useEffect(() => {
    fetchAllDashboardData();
  }, [fetchAllDashboardData]);

  // ── 3. Lifecycle Stage Computation (Deterministic Rule Engine) ──
  const projectsCount = projectsState.data.length;
  const environmentsCount = environmentsState.data.length;
  const deploymentsCount = deploymentsState.data.length;

  const lifecycleStage = useMemo(() => {
    if (projectsState.status === 'loading') return 'loading';
    if (projectsCount === 0) return 'stage_1_onboarding';
    if (environmentsCount === 0) return 'stage_2_project_created';
    if (deploymentsCount === 0) return 'stage_3_infrastructure_workflow';
    return 'stage_4_active_operations';
  }, [projectsState.status, projectsCount, environmentsCount, deploymentsCount]);

  const effectiveLifecycleStage = useMemo(() => {
    const override = preferences?.experience_level;
    if (override === 'GUIDED') return 'stage_1_onboarding';
    if (override === 'ADVANCED') return 'stage_4_active_operations';
    return lifecycleStage;
  }, [preferences?.experience_level, lifecycleStage]);

  // ── 4. Widget Eligibility Map ──
  const widgetEligibility = useMemo(() => ({
    getting_started: effectiveLifecycleStage === 'stage_1_onboarding',
    overview_metrics: projectsCount > 0,
    recent_projects: projectsCount > 0,
    environments_summary: environmentsCount > 0,
    deployments_overview: effectiveLifecycleStage === 'stage_4_active_operations' && deploymentsState.status === 'success' && deploymentsState.data.length > 0,
    attention_required: true,
    system_health: true,
    recent_activity: true,
    recommendations: true,
  }), [effectiveLifecycleStage, projectsCount, environmentsCount, deploymentsState]);

  // Widget Metadata Registry
  const WIDGET_REGISTRY = useMemo(() => ({
    getting_started: {
      id: 'getting_started',
      title: 'Getting Started & Workspace Setup',
      description: 'First-time onboarding steps to create a workspace and deploy AWS infrastructure.',
      category: 'Onboarding',
      isEligible: widgetEligibility.getting_started,
    },
    overview_metrics: {
      id: 'overview_metrics',
      title: 'Platform Overview Metrics',
      description: 'Total workspaces, active target environments, connections, and deployment stats.',
      category: 'Analytics',
      isEligible: widgetEligibility.overview_metrics,
    },
    recent_projects: {
      id: 'recent_projects',
      title: 'Recent Projects Fleet',
      description: 'Active cloud workspaces, deployment boundaries, and tech stack configurations.',
      category: 'Projects',
      isEligible: widgetEligibility.recent_projects,
    },
    environments_summary: {
      id: 'environments_summary',
      title: 'Target Environments Fleet',
      description: 'Overview of Dev, Staging, and Production stages across AWS regions.',
      category: 'Environments',
      isEligible: widgetEligibility.environments_summary,
    },
    deployments_overview: {
      id: 'deployments_overview',
      title: 'Deployments & Operational Telemetry',
      description: 'Live infrastructure state, deployment executions, and drift checks.',
      category: 'Operations',
      isEligible: widgetEligibility.deployments_overview,
    },
    attention_required: {
      id: 'attention_required',
      title: 'Attention Required & Risk Gate',
      description: 'Pending approvals, failed workloads, and critical architectural warnings.',
      category: 'Risk & Gates',
      isEligible: widgetEligibility.attention_required,
    },
    system_health: {
      id: 'system_health',
      title: 'Platform Microservices Health',
      description: 'Operational status and round-trip latency of backend orchestrators.',
      category: 'Infrastructure',
      isEligible: widgetEligibility.system_health,
    },
    recent_activity: {
      id: 'recent_activity',
      title: 'Recent Activity & Operational Audit',
      description: 'Timeline of workspace provisioning, architecture changes, and deployments.',
      category: 'Audit',
      isEligible: widgetEligibility.recent_activity,
    },
    recommendations: {
      id: 'recommendations',
      title: 'Lifecycle Recommendations Engine',
      description: 'Deterministic guidance on next steps based on current workspace maturity.',
      category: 'Guidance',
      isEligible: widgetEligibility.recommendations,
    },
  }), [widgetEligibility]);

  // ── 5. User Preferences Handling & Persistence ──
  const handleSavePreferences = async (newPrefs) => {
    setPreferences(newPrefs);
    try {
      localStorage.setItem(storageKey, JSON.stringify(newPrefs));
    } catch (e) {}

    try {
      await dashboardApi.savePreferences(newPrefs);
    } catch (err) {
      console.warn('Backend preferences sync failed (using client storage):', err.message);
    }
  };

  const handleResetPreferences = async () => {
    setPreferences(DEFAULT_PREFERENCES);
    try {
      localStorage.setItem(storageKey, JSON.stringify(DEFAULT_PREFERENCES));
      await dashboardApi.resetPreferences();
    } catch (e) {}
  };

  // ── 6. Greeting & Dynamic Introduction ──
  const timeGreeting = useMemo(() => {
    const hr = new Date().getHours();
    return hr < 12 ? 'Good morning' : hr < 18 ? 'Good afternoon' : 'Good evening';
  }, []);
  const username = user?.username || 'Developer';

  const lifecycleDescription = useMemo(() => {
    if (lifecycleStage === 'stage_1_onboarding') {
      return 'Welcome to AetherOps. Create your first project workspace to begin designing architectures and automating cloud infrastructure.';
    }
    if (lifecycleStage === 'stage_2_project_created') {
      return 'Your project workspaces are active. Connect your AWS credentials or repository to start analyzing codebase architecture.';
    }
    if (lifecycleStage === 'stage_3_infrastructure_workflow') {
      return 'Target environments are configured. Generate visual topologies, synthesize Terraform HCL, and dry-run deployments.';
    }
    return 'Cloud deployments, target fleet health, and workload telemetry across your production cloud infrastructure.';
  }, [lifecycleStage]);

  // Filtered Projects for Widget
  const filteredProjects = useMemo(() => {
    const q = projectSearchQuery.toLowerCase().trim();
    if (!q) return projectsState.data;
    return projectsState.data.filter(
      (p) =>
        (p.name || '').toLowerCase().includes(q) ||
        (p.project_type || '').toLowerCase().includes(q) ||
        (p.description || '').toLowerCase().includes(q)
    );
  }, [projectsState.data, projectSearchQuery]);

  // Attention Items
  const attentionItems = useMemo(() => {
    const items = [];
    // Check for failed deployments
    if (deploymentsState.data && deploymentsState.data.length > 0) {
      const failed = deploymentsState.data.filter((d) => d.status === 'FAILED');
      failed.forEach((f) => {
        items.push({
          id: `dep-${f.id}`,
          type: 'danger',
          title: `Deployment Failed in ${f.environment || 'Production'}`,
          description: f.error_message || 'Resource provisioning encountered Terraform state errors.',
          actionLabel: 'Inspect Logs',
          route: '/deployment',
        });
      });
    }
    // Check for unapproved architecture if in stage 3
    if (lifecycleStage === 'stage_3_infrastructure_workflow') {
      items.push({
        id: 'arch-review',
        type: 'warning',
        title: 'Architecture Sizing Review Pending',
        description: 'Verify detected technical primitives before generating Terraform HCL synthesis.',
        actionLabel: 'Review Architecture',
        route: '/architecture-studio',
      });
    }
    return items;
  }, [deploymentsState.data, lifecycleStage]);

  // ── 7. Render Individual Widgets ──

  // Widget 1: Getting Started (Stage 1 Onboarding)
  const renderGettingStartedWidget = () => (
    <div className="bg-gradient-to-br from-white via-blue-50/20 to-indigo-50/30 rounded-2xl border border-blue-200/80 p-6 sm:p-8 shadow-xs space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-100/70 border border-blue-200 text-blue-800 text-xs font-semibold mb-2">
            <Sparkles className="w-3.5 h-3.5 text-[#1e40af]" />
            New Account Onboarding Guide
          </div>
          <h2 className="text-xl sm:text-2xl font-extrabold text-slate-900 tracking-tight">
            Start Your Cloud Architecture Journey
          </h2>
        </div>

        <button
          onClick={handleCreateProjectClick}
          className="px-5 py-2.5 bg-[#1e40af] hover:bg-[#1d4ed8] text-white text-xs font-bold rounded-xl shadow-xs transition flex items-center gap-2 cursor-pointer shrink-0 self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>Create Your First Project</span>
        </button>
      </div>

      {/* 3 Step Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
        <div
          onClick={handleCreateProjectClick}
          className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs hover:shadow-md hover:border-blue-300 transition cursor-pointer group"
        >
          <div className="w-9 h-9 rounded-xl bg-blue-50 text-blue-700 flex items-center justify-center font-bold text-xs group-hover:scale-105 transition">
            1
          </div>
          <h3 className="text-sm font-bold text-slate-900 mt-3 group-hover:text-blue-700 transition">
            Create Project Workspace
          </h3>
          <p className="text-xs text-slate-500 mt-1">
            Establish a project boundary and attach Dev, Staging, and Production stages.
          </p>
          <div className="mt-4 flex items-center gap-1.5 text-xs font-semibold text-blue-700">
            <span>Launch Modal</span>
            <ArrowRight className="w-3 h-3 group-hover:translate-x-1 transition" />
          </div>
        </div>

        <div
          onClick={() => onNavigate('source_cloud', '/source-connection')}
          className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs hover:shadow-md hover:border-blue-300 transition cursor-pointer group"
        >
          <div className="w-9 h-9 rounded-xl bg-indigo-50 text-indigo-700 flex items-center justify-center font-bold text-xs group-hover:scale-105 transition">
            2
          </div>
          <h3 className="text-sm font-bold text-slate-900 mt-3 group-hover:text-indigo-700 transition">
            Connect AWS &amp; Git
          </h3>
          <p className="text-xs text-slate-500 mt-1">
            Securely authorize GitHub manifest inspection and validate AWS IAM deployment roles.
          </p>
          <div className="mt-4 flex items-center gap-1.5 text-xs font-semibold text-indigo-700">
            <span>Connect Accounts</span>
            <ArrowRight className="w-3 h-3 group-hover:translate-x-1 transition" />
          </div>
        </div>

        <div
          onClick={() => onNavigate('repo_analyzer', '/source-analysis')}
          className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs hover:shadow-md hover:border-blue-300 transition cursor-pointer group"
        >
          <div className="w-9 h-9 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center font-bold text-xs group-hover:scale-105 transition">
            3
          </div>
          <h3 className="text-sm font-bold text-slate-900 mt-3 group-hover:text-emerald-700 transition">
            Synthesize &amp; Deploy
          </h3>
          <p className="text-xs text-slate-500 mt-1">
            AST scanner automatically right-sizes AWS services and synthesizes Terraform HCL.
          </p>
          <div className="mt-4 flex items-center gap-1.5 text-xs font-semibold text-emerald-700">
            <span>Run Scanner</span>
            <ArrowRight className="w-3 h-3 group-hover:translate-x-1 transition" />
          </div>
        </div>
      </div>
    </div>
  );

  // Widget 2: Platform Metrics Overview (Layer B)
  const renderOverviewMetricsWidget = () => (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
      {/* Total Projects */}
      <div
        onClick={() => onNavigate('projects', '/projects')}
        className="bg-white p-4 sm:p-5 rounded-2xl border border-slate-200/80 shadow-xs hover:shadow-md transition cursor-pointer group"
      >
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium text-slate-500">Workspaces &amp; Projects</span>
          <div className="w-9 h-9 rounded-xl bg-blue-50 text-blue-700 flex items-center justify-center group-hover:scale-105 transition">
            <FolderKanban className="w-4 h-4" />
          </div>
        </div>
        <div className="mt-3">
          <div className="text-xl sm:text-2xl font-bold text-slate-900">{projectsCount}</div>
          <div className="text-[11px] text-slate-500 mt-0.5">Isolated tenant boundaries</div>
        </div>
      </div>

      {/* Environments Fleet */}
      <div
        onClick={() => onNavigate('environments', '/environments')}
        className="bg-white p-4 sm:p-5 rounded-2xl border border-slate-200/80 shadow-xs hover:shadow-md transition cursor-pointer group"
      >
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium text-slate-500">Target Environments</span>
          <div className="w-9 h-9 rounded-xl bg-indigo-50 text-indigo-700 flex items-center justify-center group-hover:scale-105 transition">
            <Boxes className="w-4 h-4" />
          </div>
        </div>
        <div className="mt-3">
          <div className="text-xl sm:text-2xl font-bold text-slate-900">{environmentsCount}</div>
          <div className="text-[11px] text-slate-500 mt-0.5">Dev, Staging &amp; Production</div>
        </div>
      </div>

      {/* Connected Accounts */}
      <div
        onClick={() => onNavigate('source_cloud', '/source-connection')}
        className="bg-white p-4 sm:p-5 rounded-2xl border border-slate-200/80 shadow-xs hover:shadow-md transition cursor-pointer group"
      >
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium text-slate-500">Connected Cloud &amp; Git</span>
          <div className="w-9 h-9 rounded-xl bg-cyan-50 text-cyan-700 flex items-center justify-center group-hover:scale-105 transition">
            <GitBranch className="w-4 h-4" />
          </div>
        </div>
        <div className="mt-3">
          <div className="text-xl sm:text-2xl font-bold text-slate-900">
            {connectionsState.git.length + connectionsState.cloud.length}
          </div>
          <div className="text-[11px] text-slate-500 mt-0.5">
            {connectionsState.cloud.length > 0 ? 'Live AWS Role Linked' : 'Awaiting AWS IAM connection'}
          </div>
        </div>
      </div>

      {/* Deployments Status */}
      <div
        onClick={() => onNavigate('deployments', '/deployment')}
        className="bg-white p-4 sm:p-5 rounded-2xl border border-slate-200/80 shadow-xs hover:shadow-md transition cursor-pointer group"
      >
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium text-slate-500">Deployments Executed</span>
          <div className="w-9 h-9 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center group-hover:scale-105 transition">
            <Rocket className="w-4 h-4" />
          </div>
        </div>
        <div className="mt-3">
          <div className="text-xl sm:text-2xl font-bold text-slate-900">
            {deploymentsState.status === 'success' ? deploymentsCount : 'Live'}
          </div>
          <div className="text-[11px] text-slate-500 mt-0.5">
            {deploymentsState.status === 'success' ? 'Validated infrastructure runs' : 'Deployments engine ready'}
          </div>
        </div>
      </div>
    </div>
  );

  // Widget 3: Recent Projects Fleet (Layer B)
  const renderRecentProjectsWidget = () => (
    <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
      <div className="p-4 sm:p-5 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-slate-50/50">
        <div>
          <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <FolderKanban className="w-4 h-4 text-blue-600 shrink-0" />
            <span>Active Cloud Workspaces ({projectsCount})</span>
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Projects configured with isolated environments and deployment boundaries.
          </p>
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <div className="relative flex-1 sm:w-56">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Filter projects..."
              value={projectSearchQuery}
              onChange={(e) => setProjectSearchQuery(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 text-xs rounded-lg border border-slate-200 bg-white focus:outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600"
            />
          </div>

          <button
            onClick={() => onNavigate('projects', '/projects')}
            className="px-3 py-1.5 text-xs font-semibold text-slate-700 hover:text-slate-900 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition cursor-pointer shrink-0"
          >
            View All ({projectsCount})
          </button>
        </div>
      </div>

      {projectsState.status === 'loading' ? (
        <div className="p-8 text-center text-xs text-slate-500">Loading workspaces...</div>
      ) : filteredProjects.length === 0 ? (
        <div className="p-8 text-center space-y-2">
          <p className="text-xs text-slate-500">No projects match your filter query.</p>
        </div>
      ) : (
        <div className="divide-y divide-slate-100">
          {filteredProjects.slice(0, 5).map((project) => (
            <div
              key={project.id || project.name}
              className="p-4 sm:px-6 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-slate-50/70 transition"
            >
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2 flex-wrap">
                  <span
                    className="text-xs font-bold text-slate-900 hover:text-blue-600 transition truncate cursor-pointer"
                    onClick={() => {
                      if (onSelectProject) onSelectProject(project);
                      onNavigate('projects', '/projects');
                    }}
                  >
                    {project.name}
                  </span>
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-medium bg-slate-100 text-slate-700 border border-slate-200 capitalize">
                    {project.project_type?.replace(/_/g, ' ') || 'Web App'}
                  </span>
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                    {project.status || 'ACTIVE'}
                  </span>
                </div>
                <p className="text-xs text-slate-500 mt-1 line-clamp-1 sm:truncate max-w-xl">
                  {project.description || 'Configured cloud workspace for architecture synthesis and deployments.'}
                </p>
              </div>

              <div className="flex items-center gap-2 sm:gap-3 flex-wrap sm:flex-nowrap shrink-0">
                <span className="text-xs text-slate-500 font-mono">
                  {project.environment_count || 0} envs
                </span>
                <button
                  onClick={() => {
                    if (onSelectProject) onSelectProject(project);
                    onNavigate('repo_analyzer', '/source-analysis', { projectId: project.id, project });
                  }}
                  className="px-2.5 sm:px-3 py-1.5 text-xs font-semibold text-blue-700 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg transition cursor-pointer"
                >
                  Analyze Code
                </button>
                <button
                  onClick={() => {
                    if (onSelectProject) onSelectProject(project);
                    onNavigate('architecture_studio', '/architecture-studio', { projectId: project.id, project });
                  }}
                  className="px-2.5 sm:px-3 py-1.5 text-xs font-semibold text-slate-700 bg-white hover:bg-slate-50 border border-slate-200 rounded-lg transition cursor-pointer"
                >
                  Architecture Studio
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  // Widget 4: Target Environments Fleet Summary (Layer B)
  const renderEnvironmentsSummaryWidget = () => (
    <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
      <div className="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
        <div>
          <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <Boxes className="w-4 h-4 text-indigo-600" />
            <span>Target Environments Fleet ({environmentsCount})</span>
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Active deployment stages and target AWS regions.
          </p>
        </div>
        <button
          onClick={() => onNavigate('environments', '/environments')}
          className="text-xs font-semibold text-indigo-600 hover:text-indigo-800 transition cursor-pointer"
        >
          Manage Fleet ➔
        </button>
      </div>

      {environmentsCount === 0 ? (
        <div className="p-6 text-center text-xs text-slate-500">
          No environments configured yet. Add Dev, Staging, or Production to a project.
        </div>
      ) : (
        <div className="divide-y divide-slate-100 max-h-80 overflow-y-auto">
          {environmentsState.data.slice(0, 6).map((env, idx) => (
            <div key={env.id || idx} className="p-3.5 px-5 flex items-center justify-between gap-3 hover:bg-slate-50/50 transition">
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-slate-800 truncate">{env.name}</span>
                  <span className={`px-1.5 py-0.5 rounded text-[10px] font-mono font-semibold uppercase ${
                    env.env_type === 'production'
                      ? 'bg-rose-50 text-rose-700 border border-rose-200'
                      : env.env_type === 'staging'
                      ? 'bg-amber-50 text-amber-700 border border-amber-200'
                      : 'bg-blue-50 text-blue-700 border border-blue-200'
                  }`}>
                    {env.env_type}
                  </span>
                </div>
                <div className="text-[11px] text-slate-400 font-mono mt-0.5">
                  Region: {env.aws_region || 'us-east-1'}
                </div>
              </div>

              <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                {env.status || 'ACTIVE'}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  // Widget 5: Attention Required & Risk Gate (Layer B - Never hidden if critical)
  const renderAttentionRequiredWidget = () => (
    <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
      <div className="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
        <div>
          <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-rose-600" />
            <span>Attention Required &amp; Governance Gates</span>
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Operational blockers, pending architecture approvals, and security alerts.
          </p>
        </div>
        <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
          attentionItems.length > 0
            ? 'bg-rose-50 text-rose-700 border border-rose-200'
            : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
        }`}>
          {attentionItems.length > 0 ? `${attentionItems.length} Action Needed` : 'All Systems Clear'}
        </span>
      </div>

      {attentionItems.length === 0 ? (
        <div className="p-6 text-center text-xs text-slate-500 flex items-center justify-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          <span>No critical security alerts, drift anomalies, or failed deployments detected.</span>
        </div>
      ) : (
        <div className="divide-y divide-slate-100">
          {attentionItems.map((item) => (
            <div key={item.id} className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-slate-50/60 transition">
              <div className="flex items-start gap-3">
                <AlertTriangle className={`w-4 h-4 mt-0.5 shrink-0 ${item.type === 'danger' ? 'text-rose-600' : 'text-amber-600'}`} />
                <div>
                  <h4 className="text-xs font-bold text-slate-900">{item.title}</h4>
                  <p className="text-xs text-slate-500 mt-0.5">{item.description}</p>
                </div>
              </div>
              <button
                onClick={() => {
                  const targetPath = item.route.startsWith('/') ? item.route : `/${item.route}`;
                  onNavigate(targetPath);
                }}
                className={`px-3 py-1.5 text-xs font-semibold rounded-lg shadow-2xs transition shrink-0 cursor-pointer ${
                  item.type === 'danger'
                    ? 'bg-rose-600 hover:bg-rose-700 text-white'
                    : 'bg-amber-600 hover:bg-amber-700 text-white'
                }`}
              >
                {item.actionLabel}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  // Widget 6: Deployments Overview (Layer B)
  const renderDeploymentsOverviewWidget = () => (
    <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
      <div className="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
        <div>
          <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <Rocket className="w-4 h-4 text-emerald-600" />
            <span>Deployment Pipeline &amp; Drift</span>
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Real AWS infrastructure deployments and terraform state runs.
          </p>
        </div>
        <button
          onClick={() => onNavigate('deployments', '/deployment')}
          className="text-xs font-semibold text-emerald-600 hover:text-emerald-800 transition cursor-pointer"
        >
          View Pipeline ➔
        </button>
      </div>

      {deploymentsState.status === 'unavailable' ? (
        <div className="p-6 text-center space-y-2">
          <p className="text-xs text-slate-500">Deployments service is standing by. Generate Terraform code to run execution plans.</p>
          <button
            onClick={() => onNavigate('iac', '/terraform')}
            className="px-3 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-medium rounded-lg transition cursor-pointer"
          >
            Check IaC Generator
          </button>
        </div>
      ) : deploymentsCount === 0 ? (
        <div className="p-6 text-center space-y-2">
          <p className="text-xs text-slate-500">No deployments triggered yet for active projects.</p>
          <button
            onClick={() => onNavigate('deployments', '/deployment')}
            className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold rounded-lg shadow-2xs transition cursor-pointer"
          >
            Open Execution Gate
          </button>
        </div>
      ) : (
        <div className="divide-y divide-slate-100">
          {deploymentsState.data.slice(0, 4).map((dep, idx) => (
            <div key={dep.id || idx} className="p-3.5 px-5 flex items-center justify-between gap-3 hover:bg-slate-50/50 transition">
              <div>
                <span className="text-xs font-bold text-slate-800">{dep.project_name || 'Cloud Workload'}</span>
                <div className="text-[11px] text-slate-400 font-mono">
                  {dep.environment || 'production'} • {dep.target_region || 'us-east-1'}
                </div>
              </div>
              <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-full ${
                dep.status === 'SUCCESS' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-slate-100 text-slate-700'
              }`}>
                {dep.status || 'COMPLETED'}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  // Widget 7: Microservices Health Probes (Layer B)
  const renderSystemHealthWidget = () => (
    <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
      <div className="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
        <div>
          <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <Server className="w-4 h-4 text-blue-600" />
            <span>Microservices Core Fleet</span>
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Decoupled service health, gateways, and broker status.
          </p>
        </div>
        <button
          onClick={() => fetchAllDashboardData(true)}
          disabled={refreshing}
          className="p-1.5 text-slate-400 hover:text-slate-700 rounded-lg transition cursor-pointer"
          title="Re-probe services"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin' : ''}`} />
        </button>
      </div>

      <div className="p-4 grid grid-cols-2 sm:grid-cols-3 2xl:grid-cols-6 gap-2 sm:gap-2.5">
        {[
          { code: 'gateway', name: 'API Gateway', port: 8000 },
          { code: 'projects', name: 'Project Mgr', port: 8001 },
          { code: 'connections', name: 'Source Broker', port: 8002 },
          { code: 'analyzer', name: 'AST Analyzer', port: 8003 },
          { code: 'architecture', name: 'Arch Studio', port: 8005 },
          { code: 'deployer', name: 'Deployer Engine', port: 8011 },
        ].map((svc) => {
          const probe = fleetProbes[svc.code] || { status: 'ONLINE', latency: 12 };
          const isOnline = probe.status === 'ONLINE';

          return (
            <div key={svc.code} className="p-2.5 rounded-xl border border-slate-100 bg-slate-50/70 flex flex-col justify-between gap-1">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-bold text-slate-800 truncate">{svc.name}</span>
                <span className={`w-2 h-2 rounded-full ${isOnline ? 'bg-emerald-500' : 'bg-rose-500 animate-pulse'}`} />
              </div>
              <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono">
                <span>Port {svc.port}</span>
                <span>{probe.latency}ms</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );

  // Widget 8: Recent Activity Log (Layer B)
  const renderRecentActivityWidget = () => (
    <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
      <div className="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
        <div>
          <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <Activity className="w-4 h-4 text-cyan-600" />
            <span>Audit &amp; Operations Activity</span>
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Chronological log of workspace configurations and cloud deployments.
          </p>
        </div>
        <button
          onClick={() => onNavigate('audit', '/audit')}
          className="text-xs font-semibold text-cyan-700 hover:text-cyan-900 transition cursor-pointer"
        >
          Audit History ➔
        </button>
      </div>

      <div className="divide-y divide-slate-100 text-xs">
        {projectsCount > 0 ? (
          projectsState.data.slice(0, 4).map((p, idx) => (
            <div key={p.id || idx} className="p-3.5 px-5 flex items-start gap-3">
              <Clock className="w-3.5 h-3.5 text-slate-400 mt-0.5 shrink-0" />
              <div className="min-w-0 flex-1">
                <span className="font-semibold text-slate-800">Workspace Configured: {p.name}</span>
                <div className="text-[11px] text-slate-400 font-mono mt-0.5">
                  Type: {p.project_type || 'web_application'} • Tenant: {user?.account_id || 'personal'}
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="p-6 text-center text-xs text-slate-500">
            No events recorded. Activity will automatically log as projects and architectures are modified.
          </div>
        )}
      </div>
    </div>
  );

  // Widget 9: Recommendations Engine (Layer C - Intelligent UI)
  const renderRecommendationsWidget = () => {
    const rec = dashboardSummary?.recommended_action || {
      id: 'default_rec',
      title: lifecycleStage === 'stage_1_onboarding' ? 'Create Your First Project Workspace' : 'Continue Architecture Sizing',
      description: lifecycleDescription,
      action_label: lifecycleStage === 'stage_1_onboarding' ? 'Create Project' : 'Open Studio',
      route: lifecycleStage === 'stage_1_onboarding' ? '/projects' : '/architecture-studio',
      action_type: lifecycleStage === 'stage_1_onboarding' ? 'modal' : 'navigate',
    };

    return (
      <div className="bg-gradient-to-r from-blue-900 via-indigo-900 to-slate-900 text-white rounded-2xl p-5 sm:p-6 shadow-md border border-slate-700 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1 max-w-2xl">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-cyan-400/20 text-cyan-300 text-[10px] font-bold font-mono border border-cyan-400/30">
              <Sparkles className="w-3 h-3 text-cyan-300" />
              INTELLIGENT WORKFLOW SUGGESTION
            </span>
          </div>
          <h3 className="text-base font-bold tracking-tight">{rec.title}</h3>
          <p className="text-xs text-slate-300 leading-relaxed">{rec.description}</p>
        </div>

        <button
          onClick={() => {
            if (rec.action_type === 'modal') {
              handleCreateProjectClick();
            } else {
              const targetPath = rec.route.startsWith('/') ? rec.route : `/${rec.route}`;
              onNavigate(targetPath);
            }
          }}
          className="px-4 py-2 bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white text-xs font-bold rounded-xl shadow-lg shadow-blue-500/20 transition flex items-center gap-2 cursor-pointer shrink-0"
        >
          <span>{rec.action_label}</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>
    );
  };

  const renderExperienceHeroBanner = () => {
    if (effectiveLifecycleStage === 'stage_1_onboarding') {
      return (
        <div className="bg-gradient-to-br from-blue-900 via-indigo-900 to-slate-900 text-white rounded-2xl p-6 sm:p-8 shadow-md relative overflow-hidden space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-800/80 border border-blue-700 text-cyan-300 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            New User Guided Onboarding Experience
          </div>
          <div className="space-y-2 max-w-2xl">
            <h2 className="text-xl sm:text-2xl font-extrabold tracking-tight">
              Welcome to AetherOps, {username}!
            </h2>
            <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
              Your cloud engineering workspace starts here. Build, validate and deploy AWS cloud infrastructure with an intelligent engineering workflow.
            </p>
          </div>
          <div className="pt-2 flex flex-wrap items-center gap-3">
            <button
              onClick={handleCreateProjectClick}
              className="px-5 py-2.5 bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-xs font-bold rounded-xl shadow-md transition flex items-center gap-2 cursor-pointer"
            >
              <Plus className="w-4 h-4" />
              <span>Create Your First Project</span>
            </button>
            <button
              onClick={() => onNavigate('docs', '/documentation')}
              className="px-4 py-2.5 bg-white/10 hover:bg-white/20 text-white text-xs font-semibold rounded-xl transition cursor-pointer border border-white/20"
            >
              Explore Platform Guide
            </button>
          </div>
        </div>
      );
    }

    if (effectiveLifecycleStage === 'stage_2_project_created' || effectiveLifecycleStage === 'stage_3_infrastructure_workflow') {
      const topProj = projectsState.data[0] || {};
      return (
        <div className="bg-gradient-to-r from-indigo-900 via-blue-900 to-slate-900 text-white rounded-2xl p-6 sm:p-7 shadow-md space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-800/80 border border-indigo-700 text-indigo-200 text-xs font-semibold">
            <RefreshCw className="w-3.5 h-3.5 animate-spin text-cyan-400" />
            Returning User Continuation Workflow
          </div>
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="space-y-1">
              <h2 className="text-xl font-bold tracking-tight">
                Welcome back, {username}!
              </h2>
              <p className="text-xs text-slate-300">
                Continue where you left off. Workspace: <strong className="text-white font-mono">{topProj.name || 'Default Project'}</strong> ({topProj.project_type || 'web_application'}).
              </p>
            </div>
            <button
              onClick={() => {
                if (topProj.id) {
                  onSelectProject(topProj);
                  onNavigate('projects', '/projects');
                } else {
                  handleCreateProjectClick();
                }
              }}
              className="px-4 py-2.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold rounded-xl shadow-md transition flex items-center gap-2 cursor-pointer shrink-0"
            >
              <span>Continue Project Workspace</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      );
    }

    return (
      <div className="bg-gradient-to-r from-slate-900 via-blue-950 to-indigo-950 text-white rounded-2xl p-6 sm:p-7 shadow-md space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800 border border-slate-700 text-emerald-400 text-xs font-semibold">
          <ShieldCheck className="w-3.5 h-3.5" />
          Experienced User • Cloud Operations Control Center
        </div>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <h2 className="text-xl font-bold tracking-tight">
              Active Multi-Project Infrastructure Fleet
            </h2>
            <p className="text-xs text-slate-300">
              Managing {projectsCount} isolated workspaces, {environmentsCount} target environments, and verified source/cloud credentials.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => onNavigate('deployments', '/deployment')}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-xl transition cursor-pointer flex items-center gap-1.5"
            >
              <Rocket className="w-3.5 h-3.5" />
              <span>Inspect Deployments</span>
            </button>
          </div>
        </div>
      </div>
    );
  };

  // ── 8. Render Engine mapping widgets to ordered grid ──
  const widgetRendererMap = {
    getting_started: renderGettingStartedWidget,
    overview_metrics: renderOverviewMetricsWidget,
    recent_projects: renderRecentProjectsWidget,
    environments_summary: renderEnvironmentsSummaryWidget,
    deployments_overview: renderDeploymentsOverviewWidget,
    attention_required: renderAttentionRequiredWidget,
    system_health: renderSystemHealthWidget,
    recent_activity: renderRecentActivityWidget,
    recommendations: renderRecommendationsWidget,
  };
  // Reorder and group: pinned widgets always take precedence at top
  const activeOrder = preferences.widget_order || DEFAULT_PREFERENCES.widget_order;
  const visibility = preferences.widget_visibility || DEFAULT_PREFERENCES.widget_visibility;
  const sizes = preferences.widget_sizes || DEFAULT_PREFERENCES.widget_sizes;
  const pinned = preferences.pinned_widgets || [];

  const sortedOrder = useMemo(() => {
    const pinnedSet = new Set(pinned);
    const pinnedList = activeOrder.filter((id) => pinnedSet.has(id));
    const unpinnedList = activeOrder.filter((id) => !pinnedSet.has(id));
    return [...pinnedList, ...unpinnedList];
  }, [activeOrder, pinned]);
  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* ── Layer A: Core UI (Greeting, Stage Intro, Action Bar, Layout Customization) ── */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3.5 pb-4 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
              {timeGreeting}, {username}
            </h1>
            {loading && (
              <RefreshCw className="w-3.5 h-3.5 animate-spin text-blue-600 shrink-0" />
            )}
          </div>
        </div>

        {/* Dashboard Quick Actions & Customization Button */}
        <div className="flex items-center gap-2 flex-wrap sm:flex-nowrap shrink-0 overflow-x-auto no-scrollbar py-0.5 w-full sm:w-auto">
          <button
            onClick={handleCreateProjectClick}
            className="px-3 py-1.5 bg-[#1e40af] hover:bg-[#1d4ed8] text-white text-xs font-semibold rounded-lg shadow-xs transition flex items-center gap-1.5 cursor-pointer shrink-0"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Create Project</span>
          </button>

          <button
            onClick={() => onNavigate('repo_analyzer', '/source-analysis')}
            className="px-3 py-1.5 bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 text-xs font-semibold rounded-lg shadow-2xs transition flex items-center gap-1.5 cursor-pointer shrink-0"
          >
            <FileCode2 className="w-3.5 h-3.5 text-blue-600" />
            <span className="inline">Analyze Code</span>
          </button>

          <button
            onClick={() => onNavigate('architecture_studio', '/architecture-studio')}
            className="px-3 py-1.5 bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 text-xs font-semibold rounded-lg shadow-2xs transition flex items-center gap-1.5 cursor-pointer shrink-0"
          >
            <Network className="w-3.5 h-3.5 text-indigo-600" />
            <span className="hidden sm:inline">Architecture Studio</span>
            <span className="sm:hidden">Studio</span>
          </button>
        </div>
      </div>

      {/* ── 1. ACCOUNT PROFILE SECTION ── */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="p-4 sm:p-5 border-b border-slate-100 bg-slate-50/60 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-[#1e40af] text-white flex items-center justify-center font-bold font-mono text-sm shadow-xs shrink-0">
              {(user?.username || 'AO').slice(0, 2).toUpperCase()}
            </div>
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <h2 className="text-sm sm:text-base font-bold text-slate-900 tracking-tight flex items-center gap-2">
                  <User className="w-4 h-4 text-blue-600" />
                  <span>Account Profile &amp; Workspace Identity</span>
                </h2>
                <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-slate-100 text-slate-700 border border-slate-200 font-mono">
                  {user?.role || 'USER'}
                </span>
              </div>
              <p className="text-xs text-slate-500 font-mono mt-0.5">
                Account ID: {formatAccountId(user?.account_id || '109283746519')}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={copyAccountId}
              className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-white hover:bg-slate-100 text-slate-700 border border-slate-200 shadow-2xs transition flex items-center gap-1.5 cursor-pointer shrink-0"
              title="Copy 12-Digit Account ID"
            >
              {copiedAcc ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5 text-slate-500" />}
              <span>{copiedAcc ? 'Copied Account ID' : 'Copy ID'}</span>
            </button>
          </div>
        </div>

        <div className="p-5 grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          {/* Identity Info */}
          <div className="bg-slate-50/80 p-3.5 rounded-xl border border-slate-100 space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="text-slate-500 flex items-center gap-1.5">
                <User className="w-3.5 h-3.5 text-slate-400" />
                Display Handle:
              </span>
              <span className="font-mono font-bold text-slate-900">{user?.username || 'Developer'}</span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-slate-500 flex items-center gap-1.5">
                <Mail className="w-3.5 h-3.5 text-slate-400" />
                Registered Email:
              </span>
              <span className="font-mono text-slate-700">{user?.email || `${user?.username || 'user'}@aetherops.internal`}</span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-slate-500 flex items-center gap-1.5">
                <Shield className="w-3.5 h-3.5 text-slate-400" />
                Authorization Role:
              </span>
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${isAdmin ? 'bg-indigo-50 text-indigo-700 border border-indigo-200' : 'bg-slate-100 text-slate-700'}`}>
                {isAdmin ? 'PLATFORM ADMIN' : 'WORKSPACE USER'}
              </span>
            </div>
          </div>

          {/* Tenant & Scope */}
          <div className="bg-slate-50/80 p-3.5 rounded-xl border border-slate-100 space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="text-slate-500 flex items-center gap-1.5">
                <FolderKanban className="w-3.5 h-3.5 text-slate-400" />
                Tenant Namespace:
              </span>
              <span className="font-mono font-bold text-slate-900">aetherops-default-tenant</span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-slate-500 flex items-center gap-1.5">
                <KeyRound className="w-3.5 h-3.5 text-slate-400" />
                Session Auth:
              </span>
              <span className="font-mono text-emerald-700 font-semibold">JWT Bearer &amp; Secure Cookie</span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-slate-500 flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-slate-400" />
                RBAC Isolation:
              </span>
              <span className="font-mono text-slate-700">Strict Tenant Scoped</span>
            </div>
          </div>

          {/* Quick Profile Actions */}
          <div className="bg-slate-50/80 p-3.5 rounded-xl border border-slate-100 flex flex-col justify-between gap-3">
            <div>
              <div className="text-[11px] font-bold text-slate-800 mb-1">Update Display Name</div>
              <form onSubmit={handleSaveProfile} className="flex items-center gap-2">
                <input
                  type="text"
                  value={newUsername}
                  onChange={(e) => setNewUsername(e.target.value)}
                  placeholder="New display handle"
                  className="flex-1 px-3 py-1.5 bg-white border border-slate-200 rounded-lg text-xs text-slate-900 focus:outline-none focus:border-blue-600"
                />
                <button
                  type="submit"
                  disabled={isSavingProfile}
                  className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded-lg shadow-xs transition cursor-pointer shrink-0 disabled:opacity-50"
                >
                  {isSavingProfile ? 'Saving...' : 'Save'}
                </button>
              </form>
            </div>
            {profileMsg && (
              <div className={`text-[11px] px-2 py-1 rounded ${profileMsg.type === 'success' ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'}`}>
                {profileMsg.text}
              </div>
            )}
          </div>
        </div>
      </div>
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="p-4 sm:p-5 border-b border-slate-100 bg-slate-50/60 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-[#1e40af] text-white flex items-center justify-center font-bold font-mono text-sm shadow-xs shrink-0">
              <div className="flex items-center gap-2 flex-wrap">
                <h2 className="text-sm sm:text-base font-bold text-slate-900 tracking-tight flex items-center gap-2">
                  <User className="w-4 h-4 text-blue-600" />
                  <span>Account Profile &amp; Workspace Identity</span>
                </h2>
                <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-slate-100 text-slate-700 border border-slate-200 font-mono">
                  {user?.role || 'USER'}
                </span>
              </div>
              <p className="text-xs text-slate-500 font-mono mt-0.5">
                Account ID: {formatAccountId(user?.account_id || '109283746519')}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={copyAccountId}
              className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-white hover:bg-slate-100 text-slate-700 border border-slate-200 shadow-2xs transition flex items-center gap-1.5 cursor-pointer shrink-0"
              title="Copy 12-Digit Account ID"
            >
              {copiedAcc ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5 text-slate-500" />}
              <span>{copiedAcc ? 'Copied Account ID' : 'Copy ID'}</span>
            </button>
          </div>
        </div>

        <div className="p-5 grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          {/* Identity Info */}
          <div className="bg-slate-50/80 p-3.5 rounded-xl border border-slate-100 space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="text-slate-500 flex items-center gap-1.5">
                <User className="w-3.5 h-3.5 text-slate-400" />
                Display Handle:
              </span>
              <span className="font-mono font-bold text-slate-900">{user?.username || 'Developer'}</span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-slate-500 flex items-center gap-1.5">
                <Mail className="w-3.5 h-3.5 text-slate-400" />
                Work Email:
              </span>
              <span className="font-mono text-slate-700 truncate max-w-[160px]">{user?.email || 'user@aetherops.cloud'}</span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-slate-500 flex items-center gap-1.5">
                <Shield className="w-3.5 h-3.5 text-slate-400" />
                Role:
              </span>
              <span className="font-mono font-semibold text-slate-800">{user?.role || 'USER'}</span>
            </div>
          </div>

          {/* Security Status */}
          <div className="bg-slate-50/80 p-3.5 rounded-xl border border-slate-100 space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="text-slate-500 flex items-center gap-1.5">
                <KeyRound className="w-3.5 h-3.5 text-slate-400" />
                Session Token:
              </span>
              <span className="text-[11px] font-mono text-emerald-700 font-semibold flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                Multi-Device JWT
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-slate-500 flex items-center gap-1.5">
                <Globe className="w-3.5 h-3.5 text-slate-400" />
                Network Access:
              </span>
              <span className="font-mono text-slate-700 font-medium">Tailscale Mesh / Local</span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-slate-500 flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-slate-400" />
                Multi-Device Sync:
              </span>
              <span className="font-mono text-emerald-700 font-semibold">Active &amp; Monitored</span>
            </div>
          </div>

          {/* Update Display Handle Form */}
          <form onSubmit={handleSaveProfile} className="bg-slate-50/80 p-3.5 rounded-xl border border-slate-100 flex flex-col justify-between gap-2">
            <div>
              <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-600 mb-1">
                Update Display Handle
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  required
                  minLength={3}
                  value={newUsername}
                  onChange={(e) => setNewUsername(e.target.value)}
                  placeholder="e.g. cloud_architect"
                  className="w-full px-2.5 py-1.5 text-xs font-mono bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-slate-900"
                />
                <button
                  type="submit"
                  disabled={isSavingProfile}
                  className="px-3 py-1.5 bg-[#1e40af] hover:bg-blue-700 text-white text-xs font-semibold rounded-lg shadow-2xs transition disabled:opacity-50 shrink-0 cursor-pointer"
                >
                  {isSavingProfile ? 'Saving...' : 'Save'}
                </button>
              </div>
            </div>
            {profileMsg && (
              <span className={`text-[10px] font-medium ${profileMsg.type === 'success' ? 'text-emerald-700' : 'text-rose-700'}`}>
                {profileMsg.text}
              </span>
            )}
          </form>
        </div>
      </div>

      {/* ── 2. LOGIN SESSIONS & CONNECTED DEVICES SECTION ── */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="p-4 sm:p-5 border-b border-slate-100 bg-slate-50/60 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h2 className="text-sm sm:text-base font-bold text-slate-900 tracking-tight flex items-center gap-2">
                <Smartphone className="w-4 h-4 text-indigo-600" />
                <span>Login Sessions &amp; Connected Devices</span>
              </h2>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-300 flex items-center gap-1 font-mono">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                {sessionsData.active_count} Active {sessionsData.active_count === 1 ? 'Device' : 'Devices'}
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Real-time multi-device detection (e.g. mobile phone &amp; laptop). Automatically synchronizes across all clients.
            </p>
          </div>

          <div className="flex items-center gap-2">
            {sessionsData.active_count > 1 && (
              <button
                type="button"
                onClick={handleRevokeAllOthers}
                disabled={revokingOthers}
                className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 shadow-2xs transition flex items-center gap-1.5 cursor-pointer shrink-0 disabled:opacity-50"
                title="Disconnect all other devices"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>{revokingOthers ? 'Logging out...' : 'Log Out All Others'}</span>
              </button>
            )}

            <button
              type="button"
              onClick={() => fetchSessions(false)}
              disabled={loadingSessions || refreshingSessions}
              className="p-1.5 text-slate-400 hover:text-slate-700 rounded-lg transition cursor-pointer"
              title="Refresh sessions"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${refreshingSessions ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {/* Feedback Alert */}
        {sessionStatusMsg && (
          <div className={`p-3 mx-5 mt-4 rounded-xl text-xs font-medium flex items-center justify-between ${
            sessionStatusMsg.type === 'success' ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-rose-50 text-rose-800 border border-rose-200'
          }`}>
            <span>{sessionStatusMsg.text}</span>
            <button onClick={() => setSessionStatusMsg(null)} className="font-bold text-slate-400 hover:text-slate-600">✕</button>
          </div>
        )}

        <div className="p-5 space-y-4">
          {/* Active Devices Grid */}
          {sessionsData.active_sessions.length === 0 ? (
            <div className="p-8 text-center text-xs text-slate-400">Loading active devices...</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {sessionsData.active_sessions.map((sess) => (
                 <div
                   key={sess.session_id}
                   className={`p-4 rounded-xl border transition flex flex-col justify-between shadow-2xs ${
                     sess.is_current
                       ? 'bg-blue-50/40 border-blue-200 ring-1 ring-blue-500/20'
                       : 'bg-white border-slate-200 hover:border-slate-300'
                   }`}
                 >
                   <div>
                     <div className="flex items-start justify-between gap-3">
                       <div className="flex items-center gap-3">
                         <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${
                           sess.is_current ? 'bg-blue-100 text-blue-700' : 'bg-slate-100 text-slate-600'
                         }`}>
                           {renderDeviceIcon(sess.device_type)}
                         </div>
                         <div>
                           <div className="text-xs font-bold text-slate-900">
                             {sess.device_info || `${sess.device_type} · ${sess.os} · ${sess.browser}`}
                           </div>
                           <div className="text-[11px] text-slate-500">
                             OS: <strong>{sess.os}</strong> • Browser: <strong>{sess.browser}</strong>
                           </div>
                         </div>
                       </div>

                       {sess.is_current ? (
                         <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-100 text-blue-800 border border-blue-300 flex items-center gap-1 shrink-0">
                           <span className="w-1.5 h-1.5 rounded-full bg-blue-600 animate-pulse" />
                           This Device
                         </span>
                       ) : (
                         <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-100 text-emerald-800 border border-emerald-300 flex items-center gap-1 shrink-0">
                           <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                           {formatSessionTimeAgo(sess.last_active_at)}
                         </span>
                       )}
                     </div>

                     <div className="mt-3 pt-2.5 border-t border-slate-100 grid grid-cols-2 gap-2 text-xs">
                       <div className="bg-slate-50 p-2 rounded-lg font-mono text-[11px] text-slate-700 truncate flex items-center gap-1">
                         <Globe className="w-3 h-3 text-slate-400 shrink-0" />
                         <span>{sess.ip_address}</span>
                       </div>
                       <div className="bg-slate-50 p-2 rounded-lg font-mono text-[11px] text-slate-600 truncate flex items-center gap-1">
                         <Clock className="w-3 h-3 text-slate-400 shrink-0" />
                         <span>{formatSessionTime(sess.created_at)}</span>
                       </div>
                     </div>
                   </div>

                   {!sess.is_current && (
                     <div className="mt-3 pt-2.5 border-t border-slate-100 flex justify-end">
                       <button
                         type="button"
                         onClick={() => handleRevokeSession(sess.session_id, sess.device_info)}
                         disabled={revokingId === sess.session_id}
                         className="px-3 py-1 text-xs font-semibold rounded-lg bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 transition flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                       >
                         <LogOut className="w-3.5 h-3.5" />
                         <span>{revokingId === sess.session_id ? 'Logging out...' : 'Log Out Device'}</span>
                       </button>
                     </div>
                   )}
                 </div>
               ))}
             </div>
           )}

          {/* Historical Logged Out Sessions */}
          {sessionsData.past_sessions && sessionsData.past_sessions.length > 0 && (
            <div className="pt-2">
              <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">
                Recent Disconnected Devices (Saved in Database)
              </div>
              <div className="divide-y divide-slate-100 border border-slate-200 rounded-xl overflow-hidden bg-slate-50/50 text-xs">
                {sessionsData.past_sessions.slice(0, 4).map((p) => (
                  <div key={p.session_id} className="p-2.5 px-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      {renderDeviceIcon(p.device_type)}
                      <span className="font-semibold text-slate-800">{p.device_info}</span>
                      <span className="text-[10px] text-slate-400 font-mono">({p.ip_address})</span>
                    </div>
                    <div className="text-[10px] font-mono text-slate-500 flex items-center gap-2">
                      <span className="px-1.5 py-0.2 rounded bg-slate-200 text-slate-700">
                        {p.logout_reason || 'DISCONNECTED'}
                      </span>
                      <span>{formatSessionTime(p.logout_at || p.last_active_at)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* ── 3. SESSION SECURITY AUDIT TRAIL SECTION ── */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="p-4 sm:p-5 border-b border-slate-100 bg-slate-50/60 flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h2 className="text-sm sm:text-base font-bold text-slate-900 tracking-tight flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-blue-600" />
                <span>Session Security Audit Trail</span>
              </h2>
              <span className="px-2 py-0.5 rounded text-xs font-mono font-semibold bg-slate-100 text-slate-700 border border-slate-200">
                {filteredAuditLogs.length} Events Recorded
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Chronological cryptographic security ledger of all device logins, logouts, and remote revocations.
            </p>
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={auditSearchQuery}
                onChange={(e) => setAuditSearchQuery(e.target.value)}
                placeholder="Filter by IP, device..."
                className="pl-8 pr-3 py-1 bg-white border border-slate-200 rounded-lg text-xs font-mono text-slate-800 focus:outline-none focus:ring-1 focus:ring-blue-500 w-44"
              />
            </div>

            <div className="flex items-center gap-1">
              {['ALL', 'LOGIN', 'LOGOUT', 'SESSION_REVOKED'].map((filter) => (
                <button
                  key={filter}
                  onClick={() => setAuditEventFilter(filter)}
                  className={`px-2.5 py-1 rounded-md text-[11px] font-semibold transition cursor-pointer ${
                    auditEventFilter === filter
                      ? 'bg-blue-600 text-white shadow-2xs'
                      : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
                  }`}
                >
                  {filter === 'ALL' ? 'All' : filter.replace('_', ' ')}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="p-0">
          {filteredAuditLogs.length === 0 ? (
            <div className="p-8 text-center text-xs text-slate-400">
              No audit records matching criteria.
            </div>
          ) : (
            <div className="divide-y divide-slate-100 text-xs">
              {filteredAuditLogs.slice(0, 8).map((log) => {
                const isLogin = log.event_type === 'LOGIN';
                const isLogout = log.event_type === 'LOGOUT';
                const isRevoked = log.event_type === 'SESSION_REVOKED';

                return (
                  <div key={log.id} className="p-3.5 px-5 flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 hover:bg-slate-50/60 transition">
                    <div className="flex items-start sm:items-center gap-3 min-w-0">
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${
                        isLogin ? 'bg-emerald-100 text-emerald-700' : isRevoked ? 'bg-rose-100 text-rose-700' : 'bg-slate-100 text-slate-600'
                      }`}>
                        {isLogin ? <LogIn className="w-4 h-4" /> : isRevoked ? <ShieldAlert className="w-4 h-4" /> : <LogOut className="w-4 h-4" />}
                      </div>

                      <div className="min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className={`px-1.5 py-0.2 rounded text-[10px] font-mono font-bold uppercase ${
                            isLogin
                              ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                              : isRevoked
                              ? 'bg-rose-50 text-rose-800 border border-rose-200'
                              : 'bg-slate-100 text-slate-700 border border-slate-200'
                          }`}>
                            {log.event_type}
                          </span>
                          <span className="font-bold text-slate-900">{log.device_info}</span>
                          <span className="text-[10px] text-slate-400 font-mono">({log.ip_address})</span>
                        </div>
                        <p className="text-slate-500 text-[11px] mt-0.5 break-words">
                          {log.details}
                        </p>
                      </div>
                    </div>

                    <div className="text-[11px] font-mono text-slate-400 text-right shrink-0">
                      {formatSessionTime(log.timestamp)}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* ── Layer B & C: Widgets Grid with User Customization Order & Visibility ── */}
      {/* ── Layer B & C: Responsive Widgets Grid (Mobile: 1 col, Laptop: 2 cols, PC: 12 cols / 2-wide) ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 2xl:grid-cols-12 gap-4 sm:gap-6">
        {sortedOrder.map((widgetId) => {
          const renderer = widgetRendererMap[widgetId];
          if (!renderer) return null;

          const isEligible = WIDGET_REGISTRY[widgetId]?.isEligible;
          // Ineligible widgets are not rendered
          if (!isEligible) return null;

          const isVisible = visibility[widgetId] !== false;
          // Critical warnings in attention_required cannot be hidden
          const isCritical = widgetId === 'attention_required' && attentionItems.length > 0;
          if (!isVisible && !isCritical) return null;

          const size = sizes[widgetId] || 'full';
          const colSpanClass = size === 'half' ? 'col-span-1 2xl:col-span-6' : 'col-span-1 lg:col-span-2 2xl:col-span-12';

          return (
            <div key={widgetId} className={`${colSpanClass} transition duration-150`}>
              {renderer()}
            </div>
          );
        })}
      </div>

      {/* ── Widget Customization Modal ── */}
      <WidgetCustomizerModal
        isOpen={isCustomizerOpen}
        onClose={() => setIsCustomizerOpen(false)}
        widgetRegistry={WIDGET_REGISTRY}
        preferences={preferences}
        onSavePreferences={handleSavePreferences}
        onResetPreferences={handleResetPreferences}
      />
    </div>
  );
}
