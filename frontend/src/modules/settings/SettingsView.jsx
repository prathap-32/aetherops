// frontend/src/modules/settings/SettingsView.jsx
import React, { useState } from 'react';
import { Settings, Shield, Key, Bell, Save, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function SettingsView() {
  const { user, updateProfile } = useAuth();
  const [username, setUsername] = useState(user?.username || '');
  const [email] = useState(user?.email || '');
  const [saved, setSaved] = useState(false);

  const handleSave = async (e) => {
    e.preventDefault();
    if (!username.trim()) return;
    try {
      await updateProfile(username.trim());
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      alert(`Save failed: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <div className="pb-4 border-b border-slate-200">
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Account & Workspace Settings</h1>
        <p className="text-sm text-slate-500 mt-1">
          Manage your account profile, role preferences, and API keys.
        </p>
      </div>

      <form onSubmit={handleSave} className="bg-white rounded-xl border border-slate-200 shadow-xs p-6 space-y-4">
        {saved && (
          <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold rounded-lg flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            Profile changes saved successfully.
          </div>
        )}

        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
            Display Handle / Username
          </label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full text-sm bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
            required
          />
        </div>

        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
            Verified Email Address
          </label>
          <input
            type="email"
            value={email}
            disabled
            className="w-full text-sm bg-slate-100 border border-slate-200 rounded-lg p-2.5 text-slate-500 cursor-not-allowed"
          />
        </div>

        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
            Assigned Platform Role
          </label>
          <input
            type="text"
            value={user?.role || 'USER'}
            disabled
            className="w-full text-sm bg-slate-100 border border-slate-200 rounded-lg p-2.5 text-slate-500 font-mono text-xs cursor-not-allowed"
          />
        </div>

        <div className="pt-3 border-t border-slate-100 flex justify-end">
          <button
            type="submit"
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg shadow-xs transition"
          >
            <Save className="w-3.5 h-3.5" />
            Save Profile
          </button>
        </div>
      </form>
    </div>
  );
}
