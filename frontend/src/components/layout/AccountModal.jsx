// frontend/src/components/layout/AccountModal.jsx
import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { formatAccountId } from '../../services/api';
import { X, User, Mail, Shield, KeyRound, Key, Copy, Check, LogOut, CheckCircle2 } from 'lucide-react';

export default function AccountModal({ isOpen, onClose, showToast }) {
  const { user, isAdmin, updateProfile, logout } = useAuth();
  const [newUsername, setNewUsername] = useState(user?.username || '');
  const [isSaving, setIsSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [copiedAcc, setCopiedAcc] = useState(false);

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

  const initials = (user?.username || 'AO').slice(0, 2).toUpperCase();

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs">
      <div className="bg-white border border-slate-200 rounded-2xl w-full max-w-md p-6 space-y-5 shadow-2xl animate-in fade-in zoom-in-95 duration-150">
        {/* Modal Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center gap-2.5">
            <div className="w-10 h-10 rounded-full bg-amber-600 text-white flex items-center justify-center font-bold font-mono text-sm shadow-xs">
              {initials}
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900 tracking-tight">
                {user?.username || 'User Profile'}
              </h2>
              <p className="text-[11px] text-slate-500">AetherOps Platform Account &amp; Session</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 p-1.5 rounded-lg hover:bg-slate-100 transition cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* AWS-Style Account ID Showcase Card */}
        <div className="p-4 rounded-xl bg-amber-50/90 border border-amber-200 flex items-center justify-between">
          <div>
            <div className="text-[10px] font-bold text-amber-800 uppercase tracking-wider flex items-center gap-1.5 mb-0.5">
              <Key className="w-3.5 h-3.5 text-amber-600" />
              AWS Account ID (Login ID)
            </div>
            <div className="text-base font-mono font-bold text-amber-950">
              {formatAccountId(user?.account_id || '109283746519')}
            </div>
            <div className="text-[10px] text-amber-700/80">
              Sign in anytime using this 12-digit ID, your username, or email.
            </div>
          </div>
          <button
            onClick={copyAccountId}
            title="Copy Account ID"
            className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-amber-600 hover:bg-amber-700 text-white shadow-xs transition flex items-center gap-1.5 cursor-pointer shrink-0"
          >
            {copiedAcc ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
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
              className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase border ${
                isAdmin
                  ? 'bg-amber-50 text-amber-800 border-amber-200'
                  : 'bg-emerald-50 text-emerald-700 border-emerald-200'
              }`}
            >
              {user?.role || 'USER'}
            </span>
          </div>

          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-500 flex items-center gap-1.5">
              <KeyRound className="w-3.5 h-3.5" />
              Session Status:
            </span>
            <span className="text-[11px] font-mono text-emerald-600 flex items-center gap-1 font-semibold">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
              Encrypted JWT Session
            </span>
          </div>
        </div>

        {/* Feedback messages */}
        {errorMsg && (
          <div className="p-2.5 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-xs font-medium">
            {errorMsg}
          </div>
        )}
        {successMsg && (
          <div className="p-2.5 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-medium flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 shrink-0" />
            <span>{successMsg}</span>
          </div>
        )}

        {/* Change Display Name form */}
        <form onSubmit={handleUpdate} className="space-y-2">
          <label className="block text-xs font-semibold text-slate-700">
            Display Handle / Name
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              required
              minLength={3}
              value={newUsername}
              onChange={(e) => setNewUsername(e.target.value)}
              placeholder="e.g. dev_architect"
              className="flex-1 px-3 py-2 text-xs font-mono rounded-lg border border-slate-300 focus:outline-none focus:border-amber-600 focus:ring-1 focus:ring-amber-600"
            />
            <button
              type="submit"
              disabled={isSaving}
              className="px-3.5 py-2 text-xs font-semibold rounded-lg bg-amber-600 hover:bg-amber-700 text-white shadow-xs transition disabled:opacity-50 cursor-pointer"
            >
              {isSaving ? 'Saving...' : 'Update'}
            </button>
          </div>
        </form>

        {/* Modal Footer */}
        <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold text-slate-600 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition cursor-pointer"
          >
            Close
          </button>
          <button
            type="button"
            onClick={() => {
              onClose();
              logout();
            }}
            className="px-3.5 py-2 text-xs font-semibold rounded-lg bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 transition flex items-center gap-1.5 cursor-pointer"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span>Sign Out</span>
          </button>
        </div>
      </div>
    </div>
  );
}
