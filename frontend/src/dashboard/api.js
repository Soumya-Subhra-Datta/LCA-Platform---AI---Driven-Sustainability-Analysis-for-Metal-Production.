import { apiRequest, ApiError } from '../auth/apiClient.js';
import authService from '../auth/authService.js';

function raiseUnauthorized(err) {
  if (err instanceof ApiError && err.status === 401) {
    window.dispatchEvent(new CustomEvent('lca:unauthorized'));
    err.message = 'Session expired. Please sign in again.';
  }
  throw err;
}

async function get(path) {
  try {
    return await apiRequest(path, { token: authService.getToken() });
  } catch (err) {
    raiseUnauthorized(err);
  }
}

async function post(path, body = null) {
  try {
    return await apiRequest(path, { method: 'POST', body, token: authService.getToken() });
  } catch (err) {
    raiseUnauthorized(err);
  }
}

async function del(path) {
  try {
    return await apiRequest(path, { method: 'DELETE', token: authService.getToken() });
  } catch (err) {
    raiseUnauthorized(err);
  }
}

function isUnauthorized(err) {
  return err instanceof ApiError && err.status === 401;
}

export const api = {
  get,
  post,
  delete: del,
  isUnauthorized,
  health: () => get('/health'),

  dashboard: {
    get: () => get('/api/v1/dashboard/'),
    activity: (limit = 20) => get(`/api/v1/dashboard/activity?limit=${limit}`),
    dataCounts: () => get('/api/v1/dashboard/data-counts'),
    clearAll: () => post('/api/v1/dashboard/clear-all'),
    clearPredictions: () => post('/api/v1/dashboard/clear/predictions'),
    clearLCA: () => post('/api/v1/dashboard/clear/lca'),
    clearCircularity: () => post('/api/v1/dashboard/clear/circularity'),
    clearModels: () => post('/api/v1/dashboard/clear/models'),
  },
  datasets: {
    list: () => get('/api/v1/datasets/'),
    get: (name) => get(`/api/v1/datasets/${encodeURIComponent(name)}`),
    sample: (name, rows = 10) => get(`/api/v1/datasets/${encodeURIComponent(name)}/sample?rows=${rows}`),
    stats: (name) => get(`/api/v1/datasets/${encodeURIComponent(name)}/stats`),
  },
  predictions: {
    models: () => get('/api/v1/predictions/models'),
    train: () => post('/api/v1/predictions/train'),
    trainStatus: () => get('/api/v1/predictions/train-status'),
    predict: (model, data) => post('/api/v1/predictions/predict', { model_name: model, input_data: data }),
    metrics: () => get('/api/v1/predictions/metrics'),
    history: (limit = 50) => get(`/api/v1/predictions/history?limit=${limit}`),
  },
  environmental: {
    assess: (data) => post('/api/v1/environmental/assess', data),
    benchmarks: () => get('/api/v1/environmental/benchmarks'),
    history: (limit = 50) => get(`/api/v1/environmental/history?limit=${limit}`),
    oreTypes: () => get('/api/v1/environmental/ore-types'),
  },
  circularity: {
    calculate: (data) => post('/api/v1/circularity/calculate', data),
    sustainability: (data) => post('/api/v1/circularity/sustainability', data),
    oreTypes: () => get('/api/v1/circularity/ore-types'),
    history: () => get('/api/v1/circularity/history'),
    sustainabilityHistory: () => get('/api/v1/circularity/sustainability/history'),
  },
  reports: {
    list: () => get('/api/v1/reports/'),
    get: (id) => get(`/api/v1/reports/${id}`),
    generate: (type, title) => post(`/api/v1/reports/generate?report_type=${type}&title=${encodeURIComponent(title)}`),
  },
};
