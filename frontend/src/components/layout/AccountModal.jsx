// frontend/src/components/layout/AccountModal.jsx
import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { authApi, formatAccountId } from '../../services/api';
import {
  X,
  User,
  Mail,
  Shield,
  KeyRound,
  Key,
  Copy,
  Check,
  LogOut,
  CheckCircle2,
  Smartphone,
  Laptop,
  Tablet,
  Globe,
  RefreshCw,
  Trash2,
  History,
  ShieldAlert,
  LogIn,
  Clock,
  Layers,
  AlertTriangle
} from 'lucide-react';

export default function AccountModal({ isOpen, onClose, showToast, onNavigate }) {
  const { user, isAdmin, updateProfile, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('sessions'); // 'profile' | 'sessions' | 'audit'

  // Profile Form state
  const [newUsername, setNewUsername] = useState(user?.username || '');
  const [isSaving, setIsSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [copiedAcc, setCopiedAcc] = useState(false);

  // Sessions & Devices state
  const [sessionsData, setSessionsData] = useState({
    active_count: 0,
    past_count: 0,
    current_session_id: null,
    active_sessions: [],
    past_sessions: [],
    audit_logs: [],
  });
  const [loadingSessions, setLoadingSessions] = useState(false);
  const [revokingId, setRevokingId] = useState(null);
  const [revokingOthers, setRevokingOthers] = useState(false);

  // Fetch real-time sessions data
  const fetchSessions = async (showSpinner = true) => {
    if (showSpinner) setLoadingSessions(true);
    try {
      const res = await authApi.getSessions();
      if (res && res.status === 'SUCCESS') {
        setSessionsData(res);
      }
    } catch (err) {
      console.warn('Failed to fetch user login sessions:', err);
    } finally {
      if (showSpinner) setLoadingSessions(false);
    }
  };

  // Poll sessions when modal is open
  useEffect(() => {
    if (isOpen) {
      fetchSessions(true);
      const timer = setInterval(() => {
        fetchSessions(false);
      }, 8000); // 8-second real-time poll
      return () => clearInterval(timer);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleUpdate = async (e) => {
    e.preventDefault();
    if (!newUsername.trim()) return;
    setIsSaving(true);
    setErrorMsg('');
    setSuccessMsg('');

    try {
      await updateProfile(newUsername.trim());
      setSuccessMsg(`Display name updated to "${newUsername.trim()}"!`);
      if (showToast) showToast(`Username updated to "${newUsername.trim()}"`);
      setTimeout(() => {
        setSuccessMsg('');
      }, 3000);
    } catch (err) {
      setErrorMsg(err.message || 'Failed to update username');
    } finally {
      setIsSaving(false);
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

  const handleRevokeSession = async (sessionId, deviceLabel) => {
    if (!window.confirm(`Log out and revoke the session on ${deviceLabel}?`)) return;
    setRevokingId(sessionId);
    setErrorMsg('');
    try {
      await authApi.revokeSession(sessionId);
      if (showToast) showToast(`Logged out session on ${deviceLabel}`);
      await fetchSessions(false);
    } catch (err) {
      setErrorMsg(err.message || 'Failed to revoke session');
    } finally {
      setRevokingId(null);
    }
  };

  const handleRevokeAllOthers = async () => {
    if (!window.confirm('Log out all other devices? Only this current device will stay logged in.')) return;
    setRevokingOthers(true);
    setErrorMsg('');
    try {
      const res = await authApi.revokeOtherSessions();
      if (showToast) showToast(res.message || 'All other devices logged out');
      await fetchSessions(false);
    } catch (err) {
      setErrorMsg(err.message || 'Failed to revoke other devices');
    } finally {
      setRevokingOthers(false);
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
        hour: '2-digit',
        minute: '2-digit',
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

  const initials = (user?.username || 'AO').slice(0, 2).toUpperCase();

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-slate-900/40 backdrop-blur-xs">
      <div className="bg-white border border-slate-200 rounded-2xl w-full max-w-xl max-h-[90vh] flex flex-col shadow-2xl animate-in fade-in zoom-in-95 duration-150 overflow-hidden">
        {/* Modal Top Header */}
        <div className="p-5 pb-3 border-b border-slate-100 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-[#1e40af] text-white flex items-center justify-center font-bold font-mono text-sm shadow-xs shrink-0">
              {initials}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-slate-900 tracking-tight">
                  {user?.username || 'User Profile'}
                </h2>
                <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-slate-100 text-slate-600 border border-slate-200">
                  {user?.role || 'USER'}
                </span>
              </div>
              <p className="text-xs text-slate-500 font-mono">
                Account ID: {formatAccountId(user?.account_id || '109283746519')}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 p-1.5 rounded-lg hover:bg-slate-100 transition cursor-pointer"
            title="Close modal"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="px-5 pt-2 border-b border-slate-200 bg-slate-50/70 flex items-center justify-between gap-2 shrink-0">
          <div className="flex items-center gap-1">
            <button
              type="button"
              onClick={() => setActiveTab('sessions')}
              className={`px-3 py-2 text-xs font-semibold rounded-t-lg transition flex items-center gap-1.5 border-b-2 cursor-pointer ${
                activeTab === 'sessions'
                  ? 'border-blue-600 text-blue-600 bg-white font-bold'
                  : 'border-transparent text-slate-600 hover:text-slate-900'
              }`}
            >
              <Smartphone className="w-3.5 h-3.5" />
              <span>Login Sessions</span>
              <span className="ml-1 px-1.5 py-0.2 text-[10px] rounded-full font-mono font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
                {sessionsData.active_count || 1}
              </span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab('profile')}
              className={`px-3 py-2 text-xs font-semibold rounded-t-lg transition flex items-center gap-1.5 border-b-2 cursor-pointer ${
                activeTab === 'profile'
                  ? 'border-blue-600 text-blue-600 bg-white font-bold'
                  : 'border-transparent text-slate-600 hover:text-slate-900'
              }`}
            >
              <User className="w-3.5 h-3.5" />
              <span>Account Profile</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab('audit')}
              className={`px-3 py-2 text-xs font-semibold rounded-t-lg transition flex items-center gap-1.5 border-b-2 cursor-pointer ${
                activeTab === 'audit'
                  ? 'border-blue-600 text-blue-600 bg-white font-bold'
                  : 'border-transparent text-slate-600 hover:text-slate-900'
              }`}
            >
              <History className="w-3.5 h-3.5" />
              <span>Audit Log</span>
            </button>
          </div>

          {activeTab === 'sessions' && (
            <button
              type="button"
              onClick={() => fetchSessions(true)}
              disabled={loadingSessions}
              className="text-[11px] text-slate-500 hover:text-slate-800 flex items-center gap-1 transition disabled:opacity-50 cursor-pointer"
              title="Refresh sessions"
            >
              <RefreshCw className={`w-3 h-3 ${loadingSessions ? 'animate-spin' : ''}`} />
              <span className="hidden sm:inline">Refresh</span>
            </button>
          )}
        </div>

        {/* Modal Scrollable Body */}
        <div className="p-5 overflow-y-auto space-y-4 flex-1">
          {/* Feedback messages */}
          {errorMsg && (
            <div className="p-2.5 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-xs font-medium flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}
          {successMsg && (
            <div className="p-2.5 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-medium flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>{successMsg}</span>
            </div>
          )}

          {/* TAB 1: LOGIN SESSIONS & DEVICES */}
          {activeTab === 'sessions' && (
            <div className="space-y-4">
              {/* Top Banner: Device Count & Bulk Revoke */}
              <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center shrink-0">
                    <Shield className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-slate-900">
                      {sessionsData.active_count} Active {sessionsData.active_count === 1 ? 'Device' : 'Devices'} Logged In
                    </h4>
                    <p className="text-[11px] text-slate-500">
                      You are logged in on multiple devices (e.g. mobile &amp; laptop). Manage or revoke access below.
                    </p>
                  </div>
                </div>

                {sessionsData.active_count > 1 && (
                  <button
                    type="button"
                    onClick={handleRevokeAllOthers}
                    disabled={revokingOthers}
                    className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 shadow-2xs transition flex items-center justify-center gap-1.5 cursor-pointer shrink-0 disabled:opacity-50"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                    <span>{revokingOthers ? 'Logging out...' : 'Log Out All Others'}</span>
                  </button>
                )}
              </div>

              {/* Active Sessions List */}
              <div className="space-y-2.5">
                <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider flex items-center justify-between">
                  <span>Active Device Sessions</span>
                  <span className="text-emerald-700 font-mono text-[10px]">Real-time Status</span>
                </div>

                {sessionsData.active_sessions.length === 0 ? (
                  <div className="p-4 rounded-xl border border-slate-200 text-center text-xs text-slate-400">
                    No active sessions found.
                  </div>
                ) : (
                  sessionsData.active_sessions.map((sess) => (
                    <div
                      key={sess.session_id}
                      className={`p-3.5 rounded-xl border transition flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${
                        sess.is_current
                          ? 'bg-blue-50/50 border-blue-200 ring-1 ring-blue-500/20'
                          : 'bg-white border-slate-200 hover:border-slate-300'
                      }`}
                    >
                      <div className="flex items-start gap-3 min-w-0">
                        <div className="w-9 h-9 rounded-xl bg-slate-100 flex items-center justify-center shrink-0 mt-0.5">
                          {renderDeviceIcon(sess.device_type)}
                        </div>
                        <div className="min-w-0">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="text-xs font-bold text-slate-900 truncate">
                              {sess.device_info || `${sess.device_type} · ${sess.os} · ${sess.browser}`}
                            </span>
                            {sess.is_current ? (
                              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-100 text-blue-800 border border-blue-300 flex items-center gap-1">
                                <span className="w-1.5 h-1.5 rounded-full bg-blue-600 animate-pulse" />
                                Current Device
                              </span>
                            ) : (
                              <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center gap-1">
                                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                                {formatTimeAgo(sess.last_active_at)}
                              </span>
                            )}
                          </div>

                          <div className="flex items-center gap-3 text-[11px] text-slate-500 mt-1 flex-wrap">
                            <span className="font-mono flex items-center gap-1">
                              <Globe className="w-3 h-3 text-slate-400" />
                              {sess.ip_address}
                            </span>
                            <span>•</span>
                            <span className="flex items-center gap-1">
                              <Clock className="w-3 h-3 text-slate-400" />
                              Logged in: {formatTimestamp(sess.created_at)}
                            </span>
                          </div>
                        </div>
                      </div>

                      {/* Action: Log Out Session (Non-current devices) */}
                      {!sess.is_current && (
                        <button
                          type="button"
                          onClick={() => handleRevokeSession(sess.session_id, sess.device_info)}
                          disabled={revokingId === sess.session_id}
                          className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-50 hover:bg-rose-50 text-slate-700 hover:text-rose-700 border border-slate-200 hover:border-rose-200 transition flex items-center justify-center gap-1 cursor-pointer shrink-0 disabled:opacity-50"
                          title="Remotely disconnect this device"
                        >
                          <LogOut className="w-3.5 h-3.5" />
                          <span>{revokingId === sess.session_id ? 'Logging out...' : 'Log Out Device'}</span>
                        </button>
                      )}
                    </div>
                  ))
                )}
              </div>

              {/* Past / Logged Out Sessions History */}
              {sessionsData.past_sessions && sessionsData.past_sessions.length > 0 && (
                <div className="space-y-2 pt-2">
                  <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                    Recent Logged Out Sessions (Database History)
                  </div>
                  <div className="divide-y divide-slate-100 border border-slate-200 rounded-xl overflow-hidden bg-slate-50/50">
                    {sessionsData.past_sessions.slice(0, 5).map((p) => (
                      <div key={p.session_id} className="p-2.5 px-3 flex items-center justify-between text-xs">
                        <div className="flex items-center gap-2">
                          {renderDeviceIcon(p.device_type)}
                          <span className="font-medium text-slate-700">
                            {p.device_info}
                          </span>
                          <span className="text-[10px] text-slate-400 font-mono">({p.ip_address})</span>
                        </div>
                        <div className="text-[11px] text-slate-400 flex items-center gap-2 font-mono">
                          <span className="px-1.5 py-0.2 rounded bg-slate-200/60 text-slate-600 text-[10px]">
                            {p.logout_reason || 'LOGGED_OUT'}
                          </span>
                          <span>{formatTimestamp(p.logout_at || p.last_active_at)}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 2: PROFILE & ACCOUNT DETAILS */}
          {activeTab === 'profile' && (
            <div className="space-y-4">
              {/* Account Details Box */}
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between">
                <div>
                  <div className="text-xs font-semibold text-slate-500 flex items-center gap-1.5 mb-1">
                    <Key className="w-3.5 h-3.5 text-blue-600" />
                    AWS-Style Account ID
                  </div>
                  <div className="text-sm font-mono font-bold text-slate-900">
                    {formatAccountId(user?.account_id || '109283746519')}
                  </div>
                </div>
                <button
                  type="button"
                  onClick={copyAccountId}
                  title="Copy Account ID"
                  className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-white hover:bg-slate-100 text-slate-700 border border-slate-200 shadow-xs transition flex items-center gap-1.5 cursor-pointer shrink-0"
                >
                  {copiedAcc ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5 text-slate-600" />}
                  <span>{copiedAcc ? 'Copied' : 'Copy'}</span>
                </button>
              </div>

              {/* Info Card */}
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 space-y-3">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-500 flex items-center gap-1.5">
                    <User className="w-3.5 h-3.5" />
                    Username:
                  </span>
                  <span className="font-mono font-bold text-slate-900">{user?.username}</span>
                </div>

                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-500 flex items-center gap-1.5">
                    <Mail className="w-3.5 h-3.5" />
                    Work Email:
                  </span>
                  <span className="font-mono text-slate-700">{user?.email}</span>
                </div>

                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-500 flex items-center gap-1.5">
                    <Shield className="w-3.5 h-3.5" />
                    Assigned Role:
                  </span>
                  <span
                    className={`px-2 py-0.5 rounded text-xs font-mono font-semibold uppercase border ${
                      isAdmin
                        ? 'bg-blue-50 text-blue-800 border-blue-200'
                        : 'bg-emerald-50 text-emerald-700 border-emerald-200'
                    }`}
                  >
                    {user?.role || 'USER'}
                  </span>
                </div>

                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-500 flex items-center gap-1.5">
                    <KeyRound className="w-3.5 h-3.5" />
                    Security Protocol:
                  </span>
                  <span className="text-[11px] font-mono text-emerald-600 flex items-center gap-1 font-semibold">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                    HMAC-SHA256 Multi-Device JWT
                  </span>
                </div>
              </div>

              {/* Change Display Name form */}
              <form onSubmit={handleUpdate} className="space-y-2 pt-1">
                <label className="block text-xs font-semibold text-slate-700">
                  Update Display Name / Handle
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    required
                    minLength={3}
                    value={newUsername}
                    onChange={(e) => setNewUsername(e.target.value)}
                    placeholder="e.g. cloud_engineer"
                    className="flex-1 px-3 py-2 text-xs font-mono rounded-lg border border-slate-300 focus:outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600"
                  />
                  <button
                    type="submit"
                    disabled={isSaving}
                    className="px-3.5 py-2 text-xs font-semibold rounded-lg bg-[#1e40af] hover:bg-blue-700 text-white shadow-xs transition disabled:opacity-50 cursor-pointer"
                  >
                    {isSaving ? 'Saving...' : 'Update'}
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* TAB 3: AUDIT LOGS */}
          {activeTab === 'audit' && (
            <div className="space-y-3">
              <div className="flex items-center justify-between gap-2">
                <div>
                  <h4 className="text-xs font-bold text-slate-900">Session Security Audit Trail</h4>
                  <p className="text-[11px] text-slate-500">
                    Chronological audit log of all device logins, logouts, and remote session revocations.
                  </p>
                </div>
                {onNavigate && (
                  <button
                    type="button"
                    onClick={() => {
                      onClose();
                      onNavigate('audit', '/audit');
                    }}
                    className="text-xs text-blue-600 hover:text-blue-800 font-semibold flex items-center gap-1 cursor-pointer shrink-0 underline"
                  >
                    <span>Full Audit Center</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>

              {sessionsData.audit_logs && sessionsData.audit_logs.length > 0 ? (
                <div className="divide-y divide-slate-100 border border-slate-200 rounded-xl overflow-hidden bg-white text-xs">
                  {sessionsData.audit_logs.map((log) => {
                    const isLogin = log.event_type === 'LOGIN';
                    const isLogout = log.event_type === 'LOGOUT';
                    const isRevoked = log.event_type === 'SESSION_REVOKED';

                    return (
                      <div key={log.id} className="p-3 flex items-start justify-between gap-3 hover:bg-slate-50/60 transition">
                        <div className="flex items-start gap-2.5 min-w-0">
                          <div className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 mt-0.5 ${
                            isLogin
                              ? 'bg-emerald-100 text-emerald-700'
                              : isRevoked
                              ? 'bg-rose-100 text-rose-700'
                              : 'bg-slate-100 text-slate-600'
                          }`}>
                            {isLogin ? (
                              <LogIn className="w-3.5 h-3.5" />
                            ) : isRevoked ? (
                              <ShieldAlert className="w-3.5 h-3.5" />
                            ) : (
                              <LogOut className="w-3.5 h-3.5" />
                            )}
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
                              <span className="font-semibold text-slate-900">
                                {log.device_info}
                              </span>
                            </div>
                            <p className="text-[11px] text-slate-500 mt-0.5 break-words">
                              {log.details}
                            </p>
                            <span className="text-[10px] text-slate-400 font-mono mt-0.5 block">
                              IP: {log.ip_address}
                            </span>
                          </div>
                        </div>

                        <div className="text-[10px] text-slate-400 font-mono shrink-0 whitespace-nowrap">
                          {formatTimestamp(log.timestamp)}
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="p-8 rounded-xl border border-slate-200 text-center text-xs text-slate-400">
                  No session audit history recorded yet.
                </div>
              )}
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-slate-100 bg-slate-50/70 flex items-center justify-between shrink-0">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold text-slate-600 hover:text-slate-800 hover:bg-slate-200/60 rounded-lg transition cursor-pointer"
          >
            Close
          </button>
          <button
            type="button"
            onClick={() => {
              onClose();
              logout();
            }}
            className="px-3.5 py-2 text-xs font-semibold rounded-lg bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 transition flex items-center gap-1.5 cursor-pointer shadow-2xs"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span>Sign Out Current Device</span>
          </button>
        </div>
      </div>
    </div>
  );
}
