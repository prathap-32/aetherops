// frontend/src/context/AuthContext.jsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import { authApi, getStoredUser, setStoredSession, clearStoredSession, getActiveToken } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => getStoredUser());
  const [token, setToken] = useState(() => getActiveToken());
  const [isLoading, setIsLoading] = useState(true);

  const isAdmin = user?.role === 'ADMIN' || user?.role === 'SUPER_ADMIN';

  useEffect(() => {
    async function verifySession() {
      const activeToken = getActiveToken();
      if (!activeToken) {
        setIsLoading(false);
        return;
      }

      try {
        const me = await authApi.getMe();
        if (me && me.username) {
          const updatedUser = {
            username: me.username,
            email: me.email,
            role: me.role || 'USER',
          };
          setUser(updatedUser);
          setStoredSession(activeToken, updatedUser);
        }
      } catch (err) {
        console.warn('Session verification error:', err);
        clearStoredSession();
        setUser(null);
        setToken('');
      } finally {
        setIsLoading(false);
      }
    }

    verifySession();

    const handleUnauthorized = () => {
      setUser(null);
      setToken('');
    };

    window.addEventListener('aether:unauthorized', handleUnauthorized);
    return () => window.removeEventListener('aether:unauthorized', handleUnauthorized);
  }, []);

  const login = async (username, password) => {
    const data = await authApi.login(username, password);
    const authUser = {
      username: data.username,
      email: data.email || `${data.username}@aetherops.cloud`,
      role: data.role || 'ADMIN',
    };
    setStoredSession(data.token, authUser);
    setUser(authUser);
    setToken(data.token);
    return authUser;
  };

  const register = async (username, email, password, role = 'USER') => {
    const data = await authApi.register(username, email, password);
    const authUser = {
      username: data.username,
      email: data.email || email,
      role: data.role || role,
    };
    setStoredSession(data.token, authUser);
    setUser(authUser);
    setToken(data.token);
    return authUser;
  };

  const completeOAuth = async (provider, username, email) => {
    const data = await authApi.oauthCallback(provider, username, email);
    const authUser = {
      username: data.username,
      email: email || `${data.username}@${provider}.oauth`,
      role: data.role || 'USER',
    };
    setStoredSession(data.token, authUser);
    setUser(authUser);
    setToken(data.token);
    return authUser;
  };

  const updateProfile = async (newUsername) => {
    const data = await authApi.updateProfile(newUsername, user?.email);
    const updated = {
      username: data.username,
      email: data.email || user?.email,
      role: data.role || user?.role || 'USER',
    };
    setStoredSession(data.token || token, updated);
    setUser(updated);
    if (data.token) setToken(data.token);
    return updated;
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } finally {
      clearStoredSession();
      setUser(null);
      setToken('');
    }
  };

  const setSessionManually = (tok, usr) => {
    setStoredSession(tok, usr);
    setToken(tok);
    setUser(usr);
  };

  const value = {
    user,
    token,
    isAuthenticated: !!token && !!user,
    isAdmin,
    isLoading,
    login,
    register,
    completeOAuth,
    updateProfile,
    setSessionManually,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
