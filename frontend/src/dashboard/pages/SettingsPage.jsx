import { useEffect, useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import { api } from '../api.js';
import { showToast } from '../ui.jsx';
import authService from '../../auth/authService.js';

export default function SettingsPage() {
  const { onLogout } = useOutletContext();
  const user = authService.getUser();
  const [counts, setCounts] = useState({});
  const [total, setTotal] = useState(0);

  const load = () => {
    api.dashboard.dataCounts()
      .then((res) => { setCounts(res.counts || {}); setTotal(res.total || 0); })
      .catch(() => {});
  };

  useEffect(() => { load(); }, []);

  const clearData = async (type) => {
    const label = type === 'all' ? 'ALL data' : type;
    if (!window.confirm(`Are you sure you want to delete ${label}? This cannot be undone.`)) return;
    try {
      if (type === 'all') await api.dashboard.clearAll();
      else if (type === 'predictions') await api.dashboard.clearPredictions();
      else if (type === 'lca') await api.dashboard.clearLCA();
      else if (type === 'circularity') await api.dashboard.clearCircularity();
      else if (type === 'models') await api.dashboard.clearModels();
      showToast(`${label} cleared`, 'success');
      load();
    } catch (err) {
      showToast('Failed to clear: ' + err.message, 'error');
    }
  };

  return (
    <>
      <div className="card">
        <div className="card-header"><h3>Account</h3></div>
        <div className="result-grid" style={{ marginBottom: 16 }}>
          <div className="result-item"><div className="label">Username</div><div className="value">{user?.username || 'N/A'}</div></div>
          <div className="result-item"><div className="label">Email</div><div className="value">{user?.email || 'N/A'}</div></div>
          <div className="result-item"><div className="label">Role</div><div className="value">{user?.role || 'N/A'}</div></div>
        </div>
        <button className="btn btn-danger" onClick={onLogout}>Sign Out</button>
      </div>

      <div className="card">
        <div className="card-header"><h3>Clear Data</h3></div>
        <p style={{ marginBottom: 12, color: 'var(--text-secondary)' }}>Delete all analyzed data. Users and datasets are kept.</p>
        <table className="data-table" style={{ marginBottom: 16 }}>
          <thead><tr><th>Data Type</th><th>Records</th><th>Action</th></tr></thead>
          <tbody>
            <tr><td>Predictions</td><td>{counts.predictions || 0}</td><td><button className="btn btn-outline btn-sm" onClick={() => clearData('predictions')}>Clear</button></td></tr>
            <tr><td>Model Versions</td><td>{counts.model_versions || 0}</td><td><button className="btn btn-outline btn-sm" onClick={() => clearData('models')}>Clear</button></td></tr>
            <tr><td>LCA Assessments</td><td>{counts.environmental_metrics || 0}</td><td><button className="btn btn-outline btn-sm" onClick={() => clearData('lca')}>Clear</button></td></tr>
            <tr><td>Circularity Scores</td><td>{counts.circularity_metrics || 0}</td><td><button className="btn btn-outline btn-sm" onClick={() => clearData('circularity')}>Clear</button></td></tr>
            <tr><td>Sustainability Scores</td><td>{counts.sustainability_scores || 0}</td><td><button className="btn btn-outline btn-sm" onClick={() => clearData('circularity')}>Clear</button></td></tr>
            <tr><td>Reports</td><td>{counts.reports || 0}</td><td><button className="btn btn-outline btn-sm" onClick={() => clearData('all')}>Clear</button></td></tr>
          </tbody>
        </table>
        <div style={{ padding: 12, background: '#fce8e6', borderRadius: 'var(--radius)', marginBottom: 12 }}>
          <strong style={{ color: 'var(--danger)' }}>Danger Zone</strong>
          <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 4 }}>This will delete ALL {total || 0} records across all types.</p>
        </div>
        <button className="btn btn-danger" onClick={() => clearData('all')}>Delete All Data ({total || 0} records)</button>
      </div>

      <div className="card">
        <div className="card-header"><h3>Platform Settings</h3></div>
        <div className="form-group">
          <label>API Base URL</label>
          <input type="text" value={`${window.location.origin}/api/v1`} readOnly />
        </div>
        <div className="form-group">
          <label>API Documentation</label>
          <a href="/docs" target="_blank" rel="noreferrer" className="btn btn-outline btn-sm">Open Swagger UI</a>
        </div>
        <div style={{ marginTop: 24 }}>
          <h4 style={{ marginBottom: 8 }}>System Information</h4>
          <table className="data-table">
            <tbody>
              <tr><td>Version</td><td>1.0.0</td></tr>
              <tr><td>Framework</td><td>FastAPI + Python</td></tr>
              <tr><td>ML Models</td><td>scikit-learn, GradientBoosting, RandomForest</td></tr>
              <tr><td>Frontend</td><td>React + Chart.js</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
