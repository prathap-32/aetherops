// frontend/src/pages/LoginPage.jsx
import React, { useState, useEffect, useMemo } from 'react';
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
  CheckCircle2,
  Check,
  Send,
  ExternalLink,
  Eye,
  EyeOff
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { authApi } from '../services/api';

export default function LoginPage({ onLoginSuccess }) {
  const { login, register, updateProfile, setSessionManually } = useAuth();

  const [activeTab, setActiveTab] = useState('login'); // 'login' | 'register'
  const [loginId, setLoginId] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  // Live letter-by-letter email existence check
  const [emailStatus, setEmailStatus] = useState('idle'); // 'idle' | 'checking' | 'available' | 'taken' | 'invalid'

  // Email Confirmation Workflow states
  const [isVerificationSent, setIsVerificationSent] = useState(false);
  const [verificationEmail, setVerificationEmail] = useState('');
  const [simulatedVerificationUrl, setSimulatedVerificationUrl] = useState('');
  const [isVerifyingToken, setIsVerifyingToken] = useState(false);
  const [verificationSuccess, setVerificationSuccess] = useState(false);
  const [isResending, setIsResending] = useState(false);
  const [resendNotice, setResendNotice] = useState('');

  // Post-OAuth Account Verification / Name Clarification Modal
  const [showClarificationModal, setShowClarificationModal] = useState(false);
  const [oauthProvider, setOauthProvider] = useState('Google');
  const [oauthVerifiedEmail, setOauthVerifiedEmail] = useState('');
  const [clarifiedName, setClarifiedName] = useState('');
  const [pendingOAuthToken, setPendingOAuthToken] = useState('');
  const [pendingOAuthUser, setPendingOAuthUser] = useState(null);
  // Strictly ensure light theme on document body
  useEffect(() => {
    if (typeof document !== 'undefined') {
      document.documentElement.classList.remove('dark');
      document.documentElement.classList.add('light');
      document.body.classList.remove('dark');
      document.body.classList.add('light');
    }
  }, []);

  // Check URL query parameters on load for email verification token or OAuth redirects
  useEffect(() => {
    // Restore pending verification screen if user refreshed after completing registration
    try {
      const savedPending = sessionStorage.getItem('aether_pending_verification');
      if (savedPending) {
        const parsed = JSON.parse(savedPending);
        if (parsed && parsed.email) {
          setIsVerificationSent(true);
          setVerificationEmail(parsed.email);
          setSimulatedVerificationUrl(parsed.verification_url || '');
        }
      }
    } catch (e) {}

    const params = new URLSearchParams(window.location.search);
    const verifyToken = params.get('verify_token');
    const oauthToken = params.get('token');
    const userParam = params.get('username');
    const emailParam = params.get('email');
    const roleParam = params.get('role') || 'USER';
    const accountIdParam = params.get('account_id') || '';

    // 1. Check if user arrived by clicking an email confirmation link
    if (verifyToken) {
      const confirmEmailToken = async () => {
        setIsVerifyingToken(true);
        setErrorMessage('');
        try {
          const res = await authApi.verifyEmail(verifyToken);
          setVerificationSuccess(true);
          try {
            sessionStorage.removeItem('aether_pending_verification');
          } catch (e) {}
          window.history.replaceState({}, document.title, window.location.pathname);
          if (res.token && res.user) {
            setTimeout(() => {
              setSessionManually(res.token, res.user);
              if (onLoginSuccess) onLoginSuccess();
            }, 1200);
          }
        } catch (err) {
          setErrorMessage(err.message || 'Invalid or expired confirmation link.');
        } finally {
          setIsVerifyingToken(false);
        }
      };
      confirmEmailToken();
      return;
    }

    // 2. Fallback OAuth callback redirect in same window
    if (oauthToken && userParam) {
      const authUser = {
        username: userParam,
        email: emailParam || `${userParam}@oauth.local`,
        role: roleParam,
        account_id: accountIdParam,
      };
      setPendingOAuthToken(oauthToken);
      setPendingOAuthUser(authUser);
      setOauthProvider('OAuth');
      setOauthVerifiedEmail(authUser.email);
      setClarifiedName(userParam);
      setShowClarificationModal(true);
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, [setSessionManually, onLoginSuccess]);

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
        const { token: oToken, user: oauthUser } = event.data;
        if (oToken && oauthUser) {
          // Hold token in pending state so modal can ask and save user's name first!
          setPendingOAuthToken(oToken);
          setPendingOAuthUser(oauthUser);
          setOauthProvider(event.data.type.includes('GITHUB') ? 'GitHub' : 'Google');
          setOauthVerifiedEmail(oauthUser.email || '');
          setClarifiedName(oauthUser.username || '');
          setShowClarificationModal(true);
        }
      }
    };

    window.addEventListener('message', handleOAuthMessage);
    return () => window.removeEventListener('message', handleOAuthMessage);
  }, []);

  // Debounced letter-by-letter email existence check against SQLite indexed users table
  useEffect(() => {
    if (activeTab !== 'register') {
      setEmailStatus('idle');
      return;
    }
    const trimmed = email.trim().toLowerCase();
    if (!trimmed) {
      setEmailStatus('idle');
      return;
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(trimmed)) {
      setEmailStatus(trimmed.includes('@') && trimmed.includes('.') ? 'invalid' : 'idle');
      return;
    }

    setEmailStatus('checking');
    const timer = setTimeout(async () => {
      try {
        const res = await authApi.checkEmail(trimmed);
        if (res.exists) {
          setEmailStatus('taken');
        } else {
          setEmailStatus('available');
        }
      } catch {
        setEmailStatus('idle');
      }
    }, 220);

    return () => clearTimeout(timer);
  }, [email, activeTab]);

  // Dynamic Password Strength Meter with Name/Email restriction
  const passwordStrength = useMemo(() => {
    if (!password) {
      return {
        score: 0,
        percent: 0,
        label: '',
        color: 'bg-slate-200',
        textColor: 'text-slate-400',
        containsNameOrEmail: false,
        hasLength: false,
        hasUpperLower: false,
        hasNumberSymbol: false,
      };
    }

    const userLower = (loginId || '').trim().toLowerCase();
    const emailPrefix = (email || '').split('@')[0].trim().toLowerCase();
    const passLower = password.toLowerCase();

    let containsNameOrEmail = false;
    if (userLower.length >= 3 && passLower.includes(userLower)) {
      containsNameOrEmail = true;
    }
    if (emailPrefix.length >= 3 && passLower.includes(emailPrefix)) {
      containsNameOrEmail = true;
    }

    const hasLength = password.length >= 8;
    const hasUpperLower = /[A-Z]/.test(password) && /[a-z]/.test(password);
    const hasNumberSymbol = /[0-9]/.test(password) && /[^a-zA-Z0-9]/.test(password);
    const hasExtraLength = password.length >= 12;

    let score = 0;
    if (hasLength) score++;
    if (hasUpperLower) score++;
    if (hasNumberSymbol) score++;
    if (hasExtraLength) score++;

    if (containsNameOrEmail) {
      return {
        score: 0,
        percent: 18,
        label: 'Disallowed Content',
        color: 'bg-rose-500',
        textColor: 'text-rose-600',
        containsNameOrEmail: true,
        hasLength,
        hasUpperLower,
        hasNumberSymbol,
      };
    }

    const labels = ['Too Weak', 'Weak', 'Fair', 'Strong', 'Very Strong'];
    const colors = ['bg-rose-500', 'bg-rose-500', 'bg-amber-500', 'bg-blue-600', 'bg-emerald-500'];
    const textColors = ['text-rose-600', 'text-rose-600', 'text-amber-600', 'text-blue-600', 'text-emerald-600'];
    const percents = [10, 25, 50, 75, 100];

    return {
      score,
      percent: percents[score],
      label: labels[score],
      color: colors[score],
      textColor: textColors[score],
      containsNameOrEmail: false,
      hasLength,
      hasUpperLower,
      hasNumberSymbol,
    };
  }, [password, loginId, email]);

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
      if (err.message && err.message.toLowerCase().includes('not confirmed')) {
        setErrorMessage(err.message);
        if (loginId.includes('@')) {
          setVerificationEmail(loginId.trim());
        }
      } else {
        setErrorMessage(err.message || 'Login failed. Invalid Login ID or credentials.');
      }
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

    if (emailStatus === 'taken') {
      setErrorMessage('This email is already registered. Please sign in or use another email.');
      return;
    }

    if (passwordStrength.containsNameOrEmail) {
      setErrorMessage('Password cannot contain your account username or email.');
      return;
    }

    if (!passwordStrength.hasLength) {
      setErrorMessage('Password must be at least 8 characters.');
      return;
    }

    if (password !== confirmPassword) {
      setErrorMessage('Passwords do not match. Please verify both passwords match.');
      return;
    }

    setIsLoading(true);
    try {
      const res = await register(loginId.trim(), email.trim(), password, 'USER');
      if (res && (res.requires_verification || res.status === 'VERIFICATION_SENT')) {
        const registeredEmail = res.email || email.trim();
        setIsVerificationSent(true);
        setVerificationEmail(registeredEmail);
        setSimulatedVerificationUrl(res.verification_url || '');
        try {
          sessionStorage.setItem(
            'aether_pending_verification',
            JSON.stringify({
              email: registeredEmail,
              verification_url: res.verification_url || '',
            })
          );
        } catch (e) {}
        // Clear form fields immediately so inputs do not stay dirty
        setLoginId('');
        setEmail('');
        setPassword('');
        setConfirmPassword('');
        setEmailStatus('idle');
      } else if (onLoginSuccess) {
        setLoginId('');
        setEmail('');
        setPassword('');
        setConfirmPassword('');
        setEmailStatus('idle');
        onLoginSuccess();
      }
    } catch (err) {
      setErrorMessage(err.message || 'Registration failed. Username may already be in use.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleResendConfirmation = async () => {
    if (!verificationEmail) return;
    setIsResending(true);
    setResendNotice('');
    setErrorMessage('');
    try {
      const res = await authApi.resendVerification(verificationEmail);
      setResendNotice(res.message || 'Verification link resent to your email.');
      if (res.verification_url) {
        setSimulatedVerificationUrl(res.verification_url);
      }
    } catch (err) {
      setErrorMessage(err.message || 'Failed to resend confirmation email.');
    } finally {
      setIsResending(false);
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
      const updated = await authApi.updateProfile(
        clarifiedName.trim(),
        pendingOAuthUser?.email || oauthVerifiedEmail,
        pendingOAuthToken
      );
      const finalUser = updated.user || {
        ...(pendingOAuthUser || {}),
        username: clarifiedName.trim(),
      };
      const finalToken = updated.token || pendingOAuthToken;
      setSessionManually(finalToken, finalUser);
      setShowClarificationModal(false);
      if (onLoginSuccess) onLoginSuccess();
    } catch (err) {
      // Fallback
      const finalUser = {
        ...(pendingOAuthUser || {}),
        username: clarifiedName.trim(),
      };
      setSessionManually(pendingOAuthToken, finalUser);
      setShowClarificationModal(false);
      if (onLoginSuccess) onLoginSuccess();
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#f8fafc] via-[#f1f5f9] to-[#e2e8f0] text-slate-900 flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative overflow-hidden select-none">
      {/* Ambient Cyber-Cloud Glow Orbs matching AetherOps Logo (Electric Blue & Cyber Cyan) */}
      <div className="absolute -top-24 -left-24 w-[480px] h-[480px] bg-gradient-to-br from-blue-600/12 via-indigo-500/10 to-transparent rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-24 -right-24 w-[480px] h-[480px] bg-gradient-to-tl from-cyan-500/15 via-blue-500/10 to-transparent rounded-full blur-3xl pointer-events-none" />
      <div className="absolute inset-0 bg-[radial-gradient(#3d5aea_1px,transparent_1px)] [background-size:28px_28px] opacity-[0.03] pointer-events-none" />

      <div className="sm:mx-auto sm:w-full sm:max-w-md z-10 px-4 text-center">
        {/* AetherOps Brand Mark - Integrated, Non-Downloadable, Non-Draggable */}
        <div
          className="relative inline-flex flex-col items-center justify-center mb-6 select-none pointer-events-none"
          onContextMenu={(e) => e.preventDefault()}
        >
          <div className="absolute -inset-4 bg-gradient-to-r from-blue-600/15 via-cyan-400/20 to-indigo-600/15 rounded-3xl blur-xl" />
          <picture className="relative inline-flex items-center justify-center select-none pointer-events-none">
            <source srcSet="/static/logo/aetherops_transparent.webp" type="image/webp" />
            <img
              src="/static/logo/aetherops_transparent.png"
              alt=""
              aria-hidden="true"
              role="presentation"
              draggable={false}
              onContextMenu={(e) => e.preventDefault()}
              className="relative h-12 sm:h-14 w-auto max-w-[280px] object-contain select-none pointer-events-none drop-shadow-sm"
              style={{ WebkitUserDrag: 'none', userSelect: 'none' }}
              width="280"
              height="71"
              loading="eager"
            />
          </picture>
        </div>
      </div>

      <div className="mt-2 sm:mx-auto sm:w-full sm:max-w-md z-10 px-4">
        <div className="relative bg-white/95 backdrop-blur-md py-8 px-6 shadow-2xl shadow-slate-900/8 rounded-2xl border border-slate-200/90 sm:px-10">
          <div className="absolute top-0 left-8 right-8 h-[2px] bg-gradient-to-r from-transparent via-cyan-500 to-transparent opacity-80" />

          {/* Email Verification In-Progress or Confirmed States */}
          {isVerifyingToken ? (
            <div className="py-8 text-center space-y-4">
              <div className="w-14 h-14 mx-auto rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center text-white shadow-lg shadow-blue-500/25 animate-pulse">
                <RefreshCw className="w-7 h-7 animate-spin" />
              </div>
              <h2 className="text-base font-bold text-slate-900">Verifying Email Address...</h2>
              <p className="text-xs text-slate-500 max-w-xs mx-auto">
                Confirming your activation token with the security authority.
              </p>
            </div>
          ) : verificationSuccess ? (
            <div className="py-8 text-center space-y-4 animate-in fade-in zoom-in-95 duration-200">
              <div className="w-14 h-14 mx-auto rounded-2xl bg-gradient-to-br from-emerald-500 to-cyan-500 flex items-center justify-center text-white shadow-lg shadow-emerald-500/25">
                <CheckCircle2 className="w-8 h-8" />
              </div>
              <div>
                <h2 className="text-base font-bold text-slate-900">Email Confirmed Successfully!</h2>
                <p className="text-xs text-slate-500 mt-1 max-w-xs mx-auto">
                  Your AetherOps account is now active. Launching your workspace dashboard...
                </p>
              </div>
              <div className="pt-2 flex items-center justify-center gap-2 text-xs font-semibold text-cyan-600">
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Redirecting to Console...</span>
              </div>
            </div>
          ) : isVerificationSent ? (
            /* Email Confirmation Sent Screen */
            <div className="py-4 text-center space-y-4 animate-in fade-in zoom-in-95 duration-200">
              <div className="w-14 h-14 mx-auto rounded-2xl bg-gradient-to-br from-blue-600 to-cyan-500 flex items-center justify-center text-white shadow-lg shadow-blue-500/25">
                <Mail className="w-7 h-7" />
              </div>
              <div>
                <h2 className="text-base font-bold text-slate-900">Check Your Email</h2>
                <p className="text-xs text-slate-600 mt-1.5 leading-relaxed">
                  We sent an account confirmation email to:
                </p>
                <p className="text-xs font-mono font-bold text-blue-700 bg-blue-50/80 px-3 py-1.5 rounded-lg border border-blue-200/60 inline-block mt-2 break-all">
                  {verificationEmail}
                </p>
              </div>

              <p className="text-[11px] text-slate-500 leading-relaxed text-left bg-slate-50 p-3.5 rounded-xl border border-slate-200/80">
                Click the verification button in the email to activate your account. Once verified, you will be automatically redirected to your AetherOps console.
              </p>

              {simulatedVerificationUrl && (
                <div className="pt-1">
                  <a
                    href={simulatedVerificationUrl}
                    className="w-full h-10 bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white text-xs font-bold rounded-xl shadow-md shadow-blue-500/20 transition flex items-center justify-center gap-2 cursor-pointer"
                  >
                    <span>Verify Email Now (Instant Link)</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                </div>
              )}

              {resendNotice && (
                <div className="p-2.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs flex items-center justify-center gap-2">
                  <CheckCircle2 className="w-4 h-4 shrink-0" />
                  <span>{resendNotice}</span>
                </div>
              )}

              <div className="pt-3 border-t border-slate-100 flex flex-col gap-2">
                <button
                  type="button"
                  onClick={handleResendConfirmation}
                  disabled={isResending}
                  className="text-xs font-semibold text-blue-600 hover:text-blue-700 flex items-center justify-center gap-1.5 py-1 transition cursor-pointer disabled:opacity-50"
                >
                  {isResending ? (
                    <>
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                      <span>Resending email...</span>
                    </>
                  ) : (
                    <>
                      <Send className="w-3.5 h-3.5" />
                      <span>Didn't receive email? Resend</span>
                    </>
                  )}
                </button>

                <button
                  type="button"
                  onClick={() => {
                    try {
                      sessionStorage.removeItem('aether_pending_verification');
                    } catch (e) {}
                    setIsVerificationSent(false);
                    setVerificationEmail('');
                    setSimulatedVerificationUrl('');
                    setLoginId('');
                    setEmail('');
                    setPassword('');
                    setConfirmPassword('');
                    setEmailStatus('idle');
                    setActiveTab('login');
                    setErrorMessage('');
                  }}
                  className="text-xs text-slate-500 hover:text-slate-800 transition py-1 cursor-pointer"
                >
                  Back to Sign In
                </button>
              </div>
            </div>
          ) : (
            <>
              {/* Tabs: Sign In vs Create Account */}
              <div className="flex items-center gap-1 p-1 bg-slate-100/90 rounded-xl mb-6 border border-slate-200/80">
                <button
                  type="button"
                  onClick={() => {
                    setActiveTab('login');
                    setErrorMessage('');
                  }}
                  className={`flex-1 py-2.5 text-xs font-bold rounded-lg transition ${
                    activeTab === 'login'
                      ? 'bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-600 text-white shadow-sm shadow-blue-500/25'
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
                      ? 'bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-600 text-white shadow-sm shadow-blue-500/25'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  Create Account
                </button>
              </div>

              {errorMessage && (
                <div className="mb-5 p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2.5">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span className="flex-1">{errorMessage}</span>
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
                <form onSubmit={handleSignIn} className="space-y-4" autoComplete="off">
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1.5">
                      Login ID (Username, Email, or 12-Digit Account ID)
                    </label>
                    <div className="relative">
                      <User className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                      <input
                        type="text"
                        placeholder="e.g. admin, user@company.com, or Account ID"
                        value={loginId}
                        onChange={(e) => setLoginId(e.target.value)}
                        className="w-full h-10 pl-9 pr-3 bg-white border border-slate-300 rounded-xl text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-cyan-500/20 font-medium transition"
                        required
                      />
                    </div>
                    <p className="mt-1 text-[10px] text-slate-500">
                      Use your Username, Email, or 12-digit Account ID
                    </p>
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1.5">
                      Password
                    </label>
                    <div className="relative">
                      <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                      <input
                        type={showPassword ? 'text' : 'password'}
                        placeholder="••••••••••••"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="w-full h-10 pl-9 pr-10 bg-white border border-slate-300 rounded-xl text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-cyan-500/20 font-medium transition"
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                        tabIndex={-1}
                      >
                        {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>

                  <div className="pt-2">
                    <button
                      type="submit"
                      disabled={isLoading}
                      className="w-full h-11 bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-600 hover:from-blue-500 hover:via-indigo-500 hover:to-cyan-500 text-white text-xs font-bold rounded-xl shadow-lg shadow-blue-600/20 hover:shadow-cyan-500/25 transition-all flex items-center justify-center gap-2 disabled:opacity-50 cursor-pointer"
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
                </form>
              ) : (
                /* Create Account Form */
                <form onSubmit={handleSignUp} className="space-y-4" autoComplete="off">
                  {/* Username */}
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
                        className="w-full h-10 pl-9 pr-3 bg-white border border-slate-300 rounded-xl text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-cyan-500/20 font-medium transition"
                        required
                      />
                    </div>
                  </div>

                  {/* Email with Live Letter-by-Letter Data Indexing Lookup */}
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
                        className={`w-full h-10 pl-9 pr-9 bg-white border rounded-xl text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none font-medium transition ${
                          emailStatus === 'taken'
                            ? 'border-rose-400 focus:border-rose-500 focus:ring-2 focus:ring-rose-500/20'
                            : emailStatus === 'available'
                            ? 'border-emerald-400 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20'
                            : 'border-slate-300 focus:border-blue-600 focus:ring-2 focus:ring-cyan-500/20'
                        }`}
                        required
                      />
                      <div className="absolute right-3 top-1/2 -translate-y-1/2">
                        {emailStatus === 'checking' && (
                          <RefreshCw className="w-4 h-4 animate-spin text-cyan-600" />
                        )}
                        {emailStatus === 'available' && (
                          <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                        )}
                        {emailStatus === 'taken' && (
                          <AlertCircle className="w-4 h-4 text-rose-500" />
                        )}
                      </div>
                    </div>

                    {/* Live status feedback */}
                    <div className="mt-1 min-h-[16px]">
                      {emailStatus === 'checking' && (
                        <span className="text-[10px] text-slate-400 flex items-center gap-1">
                          Checking email availability...
                        </span>
                      )}
                      {emailStatus === 'taken' && (
                        <span className="text-[10px] font-semibold text-rose-600 flex items-center gap-1">
                          <AlertCircle className="w-3 h-3 shrink-0" />
                          Email already registered. Please sign in or use another email.
                        </span>
                      )}
                      {emailStatus === 'available' && (
                        <span className="text-[10px] font-semibold text-emerald-600 flex items-center gap-1">
                          <CheckCircle2 className="w-3 h-3 shrink-0" />
                          Email address is available!
                        </span>
                      )}
                      {emailStatus === 'invalid' && (
                        <span className="text-[10px] text-amber-600 flex items-center gap-1">
                          Please enter a valid email address
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Password + Strength Range Bar */}
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1.5">
                      Password
                     </label>
                     <div className="relative">
                       <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                      <input
                        type={showPassword ? 'text' : 'password'}
                        placeholder="Minimum 8 characters"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        autoComplete="new-password"
                        className={`w-full h-10 pl-9 pr-10 bg-white border rounded-xl text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none font-medium transition ${
                          passwordStrength.containsNameOrEmail
                            ? 'border-rose-400 focus:border-rose-500 focus:ring-2 focus:ring-rose-500/20'
                            : 'border-slate-300 focus:border-blue-600 focus:ring-2 focus:ring-cyan-500/20'
                        }`}
                        required
                      />
                       <button
                         type="button"
                         onClick={() => setShowPassword(!showPassword)}
                         className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                         tabIndex={-1}
                       >
                         {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                       </button>
                     </div>

                     {/* Password Strength Range Bar */}
                     {password && (
                       <div className="mt-2 space-y-1.5">
                         <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                           <div
                             className={`h-full transition-all duration-300 ${passwordStrength.color}`}
                             style={{ width: `${passwordStrength.percent}%` }}
                           />
                         </div>

                         <div className="flex items-center justify-between text-[10px]">
                           <span className={`font-bold ${passwordStrength.textColor}`}>
                             Strength: {passwordStrength.label}
                           </span>
                           <div className="flex items-center gap-2 text-slate-400 font-medium">
                             <span className={passwordStrength.hasLength ? 'text-emerald-600 font-semibold' : ''}>
                               8+ chars
                             </span>
                             <span className={passwordStrength.hasUpperLower ? 'text-emerald-600 font-semibold' : ''}>
                               Aa
                             </span>
                             <span className={passwordStrength.hasNumberSymbol ? 'text-emerald-600 font-semibold' : ''}>
                               123#
                             </span>
                           </div>
                         </div>

                         {passwordStrength.containsNameOrEmail && (
                           <p className="text-[10px] font-semibold text-rose-600 flex items-center gap-1 mt-0.5">
                             <AlertCircle className="w-3 h-3 shrink-0" />
                             Password cannot contain your username or email address.
                           </p>
                         )}
                       </div>
                     )}
                   </div>

                   {/* Confirm Password */}
                   <div>
                     <label className="block text-xs font-bold text-slate-700 mb-1.5">
                       Confirm Password
                     </label>
                     <div className="relative">
                       <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                      <input
                        type={showConfirmPassword ? 'text' : 'password'}
                        placeholder="Re-enter password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        autoComplete="new-password"
                        className={`w-full h-10 pl-9 pr-10 bg-white border rounded-xl text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none font-medium transition ${
                          confirmPassword && confirmPassword !== password
                            ? 'border-rose-400 focus:border-rose-500 focus:ring-2 focus:ring-rose-500/20'
                            : confirmPassword && confirmPassword === password
                            ? 'border-emerald-400 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20'
                            : 'border-slate-300 focus:border-blue-600 focus:ring-2 focus:ring-cyan-500/20'
                        }`}
                        required
                      />
                       <button
                         type="button"
                         onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                         className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                         tabIndex={-1}
                       >
                         {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                       </button>
                     </div>

                     {confirmPassword && (
                       <div className="mt-1 text-[10px]">
                         {confirmPassword === password ? (
                           <span className="font-semibold text-emerald-600 flex items-center gap-1">
                             <CheckCircle2 className="w-3 h-3 shrink-0" />
                             Passwords match!
                           </span>
                         ) : (
                           <span className="font-semibold text-rose-600 flex items-center gap-1">
                             <AlertCircle className="w-3 h-3 shrink-0" />
                             Passwords do not match.
                           </span>
                         )}
                       </div>
                     )}
                   </div>

                   <div className="pt-2">
                     <button
                       type="submit"
                       disabled={
                         isLoading ||
                         emailStatus === 'taken' ||
                         passwordStrength.containsNameOrEmail ||
                         (confirmPassword && confirmPassword !== password)
                       }
                       className="w-full h-11 bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-600 hover:from-blue-500 hover:via-indigo-500 hover:to-cyan-500 text-white text-xs font-bold rounded-xl shadow-lg shadow-blue-600/20 hover:shadow-cyan-500/25 transition-all flex items-center justify-center gap-2 disabled:opacity-50 cursor-pointer"
                     >
                       {isLoading ? (
                         <>
                           <RefreshCw className="w-4 h-4 animate-spin" />
                           Creating Account &amp; Sending Email...
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
             </>
           )}
         </div>
      </div>

      {/* Post-OAuth Name Clarification Modal (Pure Light Theme) */}
      {showClarificationModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs">
          <div className="bg-white rounded-2xl max-w-md w-full shadow-2xl border border-slate-200 p-6 animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center gap-2 text-slate-900 font-bold text-base mb-1.5">
              <Sparkles className="w-5 h-5 text-cyan-600" />
              <span>Welcome to AetherOps! Confirm Your Name</span>
            </div>
            <p className="text-xs text-slate-500 mb-4 leading-relaxed">
              Authenticated via {oauthProvider} (
              <span className="text-blue-700 font-mono font-semibold">{oauthVerifiedEmail}</span>
              ). Please confirm or enter your display name to proceed:
            </p>

            <form onSubmit={handleConfirmClarifiedName} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">
                  Your Name / Account Handle
                </label>
                <div className="relative">
                  <User className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    value={clarifiedName}
                    onChange={(e) => setClarifiedName(e.target.value)}
                    placeholder="Enter preferred handle"
                    className="w-full h-10 pl-9 pr-3 bg-white border border-slate-300 rounded-xl text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-cyan-500/20 font-medium transition"
                    required
                  />
                </div>
              </div>

              <div className="pt-2 border-t border-slate-100 flex items-center justify-end">
                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full h-10 bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white text-xs font-bold rounded-xl shadow-md shadow-blue-500/20 transition flex items-center justify-center gap-2 cursor-pointer"
                >
                  {isLoading ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Saving to Database...
                    </>
                  ) : (
                    <>
                      Save Name &amp; Launch Dashboard
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
