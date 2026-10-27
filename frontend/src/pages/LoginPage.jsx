// frontend/src/pages/LoginPage.jsx
import React, { useState, useEffect } from 'react';
import {
  Shield,
  Lock,
  Mail,
  User,
  ArrowRight,
  AlertCircle,
  RefreshCw,
  FolderGit2,
  Sparkles,
  Key
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function LoginPage({ onLoginSuccess }) {
  const { login, register, updateProfile, setSessionManually } = useAuth();

  const [activeTab, setActiveTab] = useState('login'); // 'login' | 'register'
  const [loginId, setLoginId] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('USER'); // 'USER' | 'ADMIN'
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  // Post-OAuth Account Verification / Name Clarification Modal
  const [showClarificationModal, setShowClarificationModal] = useState(false);
  const [oauthProvider, setOauthProvider] = useState('Google');
  const [oauthVerifiedEmail, setOauthVerifiedEmail] = useState('');
  const [clarifiedName, setClarifiedName] = useState('');
  const [pendingToken, setPendingToken] = useState('');

  // Strictly ensure light theme on document body
  useEffect(() => {
    if (typeof document !== 'undefined') {
      document.documentElement.classList.remove('dark');
      document.documentElement.classList.add('light');
      document.body.classList.remove('dark');
      document.body.classList.add('light');
    }
  }, []);

  // Listen for OAuth messages from popup window (validating origin to prevent cross-site message injection)
  useEffect(() => {
    const handleOAuthMessage = async (event) => {
      if (event.origin !== window.location.origin) return;
      if (!event.data) return;
      if (
        event.data.type === 'GOOGLE_OAUTH_SUCCESS' ||
        event.data.type === 'GITHUB_OAUTH_SUCCESS' ||
        event.data.type === 'OAUTH_AUTH_SUCCESS'
      ) {
        const { token, user: oauthUser } = event.data;
        if (token && oauthUser) {
          setSessionManually(token, oauthUser);
          setPendingToken(token);
          setOauthProvider(event.data.type.includes('GITHUB') ? 'GitHub' : 'Google');
          setOauthVerifiedEmail(oauthUser.email || '');
          setClarifiedName(oauthUser.username || '');
          setShowClarificationModal(true);
        }
      }
    };

    window.addEventListener('message', handleOAuthMessage);
    return () => window.removeEventListener('message', handleOAuthMessage);
  }, [setSessionManually]);

  // Check URL query parameters for OAuth callbacks if popup was redirected in same window
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get('token');
    const userParam = params.get('username');
    const emailParam = params.get('email');
    const roleParam = params.get('role') || 'USER';
    const accountIdParam = params.get('account_id') || '';

    if (token && userParam) {
      const authUser = {
        username: userParam,
        email: emailParam || `${userParam}@oauth.local`,
        role: roleParam,
        account_id: accountIdParam,
      };
      setSessionManually(token, authUser);
      setPendingToken(token);
      setOauthProvider('OAuth');
      setOauthVerifiedEmail(authUser.email);
      setClarifiedName(userParam);
      setShowClarificationModal(true);
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, [setSessionManually]);

  const handleSignIn = async (e) => {
    e.preventDefault();
    setErrorMessage('');
    if (!loginId.trim() || !password) {
      setErrorMessage('Please enter your Login ID (Username, Email, or 12-digit Account ID) and password.');
      return;
    }

    setIsLoading(true);
    try {
      await login(loginId.trim(), password);
      if (onLoginSuccess) onLoginSuccess();
    } catch (err) {
      setErrorMessage(err.message || 'Login failed. Invalid Login ID or credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSignUp = async (e) => {
    e.preventDefault();
    setErrorMessage('');
    if (!loginId.trim() || !email.trim() || !password) {
      setErrorMessage('Please complete all registration fields.');
      return;
    }

    setIsLoading(true);
    try {
      await register(loginId.trim(), email.trim(), password, role);
      if (onLoginSuccess) onLoginSuccess();
    } catch (err) {
      setErrorMessage(err.message || 'Registration failed. Username may already be in use.');
    } finally {
      setIsLoading(false);
    }
  };

  const openOAuthPopup = (url, title) => {
    const w = 520;
    const h = 650;
    const left = window.screen.width / 2 - w / 2;
    const top = window.screen.height / 2 - h / 2;
    const popup = window.open(
      url,
      title,
      `width=${w},height=${h},top=${top},left=${left},scrollbars=yes,status=no,resizable=yes`
    );
    if (!popup || popup.closed || typeof popup.closed === 'undefined') {
      window.location.href = url;
    }
  };

  const handleGoogleOAuth = () => {
    openOAuthPopup('/api/v1/auth/google/login', 'google_oauth');
  };

  const handleGitHubOAuth = () => {
    openOAuthPopup('/api/v1/auth/github/login', 'github_oauth');
  };

  const handleConfirmClarifiedName = async (e) => {
    e.preventDefault();
    if (!clarifiedName.trim()) return;

    setIsLoading(true);
    try {
      await updateProfile(clarifiedName.trim());
      setShowClarificationModal(false);
      if (onLoginSuccess) onLoginSuccess();
    } catch (err) {
      setShowClarificationModal(false);
      if (onLoginSuccess) onLoginSuccess();
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-900 flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative overflow-hidden select-none">
      {/* Subtle Warm Amber Glow Orbs (Light Theme Only) */}
      <div className="absolute top-0 -left-20 w-96 h-96 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 -right-20 w-96 h-96 bg-orange-500/10 rounded-full blur-3xl pointer-events-none" />

      <div className="sm:mx-auto sm:w-full sm:max-w-md z-10 px-4 text-center">
        {/* AetherOps Brand Image */}
        <div className="flex justify-center mb-4">
          <img
            src="/static/logo/aetherops_light.png"
            alt="AetherOps"
            className="h-12 max-w-[260px] object-contain drop-shadow-xs"
          />
        </div>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md z-10 px-4">
        <div className="bg-white py-8 px-6 shadow-xl shadow-slate-200/60 rounded-2xl border border-slate-200/90 sm:px-10">
          {/* Tabs: Sign In vs Create Account */}
          <div className="flex items-center gap-1 p-1 bg-slate-100 rounded-xl mb-6 border border-slate-200">
            <button
              type="button"
              onClick={() => {
                setActiveTab('login');
                setErrorMessage('');
              }}
              className={`flex-1 py-2.5 text-xs font-bold rounded-lg transition ${
                activeTab === 'login'
                  ? 'bg-amber-600 text-white shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Sign In
            </button>
            <button
              type="button"
              onClick={() => {
                setActiveTab('register');
                setErrorMessage('');
              }}
              className={`flex-1 py-2.5 text-xs font-bold rounded-lg transition ${
                activeTab === 'register'
                  ? 'bg-amber-600 text-white shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Create Account
            </button>
          </div>

          {errorMessage && (
            <div className="mb-5 p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2.5">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          {/* Social OAuth Providers */}
          <div className="space-y-3 mb-6">
            <button
              type="button"
              onClick={handleGoogleOAuth}
              className="w-full flex items-center justify-center gap-3 py-2.5 px-4 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-xs font-semibold text-slate-800 shadow-xs transition cursor-pointer"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24">
                <path
                  fill="#4285F4"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="#34A853"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="#FBBC05"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
                />
                <path
                  fill="#EA4335"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
                />
              </svg>
              <span>Continue with Google</span>
            </button>

            <button
              type="button"
              onClick={handleGitHubOAuth}
              className="w-full flex items-center justify-center gap-3 py-2.5 px-4 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-xs font-semibold text-slate-800 shadow-xs transition cursor-pointer"
            >
              <FolderGit2 className="w-4 h-4 text-slate-800" />
              <span>Continue with GitHub</span>
            </button>
          </div>

          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-200" />
            </div>
            <div className="relative flex justify-center text-xs">
              <span className="px-3 bg-white text-slate-400 font-semibold uppercase tracking-wider text-[10px]">
                Or with credentials
              </span>
            </div>
          </div>

          {/* Sign In Form with Login ID */}
          {activeTab === 'login' ? (
            <form onSubmit={handleSignIn} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">
                  Login ID (Username, Email, or 12-Digit Account ID)
                </label>
                <div className="relative">
                  <User className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    placeholder="e.g. admin, user@company.com, or 109283746519"
                    value={loginId}
                    onChange={(e) => setLoginId(e.target.value)}
                    className="w-full h-10 pl-9 pr-3 bg-white border border-slate-300 rounded-xl text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-amber-600 focus:ring-1 focus:ring-amber-600 font-medium"
                    required
                  />
                </div>
                <p className="mt-1 text-[10px] text-slate-500">
                  Use your Username, Email, or AWS-style 12-digit Account ID
                </p>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">
                  Password
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="password"
                    placeholder="••••••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full h-10 pl-9 pr-3 bg-white border border-slate-300 rounded-xl text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-amber-600 focus:ring-1 focus:ring-amber-600 font-medium"
                    required
                  />
                </div>
              </div>

              <div className="pt-2">
                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full h-11 bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold rounded-xl shadow-md shadow-amber-500/20 transition flex items-center justify-center gap-2 disabled:opacity-50 cursor-pointer"
                >
                  {isLoading ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Authenticating...
                    </>
                  ) : (
                    <>
                      Sign In to Console
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </div>

              <div className="text-center pt-3 border-t border-slate-100">
                <p className="text-[11px] text-slate-500">
                  Default Operator:{' '}
                  <code className="text-slate-700 font-mono font-bold bg-slate-100 px-1 py-0.5 rounded">
                    admin
                  </code>{' '}
                  /{' '}
                  <code className="text-slate-700 font-mono font-bold bg-slate-100 px-1 py-0.5 rounded">
                    admin123
                  </code>
                </p>
                <p className="text-[10px] text-amber-700 font-mono mt-1 font-semibold">
                  AWS Account ID: 1092-8374-6519
                </p>
              </div>
            </form>
          ) : (
            /* Create Account Form */
            <form onSubmit={handleSignUp} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">
                  Account Username / Handle
                </label>
                <div className="relative">
                  <User className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    placeholder="e.g. cloud_engineer"
                    value={loginId}
                    onChange={(e) => setLoginId(e.target.value)}
                    className="w-full h-10 pl-9 pr-3 bg-white border border-slate-300 rounded-xl text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-amber-600 focus:ring-1 focus:ring-amber-600 font-medium"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="email"
                    placeholder="engineer@company.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full h-10 pl-9 pr-3 bg-white border border-slate-300 rounded-xl text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-amber-600 focus:ring-1 focus:ring-amber-600 font-medium"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">
                  Password
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="password"
                    placeholder="Minimum 8 characters"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full h-10 pl-9 pr-3 bg-white border border-slate-300 rounded-xl text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-amber-600 focus:ring-1 focus:ring-amber-600 font-medium"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">
                  Platform Role
                </label>
                <select
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className="w-full h-10 px-3 bg-white border border-slate-300 rounded-xl text-xs text-slate-900 focus:outline-none focus:border-amber-600 font-medium"
                >
                  <option value="USER">Standard User (Workspace &amp; Projects)</option>
                  <option value="ADMIN">Platform Admin (Includes Admin Console)</option>
                </select>
              </div>

              <div className="p-2.5 rounded-lg bg-amber-50 border border-amber-200 text-[11px] text-amber-800 flex items-center gap-2">
                <Key className="w-4 h-4 text-amber-600 shrink-0" />
                <span>A 12-digit AWS-style Account ID will be allocated automatically upon registration.</span>
              </div>

              <div className="pt-2">
                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full h-11 bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold rounded-xl shadow-md shadow-amber-500/20 transition flex items-center justify-center gap-2 disabled:opacity-50 cursor-pointer"
                >
                  {isLoading ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Creating Account...
                    </>
                  ) : (
                    <>
                      Complete Registration
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>

      {/* Post-OAuth Name Clarification Modal (Pure Light Theme) */}
      {showClarificationModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs">
          <div className="bg-white rounded-2xl max-w-md w-full shadow-2xl border border-slate-200 p-6 animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center gap-2 text-slate-900 font-bold text-base mb-1.5">
              <Sparkles className="w-5 h-5 text-amber-600" />
              <span>Confirm Account Handle</span>
            </div>
            <p className="text-xs text-slate-500 mb-4 leading-relaxed">
              Authenticated via {oauthProvider} (
              <span className="text-amber-700 font-mono font-semibold">{oauthVerifiedEmail}</span>
              ). Please confirm your display name:
            </p>

            <form onSubmit={handleConfirmClarifiedName} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">
                  Display Username / Account Handle
                </label>
                <div className="relative">
                  <User className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    value={clarifiedName}
                    onChange={(e) => setClarifiedName(e.target.value)}
                    placeholder="Enter preferred handle"
                    className="w-full h-10 pl-9 pr-3 bg-white border border-slate-300 rounded-xl text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-amber-600 focus:ring-1 focus:ring-amber-600 font-medium"
                    required
                  />
                </div>
              </div>

              <div className="pt-2 border-t border-slate-100 flex items-center justify-end">
                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full h-10 bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold rounded-xl shadow-sm transition flex items-center justify-center gap-2 cursor-pointer"
                >
                  {isLoading ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Saving to Database...
                    </>
                  ) : (
                    <>
                      Confirm &amp; Proceed to Dashboard
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
