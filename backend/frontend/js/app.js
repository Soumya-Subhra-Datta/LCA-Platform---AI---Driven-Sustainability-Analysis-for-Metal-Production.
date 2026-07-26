let currentPage = 'dashboard';

function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('open');
}

function showToast(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}

function showModal(title, bodyHtml) {
    document.getElementById('modal-title').textContent = title;
    document.getElementById('modal-body').innerHTML = bodyHtml;
    document.getElementById('modal-overlay').style.display = 'flex';
}

function closeModal() {
    document.getElementById('modal-overlay').style.display = 'none';
}

function formatNumber(n) {
    if (n === null || n === undefined) return 'N/A';
    if (Math.abs(n) >= 1e6) return (n / 1e6).toFixed(2) + 'M';
    if (Math.abs(n) >= 1e3) return (n / 1e3).toFixed(1) + 'K';
    return typeof n === 'number' ? n.toFixed(2) : String(n);
}

function loadingHtml() {
    return '<div style="text-align:center;padding:40px;"><div class="spinner"></div><p style="margin-top:12px;color:var(--text-secondary);">Loading...</p></div>';
}

function errorHtml(msg) {
    return `<div class="card" style="text-align:center;padding:40px;"><p style="color:var(--danger);font-size:16px;">${msg}</p></div>`;
}

function updateNavUser() {
    const user = getCurrentUser();
    const el = document.getElementById('user-display');
    if (el) el.textContent = user ? user.username : 'Guest';
}

const pages = {};

// ===== LOGIN PAGE =====
pages.login = function() {
    const el = document.getElementById('content-area');
    document.getElementById('sidebar').style.display = 'none';
    document.querySelector('.top-bar').style.display = 'none';
    el.innerHTML = `
        <div class="auth-page">
            <div class="auth-card">
                <div class="auth-header">
                    <h2 class="logo">LCA Platform - AI-Driven Sustainability Analysis</h2>
                    <p>Sign in to your account</p>
                </div>
                <form id="login-form" onsubmit="return handleLogin(event)">
                    <div class="form-group">
                        <label>Username or Email</label>
                        <input type="text" id="login-username" required placeholder="Enter username or email" autocomplete="username">
                    </div>
                    <div class="form-group">
                        <label>Password</label>
                        <input type="password" id="login-password" required placeholder="Enter password" autocomplete="current-password">
                    </div>
                    <div id="login-error" style="color:var(--danger);margin-bottom:12px;font-size:14px;display:none;"></div>
                    <button type="submit" class="btn btn-primary btn-full" id="login-btn">Sign In</button>
                </form>
                <div class="auth-footer">
                    <p>Don't have an account? <a href="#register">Create one</a></p>
                </div>
            </div>
        </div>`;
};

window.handleLogin = async function(e) {
    e.preventDefault();
    const btn = document.getElementById('login-btn');
    const errEl = document.getElementById('login-error');
    btn.disabled = true;
    btn.textContent = 'Signing in...';
    errEl.style.display = 'none';
    try {
        const res = await api.auth.login(
            document.getElementById('login-username').value,
            document.getElementById('login-password').value
        );
        localStorage.setItem('token', res.access_token);
        localStorage.setItem('user', JSON.stringify(res.user));
        showToast('Signed in successfully', 'success');
        updateNavUser();
        document.getElementById('sidebar').style.display = '';
        document.querySelector('.top-bar').style.display = '';
        window.location.hash = '#dashboard';
    } catch (err) {
        errEl.textContent = err.message;
        errEl.style.display = 'block';
    }
    btn.disabled = false;
    btn.textContent = 'Sign In';
};

// ===== REGISTER PAGE =====
pages.register = function() {
    const el = document.getElementById('content-area');
    document.getElementById('sidebar').style.display = 'none';
    document.querySelector('.top-bar').style.display = 'none';
    el.innerHTML = `
        <div class="auth-page">
            <div class="auth-card">
                <div class="auth-header">
                    <h2 class="logo">LCA Platform - AI-Driven Sustainability Analysis</h2>
                    <p>Create a new account</p>
                </div>
                <form id="register-form" onsubmit="return handleRegister(event)">
                    <div class="form-group">
                        <label>Full Name</label>
                        <input type="text" id="reg-fullname" placeholder="John Doe">
                    </div>
                    <div class="form-group">
                        <label>Username</label>
                        <input type="text" id="reg-username" required minlength="3" maxlength="50" placeholder="Choose a username" autocomplete="username">
                    </div>
                    <div class="form-group">
                        <label>Email</label>
                        <input type="email" id="reg-email" required placeholder="you@example.com" autocomplete="email">
                    </div>
                    <div class="form-group">
                        <label>Password</label>
                        <input type="password" id="reg-password" required minlength="8" placeholder="Min 8 characters" autocomplete="new-password">
                    </div>
                    <div class="form-group">
                        <label>Confirm Password</label>
                        <input type="password" id="reg-password2" required placeholder="Repeat password" autocomplete="new-password">
                    </div>
                    <div id="register-error" style="color:var(--danger);margin-bottom:12px;font-size:14px;display:none;"></div>
                    <button type="submit" class="btn btn-primary btn-full" id="register-btn">Create Account</button>
                </form>
                <div class="auth-footer">
                    <p>Already have an account? <a href="#login">Sign in</a></p>
                </div>
            </div>
        </div>`;
};

window.handleRegister = async function(e) {
    e.preventDefault();
    const btn = document.getElementById('register-btn');
    const errEl = document.getElementById('register-error');
    btn.disabled = true;
    btn.textContent = 'Creating account...';
    errEl.style.display = 'none';

    const pw = document.getElementById('reg-password').value;
    const pw2 = document.getElementById('reg-password2').value;
    if (pw !== pw2) {
        errEl.textContent = 'Passwords do not match';
        errEl.style.display = 'block';
        btn.disabled = false;
        btn.textContent = 'Create Account';
        return false;
    }

    try {
        await api.auth.register({
            username: document.getElementById('reg-username').value,
            email: document.getElementById('reg-email').value,
            password: pw,
            full_name: document.getElementById('reg-fullname').value,
        });
        showToast('Account created! Please sign in.', 'success');
        window.location.hash = '#login';
    } catch (err) {
        errEl.textContent = err.message;
        errEl.style.display = 'block';
    }
    btn.disabled = false;
    btn.textContent = 'Create Account';
    return false;
};

// ===== PROTECTED PAGES =====
function requireAuth() {
    if (!isLoggedIn()) {
        window.location.hash = '#login';
        return false;
    }
    document.getElementById('sidebar').style.display = '';
    document.querySelector('.top-bar').style.display = '';
    updateNavUser();
    return true;
}

pages.dashboard = async function() {
    if (!requireAuth()) return;
    const el = document.getElementById('content-area');
    el.innerHTML = loadingHtml();
    try {
        const data = await api.dashboard.get();
        const s = data.summary;
        el.innerHTML = `
            <div class="stats-grid">
                <div class="stat-card"><div class="stat-icon blue">D</div><div class="stat-info"><h4>${s.total_datasets}</h4><p>Datasets</p></div></div>
                <div class="stat-card"><div class="stat-icon green">R</div><div class="stat-info"><h4>${formatNumber(s.total_rows)}</h4><p>Total Rows</p></div></div>
                <div class="stat-card"><div class="stat-icon orange">P</div><div class="stat-info"><h4>${s.prediction_count}</h4><p>Predictions</p></div></div>
                <div class="stat-card"><div class="stat-icon red">L</div><div class="stat-info"><h4>${s.lca_assessment_count}</h4><p>LCA Assessments</p></div></div>
            </div>
            <div class="chart-grid">
                <div class="card">
                    <div class="card-header"><h3>REE Mining Projects by Continent</h3></div>
                    <div class="chart-container"><canvas id="chart-continent"></canvas></div>
                </div>
                <div class="card">
                    <div class="card-header"><h3>Deposit Type Distribution</h3></div>
                    <div class="chart-container"><canvas id="chart-deposits"></canvas></div>
                </div>
            </div>
            <div class="card">
                <div class="card-header"><h3>Model Performance</h3></div>
                <div class="chart-container"><canvas id="chart-models"></canvas></div>
            </div>
            <div class="card">
                <div class="card-header"><h3>Recent Activity</h3></div>
                <table class="data-table">
                    <thead><tr><th>Type</th><th>Details</th><th>Time</th></tr></thead>
                    <tbody id="activity-table"></tbody>
                </table>
            </div>`;
        const cd = data.mining_overview.continent_distribution;
        if (Object.keys(cd).length > 0) {
            createDoughnutChart('chart-continent', Object.keys(cd), Object.values(cd));
        }
        const dd = data.mining_overview.deposit_distribution;
        if (Object.keys(dd).length > 0) {
            createBarChart('chart-deposits', Object.keys(dd), [{ label: 'Projects', data: Object.values(dd), backgroundColor: '#1a73e8' }]);
        }
        const mm = data.model_metrics;
        if (Object.keys(mm).length > 0) {
            const modelNames = Object.keys(mm);
            const r2Scores = modelNames.map(n => mm[n].r2 || mm[n].accuracy || 0);
            createBarChart('chart-models', modelNames.map(n => n.replace('_', ' ')), [{ label: 'R2 / Accuracy', data: r2Scores, backgroundColor: '#34a853' }]);
        }
        const actTable = document.getElementById('activity-table');
        if (data.recent_activity.predictions.length > 0) {
            data.recent_activity.predictions.forEach(p => {
                actTable.innerHTML += `<tr><td><span class="tag tag-info">Prediction</span></td><td>${p.model}</td><td>${p.time || 'N/A'}</td></tr>`;
            });
        }
        if (data.recent_activity.lca_assessments.length > 0) {
            data.recent_activity.lca_assessments.forEach(m => {
                actTable.innerHTML += `<tr><td><span class="tag tag-success">LCA</span></td><td>${m.facility} - ${formatNumber(m.carbon)} kg CO2</td><td>${m.time || 'N/A'}</td></tr>`;
            });
        }
    } catch (err) {
        el.innerHTML = errorHtml('Failed to load dashboard: ' + err.message);
    }
};

pages.datasets = async function() {
    if (!requireAuth()) return;
    const el = document.getElementById('content-area');
    el.innerHTML = loadingHtml();
    try {
        const data = await api.datasets.list();
        let rows = '';
        data.datasets.forEach(d => {
            rows += `<tr style="cursor:pointer" onclick="showDatasetDetail('${d.name}')">
                <td><strong>${d.name}</strong></td><td>${d.rows}</td><td>${d.columns}</td>
                <td>${(d.memory_mb || 0).toFixed(1)} MB</td>
                <td><span class="tag ${d.status === 'loaded' ? 'tag-success' : 'tag-danger'}">${d.status}</span></td></tr>`;
        });
        el.innerHTML = `
            <div class="card">
                <div class="card-header"><h3>All Datasets (${data.datasets.length})</h3>
                    <button class="btn btn-primary" onclick="reloadDatasets()">Reload</button></div>
                <table class="data-table">
                    <thead><tr><th>Name</th><th>Rows</th><th>Columns</th><th>Size</th><th>Status</th></tr></thead>
                    <tbody>${rows}</tbody>
                </table>
            </div>`;
    } catch (err) {
        el.innerHTML = errorHtml('Failed to load datasets: ' + err.message);
    }
};

window.showDatasetDetail = async function(name) {
    try {
        const [info, sample] = await Promise.all([api.datasets.get(name), api.datasets.sample(name, 5)]);
        const cols = info.column_names || [];
        let tableHtml = '<table class="data-table"><thead><tr>';
        cols.slice(0, 10).forEach(c => tableHtml += `<th>${c}</th>`);
        if (cols.length > 10) tableHtml += '<th>...</th>';
        tableHtml += '</tr></thead><tbody>';
        (sample.sample || []).forEach(row => {
            tableHtml += '<tr>';
            cols.slice(0, 10).forEach(c => tableHtml += `<td>${row[c] !== null && row[c] !== undefined ? String(row[c]).substring(0, 30) : ''}</td>`);
            if (cols.length > 10) tableHtml += '<td>...</td>';
            tableHtml += '</tr>';
        });
        tableHtml += '</tbody></table>';
        showModal(`Dataset: ${name}`, `
            <p><strong>Rows:</strong> ${info.rows} | <strong>Columns:</strong> ${info.columns} | <strong>Memory:</strong> ${(info.memory_mb||0).toFixed(1)} MB</p>
            <h4 style="margin:16px 0 8px;">Sample Data</h4>${tableHtml}`);
    } catch (err) { showToast('Failed to load dataset details: ' + err.message, 'error'); }
};

window.reloadDatasets = async function() {
    try { await api.post('/datasets/reload'); showToast('Datasets reloaded', 'success'); pages.datasets(); }
    catch (err) { showToast('Reload failed: ' + err.message, 'error'); }
};

pages.predictions = async function() {
    if (!requireAuth()) return;
    const el = document.getElementById('content-area');
    el.innerHTML = `
        <div class="stats-grid">
            <div class="stat-card"><div class="stat-icon blue">M</div><div class="stat-info"><h4>4</h4><p>Available Models</p></div></div>
        </div>
        <div class="grid-2">
            <div class="card">
                <div class="card-header"><h3>Train Models</h3></div>
                <p style="margin-bottom:16px;color:var(--text-secondary)">Train all ML models on the mining projects dataset.</p>
                <button class="btn btn-primary" id="btn-train" onclick="trainModels()">Train All Models</button>
                <div id="train-result" style="margin-top:12px;"></div>
            </div>
            <div class="card">
                <div class="card-header"><h3>Model Metrics</h3></div>
                <div id="model-metrics-display"></div>
            </div>
        </div>
        <div class="card">
            <div class="card-header"><h3>Run Prediction</h3></div>
            <div class="form-row">
                <div class="form-group">
                    <label>Model</label>
                    <select id="pred-model">
                        <option value="hree_predictor">HREE Percentage Predictor</option>
                        <option value="deposit_classifier">Deposit Type Classifier</option>
                        <option value="resource_estimator">Resource Size Estimator</option>
                        <option value="dy_predictor">Dy2O3 Content Predictor</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Log Resource</label>
                    <input type="number" id="pred-log-resource" value="6" step="0.1">
                </div>
            </div>
            <div class="form-row-3">
                <div class="form-group"><label>Grade %</label><input type="number" id="pred-grade" value="3.0" step="0.1"></div>
                <div class="form-group"><label>Continent</label>
                    <select id="pred-continent"><option value="0">Asia</option><option value="1">Australia</option><option value="2">Europe</option><option value="3">North America</option><option value="4">South America</option><option value="5">Africa</option></select></div>
                <div class="form-group"><label>Deposit Type</label>
                    <select id="pred-deposit"><option value="0">Alkaline rock</option><option value="1">Carbonatite</option><option value="2">Hydrothermal/IOCG</option><option value="3">Ionic Clay</option><option value="4">Placer</option><option value="5">Other</option></select></div>
            </div>
            <button class="btn btn-success" onclick="runPrediction()">Run Prediction</button>
            <div id="prediction-result" style="margin-top:16px;"></div>
        </div>
        <div class="card">
            <div class="card-header"><h3>Prediction History</h3></div>
            <div id="prediction-history"></div>
        </div>`;
    loadModelMetrics();
    loadPredictionHistory();
};

window.trainModels = async function() {
    const btn = document.getElementById('btn-train');
    btn.disabled = true; btn.textContent = 'Training...';
    document.getElementById('train-result').innerHTML = '<div class="spinner"></div>';
    try {
        const res = await api.predictions.train();
        let html = '<div class="result-box"><h4>Training Results</h4><div class="result-grid">';
        for (const [name, metrics] of Object.entries(res.results)) {
            const score = metrics.r2 || metrics.accuracy || 0;
            html += `<div class="result-item"><div class="label">${name}</div><div class="value">${(score * 100).toFixed(1)}%</div></div>`;
        }
        html += '</div></div>';
        document.getElementById('train-result').innerHTML = html;
        showToast('Models trained successfully', 'success');
        loadModelMetrics();
    } catch (err) {
        document.getElementById('train-result').innerHTML = `<p style="color:var(--danger)">Training failed: ${err.message}</p>`;
        showToast('Training failed', 'error');
    }
    btn.disabled = false; btn.textContent = 'Train All Models';
};

async function loadModelMetrics() {
    try {
        const data = await api.predictions.metrics();
        let html = '<table class="data-table"><thead><tr><th>Model</th><th>Score</th><th>Cross-Val</th></tr></thead><tbody>';
        for (const [name, m] of Object.entries(data)) {
            const score = m.r2 || m.accuracy || 0;
            const cv = m.cv_r2_mean || 0;
            html += `<tr><td>${name}</td><td>${(score * 100).toFixed(1)}%</td><td>${(cv * 100).toFixed(1)}%</td></tr>`;
        }
        html += '</tbody></table>';
        document.getElementById('model-metrics-display').innerHTML = html;
    } catch (err) {
        document.getElementById('model-metrics-display').innerHTML = '<p style="color:var(--text-secondary)">No trained models found. Train models first.</p>';
    }
}

window.runPrediction = async function() {
    const model = document.getElementById('pred-model').value;
    const input = {
        log_resource: parseFloat(document.getElementById('pred-log-resource').value),
        grade_pct: parseFloat(document.getElementById('pred-grade').value),
        continent_encoded: parseInt(document.getElementById('pred-continent').value),
        deposit_type_encoded: parseInt(document.getElementById('pred-deposit').value),
    };
    const resultEl = document.getElementById('prediction-result');
    resultEl.innerHTML = '<div class="spinner"></div>';
    try {
        const res = await api.predictions.predict(model, input);
        let html = '<div class="result-box"><h4>Prediction Result</h4><div class="result-grid">';
        for (const [k, v] of Object.entries(res.result)) {
            if (typeof v === 'object') continue;
            html += `<div class="result-item"><div class="label">${k}</div><div class="value">${typeof v === 'number' ? v.toFixed(4) : v}</div></div>`;
        }
        html += '</div>';
        if (res.explanation && res.explanation.natural_language) {
            html += `<div style="margin-top:12px;padding:12px;background:#e8f0fe;border-radius:var(--radius);font-size:14px;"><strong>Explanation:</strong> ${res.explanation.natural_language}</div>`;
        }
        html += `<p style="margin-top:8px;font-size:12px;color:var(--text-secondary)">Execution time: ${res.execution_time_ms}ms</p></div>`;
        resultEl.innerHTML = html;
        showToast('Prediction completed', 'success');
        loadPredictionHistory();
    } catch (err) {
        resultEl.innerHTML = `<p style="color:var(--danger)">Prediction failed: ${err.message}</p>`;
    }
};

async function loadPredictionHistory() {
    try {
        const data = await api.predictions.history(10);
        let html = '<table class="data-table"><thead><tr><th>Model</th><th>Result</th><th>Time</th></tr></thead><tbody>';
        (data.predictions || []).forEach(p => {
            const resultStr = JSON.stringify(p.result).substring(0, 80);
            html += `<tr><td>${p.model}</td><td>${resultStr}...</td><td>${p.time || 'N/A'}</td></tr>`;
        });
        html += '</tbody></table>';
        document.getElementById('prediction-history').innerHTML = html || '<p style="color:var(--text-secondary)">No predictions yet.</p>';
    } catch (err) { document.getElementById('prediction-history').innerHTML = '<p style="color:var(--text-secondary)">Could not load history.</p>'; }
}

pages.lca = async function() {
    if (!requireAuth()) return;
    const el = document.getElementById('content-area');
    let oreOptions = '';
    try {
        const oreData = await api.get('/environmental/ore-types');
        oreOptions = (oreData.ore_types || []).map(o =>
            `<option value="${o.key}" ${o.key === 'REE' ? 'selected' : ''}>${o.name} - ${o.description.substring(0, 50)}...</option>`
        ).join('');
    } catch(e) {
        oreOptions = '<option value="REE">Rare Earth Elements</option>';
    }
    el.innerHTML = `
        <div class="card">
            <div class="card-header"><h3>Life Cycle Assessment</h3></div>
            <div class="form-row-3">
                <div class="form-group"><label>Facility Name</label><input type="text" id="lca-facility" value="REE Processing Plant"></div>
                <div class="form-group"><label>Ore / Metal Type</label>
                    <select id="lca-ore-type">${oreOptions}</select></div>
                <div class="form-group"><label>Mining Type</label>
                    <select id="lca-mining"><option value="Surface">Surface</option><option value="Underground">Underground</option></select></div>
            </div>
            <div class="form-row-3">
                <div class="form-group"><label>Resource (tonnes)</label><input type="number" id="lca-resource" value="100000" step="1000"></div>
                <div class="form-group"><label>Grade (%)</label><input type="number" id="lca-grade" value="5.0" step="0.1"></div>
                <div class="form-group"><label>Transport Distance (km)</label><input type="number" id="lca-transport" value="200" step="10"></div>
            </div>
            <div class="form-row">
                <div class="form-group"><label>Processing</label>
                    <select id="lca-processing"><option value="crushing,grinding,leaching,solvent_extraction">Full REE Processing</option>
                    <option value="crushing,grinding">Crushing + Grinding Only</option>
                    <option value="leaching,solvent_extraction">Hydromet Only</option>
                    <option value="crushing,grinding,flotation,smelting">Flotation + Smelting</option>
                    <option value="crushing,grinding,flotation,smelting,electrorefining">Full Pyromet + Electro</option></select></div>
            </div>
            <button class="btn btn-success" onclick="runLCA()">Run Assessment</button>
            <div id="lca-result" style="margin-top:16px;"></div>
        </div>
        <div class="card">
            <div class="card-header"><h3>Industry Benchmarks</h3></div>
            <div id="benchmark-display"></div>
        </div>`;
    loadBenchmarks();
};

window.runLCA = async function() {
    const el = document.getElementById('lca-result');
    el.innerHTML = '<div class="spinner"></div>';
    try {
        const res = await api.environmental.assess({
            facility_name: document.getElementById('lca-facility').value,
            resource_tonnes: parseFloat(document.getElementById('lca-resource').value),
            grade_pct: parseFloat(document.getElementById('lca-grade').value),
            mining_type: document.getElementById('lca-mining').value,
            ore_type: document.getElementById('lca-ore-type').value,
            transport_distance_km: parseFloat(document.getElementById('lca-transport').value),
            processing_method: document.getElementById('lca-processing').value,
        });
        const s = res.summary;
        el.innerHTML = `
            <div class="result-box">
                <h4>LCA Results - <span style="color:var(--text-primary)">${s.ore_type || 'REE'}</span> - Impact Grade: <span class="tag ${s.impact_grade <= 'B' ? 'tag-success' : s.impact_grade <= 'C' ? 'tag-warning' : 'tag-danger'}">${s.impact_grade}</span></h4>
                <div class="result-grid" style="margin-top:12px;">
                    <div class="result-item"><div class="label">Total CO2</div><div class="value">${formatNumber(s.total_co2_tonnes)} t</div></div>
                    <div class="result-item"><div class="label">Total Water</div><div class="value">${formatNumber(s.total_water_m3)} m3</div></div>
                    <div class="result-item"><div class="label">Total Energy</div><div class="value">${formatNumber(s.total_energy_mwh)} MWh</div></div>
                    <div class="result-item"><div class="label">Total Waste</div><div class="value">${formatNumber(s.total_waste_tonnes)} t</div></div>
                </div>
                <div class="chart-grid" style="margin-top:16px;">
                    <div><div class="chart-container"><canvas id="chart-lca-breakdown"></canvas></div></div>
                    <div><div class="chart-container"><canvas id="chart-lca-radar"></canvas></div></div>
                </div>
            </div>`;
        const cf = res.carbon_footprint;
        createDoughnutChart('chart-lca-breakdown',
            ['Mining', 'Processing', 'Transport'],
            [cf.mining_kg_co2 / 1000, cf.processing_kg_co2 / 1000, cf.transport_kg_co2 / 1000]);
        createRadarChart('chart-lca-radar',
            ['Carbon', 'Water', 'Energy', 'Waste', 'Acidification'],
            [{ label: 'Impact', data: [
                Math.min(res.carbon_footprint.intensity_kg_co2_per_t_ore * 5, 100),
                Math.min(res.water_footprint.intensity_m3_per_t_ore * 20, 100),
                Math.min(res.energy_consumption.intensity_mj_per_t_ore * 2, 100),
                Math.min(res.waste_generation.waste_to_ore_ratio * 10, 100),
                Math.min(res.acidification.total_kg_so2_eq * 10, 100),
            ], backgroundColor: 'rgba(26,115,232,0.2)', borderColor: '#1a73e8' }]);
        showToast('LCA assessment completed', 'success');
    } catch (err) { el.innerHTML = `<p style="color:var(--danger)">Assessment failed: ${err.message}</p>`; }
};

async function loadBenchmarks() {
    try {
        const data = await api.environmental.benchmarks();
        let html = '<div class="result-grid">';
        for (const [category, benchmarks] of Object.entries(data)) {
            html += `<div class="result-item"><div class="label" style="text-transform:capitalize;">${category}</div>`;
            for (const [k, v] of Object.entries(benchmarks)) {
                html += `<div style="font-size:13px;margin-top:4px;"><strong>${k}:</strong> ${typeof v === 'number' ? v.toFixed(4) : v}</div>`;
            }
            html += '</div>';
        }
        html += '</div>';
        document.getElementById('benchmark-display').innerHTML = html;
    } catch (err) { document.getElementById('benchmark-display').innerHTML = '<p>Could not load benchmarks.</p>'; }
}

pages.circularity = async function() {
    if (!requireAuth()) return;
    const el = document.getElementById('content-area');
    let oreOptions = '';
    try {
        const oreData = await api.get('/circularity/ore-types');
        oreOptions = (oreData.ore_types || []).map(o =>
            `<option value="${o.key}" ${o.key === 'REE' ? 'selected' : ''}>${o.name}</option>`
        ).join('');
    } catch(e) {
        oreOptions = '<option value="REE">Rare Earth Elements</option>';
    }
    el.innerHTML = `
        <div class="card">
            <div class="card-header"><h3>Circularity Assessment</h3></div>
            <div class="form-row-3">
                <div class="form-group"><label>Facility Name</label><input type="text" id="circ-facility" value="REE Mine"></div>
                <div class="form-group"><label>Ore / Metal Type</label>
                    <select id="circ-ore-type">${oreOptions}</select></div>
                <div class="form-group"><label>Ore Processed (t)</label><input type="number" id="circ-ore" value="100000"></div>
            </div>
            <div class="form-row-3">
                <div class="form-group"><label>Waste Generated (t)</label><input type="number" id="circ-waste" value="50000"></div>
                <div class="form-group"><label>Water Used (m3)</label><input type="number" id="circ-water" value="100000"></div>
                <div class="form-group"><label>Energy (MJ)</label><input type="number" id="circ-energy" value="500000"></div>
            </div>
            <div class="form-row-3">
                <div class="form-group"><label>Recycled Material (t)</label><input type="number" id="circ-recycled" value="500"></div>
                <div class="form-group"><label>Product Output (t)</label><input type="number" id="circ-product" value="5000"></div>
            </div>
            <button class="btn btn-success" onclick="runCircularity()">Calculate Circularity</button>
            <div id="circularity-result" style="margin-top:16px;"></div>
        </div>`;
};

window.runCircularity = async function() {
    const el = document.getElementById('circularity-result');
    el.innerHTML = '<div class="spinner"></div>';
    try {
        const res = await api.circularity.calculate({
            facility_name: document.getElementById('circ-facility').value,
            ore_type: document.getElementById('circ-ore-type').value,
            ore_processed_tonnes: parseFloat(document.getElementById('circ-ore').value),
            waste_generated_tonnes: parseFloat(document.getElementById('circ-waste').value),
            water_used_m3: parseFloat(document.getElementById('circ-water').value),
            energy_consumed_mj: parseFloat(document.getElementById('circ-energy').value),
            recycled_material_tonnes: parseFloat(document.getElementById('circ-recycled').value),
            product_output_tonnes: parseFloat(document.getElementById('circ-product').value),
        });
        const scoreColor = res.circularity_score > 50 ? 'var(--accent)' : res.circularity_score > 25 ? 'var(--warning)' : 'var(--danger)';
        el.innerHTML = `
            <div class="score-display">
                <div class="score-value" style="color:${scoreColor}">${res.circularity_score}</div>
                <div class="score-grade">Circularity Score (${res.ore_name || 'REE'})</div>
                <div class="score-bar"><div class="score-bar-fill" style="width:${res.circularity_score}%;background:${scoreColor}"></div></div>
            </div>
            <div class="result-grid">
                <div class="result-item"><div class="label">Recycling Potential</div><div class="value">${res.recycling_potential}%</div></div>
                <div class="result-item"><div class="label">Resource Efficiency</div><div class="value">${res.resource_efficiency}%</div></div>
                <div class="result-item"><div class="label">Material Recovery</div><div class="value">${res.material_recovery_rate}%</div></div>
                <div class="result-item"><div class="label">Waste Diversion</div><div class="value">${res.waste_diversion_rate}%</div></div>
            </div>
            <div class="card" style="margin-top:16px;"><h4 style="margin-bottom:8px;">Recommendations</h4>
                <ul style="padding-left:20px;">${(res.recommendations || []).map(r => `<li style="margin-bottom:6px;font-size:14px;">${r}</li>`).join('')}</ul>
            </div>`;
        showToast('Circularity calculated', 'success');
    } catch (err) { el.innerHTML = `<p style="color:var(--danger)">Calculation failed: ${err.message}</p>`; }
};

pages.sustainability = async function() {
    if (!requireAuth()) return;
    const el = document.getElementById('content-area');
    let oreOptions = '';
    try {
        const oreData = await api.get('/circularity/ore-types');
        oreOptions = (oreData.ore_types || []).map(o =>
            `<option value="${o.key}" ${o.key === 'REE' ? 'selected' : ''}>${o.name}</option>`
        ).join('');
    } catch(e) {
        oreOptions = '<option value="REE">Rare Earth Elements</option>';
    }
    el.innerHTML = `
        <div class="card">
            <div class="card-header"><h3>Sustainability Score</h3></div>
            <div class="form-row-3">
                <div class="form-group"><label>Facility Name</label><input type="text" id="sus-facility" value="REE Mine"></div>
                <div class="form-group"><label>Ore / Metal Type</label>
                    <select id="sus-ore-type">${oreOptions}</select></div>
                <div class="form-group"><label>Carbon (kg CO2)</label><input type="number" id="sus-carbon" value="500000"></div>
            </div>
            <div class="form-row-3">
                <div class="form-group"><label>Water (m3)</label><input type="number" id="sus-water" value="100000"></div>
                <div class="form-group"><label>Energy (MJ)</label><input type="number" id="sus-energy" value="2000000"></div>
                <div class="form-group"><label>Waste (kg)</label><input type="number" id="sus-waste" value="5000000"></div>
            </div>
            <div class="form-row-3">
                <div class="form-group"><label>Recycling Rate (%)</label><input type="number" id="sus-recycling" value="15" step="1"></div>
                <div class="form-group"><label>Community Investment ($)</label><input type="number" id="sus-community" value="50000"></div>
                <div class="form-group"><label>Employees</label><input type="number" id="sus-employees" value="200"></div>
            </div>
            <div class="form-row">
                <div class="form-group"><label>Revenue ($)</label><input type="number" id="sus-revenue" value="50000000"></div>
            </div>
            <button class="btn btn-success" onclick="runSustainability()">Calculate Score</button>
            <div id="sustainability-result" style="margin-top:16px;"></div>
        </div>`;
};

window.runSustainability = async function() {
    const el = document.getElementById('sustainability-result');
    el.innerHTML = '<div class="spinner"></div>';
    try {
        const res = await api.circularity.sustainability({
            facility_name: document.getElementById('sus-facility').value,
            ore_type: document.getElementById('sus-ore-type').value,
            carbon_footprint_kg_co2: parseFloat(document.getElementById('sus-carbon').value),
            water_footprint_m3: parseFloat(document.getElementById('sus-water').value),
            energy_consumption_mj: parseFloat(document.getElementById('sus-energy').value),
            waste_generation_kg: parseFloat(document.getElementById('sus-waste').value),
            recycling_rate: parseFloat(document.getElementById('sus-recycling').value),
            community_investment_usd: parseFloat(document.getElementById('sus-community').value),
            employees: parseInt(document.getElementById('sus-employees').value),
            revenue_usd: parseFloat(document.getElementById('sus-revenue').value),
        });
        const gradeColors = { 'A+': '#34a853', 'A': '#34a853', 'B+': '#1a73e8', 'B': '#1a73e8', 'C+': '#fbbc04', 'C': '#fbbc04', 'D': '#ea4335', 'F': '#ea4335' };
        const gc = gradeColors[res.grade] || '#666';
        el.innerHTML = `
            <div class="score-display">
                <div class="score-value" style="color:${gc}">${res.overall_score.toFixed(1)}</div>
                <div class="score-grade">Grade: <span style="color:${gc}">${res.grade}</span></div>
                <div class="score-bar"><div class="score-bar-fill" style="width:${res.overall_score}%;background:${gc}"></div></div>
            </div>
            <div class="result-grid">
                <div class="result-item"><div class="label">Environmental</div><div class="value">${res.environmental_score.toFixed(1)}</div></div>
                <div class="result-item"><div class="label">Social</div><div class="value">${res.social_score.toFixed(1)}</div></div>
                <div class="result-item"><div class="label">Governance</div><div class="value">${res.governance_score.toFixed(1)}</div></div>
                <div class="result-item"><div class="label">Economic</div><div class="value">${res.economic_score.toFixed(1)}</div></div>
                <div class="result-item"><div class="label">Innovation</div><div class="value">${res.innovation_score.toFixed(1)}</div></div>
            </div>
            <div class="chart-container" style="height:250px;margin-top:16px;"><canvas id="chart-sus-radar"></canvas></div>
            <div class="card" style="margin-top:16px;"><h4 style="margin-bottom:8px;">Recommendations</h4>
                <ul style="padding-left:20px;">${(res.recommendations || []).map(r => `<li style="margin-bottom:6px;font-size:14px;">${r}</li>`).join('')}</ul>
            </div>`;
        createRadarChart('chart-sus-radar',
            ['Environmental', 'Social', 'Governance', 'Economic', 'Innovation'],
            [{ label: 'Score', data: [res.environmental_score, res.social_score, res.governance_score, res.economic_score, res.innovation_score], backgroundColor: 'rgba(26,115,232,0.2)', borderColor: '#1a73e8' }]);
        showToast('Sustainability score calculated', 'success');
    } catch (err) { el.innerHTML = `<p style="color:var(--danger)">Calculation failed: ${err.message}</p>`; }
};

pages.reports = async function() {
    if (!requireAuth()) return;
    const el = document.getElementById('content-area');
    el.innerHTML = `
        <div class="card">
            <div class="card-header"><h3>Generate Report</h3></div>
            <div class="form-row">
                <div class="form-group"><label>Report Type</label>
                    <select id="report-type">
                        <option value="comprehensive">Comprehensive Report</option>
                        <option value="lca_summary">LCA Summary</option>
                        <option value="sustainability">Sustainability Summary</option>
                        <option value="predictions">Predictions Summary</option>
                    </select></div>
                <div class="form-group"><label>Title</label><input type="text" id="report-title" value="Analysis Report"></div>
            </div>
            <button class="btn btn-primary" onclick="generateReport()">Generate Report</button>
            <div id="report-result" style="margin-top:16px;"></div>
        </div>
        <div class="card">
            <div class="card-header"><h3>Previous Reports</h3></div>
            <div id="reports-list"></div>
        </div>`;
    loadReports();
};

window.generateReport = async function() {
    const el = document.getElementById('report-result');
    el.innerHTML = '<div class="spinner"></div>';
    try {
        const type = document.getElementById('report-type').value;
        const title = document.getElementById('report-title').value;
        const res = await api.reports.generate(type, title);
        el.innerHTML = `<div class="result-box"><h4>Report Generated: ${res.title}</h4>
            <pre style="white-space:pre-wrap;font-size:13px;margin-top:8px;max-height:400px;overflow-y:auto;">${JSON.stringify(res.content, null, 2)}</pre></div>`;
        showToast('Report generated', 'success');
        loadReports();
    } catch (err) { el.innerHTML = `<p style="color:var(--danger)">Generation failed: ${err.message}</p>`; }
};

async function loadReports() {
    try {
        const data = await api.reports.list();
        let html = '<table class="data-table"><thead><tr><th>Title</th><th>Type</th><th>Status</th><th>Date</th></tr></thead><tbody>';
        (data.reports || []).forEach(r => {
            html += `<tr><td>${r.title}</td><td><span class="tag tag-info">${r.type}</span></td><td>${r.status}</td><td>${r.created_at || 'N/A'}</td></tr>`;
        });
        html += '</tbody></table>';
        document.getElementById('reports-list').innerHTML = html || '<p style="color:var(--text-secondary)">No reports generated yet.</p>';
    } catch (err) { document.getElementById('reports-list').innerHTML = '<p>Could not load reports.</p>'; }
}

pages.settings = async function() {
    if (!requireAuth()) return;
    const el = document.getElementById('content-area');
    let dataCounts = { counts: {}, total: 0 };
    try { dataCounts = await api.dashboard.dataCounts(); } catch(e) {}
    const c = dataCounts.counts || {};
    el.innerHTML = `
        <div class="card">
            <div class="card-header"><h3>Account</h3></div>
            <div class="result-grid" style="margin-bottom:16px;">
                <div class="result-item"><div class="label">Username</div><div class="value">${getCurrentUser()?.username || 'N/A'}</div></div>
                <div class="result-item"><div class="label">Email</div><div class="value">${getCurrentUser()?.email || 'N/A'}</div></div>
                <div class="result-item"><div class="label">Role</div><div class="value">${getCurrentUser()?.role || 'N/A'}</div></div>
            </div>
            <button class="btn btn-danger" onclick="logout()">Sign Out</button>
        </div>
        <div class="card">
            <div class="card-header"><h3>Clear Data</h3></div>
            <p style="margin-bottom:12px;color:var(--text-secondary);">Delete all analyzed data. Users and datasets are kept.</p>
            <table class="data-table" style="margin-bottom:16px;">
                <thead><tr><th>Data Type</th><th>Records</th><th>Action</th></tr></thead>
                <tbody>
                    <tr><td>Predictions</td><td>${c.predictions || 0}</td><td><button class="btn btn-outline btn-sm" onclick="clearData('predictions')">Clear</button></td></tr>
                    <tr><td>Model Versions</td><td>${c.model_versions || 0}</td><td><button class="btn btn-outline btn-sm" onclick="clearData('models')">Clear</button></td></tr>
                    <tr><td>LCA Assessments</td><td>${c.environmental_metrics || 0}</td><td><button class="btn btn-outline btn-sm" onclick="clearData('lca')">Clear</button></td></tr>
                    <tr><td>Circularity Scores</td><td>${c.circularity_metrics || 0}</td><td><button class="btn btn-outline btn-sm" onclick="clearData('circularity')">Clear</button></td></tr>
                    <tr><td>Sustainability Scores</td><td>${c.sustainability_scores || 0}</td><td><button class="btn btn-outline btn-sm" onclick="clearData('circularity')">Clear</button></td></tr>
                    <tr><td>Reports</td><td>${c.reports || 0}</td><td><button class="btn btn-outline btn-sm" onclick="clearData('all')">Clear</button></td></tr>
                </tbody>
            </table>
            <div style="padding:12px;background:#fce8e6;border-radius:var(--radius);margin-bottom:12px;">
                <strong style="color:var(--danger);">Danger Zone</strong>
                <p style="font-size:13px;color:var(--text-secondary);margin-top:4px;">This will delete ALL ${dataCounts.total || 0} records across all types.</p>
            </div>
            <button class="btn btn-danger" onclick="clearData('all')">Delete All Data (${dataCounts.total || 0} records)</button>
        </div>
        <div class="card">
            <div class="card-header"><h3>Platform Settings</h3></div>
            <div class="form-group"><label>API Base URL</label><input type="text" value="${window.location.origin}/api/v1" readonly></div>
            <div class="form-group"><label>API Documentation</label><a href="/docs" target="_blank" class="btn btn-outline btn-sm">Open Swagger UI</a></div>
            <div style="margin-top:24px;"><h4 style="margin-bottom:8px;">System Information</h4>
                <table class="data-table"><tbody>
                    <tr><td>Version</td><td>1.0.0</td></tr>
                    <tr><td>Framework</td><td>FastAPI + Python</td></tr>
                    <tr><td>ML Models</td><td>scikit-learn, GradientBoosting, RandomForest</td></tr>
                    <tr><td>Frontend</td><td>Vanilla JS + Chart.js</td></tr>
                </tbody></table>
            </div>
        </div>`;
};

window.clearData = async function(type) {
    const label = type === 'all' ? 'ALL data' : type;
    if (!confirm(`Are you sure you want to delete ${label}? This cannot be undone.`)) return;
    try {
        if (type === 'all') {
            await api.dashboard.clearAll();
        } else if (type === 'predictions') {
            await api.dashboard.clearPredictions();
        } else if (type === 'lca') {
            await api.dashboard.clearLCA();
        } else if (type === 'circularity') {
            await api.dashboard.clearCircularity();
        } else if (type === 'models') {
            await api.dashboard.clearModels();
        }
        showToast(`${label} cleared`, 'success');
        pages.settings();
    } catch (err) {
        showToast('Failed to clear: ' + err.message, 'error');
    }
};

// Router
function navigateTo(page) {
    currentPage = page;
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    const navItem = document.querySelector(`[data-page="${page}"]`);
    if (navItem) navItem.classList.add('active');
    document.getElementById('page-title').textContent = page.charAt(0).toUpperCase() + page.slice(1);
    if (pages[page]) pages[page]();
    else document.getElementById('content-area').innerHTML = errorHtml(`Page "${page}" not found`);
}

function handleHash() {
    let page = window.location.hash.replace('#', '') || 'dashboard';
    if (!isLoggedIn() && page !== 'login' && page !== 'register') {
        page = 'login';
    }
    if (isLoggedIn() && (page === 'login' || page === 'register')) {
        page = 'dashboard';
    }
    window.location.hash = '#' + page;
    navigateTo(page);
}

window.addEventListener('hashchange', handleHash);
window.addEventListener('load', () => {
    handleHash();
    api.get('/health').then(() => {
        document.getElementById('api-status').textContent = 'Connected';
        document.getElementById('api-status').className = 'status-badge';
    }).catch(() => {
        document.getElementById('api-status').textContent = 'Disconnected';
        document.getElementById('api-status').className = 'status-badge';
        document.getElementById('api-status').style.background = '#fce8e6';
        document.getElementById('api-status').style.color = 'var(--danger)';
    });
});
