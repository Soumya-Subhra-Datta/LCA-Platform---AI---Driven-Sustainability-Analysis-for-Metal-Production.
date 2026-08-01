import { apiRequest } from './apiClient.js';

const TOKEN_KEY = 'lca_access_token';
const USER_KEY = 'lca_user';

function deriveUsername(email) {
  const local = String(email || '').split('@')[0].replace(/[^a-zA-Z0-9_.-]/g, '');
  const base = local || 'user';
  if (base.length >= 3) return base;
  return `${base}${Date.now().toString().slice(-4)}`.slice(0, 50);
}

const authService = {
  async login({ email, password }) {
    const data = await apiRequest('/api/v1/auth/login', {
      method: 'POST',
      body: { username: email, password },
    });
    if (data && data.access_token) {
      localStorage.setItem(TOKEN_KEY, data.access_token);
      localStorage.setItem(USER_KEY, JSON.stringify(data.user || {}));
    }
    return data;
  },

  async signup({ name, email, password }) {
    const payload = {
      username: deriveUsername(email),
      email,
      password,
      full_name: name,
    };
    const data = await apiRequest('/api/v1/auth/register', {
      method: 'POST',
      body: payload,
    });
    return data;
  },

  logout() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  },

  getToken() {
    return localStorage.getItem(TOKEN_KEY);
  },

  getUser() {
    try {
      const raw = localStorage.getItem(USER_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (err) {
      return null;
    }
  },

  isAuthenticated() {
    return Boolean(this.getToken());
  },
};

export default authService;
