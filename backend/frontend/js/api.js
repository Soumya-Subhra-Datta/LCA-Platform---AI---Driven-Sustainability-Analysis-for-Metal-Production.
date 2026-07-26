const API_BASE = '/api/v1';

const api = {
    async request(method, path, body = null) {
        const opts = {
            method,
            headers: { 'Content-Type': 'application/json' },
        };
        const token = localStorage.getItem('token');
        if (token) opts.headers['Authorization'] = `Bearer ${token}`;
        if (body) opts.body = JSON.stringify(body);
        try {
            const res = await fetch(`${API_BASE}${path}`, opts);
            if (res.status === 401 && path !== '/auth/login' && path !== '/auth/register') {
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                window.location.hash = '#login';
                throw new Error('Session expired');
            }
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
            return data;
        } catch (err) {
            console.error(`API Error [${method} ${path}]:`, err);
            throw err;
        }
    },
    get(path) { return this.request('GET', path); },
    post(path, body) { return this.request('POST', path, body); },
    put(path, body) { return this.request('PUT', path, body); },
    delete(path) { return this.request('DELETE', path); },

    auth: {
        login(username, password) { return api.post('/auth/login', { username, password }); },
        register(data) { return api.post('/auth/register', data); },
        me() { return api.get('/auth/me'); },
    },
    dashboard: {
        get() { return api.get('/dashboard/'); },
        activity(limit = 20) { return api.get(`/dashboard/activity?limit=${limit}`); },
        dataCounts() { return api.get('/dashboard/data-counts'); },
        clearAll() { return api.post('/dashboard/clear-all'); },
        clearPredictions() { return api.post('/dashboard/clear/predictions'); },
        clearLCA() { return api.post('/dashboard/clear/lca'); },
        clearCircularity() { return api.post('/dashboard/clear/circularity'); },
        clearModels() { return api.post('/dashboard/clear/models'); },
    },
    datasets: {
        list() { return api.get('/datasets/'); },
        get(name) { return api.get(`/datasets/${name}`); },
        sample(name, rows = 10) { return api.get(`/datasets/${name}/sample?rows=${rows}`); },
        stats(name) { return api.get(`/datasets/${name}/stats`); },
    },
    predictions: {
        models() { return api.get('/predictions/models'); },
        train() { return api.post('/predictions/train'); },
        predict(model, data) { return api.post('/predictions/predict', { model_name: model, input_data: data }); },
        metrics() { return api.get('/predictions/metrics'); },
        history(limit = 50) { return api.get(`/predictions/history?limit=${limit}`); },
    },
    environmental: {
        assess(data) { return api.post('/environmental/assess', data); },
        benchmarks() { return api.get('/environmental/benchmarks'); },
        history(limit = 50) { return api.get(`/environmental/history?limit=${limit}`); },
    },
    circularity: {
        calculate(data) { return api.post('/circularity/calculate', data); },
        sustainability(data) { return api.post('/circularity/sustainability', data); },
        history() { return api.get('/circularity/history'); },
        sustainabilityHistory() { return api.get('/circularity/sustainability/history'); },
    },
    reports: {
        list() { return api.get('/reports/'); },
        get(id) { return api.get(`/reports/${id}`); },
        generate(type, title) { return api.post(`/reports/generate?report_type=${type}&title=${encodeURIComponent(title)}`); },
    },
};

function isLoggedIn() {
    return !!localStorage.getItem('token');
}

function getCurrentUser() {
    try {
        return JSON.parse(localStorage.getItem('user'));
    } catch { return null; }
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.hash = '#login';
}
