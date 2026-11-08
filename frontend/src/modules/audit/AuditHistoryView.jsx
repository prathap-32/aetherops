// frontend/src/modules/audit/AuditHistoryView.jsx
import React, { useState, useEffect } from 'react';
import {
  Shield,
  ShieldCheck,
  ShieldAlert,
  RefreshCw,
  Smartphone,
  Laptop,
  Tablet,
  Globe,
  Clock,
  LogIn,
  LogOut,
  Trash2,
  Search,
  Filter,
  AlertTriangle,
  Key,
  Activity,
  CheckCircle2,
  Copy,
  Check,
  ExternalLink
} from 'lucide-react';
import { authApi, adminApi, formatAccountId } from '../../services/api';
import { useAuth } from '../../context/AuthContext';

export default function AuditHistoryView({ onNavigate }) {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('sessions'); // 'sessions' | 'audit_trail' | 'operations'
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [statusMsg, setStatusMsg] = useState(null);

  // Sessions state from /api/v1/auth/sessions
  const [sessionsData, setSessionsData] = useState({
    active_count: 0,
    past_count: 0,
    current_session_id: null,
    active_sessions: [],
    past_sessions: [],
    audit_logs: [],
  });

  // Operations logs state from /api/v1/admin/audit
  const [operationLogs, setOperationLogs] = useState([]);

  // Search & Filter state
  const [searchQuery, setSearchQuery] = useState('');
  const [eventFilter, setEventFilter] = useState('ALL'); // 'ALL' | 'LOGIN' | 'LOGOUT' | 'SESSION_REVOKED'
  const [revokingId, setRevokingId] = useState(null);
  const [revokingOthers, setRevokingOthers] = useState(false);
  const [copiedId, setCopiedId] = useState(null);

  const fetchAllData = async (silent = false) => {
    if (!silent) setLoading(true);
    else setRefreshing(true);

    try {
      const [sessRes, opRes] = await Promise.all([
        authApi.getSessions().catch(() => null),
        adminApi.getAuditLogs().catch(() => ({ audit_logs: [] })),
      ]);

      if (sessRes && sessRes.status === 'SUCCESS') {
        setSessionsData(sessRes);
      }
      if (opRes && Array.isArray(opRes.audit_logs)) {
        setOperationLogs(opRes.audit_logs);
      }
    } catch (err) {
      console.warn('Failed to load audit data:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchAllData();
    // Auto-refresh sessions every 10 seconds while on this page
    const timer = setInterval(() => {
      fetchAllData(true);
    }, 10000);
    return () => clearInterval(timer);
  }, []);

  const handleRevokeSession = async (sessionId, deviceLabel) => {
    if (!window.confirm(`Are you sure you want to log out and terminate the session on ${deviceLabel}?`)) return;
    setRevokingId(sessionId);
    setStatusMsg(null);
    try {
      await authApi.revokeSession(sessionId);
      setStatusMsg({ type: 'success', text: `Successfully logged out session on ${deviceLabel}` });
      await fetchAllData(true);
    } catch (err) {
      setStatusMsg({ type: 'error', text: err.message || 'Failed to revoke session' });
    } finally {
      setRevokingId(null);
    }
  };

  const handleRevokeAllOthers = async () => {
    if (!window.confirm('Log out all other devices? Only this current device will remain logged in.')) return;
    setRevokingOthers(true);
    setStatusMsg(null);
    try {
      const res = await authApi.revokeOtherSessions();
      setStatusMsg({ type: 'success', text: res.message || 'All other devices logged out' });
      await fetchAllData(true);
    } catch (err) {
      setStatusMsg({ type: 'error', text: err.message || 'Failed to revoke other devices' });
    } finally {
      setRevokingOthers(false);
    }
  };

  const copyToClipboard = (text, id) => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(text);
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
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

  const formatTimestamp = (isoStr) => {
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

  const formatTimeAgo = (isoStr) => {
    if (!isoStr) return 'Just now';
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

  // Filter audit logs
  const filteredAuditLogs = (sessionsData.audit_logs || []).filter((item) => {
    if (eventFilter !== 'ALL' && item.event_type !== eventFilter) {
      return false;
    }
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const matchDevice = String(item.device_info || '').toLowerCase().includes(q);
      const matchIp = String(item.ip_address || '').toLowerCase().includes(q);
      const matchDetails = String(item.details || '').toLowerCase().includes(q);
      const matchEvent = String(item.event_type || '').toLowerCase().includes(q);
      return matchDevice || matchIp || matchDetails || matchEvent;
    }
    return true;
  });

  const currentDevice = sessionsData.active_sessions.find((s) => s.is_current) || sessionsData.active_sessions[0];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2.5 flex-wrap">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Security &amp; Session Audit</h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-300 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              Live Ledger
            </span>
            <span className="px-2.5 py-0.5 rounded text-xs font-mono font-semibold bg-slate-100 text-slate-700 border border-slate-200">
              Account: {formatAccountId(user?.account_id || '109283746519')}
            </span>
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Real-time multi-device session tracking, remote device revocation, and cryptographic security audit logs.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {sessionsData.active_count > 1 && (
            <button
              onClick={handleRevokeAllOthers}
              disabled={revokingOthers}
              className="px-3.5 py-2 rounded-xl bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 text-xs font-semibold transition flex items-center gap-1.5 cursor-pointer shadow-xs disabled:opacity-50"
              title="Terminate all sessions except this current device"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>{revokingOthers ? 'Logging out...' : 'Log Out All Other Devices'}</span>
            </button>
          )}

          <button
            onClick={() => fetchAllData(false)}
            disabled={loading || refreshing}
            className="px-3.5 py-2 rounded-xl bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-semibold transition flex items-center gap-1.5 cursor-pointer shadow-xs disabled:opacity-50"
            title="Refresh session and audit ledger"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${refreshing || loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Status Notifications */}
      {statusMsg && (
        <div
          className={`p-3.5 rounded-xl border text-xs font-medium flex items-center justify-between gap-3 ${
            statusMsg.type === 'success'
              ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
              : 'bg-rose-50 border-rose-200 text-rose-800'
          }`}
        >
          <div className="flex items-center gap-2">
            {statusMsg.type === 'success' ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            ) : (
              <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />
            )}
            <span>{statusMsg.text}</span>
          </div>
          <button
            onClick={() => setStatusMsg(null)}
            className="text-slate-400 hover:text-slate-600 text-xs font-bold"
          >
            ✕
          </button>
        </div>
      )}

      {/* Top Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Active Devices */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center shrink-0">
            <Smartphone className="w-6 h-6" />
          </div>
          <div>
            <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
              Active Devices
            </div>
            <div className="text-2xl font-bold font-mono text-slate-900 mt-0.5 flex items-center gap-2">
              <span>{sessionsData.active_count}</span>
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            </div>
            <div className="text-[11px] text-slate-500 mt-0.5">
              {sessionsData.active_count === 1 ? '1 active connection' : `${sessionsData.active_count} simultaneous devices`}
            </div>
          </div>
        </div>

        {/* Card 2: Recorded Audit Events */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center shrink-0">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
              Security Audit Logs
            </div>
            <div className="text-2xl font-bold font-mono text-slate-900 mt-0.5">
              {(sessionsData.audit_logs?.length || 0)}
            </div>
            <div className="text-[11px] text-slate-500 mt-0.5">
              Recorded in SQLite audit vault
            </div>
          </div>
        </div>

        {/* Card 3: Current Device */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-indigo-100 text-indigo-700 flex items-center justify-center shrink-0">
            <Laptop className="w-6 h-6" />
          </div>
          <div className="min-w-0">
            <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
              Current Device
            </div>
            <div className="text-xs font-bold text-slate-900 truncate mt-1">
              {currentDevice?.device_info || 'Current Terminal'}
            </div>
            <div className="text-[11px] font-mono text-indigo-700 mt-0.5 truncate">
              IP: {currentDevice?.ip_address || '127.0.0.1'}
            </div>
          </div>
        </div>

        {/* Card 4: Historical Sessions */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-slate-100 text-slate-700 flex items-center justify-center shrink-0">
            <Clock className="w-6 h-6" />
          </div>
          <div>
            <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
              Logged Out History
            </div>
            <div className="text-2xl font-bold font-mono text-slate-900 mt-0.5">
              {sessionsData.past_count || 0}
            </div>
            <div className="text-[11px] text-slate-500 mt-0.5">
              Archived in database
            </div>
          </div>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="flex items-center gap-2 border-b border-slate-200">
        <button
          onClick={() => setActiveTab('sessions')}
          className={`pb-3 px-4 text-xs font-semibold flex items-center gap-2 border-b-2 transition cursor-pointer ${
            activeTab === 'sessions'
              ? 'border-blue-600 text-blue-600 font-bold'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Smartphone className="w-4 h-4" />
          <span>Active Device Sessions ({sessionsData.active_count})</span>
        </button>

        <button
          onClick={() => setActiveTab('audit_trail')}
          className={`pb-3 px-4 text-xs font-semibold flex items-center gap-2 border-b-2 transition cursor-pointer ${
            activeTab === 'audit_trail'
              ? 'border-blue-600 text-blue-600 font-bold'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <ShieldAlert className="w-4 h-4" />
          <span>Login &amp; Security Audit Trail ({sessionsData.audit_logs?.length || 0})</span>
        </button>

        <button
          onClick={() => setActiveTab('operations')}
          className={`pb-3 px-4 text-xs font-semibold flex items-center gap-2 border-b-2 transition cursor-pointer ${
            activeTab === 'operations'
              ? 'border-blue-600 text-blue-600 font-bold'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Activity className="w-4 h-4" />
          <span>Platform Operations Ledger ({operationLogs.length})</span>
        </button>
      </div>

      {/* TAB 1: ACTIVE & PAST DEVICE SESSIONS */}
      {activeTab === 'sessions' && (
        <div className="space-y-6">
          {/* Active Sessions Grid */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <span>Real-Time Logged In Devices</span>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-emerald-100 text-emerald-800 border border-emerald-300">
                  {sessionsData.active_count} Connected
                </span>
              </h3>
              <span className="text-xs text-slate-500">
                Auto-polled live status (SQLite user_sessions)
              </span>
            </div>

            {loading ? (
              <div className="p-12 text-center text-xs text-slate-400 bg-white rounded-2xl border border-slate-200">
                Loading device sessions...
              </div>
            ) : sessionsData.active_sessions.length === 0 ? (
              <div className="p-12 text-center text-xs text-slate-400 bg-white rounded-2xl border border-slate-200">
                No active device sessions detected.
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {sessionsData.active_sessions.map((sess) => (
                  <div
                    key={sess.session_id}
                    className={`bg-white rounded-2xl p-5 border transition flex flex-col justify-between shadow-xs ${
                      sess.is_current
                        ? 'border-blue-300 ring-2 ring-blue-500/15'
                        : 'border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <div>
                      {/* Top Row: Device icon, Name & Status */}
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex items-center gap-3">
                          <div className={`w-11 h-11 rounded-xl flex items-center justify-center shrink-0 ${
                            sess.is_current ? 'bg-blue-100' : 'bg-slate-100'
                          }`}>
                            {renderDeviceIcon(sess.device_type)}
                          </div>
                          <div>
                            <div className="text-sm font-bold text-slate-900">
                              {sess.device_info || `${sess.device_type} · ${sess.os} · ${sess.browser}`}
                            </div>
                            <div className="text-[11px] text-slate-500">
                              OS: <strong>{sess.os}</strong> • Browser: <strong>{sess.browser}</strong>
                            </div>
                          </div>
                        </div>

                        {sess.is_current ? (
                          <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-blue-100 text-blue-800 border border-blue-300 flex items-center gap-1.5 shrink-0">
                            <span className="w-1.5 h-1.5 rounded-full bg-blue-600 animate-pulse" />
                            This Device
                          </span>
                        ) : (
                          <span className="px-2.5 py-1 rounded-full text-[10px] font-semibold bg-emerald-100 text-emerald-800 border border-emerald-300 flex items-center gap-1.5 shrink-0">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-600" />
                            {formatTimeAgo(sess.last_active_at)}
                          </span>
                        )}
                      </div>

                      {/* Technical Connection Details */}
                      <div className="mt-4 pt-3 border-t border-slate-100 grid grid-cols-2 gap-2 text-xs">
                        <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                          <div className="text-[10px] uppercase font-bold text-slate-400">
                            IP Address / Network
                          </div>
                          <div className="font-mono text-slate-800 font-semibold mt-0.5 truncate flex items-center gap-1">
                            <Globe className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                            <span>{sess.ip_address}</span>
                          </div>
                        </div>

                        <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                          <div className="text-[10px] uppercase font-bold text-slate-400">
                            Login Timestamp
                          </div>
                          <div className="font-mono text-slate-700 text-[11px] mt-0.5 truncate flex items-center gap-1">
                            <Clock className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                            <span>{formatTimestamp(sess.created_at)}</span>
                          </div>
                        </div>
                      </div>

                      <div className="mt-2 text-[10px] font-mono text-slate-400 flex items-center justify-between">
                        <span>Session ID: {sess.session_id.slice(0, 16)}...</span>
                        <button
                          onClick={() => copyToClipboard(sess.session_id, sess.session_id)}
                          className="hover:text-slate-600 underline cursor-pointer"
                        >
                          {copiedId === sess.session_id ? 'Copied' : 'Copy ID'}
                        </button>
                      </div>
                    </div>

                    {/* Footer / Revocation */}
                    <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
                      <span className="text-[11px] text-slate-400">
                        {sess.is_current ? 'Active session on this browser' : 'Remote active session'}
                      </span>

                      {!sess.is_current ? (
                        <button
                          onClick={() => handleRevokeSession(sess.session_id, sess.device_info)}
                          disabled={revokingId === sess.session_id}
                          className="px-3.5 py-1.5 rounded-xl bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 text-xs font-semibold transition flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                        >
                          <LogOut className="w-3.5 h-3.5" />
                          <span>{revokingId === sess.session_id ? 'Revoking...' : 'Log Out Device'}</span>
                        </button>
                      ) : (
                        <span className="text-xs font-medium text-slate-400 italic">
                          (Current session)
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Past Logged Out Sessions Table */}
          {sessionsData.past_sessions && sessionsData.past_sessions.length > 0 && (
            <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
              <div className="p-5 border-b border-slate-100 flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold text-slate-900">Historical Disconnected Devices</h3>
                  <p className="text-[11px] text-slate-500">
                    Sessions permanently stored in database after user sign-out or remote revocation.
                  </p>
                </div>
                <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                  {sessionsData.past_sessions.length} Recorded in DB
                </span>
              </div>

              <div className="divide-y divide-slate-100 text-xs">
                {sessionsData.past_sessions.map((p) => (
                  <div key={p.session_id} className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-slate-50/50 transition">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-xl bg-slate-100 text-slate-400 flex items-center justify-center shrink-0">
                        {renderDeviceIcon(p.device_type)}
                      </div>
                      <div>
                        <div className="font-semibold text-slate-800">
                          {p.device_info}
                        </div>
                        <div className="text-[11px] text-slate-500 font-mono flex items-center gap-2 mt-0.5">
                          <span>IP: {p.ip_address}</span>
                          <span>•</span>
                          <span>Logged in: {formatTimestamp(p.created_at)}</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 self-end sm:self-auto font-mono text-right">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-slate-100 text-slate-600 border border-slate-200">
                        {p.logout_reason || 'USER_LOGOUT'}
                      </span>
                      <div className="text-[11px] text-slate-500">
                        Disconnected: {formatTimestamp(p.logout_at || p.last_active_at)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: DETAILED LOGIN & SECURITY AUDIT TRAIL */}
      {activeTab === 'audit_trail' && (
        <div className="space-y-4">
          {/* Controls: Search and Event Filters */}
          <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-3">
            {/* Search Box */}
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search audit events by IP, device, or keyword..."
                className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-mono text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
              />
            </div>

            {/* Event Filter Buttons */}
            <div className="flex items-center gap-1.5 flex-wrap">
              {['ALL', 'LOGIN', 'LOGOUT', 'SESSION_REVOKED'].map((filter) => (
                <button
                  key={filter}
                  onClick={() => setEventFilter(filter)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer ${
                    eventFilter === filter
                      ? 'bg-blue-600 text-white shadow-2xs'
                      : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
                  }`}
                >
                  {filter === 'ALL' ? 'All Events' : filter.replace('_', ' ')}
                </button>
              ))}
            </div>
          </div>

          {/* Audit Ledger Table */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
            <div className="p-4 px-5 border-b border-slate-100 flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-slate-900">Session Security Audit Trail</h3>
                <p className="text-[11px] text-slate-500">
                  Chronological, immutable ledger of all authentications and remote session terminations.
                </p>
              </div>
              <span className="text-xs font-mono font-semibold text-slate-500">
                Showing {filteredAuditLogs.length} events
              </span>
            </div>

            {filteredAuditLogs.length === 0 ? (
              <div className="p-12 text-center text-xs text-slate-400">
                No audit events matching criteria.
              </div>
            ) : (
              <div className="divide-y divide-slate-100 text-xs">
                {filteredAuditLogs.map((log) => {
                  const isLogin = log.event_type === 'LOGIN';
                  const isLogout = log.event_type === 'LOGOUT';
                  const isRevoked = log.event_type === 'SESSION_REVOKED';

                  return (
                    <div
                      key={log.id}
                      className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-slate-50/60 transition"
                    >
                      <div className="flex items-start gap-3 min-w-0">
                        <div className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 mt-0.5 ${
                          isLogin
                            ? 'bg-emerald-100 text-emerald-700'
                            : isRevoked
                            ? 'bg-rose-100 text-rose-700'
                            : 'bg-slate-100 text-slate-600'
                        }`}>
                          {isLogin ? (
                            <LogIn className="w-4 h-4" />
                          ) : isRevoked ? (
                            <ShieldAlert className="w-4 h-4" />
                          ) : (
                            <LogOut className="w-4 h-4" />
                          )}
                        </div>

                        <div className="min-w-0">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase ${
                              isLogin
                                ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                                : isRevoked
                                ? 'bg-rose-50 text-rose-800 border border-rose-200'
                                : 'bg-slate-100 text-slate-700 border border-slate-200'
                            }`}>
                              {log.event_type}
                            </span>
                            <span className="font-bold text-slate-900">
                              {log.device_info}
                            </span>
                            <span className="text-[10px] text-slate-400 font-mono">
                              ({log.ip_address})
                            </span>
                          </div>

                          <p className="text-slate-600 text-[11px] mt-1 break-words">
                            {log.details}
                          </p>

                          <div className="text-[10px] text-slate-400 font-mono mt-1">
                            Event ID: {log.event_id}
                          </div>
                        </div>
                      </div>

                      <div className="text-right shrink-0 font-mono text-[11px] text-slate-500 self-end sm:self-auto">
                        {formatTimestamp(log.timestamp)}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 3: PLATFORM OPERATIONS LEDGER */}
      {activeTab === 'operations' && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
          <div className="p-5 border-b border-slate-100">
            <h3 className="text-sm font-bold text-slate-900">Recorded Infrastructure Operations</h3>
            <p className="text-[11px] text-slate-500">
              Administrative deployments, Terraform synthesis, and AWS configuration events
            </p>
          </div>

          {loading ? (
            <div className="p-12 text-center text-xs text-slate-400">Loading operations ledger...</div>
          ) : operationLogs.length === 0 ? (
            <div className="p-12 text-center text-xs text-slate-400">
              No administrative infrastructure events recorded in this session.
            </div>
          ) : (
            <div className="divide-y divide-slate-100 text-xs">
              {operationLogs.map((log) => (
                <div key={log.id} className="p-4 flex items-center justify-between hover:bg-slate-50/60 transition">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-slate-100 text-slate-600 flex items-center justify-center font-bold text-xs font-mono">
                      <Shield className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="text-xs font-bold text-slate-900 flex items-center gap-2">
                        <span>{log.action}</span>
                        <span className="text-[10px] font-mono text-slate-500 font-normal">by @{log.username}</span>
                      </div>
                      <div className="text-[10px] text-slate-500 mt-0.5">{log.details || 'System event'}</div>
                    </div>
                  </div>

                  <div className="text-right">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase ${
                        log.status === 'SUCCESS' ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'
                      }`}
                    >
                      {log.status}
                    </span>
                    <div className="text-[10px] font-mono text-slate-400 mt-1">
                      {formatTimestamp(log.created_at)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
