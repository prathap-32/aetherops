// frontend/src/modules/settings/SettingsView.jsx
import React, { useState, useEffect } from 'react';
import { Save, CheckCircle2, AlertCircle, Shield, Key, GitBranch, Eye, EyeOff, RefreshCw, Lock } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { connectionsApi, formatAccountId } from '../../services/api';
import { AWS_REGIONS_39 } from '../../constants/awsRegions';

export default function SettingsView() {
  const { user, updateProfile } = useAuth();
  
  // Profile state
  const [username, setUsername] = useState(user?.username || '');
  const [email] = useState(user?.email || '');
  const [profileSaved, setProfileSaved] = useState(false);
  const [profileError, setProfileError] = useState('');

  // AWS Credentials state (Access Keys only, 39 regions)
  const [awsRegion, setAwsRegion] = useState('us-east-1');
  const [accessKeyId, setAccessKeyId] = useState('');
  const [secretAccessKey, setSecretAccessKey] = useState('');
  const [sessionToken, setSessionToken] = useState('');
  const [showSecret, setShowSecret] = useState(false);
  const [awsStatus, setAwsStatus] = useState(null); // { type: 'success'|'error', text: '', details: '' }
  const [isAwsTesting, setIsAwsTesting] = useState(false);

  // GitHub integration state & granular permission choices
  const [githubStatus, setGithubStatus] = useState('Not connected');
  const [accessLevel, setAccessLevel] = useState('rw'); // 'read' or 'rw'
  const [repoScope, setRepoScope] = useState('all');   // 'all' or 'selected'
  const [visibility, setVisibility] = useState('all'); // 'all' or 'public'
  const [patToken, setPatToken] = useState('');
  const [ghStatusMsg, setGhStatusMsg] = useState(null);

  // Fetch existing Git connections on mount to synchronize connection status
  useEffect(() => {
    connectionsApi.listGit().then((conns) => {
      if (Array.isArray(conns) && conns.length > 0) {
        const c = conns[0];
        const repoName = c.repo_full_name || c.repository || c.owner || 'Linked Repository';
        setGithubStatus(`Connected to repo: ${repoName}`);
      }
    }).catch(() => {});
  }, []);

  // Listen for OAuth postMessage updates from popup window
  useEffect(() => {
    const handleMessage = (event) => {
      if (event.data && event.data.type === 'GITHUB_OAUTH_SUCCESS') {
        const ghUser = event.data.user?.login || 'developer';
        setGithubStatus(`Connected as @${ghUser}`);
        setGhStatusMsg({
          type: 'success',
          text: `Successfully authenticated & linked GitHub account @${ghUser}!`
        });
        // Refresh git connections list
        connectionsApi.listGit().then((conns) => {
          if (Array.isArray(conns) && conns.length > 0) {
            const c = conns[0];
            const repoName = c.repo_full_name || c.repository || c.owner || 'Linked Repository';
            setGithubStatus(`Connected to repo: ${repoName}`);
          }
        }).catch(() => {});
      } else if (event.data && event.data.type === 'GITHUB_OAUTH_ERROR') {
        setGhStatusMsg({
          type: 'error',
          text: event.data.error || 'GitHub authorization failed.'
        });
      }
    };
    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, []);

  const handleProfileSave = async (e) => {
    e.preventDefault();
    if (!username.trim()) return;
    setProfileError('');
    try {
      await updateProfile(username.trim());
      setProfileSaved(true);
      setTimeout(() => setProfileSaved(false), 3000);
    } catch (err) {
      setProfileError(err.message || 'Failed to update profile');
    }
  };

  const handleTestAndSaveAws = async (e) => {
    e.preventDefault();
    if (!accessKeyId.trim() || !secretAccessKey.trim()) {
      setAwsStatus({ type: 'error', text: 'AWS Access Key ID and Secret Access Key are required.' });
      return;
    }
    setIsAwsTesting(true);
    setAwsStatus(null);
    try {
      const payload = {
        auth_type: 'ACCESS_KEYS',
        aws_region: awsRegion,
        access_key_id: accessKeyId.trim(),
        secret_access_key: secretAccessKey.trim(),
        session_token: sessionToken.trim() || null,
      };

      const res = await connectionsApi.validateAws(payload);
      if (res && (res.status === 'success' || res.account_id)) {
        setAwsStatus({
          type: 'success',
          text: `AWS STS GetCallerIdentity verified successfully! Account ID: ${res.account_id}`,
          details: `Caller ARN: ${res.caller_arn || 'Verified'} | Region: ${awsRegion}`
        });
      } else {
        throw new Error(res.detail || 'AWS credential verification failed.');
      }
    } catch (err) {
      setAwsStatus({
        type: 'error',
        text: err.message || 'AWS authentication check failed. Please verify your keys and region.',
      });
    } finally {
      setIsAwsTesting(false);
    }
  };

  const handleConnectGithubOAuth = () => {
    const width = 600, height = 700;
    const left = window.screen.width / 2 - width / 2;
    const top = window.screen.height / 2 - height / 2;
    const url = `/api/v1/connections/github/login?access_level=${accessLevel}&repo_scope=${repoScope}&visibility=${visibility}`;
    window.open(
      url,
      'AetherOpsGitHubOAuth',
      `width=${width},height=${height},top=${top},left=${left},scrollbars=yes,status=yes`
    );
  };

  const handleVerifyPat = async (e) => {
    e.preventDefault();
    if (!patToken.trim()) return;
    setGhStatusMsg(null);
    try {
      const res = await connectionsApi.verifyPat(patToken.trim());
      const loginName = res.user?.login || 'developer';
      setGithubStatus(`Connected as @${loginName} (via PAT)`);
      setGhStatusMsg({
        type: 'success',
        text: `PAT Token verified successfully for @${loginName}. Access and repositories linked.`
      });
      setPatToken('');
    } catch (err) {
      setGhStatusMsg({
        type: 'error',
        text: `PAT Verification Failed: ${err.message || 'Invalid or expired Personal Access Token.'}`
      });
    }
  };

  return (
    <div className="space-y-8 max-w-4xl pb-12 select-none">
      {/* Header */}
      <div className="pb-4 border-b border-slate-200">
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2.5">
          <Shield className="w-7 h-7 text-blue-600" />
          User Account &amp; Credential Security Settings
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Manage your personal platform profile, AWS infrastructure keys across all 39 regions, and secure GitHub integrations.
        </p>
      </div>

      {/* 1. Account Profile Section */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs p-6 space-y-5">
        <div className="flex items-center gap-3 pb-3 border-b border-slate-100">
          <div className="w-9 h-9 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-sm">
            {username ? username.slice(0, 2).toUpperCase() : 'AO'}
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-900">Personal Profile &amp; Account ID</h2>
            <p className="text-xs text-slate-500">Unique AWS-style 12-digit account identifier and display handle.</p>
          </div>
        </div>

        {profileSaved && (
          <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold rounded-xl flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            Profile updated successfully.
          </div>
        )}

        {profileError && (
          <div className="p-3 bg-rose-50 border border-rose-200 text-rose-800 text-xs font-semibold rounded-xl flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
            {profileError}
          </div>
        )}

        <form onSubmit={handleProfileSave} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                Display Handle / Username
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full text-sm bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 font-medium"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                Account ID (12-Digit Secure Hash)
              </label>
              <input
                type="text"
                value={formatAccountId(user?.account_id || '109283746519')}
                disabled
                className="w-full text-sm bg-slate-100 border border-slate-200 rounded-xl p-2.5 text-slate-600 font-mono font-bold cursor-not-allowed"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                Verified Email Address
              </label>
              <input
                type="email"
                value={email}
                disabled
                className="w-full text-sm bg-slate-100 border border-slate-200 rounded-xl p-2.5 text-slate-500 cursor-not-allowed"
              />
            </div>
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                Assigned Platform Role
              </label>
              <input
                type="text"
                value={user?.role || 'DEVELOPER'}
                disabled
                className="w-full text-sm bg-slate-100 border border-slate-200 rounded-xl p-2.5 text-slate-600 font-mono text-xs font-bold cursor-not-allowed"
              />
            </div>
          </div>

          <div className="flex justify-end pt-2">
            <button
              type="submit"
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-xl shadow-xs transition cursor-pointer"
            >
              <Save className="w-3.5 h-3.5" />
              Save Profile
            </button>
          </div>
        </form>
      </div>

      {/* 2. AWS Credentials Management Section (39 Regions, Access Keys Only) */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs p-6 space-y-5">
        <div className="flex items-center gap-3 pb-3 border-b border-slate-100">
          <div className="w-9 h-9 rounded-xl bg-orange-50 text-orange-600 flex items-center justify-center font-bold text-sm">
            <Key className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-900">AWS Cloud Credentials &amp; 39-Region Selector</h2>
            <p className="text-xs text-slate-500">Configure your AWS Access Key Pair and target AWS region for infrastructure synthesis and deployment.</p>
          </div>
        </div>

        {awsStatus && (
          <div className={`p-4 rounded-xl border text-xs space-y-1 ${awsStatus.type === 'success' ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-rose-50 border-rose-200 text-rose-800'}`}>
            <div className="font-bold flex items-center gap-1.5">
              {awsStatus.type === 'success' ? <CheckCircle2 className="w-4 h-4 text-emerald-600" /> : <AlertCircle className="w-4 h-4 text-rose-600" />}
              <span>{awsStatus.text}</span>
            </div>
            {awsStatus.details && <div className="font-mono text-[11px] opacity-90">{awsStatus.details}</div>}
          </div>
        )}

        <form onSubmit={handleTestAndSaveAws} className="space-y-4">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
              Target AWS Deployment Region (All 39 Global Regions Available)
            </label>
            <select
              value={awsRegion}
              onChange={(e) => setAwsRegion(e.target.value)}
              className="w-full text-sm bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-slate-900 font-mono focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500"
            >
              {AWS_REGIONS_39.map((r) => (
                <option key={r.code} value={r.code}>
                  {r.code} — {r.name} ({r.geo})
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-3 p-4 rounded-xl bg-slate-50 border border-slate-200">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
                AWS Access Key ID <span className="text-orange-600">*</span>
              </label>
              <input
                type="text"
                placeholder="AKIAIOSFODNN7EXAMPLE"
                value={accessKeyId}
                onChange={(e) => setAccessKeyId(e.target.value)}
                className="w-full text-xs font-mono bg-white border border-slate-200 rounded-lg p-2.5 text-slate-900 focus:outline-none focus:ring-2 focus:ring-orange-500/20"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
                AWS Secret Access Key <span className="text-orange-600">*</span>
              </label>
              <div className="relative">
                <input
                  type={showSecret ? 'text' : 'password'}
                  placeholder="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
                  value={secretAccessKey}
                  onChange={(e) => setSecretAccessKey(e.target.value)}
                  className="w-full text-xs font-mono bg-white border border-slate-200 rounded-lg p-2.5 pr-10 text-slate-900 focus:outline-none focus:ring-2 focus:ring-orange-500/20"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowSecret(!showSecret)}
                  className="absolute right-2.5 top-2.5 text-slate-400 hover:text-slate-700 cursor-pointer"
                >
                  {showSecret ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
                Session Token <span className="text-slate-400 font-normal">(Optional for temporary STS credentials)</span>
              </label>
              <input
                type="password"
                placeholder="AQoDYXdzEJr1..."
                value={sessionToken}
                onChange={(e) => setSessionToken(e.target.value)}
                className="w-full text-xs font-mono bg-white border border-slate-200 rounded-lg p-2.5 text-slate-900 focus:outline-none focus:ring-2 focus:ring-orange-500/20"
              />
            </div>
          </div>

          <div className="flex justify-between items-center pt-2">
            <span className="text-[11px] text-slate-500 flex items-center gap-1">
              <Lock className="w-3 h-3 text-emerald-600" />
              Encrypted via AES-256-GCM hardware envelope before storage.
            </span>
            <button
              type="submit"
              disabled={isAwsTesting}
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-amber-600 hover:bg-amber-700 text-white text-xs font-semibold rounded-xl shadow-xs transition cursor-pointer disabled:opacity-50"
            >
              {isAwsTesting ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Key className="w-3.5 h-3.5" />}
              {isAwsTesting ? 'Validating STS...' : 'Test & Save AWS Credentials'}
            </button>
          </div>
        </form>
      </div>

      {/* 3. GitHub Account & OAuth Integration Section with Granular Trust Permissions */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs p-6 space-y-5">
        <div className="flex items-center gap-3 pb-3 border-b border-slate-100">
          <div className="w-9 h-9 rounded-xl bg-slate-900 text-white flex items-center justify-center">
            <GitBranch className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-900">GitHub Account &amp; Granular OAuth Permissions</h2>
            <p className="text-xs text-slate-500">Connect securely with transparent permission toggles (Read vs RW, All vs Selected Repos) or verify via PAT token.</p>
          </div>
        </div>

        {ghStatusMsg && (
          <div className={`p-3 rounded-xl border text-xs font-semibold flex items-center gap-2 ${ghStatusMsg.type === 'success' ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-rose-50 border-rose-200 text-rose-800'}`}>
            {ghStatusMsg.type === 'success' ? <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" /> : <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />}
            <span>{ghStatusMsg.text}</span>
          </div>
        )}

        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 rounded-xl bg-slate-50 border border-slate-200">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-slate-900 text-white flex items-center justify-center text-xs font-bold font-mono">
                GH
              </div>
              <div>
                <div className="text-xs font-bold text-slate-900">GitHub Connection Status</div>
                <div className="text-xs text-slate-600 font-mono mt-0.5">{githubStatus}</div>
              </div>
            </div>
            <div className="text-xs font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-3 py-1 rounded-full">
              Ready to Connect
            </div>
          </div>

          {/* Granular Permission Conditions for User Trust */}
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
              Granular OAuth Permission Conditions (User Trust &amp; Transparency)
            </h3>
            
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {/* Access Level */}
              <div className="space-y-1.5">
                <label className="block text-[11px] font-semibold text-slate-600">Access Level</label>
                <select
                  value={accessLevel}
                  onChange={(e) => setAccessLevel(e.target.value)}
                  className="w-full text-xs bg-white border border-slate-200 rounded-lg p-2 font-medium text-slate-800"
                >
                  <option value="rw">Read &amp; Write (Full RW)</option>
                  <option value="read">Read-Only (Analysis Only)</option>
                </select>
              </div>

              {/* Repository Scope */}
              <div className="space-y-1.5">
                <label className="block text-[11px] font-semibold text-slate-600">Repository Scope</label>
                <select
                  value={repoScope}
                  onChange={(e) => setRepoScope(e.target.value)}
                  className="w-full text-xs bg-white border border-slate-200 rounded-lg p-2 font-medium text-slate-800"
                >
                  <option value="all">All Repositories</option>
                  <option value="selected">Selected Repositories Only</option>
                </select>
              </div>

              {/* Visibility */}
              <div className="space-y-1.5">
                <label className="block text-[11px] font-semibold text-slate-600">Repository Visibility</label>
                <select
                  value={visibility}
                  onChange={(e) => setVisibility(e.target.value)}
                  className="w-full text-xs bg-white border border-slate-200 rounded-lg p-2 font-medium text-slate-800"
                >
                  <option value="all">Public &amp; Private Repos</option>
                  <option value="public">Public Repos Only</option>
                </select>
              </div>
            </div>

            <div className="pt-2 flex justify-end">
              <button
                type="button"
                onClick={handleConnectGithubOAuth}
                className="px-5 py-2.5 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded-xl shadow-xs transition cursor-pointer flex items-center gap-2"
              >
                <GitBranch className="w-4 h-4" />
                Connect GitHub via OAuth (With Selected Permissions)
              </button>
            </div>
          </div>

          {/* PAT Token Verification Card */}
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
              Alternative: Personal Access Token (PAT) Verification
            </h3>
            <p className="text-[11px] text-slate-500">
              Supply a fine-grained GitHub Personal Access Token with repository scopes for instant, secure authentication without browser popups.
            </p>
            <form onSubmit={handleVerifyPat} className="flex gap-2">
              <input
                type="password"
                placeholder="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                value={patToken}
                onChange={(e) => setPatToken(e.target.value)}
                className="flex-1 text-xs font-mono bg-white border border-slate-200 rounded-xl p-2.5 text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900/20"
                required
              />
              <button
                type="submit"
                className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-xl transition cursor-pointer shrink-0"
              >
                Verify &amp; Link PAT
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
