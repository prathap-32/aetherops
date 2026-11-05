// frontend/src/App.jsx
import React, { useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import { Shield, RefreshCw } from 'lucide-react';

function AppContent() {
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    // Strictly enforce light theme only
    if (typeof document !== 'undefined') {
      document.documentElement.classList.remove('dark');
      document.documentElement.classList.add('light');
      document.body.classList.remove('dark');
      document.body.classList.add('light');
    }
  }, []);

  // Show authenticating splash screen in light theme while checking session credentials
  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center text-slate-800">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-600 flex items-center justify-center shadow-lg shadow-blue-500/25 mb-4 animate-pulse">
          <Shield className="w-6 h-6 text-white" />
        </div>
        <div className="flex items-center gap-2 text-sm text-slate-600 font-medium">
          <RefreshCw className="w-4 h-4 animate-spin text-cyan-600" />
          <span>Verifying secure platform session...</span>
        </div>
      </div>
    );
  }

  // Direct Link Security: If not authenticated, force LoginPage
  if (!isAuthenticated) {
    return <LoginPage />;
  }

  // Authenticated: Render unified dashboard
  return <DashboardPage />;
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
