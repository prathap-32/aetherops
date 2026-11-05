// frontend/src/modules/settings/SettingsView.jsx
import React, { useState } from 'react';
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

  // AWS Credentials state
  const [awsAuthMode, setAwsAuthMode] = useState('ACCESS_KEYS');
  const [awsRegion, setAwsRegion] = useState('us-east-1');
  const [accessKeyId, setAccessKeyId] = useState('');
  const [secretAccessKey, setSecretAccessKey] = useState('');
  const [roleArn, setRoleArn] = useState('');
  const [externalId, setExternalId] = useState('');
  const [showSecret, setShowSecret] = useState(false);
  const [awsStatus, setAwsStatus] = useState(null); // { type: 'success'|'error', text: '', details: '' }
  const [isAwsTesting, setIsAwsTesting] = useState(false);

  // GitHub integration state
  const [githubStatus, setGithubStatus] = useState('Not connected');
  const [patToken, setPatToken] = useState('');
  const [ghStatusMsg, setGhStatusMsg] = useState(null);

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
    setIsAwsTesting(true);
    setAwsStatus(null);
    try {
      const payload = {
        auth_type: awsAuthMode,
        aws_region: awsRegion,
        access_key_id: awsAuthMode === 'ACCESS_KEYS' ? accessKeyId.trim() : null,
        secret_access_key: awsAuthMode === 'ACCESS_KEYS' ? secretAccessKey.trim() : null,
        role_arn: awsAuthMode === 'IAM_ROLE_ARN' ? roleArn.trim() : null,
        external_id: awsAuthMode === 'IAM_ROLE_ARN' ? externalId.trim() : null,
      };

      const res = await connectionsApi.validateAws(payload);
      if (res && (res.status === 'success' || res.account_id)) {
        setAwsStatus({
          type: 'success',
          text: `AWS STS GetCallerIdentity verified successfully! Account ID: ${res.account_id}`,
          details: `ARN: ${res.caller_arn || res.role_arn || 'Verified'} | Region: ${awsRegion}`
        });
      } else {
        throw new Error(res.detail || 'AWS credential verification failed.');
      }
    } catch (err) {
      setAwsStatus({
        type: 'error',
        text: err.message || 'AWS authentication check failed. Please verify credentials.',
      });
    } finally {
      setIsAwsTesting(false);
    }
  };

  const handleConnectGithub = () => {
    const width = 600, height = 700;
    const left = window.screen.width / 2 - width / 2;
    const top = window.screen.height / 2 - height / 2;
    window.open(
      '/api/v1/connections/github/login',
      'AetherOpsGitHubOAuth',
      `width=${width},height=${height},top=${top},left=${left},scrollbars=yes,status=yes`
    );
  };

  const handleVerifyPat = async () => {
    if (!patToken.trim()) return;
    setGhStatusMsg(null);
    try {
      const res = await connectionsApi.verifyPat(patToken.trim());
      setGithubStatus(`Connected as @${res.user?.login || 'developer'}`);
      setGhStatusMsg({ type: 'success', text: `Successfully linked GitHub Personal Access Token for @${res.user?.login}` });
      setPatToken('');
    } catch (err) {
      setGhStatusMsg({ type: 'error', text: `PAT verification failed: ${err.message}` });
    }
  };

  return (
    <div className="space-y-8 max-w-4xl pb-12">
      {/* Header */}
      <div className="pb-4 border-b border-slate-200">
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2.5">
          <Shield className="w-7 h-7 text-blue-600" />
          User Account &amp; Credential Security Settings
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Manage your personal platform profile, separate AWS infrastructure credentials, and GitHub integrations securely.
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

      {/* 2. AWS Credentials Management Section */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs p-6 space-y-5">
        <div className="flex items-center gap-3 pb-3 border-b border-slate-100">
          <div className="w-9 h-9 rounded-xl bg-orange-50 text-orange-600 flex items-center justify-center font-bold text-sm">
            <Key className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-900">AWS Cloud Credentials &amp; Region Management</h2>
            <p className="text-xs text-slate-500">Configure your AWS Access Key Pair or IAM Role ARN for cloud infrastructure generation &amp; deployment.</p>
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
          <div className="grid grid-cols-2 gap-3">
            <button
              type="button"
              onClick={() => setAwsAuthMode('ACCESS_KEYS')}
              className={`p-3 rounded-xl border text-xs font-semibold flex items-center gap-2.5 cursor-pointer transition ${awsAuthMode === 'ACCESS_KEYS' ? 'border-orange-500 bg-orange-50/70 text-orange-900 font-bold' : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50'}`}
            >
              <span className="w-6 h-6 rounded-lg bg-orange-500 text-white flex items-center justify-center font-bold text-[10px]">AK</span>
              <div className="text-left">
                <div>Access Key &amp; Secret Key</div>
                <div className="text-[10px] text-slate-500 font-normal">Standard IAM credentials</div>
              </div>
            </button>

            <button
              type="button"
              onClick={() => setAwsAuthMode('IAM_ROLE_ARN')}
              className={`p-3 rounded-xl border text-xs font-semibold flex items-center gap-2.5 cursor-pointer transition ${awsAuthMode === 'IAM_ROLE_ARN' ? 'border-orange-500 bg-orange-50/70 text-orange-900 font-bold' : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50'}`}
            >
              <span className="w-6 h-6 rounded-lg bg-slate-800 text-white flex items-center justify-center font-bold text-[10px]">ARN</span>
              <div className="text-left">
                <div>IAM Role ARN</div>
                <div className="text-[10px] text-slate-500 font-normal">Assume role / cross-account</div>
              </div>
            </button>
          </div>

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
              Target AWS Region
            </label>
            <select
              value={awsRegion}
              onChange={(e) => setAwsRegion(e.target.value)}
              className="w-full text-sm bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-slate-900 font-mono focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500"
            >
              {AWS_REGIONS_39.map((r) => (
                <option key={r.code} value={r.code}>
                  {r.code} ({r.name})
                </option>
              ))}
            </select>
          </div>

          {awsAuthMode === 'ACCESS_KEYS' ? (
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
            </div>
          ) : (
            <div className="space-y-3 p-4 rounded-xl bg-slate-50 border border-slate-200">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
                  IAM Role or User ARN <span className="text-orange-600">*</span>
                </label>
                <input
                  type="text"
                  placeholder="arn:aws:iam::123456789012:role/AetherOpsExecutionRole"
                  value={roleArn}
                  onChange={(e) => setRoleArn(e.target.value)}
                  className="w-full text-xs font-mono bg-white border border-slate-200 rounded-lg p-2.5 text-slate-900 focus:outline-none focus:ring-2 focus:ring-orange-500/20"
                />
              </div>
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
                  External ID <span className="text-slate-400 font-normal">(Optional cross-account protection)</span>
                </label>
                <input
                  type="text"
                  placeholder="e.g. aether-corp-production"
                  value={externalId}
                  onChange={(e) => setExternalId(e.target.value)}
                  className="w-full text-xs font-mono bg-white border border-slate-200 rounded-lg p-2.5 text-slate-900 focus:outline-none focus:ring-2 focus:ring-orange-500/20"
                />
              </div>
            </div>
          )}

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

      {/* 3. GitHub Integration & OAuth Management Section */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs p-6 space-y-5">
        <div className="flex items-center gap-3 pb-3 border-b border-slate-100">
          <div className="w-9 h-9 rounded-xl bg-slate-900 text-white flex items-center justify-center">
            <GitBranch className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-900">GitHub Account &amp; Repository Connection</h2>
            <p className="text-xs text-slate-500">Connect via OAuth 2.0 or supply a secure Personal Access Token (PAT) for repository scanning and CI/CD.</p>
          </div>
        </div>

        {ghStatusMsg && (
          <div className={`p-3 rounded-xl border text-xs font-semibold flex items-center gap-2 ${ghStatusMsg.type === 'success' ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-rose-50 border-rose-200 text-rose-800'}`}>
            {ghStatusMsg.type === 'success' ? <CheckCircle2 className="w-4 h-4 text-emerald-600" /> : <AlertCircle className="w-4 h-4 text-rose-600" />}
            {ghStatusMsg.text}
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
            <button
              type="button"
              onClick={handleConnectGithub}
              className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded-xl shadow-xs transition cursor-pointer flex items-center gap-1.5"
            >
              <GitBranch className="w-3.5 h-3.5" />
              Connect / Switch GitHub Account
            </button>
          </div>

          <div className="space-y-2">
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-700">
              Or Link via Personal Access Token (PAT)
            </label>
            <div className="flex gap-2">
              <input
                type="password"
                placeholder="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                value={patToken}
                onChange={(e) => setPatToken(e.target.value)}
                className="flex-1 text-xs font-mono bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900/20"
              />
              <button
                type="button"
                onClick={handleVerifyPat}
                className="px-4 py-2.5 bg-slate-800 hover:bg-slate-900 text-white text-xs font-semibold rounded-xl transition cursor-pointer"
              >
                Verify &amp; Link PAT
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
