// frontend/src/App.jsx
import React from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import { Shield, RefreshCw } from 'lucide-react';

function AppContent() {
  const { isAuthenticated, isLoading } = useAuth();

  // Show authenticating splash screen while checking session credentials
  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-900 flex flex-col items-center justify-center text-white">
        <div className="w-12 h-12 rounded-xl bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/30 mb-4 animate-pulse">
          <Shield className="w-6 h-6 text-white" />
        </div>
        <div className="flex items-center gap-2 text-sm text-slate-300 font-medium">
          <RefreshCw className="w-4 h-4 animate-spin text-blue-400" />
          <span>Verifying secure platform session...</span>
        </div>
      </div>
    );
  }

  // Direct Link Security: If not authenticated, ignore deep direct link and force LoginPage
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
