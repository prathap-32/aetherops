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

export function formatAccountId(accountId) {
  if (!accountId) return '1092-8374-6519';
  const s = String(accountId).replace(/\D/g, '');
  if (s.length === 12) {
    return `${s.slice(0, 4)}-${s.slice(4, 8)}-${s.slice(8, 12)}`;
  }
  return accountId;
}

export async function apiRequest(endpoint, options = {}) {
  const token = getActiveToken();
  const user = getStoredUser();
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'X-Admin-Key': token, 'Authorization': `Bearer ${token}` } : {}),
    ...(user && user.account_id ? { 'X-Account-ID': user.account_id } : {}),
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
    let errorMsg = 'API Request failed';
    if (typeof data === 'string' && data.trim()) {
      errorMsg = data;
    } else if (data && typeof data.detail === 'string') {
      errorMsg = data.detail;
    } else if (data && Array.isArray(data.detail)) {
      errorMsg = data.detail
        .map((d) => (typeof d === 'string' ? d : d.msg || `${d.loc ? d.loc.slice(-1) : 'field'}: ${d.msg || 'invalid'}`))
        .join(', ');
    } else if (data && typeof data.detail === 'object' && data.detail !== null) {
      errorMsg = data.detail.msg || data.detail.message || JSON.stringify(data.detail);
    } else if (data && data.message) {
      errorMsg = typeof data.message === 'string' ? data.message : JSON.stringify(data.message);
    }
    throw new Error(errorMsg);
  }

  return data;
}

// Auth API points directly to auth microservice (port 7999)
const AUTH_SERVICE_URL = 'http://localhost:7999';

export const authApi = {
  login: (username, password) =>
    apiRequest(`${AUTH_SERVICE_URL}/api/v1/auth/login`, {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }),

  register: (username, email, password, role = 'USER') =>
    apiRequest(`${AUTH_SERVICE_URL}/api/v1/auth/register`, {
      method: 'POST',
      body: JSON.stringify({ username, email, password, role }),
    }),

  oauthCallback: (provider, username, email) =>
    apiRequest(`${AUTH_SERVICE_URL}/api/v1/auth/oauth-callback`, {
      method: 'POST',
      body: JSON.stringify({ provider, username, email }),
    }),

  getMe: () => apiRequest(`${AUTH_SERVICE_URL}/api/v1/auth/me`),

  updateProfile: (username, email) =>
    apiRequest(`${AUTH_SERVICE_URL}/api/v1/auth/profile`, {
      method: 'PUT',
      body: JSON.stringify({ username, email }),
    }),

  verifyTenant: (account_id, tenant_id) =>
    apiRequest(`${AUTH_SERVICE_URL}/api/v1/auth/verify-tenant`, {
      method: 'POST',
      body: JSON.stringify({ account_id, tenant_id }),
    }),

  logout: () =>
    apiRequest(`${AUTH_SERVICE_URL}/api/v1/auth/logout`, { method: 'POST' }).catch(() => {}),
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
      body: JSON.stringify({ pat_token: token, token }),
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
  checkReadiness: (payload) =>
    apiRequest('/api/v1/repo/readiness', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  scanReport: (payload) =>
    apiRequest('/api/v1/repo/scan-report', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  acceptAndSize: (payload) =>
    apiRequest('/api/v1/repo/accept-and-size', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
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
  recalculateSizing: (payload) =>
    apiRequest('/api/v1/repo/recalculate-sizing', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
};

export const architectureStudioApi = {
  getHealth: () =>
    apiRequest('/api/v1/architecture/health'),
  generateGraph: (payload) =>
    apiRequest('/api/v1/architecture/generate-graph', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  saveSession: (payload) =>
    apiRequest('/api/v1/architecture/studio/save', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  getState: (projectId, envId) =>
    apiRequest(`/api/v1/architecture/studio/state?project_id=${projectId || ''}&environment_id=${envId || ''}`),
  validate: (payload) =>
    apiRequest('/api/v1/architecture/validate', {
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

