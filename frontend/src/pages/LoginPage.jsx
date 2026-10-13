// frontend/src/pages/LoginPage.jsx
import React, { useState, useEffect } from 'react';
import {
  Shield,
  Lock,
  Mail,
  User,
  ArrowRight,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  FolderGit2,
  Sparkles,
  Key
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function LoginPage({ onLoginSuccess }) {
  const { login, register, completeOAuth, updateProfile, setSessionManually } = useAuth();

  const [activeTab, setActiveTab] = useState('login'); // 'login' | 'register'
  const [username, setUsername] = useState('');
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

  // Listen for OAuth messages from popup window
  useEffect(() => {
    const handleOAuthMessage = async (event) => {
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

    if (token && userParam) {
      const authUser = {
        username: userParam,
        email: emailParam || `${userParam}@oauth.local`,
        role: roleParam,
      };
      setSessionManually(token, authUser);
      setPendingToken(token);
      setOauthProvider('Google');
      setOauthVerifiedEmail(authUser.email);
      setClarifiedName(userParam);
      setShowClarificationModal(true);
      // Clean query string from browser bar
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, [setSessionManually]);

  const handleSignIn = async (e) => {
    e.preventDefault();
    setErrorMessage('');
    if (!username.trim() || !password) {
      setErrorMessage('Please enter both username and password.');
      return;
    }

    setIsLoading(true);
    try {
      await login(username.trim(), password);
      if (onLoginSuccess) onLoginSuccess();
    } catch (err) {
      setErrorMessage(err.message || 'Login failed. Invalid username or credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSignUp = async (e) => {
    e.preventDefault();
    setErrorMessage('');
    if (!username.trim() || !email.trim() || !password) {
      setErrorMessage('Please complete all registration fields.');
      return;
    }

    setIsLoading(true);
    try {
      await register(username.trim(), email.trim(), password, role);
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
      // Popups blocked by browser; navigate in current window
      window.location.href = url;
    }
  };

  const handleGoogleOAuth = () => {
    openOAuthPopup('/api/v1/auth/google/login', 'google_oauth');
  };

  const handleGitHubOAuth = () => {
    openOAuthPopup('/api/v1/auth/github/login', 'github_oauth');
  };

  // Submit Post-OAuth Name Clarification to persist into PostgreSQL
  const handleConfirmClarifiedName = async (e) => {
    e.preventDefault();
    if (!clarifiedName.trim()) return;

    setIsLoading(true);
    try {
      // Persist chosen handle to DB profile
      await updateProfile(clarifiedName.trim());
      setShowClarificationModal(false);
      if (onLoginSuccess) onLoginSuccess();
    } catch (err) {
      // Fallback: continue into dashboard with verified name
      setShowClarificationModal(false);
      if (onLoginSuccess) onLoginSuccess();
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[var(--bg-page)] dark:bg-slate-900 flex flex-col justify-center py-16 sm:px-6 lg:px-8 relative overflow-hidden selection:bg-[var(--accent-primary)] selection:text-white">
      {/* Background Glow Orbs - Warmer tones */}
      <div className="absolute top-0 -left-20 w-96 h-96 bg-amber-600/8 dark:bg-amber-600/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 -right-20 w-96 h-96 bg-orange-600/8 dark:bg-orange-600/10 rounded-full blur-3xl pointer-events-none" />

      <div className="sm:mx-auto sm:w-full sm:max-w-md z-10 px-4">
        <div className="flex items-center justify-center gap-4 mb-3">
          <div className="w-12 h-12 rounded-xl bg-[var(--accent-primary)] flex items-center justify-center text-white shadow-lg shadow-amber-500/25 dark:shadow-amber-500/30">
            <Shield className="w-7 h-7" />
          </div>
          <div>
            <h2 className="text-3xl font-black tracking-tight text-[var(--text-primary)]">AETHER CLOUD</h2>
            <p className="text-[11px] font-semibold uppercase tracking-widest text-[var(--accent-primary)]">
              Autonomous Cloud Platform
            </p>
          </div>
        </div>
        <p className="mt-4 text-center text-sm text-[var(--text-muted)] max-w-sm mx-auto leading-relaxed">
          Decoupled Multi-Service DevOps & Cloud Architecture Engine
        </p>
      </div>

      <div className="mt-10 sm:mx-auto sm:w-full sm:max-w-md z-10 px-4">
        <div className="bg-[var(--bg-surface)] dark:bg-slate-800/80 dark:backdrop-blur-xl py-10 px-8 shadow-[var(--card-shadow)] rounded-2xl border border-[var(--border)] dark:border-slate-700 sm:px-12">
          {/* Tabs: Sign In vs Sign Up */}
          <div className="flex items-center gap-2 p-1.5 bg-[var(--bg-subtle)] dark:bg-slate-900/80 rounded-xl mb-8 border border-[var(--border)] dark:border-slate-700/60">
            <button
              type="button"
              onClick={() => {
                setActiveTab('login');
                setErrorMessage('');
              }}
              className={`flex-1 py-3 text-sm font-bold rounded-lg transition ${
                activeTab === 'login'
                  ? 'bg-[var(--accent-primary)] text-white shadow-md'
                  : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'
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
              className={`flex-1 py-3 text-sm font-bold rounded-lg transition ${
                activeTab === 'register'
                  ? 'bg-[var(--accent-primary)] text-white shadow-md'
                  : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'
              }`}
            >
              Create Account
            </button>
          </div>

          {errorMessage && (
            <div className="mb-6 p-4 rounded-xl bg-[var(--status-error-bg)] border border-red-200 dark:border-rose-500/20 text-[var(--status-error-text)] dark:text-rose-300 text-sm flex items-center gap-3">
              <AlertCircle className="w-5 h-5 shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          {/* Social OAuth Buttons */}
          <div className="space-y-4 mb-8">
            <button
              type="button"
              onClick={handleGoogleOAuth}
              className="w-full flex items-center justify-center gap-3 py-3 px-4 rounded-xl border border-[var(--border)] dark:border-slate-600 bg-[var(--bg-surface)] dark:bg-slate-700/50 hover:bg-[var(--bg-subtle)] dark:hover:bg-slate-700 text-sm font-semibold text-[var(--text-primary)] dark:text-white shadow-sm transition cursor-pointer"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24">
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
              className="w-full flex items-center justify-center gap-3 py-3 px-4 rounded-xl border border-[var(--border)] dark:border-slate-600 bg-[var(--bg-surface)] dark:bg-slate-700/50 hover:bg-[var(--bg-subtle)] dark:hover:bg-slate-700 text-sm font-semibold text-[var(--text-primary)] dark:text-white shadow-sm transition cursor-pointer"
            >
              <FolderGit2 className="w-5 h-5" />
              <span>Continue with GitHub</span>
            </button>
          </div>

          <div className="relative my-8">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-[var(--border)] dark:border-slate-700" />
            </div>
            <div className="relative flex justify-center text-xs">
              <span className="px-4 bg-[var(--bg-surface)] dark:bg-slate-800 text-[var(--text-muted)] font-semibold uppercase tracking-widest text-[11px]">
                Or with credentials
              </span>
            </div>
          </div>

          {/* Sign In Form */}
          {activeTab === 'login' ? (
            <form onSubmit={handleSignIn} className="space-y-6">
              <div>
                <label className="block text-sm font-semibold text-[var(--text-secondary)] mb-2">
                  Username or Handle
                </label>
                <div className="relative">
                  <User className="w-5 h-5 text-[var(--text-muted)] absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    placeholder="e.g. admin or developer"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="w-full h-11 pl-11 pr-4 bg-[var(--bg-surface)] dark:bg-slate-900 border border-[var(--border)] dark:border-slate-700 rounded-xl text-sm text-[var(--text-primary)] dark:text-white placeholder-[var(--text-muted)] dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)]/40 focus:border-[var(--accent-primary)] font-medium"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-[var(--text-secondary)] mb-2">
                  Password
                </label>
                <div className="relative">
                  <Lock className="w-5 h-5 text-[var(--text-muted)] absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="password"
                    placeholder="••••••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full h-11 pl-11 pr-4 bg-[var(--bg-surface)] dark:bg-slate-900 border border-[var(--border)] dark:border-slate-700 rounded-xl text-sm text-[var(--text-primary)] dark:text-white placeholder-[var(--text-muted)] dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)]/40 focus:border-[var(--accent-primary)] font-medium"
                    required
                  />
                </div>
              </div>

              <div className="pt-2">
                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full h-12 bg-[var(--accent-primary)] hover:bg-[var(--accent-primary-hover)] text-white text-sm font-bold rounded-xl shadow-lg shadow-amber-500/20 dark:shadow-amber-500/25 transition flex items-center justify-center gap-2 disabled:opacity-50 cursor-pointer"
                >
                  {isLoading ? (
                    <>
                      <RefreshCw className="w-5 h-5 animate-spin" />
                      Authenticating...
                    </>
                  ) : (
                    <>
                      Sign In to Dashboard
                      <ArrowRight className="w-5 h-5" />
                    </>
                  )}
                </button>
              </div>

              <div className="text-center pt-3 border-t border-[var(--border)] dark:border-slate-700">
                <p className="text-xs text-[var(--text-muted)]">
                  Default Operator: <code className="text-[var(--text-secondary)] font-mono font-semibold">admin</code> / <code className="text-[var(--text-secondary)] font-mono font-semibold">admin123</code>
                </p>
              </div>
            </form>
          ) : (
            /* Sign Up Form */
            <form onSubmit={handleSignUp} className="space-y-6">
              <div>
                <label className="block text-sm font-semibold text-[var(--text-secondary)] mb-2">
                  Username
                </label>
                <div className="relative">
                  <User className="w-5 h-5 text-[var(--text-muted)] absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    placeholder="e.g. dev_engineer"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="w-full h-11 pl-11 pr-4 bg-[var(--bg-surface)] dark:bg-slate-900 border border-[var(--border)] dark:border-slate-700 rounded-xl text-sm text-[var(--text-primary)] dark:text-white placeholder-[var(--text-muted)] dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)]/40 focus:border-[var(--accent-primary)] font-medium"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-[var(--text-secondary)] mb-2">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="w-5 h-5 text-[var(--text-muted)] absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="email"
                    placeholder="engineer@company.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full h-11 pl-11 pr-4 bg-[var(--bg-surface)] dark:bg-slate-900 border border-[var(--border)] dark:border-slate-700 rounded-xl text-sm text-[var(--text-primary)] dark:text-white placeholder-[var(--text-muted)] dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)]/40 focus:border-[var(--accent-primary)] font-medium"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-[var(--text-secondary)] mb-2">
                  Password
                </label>
                <div className="relative">
                  <Lock className="w-5 h-5 text-[var(--text-muted)] absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="password"
                    placeholder="Minimum 8 characters"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full h-11 pl-11 pr-4 bg-[var(--bg-surface)] dark:bg-slate-900 border border-[var(--border)] dark:border-slate-700 rounded-xl text-sm text-[var(--text-primary)] dark:text-white placeholder-[var(--text-muted)] dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)]/40 focus:border-[var(--accent-primary)] font-medium"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-[var(--text-secondary)] mb-2">
                  Platform Role
                </label>
                <select
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className="w-full h-11 py-2.5 px-3.5 bg-[var(--bg-surface)] dark:bg-slate-900 border border-[var(--border)] dark:border-slate-700 rounded-xl text-sm text-[var(--text-primary)] dark:text-white focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)]/40 focus:border-[var(--accent-primary)] font-medium"
                >
                  <option value="USER">Standard User (Workspace & Projects)</option>
                  <option value="ADMIN">Platform Admin (Includes Admin Console)</option>
                </select>
              </div>

              <div className="pt-2">
                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full h-12 bg-[var(--accent-primary)] hover:bg-[var(--accent-primary-hover)] text-white text-sm font-bold rounded-xl shadow-lg shadow-amber-500/20 dark:shadow-amber-500/25 transition flex items-center justify-center gap-2 disabled:opacity-50 cursor-pointer"
                >
                  {isLoading ? (
                    <>
                      <RefreshCw className="w-5 h-5 animate-spin" />
                      Creating Account...
                    </>
                  ) : (
                    <>
                      Complete Registration
                      <ArrowRight className="w-5 h-5" />
                    </>
                  )}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>

      {/* Post-OAuth Name Clarification Modal */}
      {showClarificationModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 dark:bg-slate-950/90 backdrop-blur-md">
          <div className="bg-[var(--bg-surface)] dark:bg-slate-800 rounded-2xl max-w-md w-full shadow-2xl border border-[var(--border)] dark:border-slate-700 p-8 animate-in fade-in zoom-in-95 duration-200">
            <div className="flex items-center gap-3 text-[var(--text-primary)] dark:text-white font-bold text-xl mb-2">
              <Sparkles className="w-6 h-6 text-[var(--accent-primary)]" />
              <span>Confirm Account Handle</span>
            </div>
            <p className="text-sm text-[var(--text-muted)] mb-6 leading-relaxed">
              Your {oauthProvider.toUpperCase()} identity was authenticated (<span className="text-[var(--accent-primary)] font-mono font-semibold">{oauthVerifiedEmail}</span>). Please confirm or adjust your display name to persist in database.
            </p>

            <form onSubmit={handleConfirmClarifiedName} className="space-y-6">
              <div>
                <label className="block text-sm font-semibold text-[var(--text-secondary)] mb-2">
                  Display Username / Account Handle
                </label>
                <div className="relative">
                  <User className="w-5 h-5 text-[var(--text-muted)] absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    value={clarifiedName}
                    onChange={(e) => setClarifiedName(e.target.value)}
                    placeholder="Enter preferred handle"
                    className="w-full h-11 pl-11 pr-4 bg-[var(--bg-surface)] dark:bg-slate-900 border border-[var(--border)] dark:border-slate-700 rounded-xl text-sm text-[var(--text-primary)] dark:text-white placeholder-[var(--text-muted)] dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)]/40 focus:border-[var(--accent-primary)] font-medium"
                    required
                  />
                </div>
              </div>

              <div className="flex items-center justify-end pt-4 border-t border-[var(--border)] dark:border-slate-700">
                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full h-12 bg-[var(--accent-primary)] hover:bg-[var(--accent-primary-hover)] text-white text-sm font-bold rounded-xl shadow-lg shadow-amber-500/20 dark:shadow-amber-500/25 transition flex items-center justify-center gap-2 cursor-pointer"
                >
                  {isLoading ? (
                    <>
                      <RefreshCw className="w-5 h-5 animate-spin" />
                      Saving to Database...
                    </>
                  ) : (
                    <>
                      Confirm & Proceed to Dashboard
                      <ArrowRight className="w-5 h-5" />
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
