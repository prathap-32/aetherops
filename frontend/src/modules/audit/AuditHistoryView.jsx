// frontend/src/modules/audit/AuditHistoryView.jsx
import React, { useState, useEffect } from 'react';
import { History, Shield, CheckCircle2, Clock, RefreshCw } from 'lucide-react';
import { adminApi } from '../../services/api';

export default function AuditHistoryView() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const data = await adminApi.getAuditLogs();
      setLogs(data.audit_logs || []);
    } catch (err) {
      console.warn('Failed to load audit logs:', err);
      // Fallback to empty if not privileged
      setLogs([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-slate-100 text-slate-700 border border-slate-200">
              MODULE // AUDIT TRAIL
            </span>
            <span className="text-xs text-slate-400 font-mono">Immutable Operations &amp; Session Vault</span>
          </div>
          <h1 className="text-xl font-bold text-slate-900 mt-1">Audit &amp; Operations History</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Cryptographic ledger tracking authentication events, OAuth tokens, and infrastructure changes.
          </p>
        </div>

        <button
          onClick={fetchLogs}
          disabled={loading}
          className="px-3.5 py-2 rounded-xl bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-semibold transition flex items-center gap-1.5 cursor-pointer shadow-xs"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Audit</span>
        </button>
      </div>

      {/* Audit Log Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="p-5 border-b border-slate-100">
          <h3 className="text-sm font-bold text-slate-900">Recorded Security Events</h3>
          <p className="text-[11px] text-slate-500">Live events recorded in PostgreSQL admin_security vault</p>
        </div>

        {loading ? (
          <div className="p-8 text-center text-xs text-slate-400">Loading audit ledger...</div>
        ) : logs.length === 0 ? (
          <div className="p-8 text-center text-xs text-slate-400">
            No audit events recorded yet or requires administrative session.
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {logs.map((log) => (
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
                    {new Date(log.created_at).toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
