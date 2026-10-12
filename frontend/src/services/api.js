// frontend/src/services/api.js

export function getActiveToken() {
  return localStorage.getItem('X-Admin-Key') || '';
}

export function getStoredUser() {
  try {
    const raw = localStorage.getItem('aether_user');
    return raw ? JSON.parse(raw) : null;
  } catch (e) {
    return null;
  }
}

export function setStoredSession(token, user) {
  if (token) localStorage.setItem('X-Admin-Key', token);
  if (user) localStorage.setItem('aether_user', JSON.stringify(user));
}

export function clearStoredSession() {
  localStorage.removeItem('X-Admin-Key');
  localStorage.removeItem('aether_user');
}

export async function apiRequest(endpoint, options = {}) {
  const token = getActiveToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'X-Admin-Key': token, 'Authorization': `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };

  const config = {
    ...options,
    headers,
    credentials: 'include', // Include HttpOnly cookies
  };

  const response = await fetch(endpoint, config);

  if (response.status === 401) {
    clearStoredSession();
    // Dispatch unauthorized event so app can redirect
    window.dispatchEvent(new CustomEvent('aether:unauthorized'));
    throw new Error('Session expired or unauthorized. Please log in.');
  }

  const contentType = response.headers.get('content-type') || '';
  let data = null;
  if (contentType.includes('application/json')) {
    data = await response.json();
  } else {
    data = await response.text();
  }

  if (!response.ok) {
    const errorMsg = (data && data.detail) || (data && data.message) || (typeof data === 'string' ? data : 'API Request failed');
    throw new Error(errorMsg);
  }

  return data;
}

export const authApi = {
  login: (username, password) =>
    apiRequest('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }),

  register: (username, email, password) =>
    apiRequest('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, email, password }),
    }),

  oauthCallback: (provider, username, email) =>
    apiRequest('/api/v1/auth/oauth-callback', {
      method: 'POST',
      body: JSON.stringify({ provider, username, email }),
    }),

  getMe: () => apiRequest('/api/v1/auth/me'),

  updateProfile: (username, email) =>
    apiRequest('/api/v1/auth/profile', {
      method: 'PUT',
      body: JSON.stringify({ username, email }),
    }),

  logout: () =>
    apiRequest('/api/v1/auth/logout', { method: 'POST' }).catch(() => {}),
};

export const projectsApi = {
  list: async () => {
    const res = await apiRequest('/api/v1/projects');
    return Array.isArray(res) ? res : (res.projects || []);
  },
  get: (id) => apiRequest(`/api/v1/projects/${id}`),
  create: (project) =>
    apiRequest('/api/v1/projects', {
      method: 'POST',
      body: JSON.stringify(project),
    }),
  delete: (id) =>
    apiRequest(`/api/v1/projects/${id}`, {
      method: 'DELETE',
    }),
  listEnvironments: async (projectId) => {
    const res = await apiRequest(`/api/v1/projects/${projectId}/environments`);
    return Array.isArray(res) ? res : (res.environments || []);
  },
  createEnvironment: (projectId, env) =>
    apiRequest(`/api/v1/projects/${projectId}/environments`, {
      method: 'POST',
      body: JSON.stringify(env),
    }),
};

export const connectionsApi = {
  listGit: async () => {
    const res = await apiRequest('/api/v1/connections');
    return Array.isArray(res) ? res : (res.connections || []);
  },
  listCloud: async () => {
    const res = await apiRequest('/api/v1/cloud/connections');
    return Array.isArray(res) ? res : (res.connections || []);
  },
  verifyPat: (token) =>
    apiRequest('/api/v1/github/verify-pat', {
      method: 'POST',
      body: JSON.stringify({ token }),
    }),
  getRepos: (token) =>
    apiRequest(`/api/v1/github/repos${token ? `?token=${encodeURIComponent(token)}` : ''}`),
  getBranches: (owner, repo, token) =>
    apiRequest(`/api/v1/github/repos/${owner}/${repo}/branches${token ? `?token=${encodeURIComponent(token)}` : ''}`),
  validateAws: (credentials) =>
    apiRequest('/api/v1/cloud/aws/validate', {
      method: 'POST',
      body: JSON.stringify(credentials),
    }),
  finalize: (payload) =>
    apiRequest('/api/v1/connections/finalize', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  getSnapshot: (connectionId) =>
    apiRequest(`/api/v1/connections/${connectionId}/snapshot`),
  refreshSnapshot: (connectionId) =>
    apiRequest(`/api/v1/connections/${connectionId}/refresh`, {
      method: 'POST',
    }),
};

export const repoAnalyzerApi = {
  scanRepo: (payload) =>
    apiRequest('/api/v1/repo/scan', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  scanAndSize: (payload) =>
    apiRequest('/api/v1/repo/scan-and-size', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  dispatch: (payload) =>
    apiRequest('/api/v1/repo/dispatch', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
};

export const adminApi = {
  probe: (region = 'us-east-1') =>
    apiRequest(`/api/admin/probe?region=${encodeURIComponent(region)}`),
  getCatalog: (category = 'all', region = 'us-east-1') =>
    apiRequest(`/api/admin/catalog?category=${encodeURIComponent(category)}&region=${encodeURIComponent(region)}`),
  getModules: () =>
    apiRequest('/api/admin/modules'),
  getAuditLogs: () =>
    apiRequest('/api/admin/auth/audit'),
  clearCache: () =>
    apiRequest('/api/admin/clear-cache', { method: 'POST' }),
  syncCatalog: () =>
    apiRequest('/api/admin/sync', { method: 'POST' }),
};

