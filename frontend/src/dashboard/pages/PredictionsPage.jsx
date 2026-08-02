import { useEffect, useState } from 'react';
import { api } from '../api.js';
import { showToast, formatNumber, Loading, ErrorBox, Modal } from '../ui.jsx';

const MODEL_OPTIONS = [
  { value: 'hree_predictor', label: 'HREE Percentage Predictor' },
  { value: 'deposit_classifier', label: 'Deposit Type Classifier' },
  { value: 'resource_estimator', label: 'Resource Size Estimator' },
  { value: 'dy_predictor', label: 'Dy2O3 Content Predictor' },
];

export default function PredictionsPage() {
  const [metrics, setMetrics] = useState({});
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [training, setTraining] = useState(false);
  const [trainResult, setTrainResult] = useState(null);
  const [predicting, setPredicting] = useState(false);
  const [predResult, setPredResult] = useState(null);
  const [error, setError] = useState(null);
  const [form, setForm] = useState({
    model: 'hree_predictor',
    log_resource: 6,
    grade_pct: 3.0,
    continent_encoded: 0,
    deposit_type_encoded: 0,
  });

  useEffect(() => { loadMetrics(); loadHistory(); setLoading(false); }, []);

  const loadMetrics = async () => {
    try { const data = await api.predictions.metrics(); setMetrics(data); }
    catch { setMetrics({}); }
  };

  const loadHistory = async () => {
    try { const data = await api.predictions.history(10); setHistory(data.predictions || []); }
    catch { setHistory([]); }
  };

  const handleTrain = async () => {
    setTraining(true); setTrainResult(null);
    try {
      const res = await api.predictions.train();
      let html = '<div class="result-box"><h4>Training Results</h4><div class="result-grid">';
      for (const [name, m] of Object.entries(res.results)) {
        const score = m.r2 || m.accuracy || 0;
        html += `<div class="result-item"><div class="label">${name}</div><div class="value">${(score * 100).toFixed(1)}%</div></div>`;
      }
      html += '</div></div>';
      setTrainResult(html);
      showToast('Models trained successfully', 'success');
      loadMetrics();
    } catch (err) {
      setTrainResult(`<p style="color:var(--danger)">Training failed: ${err.message}</p>`);
      showToast('Training failed', 'error');
    }
    setTraining(false);
  };

  const handlePredict = async (e) => {
    e.preventDefault();
    setPredicting(true); setPredResult(null);
    try {
      const res = await api.predictions.predict(form.model, form);
      let html = '<div class="result-box"><h4>Prediction Result</h4><div class="result-grid">';
      for (const [k, v] of Object.entries(res.result)) {
        if (typeof v === 'object') continue;
        html += `<div class="result-item"><div class="label">${k}</div><div class="value">${typeof v === 'number' ? v.toFixed(4) : v}</div></div>`;
      }
      html += '</div>';
      if (res.explanation?.natural_language) {
        html += `<div style="margin-top:12px;padding:12px;background:#e8f0fe;border-radius:var(--radius);font-size:14px;"><strong>Explanation:</strong> ${res.explanation.natural_language}</div>`;
      }
      html += `<p style="margin-top:8px;font-size:12px;color:var(--text-secondary)">Execution time: ${res.execution_time_ms}ms</p></div>`;
      setPredResult(html);
      showToast('Prediction completed', 'success');
      loadHistory();
    } catch (err) {
      setPredResult(`<p style="color:var(--danger)">Prediction failed: ${err.message}</p>`);
    }
    setPredicting(false);
  };

  if (loading) return <Loading />;
  if (error) return <ErrorBox msg={error} />;

  return (
    <>
      <div className="stats-grid">
        <div className="stat-card"><div className="stat-icon blue">M</div><div className="stat-info"><h4>4</h4><p>Available Models</p></div></div>
      </div>
      <div className="grid-2">
        <div className="card">
          <div className="card-header"><h3>Train Models</h3></div>
          <p style={{ marginBottom: 16, color: 'var(--text-secondary)' }}>Train all ML models on the mining projects dataset.</p>
          <button className="btn btn-primary" onClick={handleTrain} disabled={training}>
            {training ? <><span className="spinner" /> Training...</> : 'Train All Models'}
          </button>
          <div id="train-result" style={{ marginTop: 12 }} dangerouslySetInnerHTML={{ __html: trainResult || '' }} />
        </div>
        <div className="card">
          <div className="card-header"><h3>Model Metrics</h3></div>
          <div id="model-metrics-display">
            {Object.keys(metrics).length === 0 ? (
              <p style={{ color: 'var(--text-secondary)' }}>No trained models found. Train models first.</p>
            ) : (
              <table className="data-table">
                <thead><tr><th>Model</th><th>Score</th><th>Cross-Val</th></tr></thead>
                <tbody>
                  {Object.entries(metrics).map(([name, m]) => {
                    const score = m.r2 || m.accuracy || 0;
                    const cv = m.cv_r2_mean || 0;
                    return <tr key={name}><td>{name}</td><td>{(score * 100).toFixed(1)}%</td><td>{(cv * 100).toFixed(1)}%</td></tr>;
                  })}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>
      <div className="card">
        <div className="card-header"><h3>Run Prediction</h3></div>
        <form onSubmit={handlePredict}>
          <div className="form-row">
            <div className="form-group">
              <label>Model</label>
              <select value={form.model} onChange={e => setForm({...form, model: e.target.value})}>
                {MODEL_OPTIONS.map(m => <option key={m.value} value={m.value}>{m.label}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Log Resource</label>
              <input type="number" step="0.1" value={form.log_resource} onChange={e => setForm({...form, log_resource: parseFloat(e.target.value)})} />
            </div>
          </div>
          <div className="form-row-3">
            <div className="form-group"><label>Grade %</label><input type="number" step="0.1" value={form.grade_pct} onChange={e => setForm({...form, grade_pct: parseFloat(e.target.value)})} /></div>
            <div className="form-group">
              <label>Continent</label>
              <select value={form.continent_encoded} onChange={e => setForm({...form, continent_encoded: parseInt(e.target.value)})}>
                <option value={0}>Asia</option><option value={1}>Australia</option><option value={2}>Europe</option>
                <option value={3}>North America</option><option value={4}>South America</option><option value={5}>Africa</option>
              </select>
            </div>
            <div className="form-group">
              <label>Deposit Type</label>
              <select value={form.deposit_type_encoded} onChange={e => setForm({...form, deposit_type_encoded: parseInt(e.target.value)})}>
                <option value={0}>Alkaline rock</option><option value={1}>Carbonatite</option><option value={2}>Hydrothermal/IOCG</option>
                <option value={3}>Ionic Clay</option><option value={4}>Placer</option><option value={5}>Other</option>
              </select>
            </div>
          </div>
          <button type="submit" className="btn btn-success" disabled={predicting}>
            {predicting ? <><span className="spinner" /> Predicting...</> : 'Run Prediction'}
          </button>
          <div id="prediction-result" style={{ marginTop: 16 }} dangerouslySetInnerHTML={{ __html: predResult || '' }} />
        </form>
      </div>
      <div className="card">
        <div className="card-header"><h3>Prediction History</h3></div>
        <div id="prediction-history">
          {history.length === 0 ? (
            <p style={{ color: 'var(--text-secondary)' }}>No predictions yet.</p>
          ) : (
            <table className="data-table">
              <thead><tr><th>Model</th><th>Result</th><th>Time</th></tr></thead>
              <tbody>
                {history.map((p, i) => (
                  <tr key={i}><td>{p.model}</td><td>{JSON.stringify(p.result).substring(0, 80)}...</td><td>{p.time || 'N/A'}</td></tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </>
  );
}