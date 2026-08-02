import { useEffect, useState } from 'react';
import { api } from '../api.js';
import { createDoughnutChart, createBarChart, destroyChart } from '../charts.js';
import { Loading, ErrorBox, showToast, formatNumber } from '../ui.jsx';

export default function DashboardPage() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const chartRefs = { continent: 'chart-continent', deposits: 'chart-deposits', models: 'chart-models' };

  useEffect(() => {
    let mounted = true;
    api.dashboard.get()
      .then(res => mounted && setData(res))
      .catch(err => mounted && (setError(err.message), showToast('Failed to load dashboard: ' + err.message, 'error')));
    return () => { mounted = false; };
  }, []);

  useEffect(() => {
    if (!data) return;
    const cd = data.mining_overview?.continent_distribution;
    const dd = data.mining_overview?.deposit_distribution;
    const mm = data.model_metrics;
    if (cd && Object.keys(cd).length) createDoughnutChart(chartRefs.continent, Object.keys(cd), Object.values(cd));
    if (dd && Object.keys(dd).length) createBarChart(chartRefs.deposits, Object.keys(dd), [{ label: 'Projects', data: Object.values(dd), backgroundColor: '#1a73e8' }]);
    if (mm && Object.keys(mm).length) {
      const names = Object.keys(mm);
      const scores = names.map(n => mm[n].r2 || mm[n].accuracy || 0);
      createBarChart(chartRefs.models, names.map(n => n.replace('_', ' ')), [{ label: 'R2 / Accuracy', data: scores, backgroundColor: '#34a853' }]);
    }
    return () => Object.values(chartRefs).forEach(destroyChart);
  }, [data]);

  if (error) return <ErrorBox msg={error} />;
  if (!data) return <Loading />;

  const s = data.summary;
  const preds = data.recent_activity?.predictions || [];
  const lcas = data.recent_activity?.lca_assessments || [];

  return (
    <>
      <div className="stats-grid">
        <div className="stat-card"><div className="stat-icon blue">D</div><div className="stat-info"><h4>{s.total_datasets}</h4><p>Datasets</p></div></div>
        <div className="stat-card"><div className="stat-icon green">R</div><div className="stat-info"><h4>{formatNumber(s.total_rows)}</h4><p>Total Rows</p></div></div>
        <div className="stat-card"><div className="stat-icon orange">P</div><div className="stat-info"><h4>{s.prediction_count}</h4><p>Predictions</p></div></div>
        <div className="stat-card"><div className="stat-icon red">L</div><div className="stat-info"><h4>{s.lca_assessment_count}</h4><p>LCA Assessments</p></div></div>
      </div>
      <div className="chart-grid">
        <div className="card">
          <div className="card-header"><h3>REE Mining Projects by Continent</h3></div>
          <div className="chart-container"><canvas id="chart-continent" /></div>
        </div>
        <div className="card">
          <div className="card-header"><h3>Deposit Type Distribution</h3></div>
          <div className="chart-container"><canvas id="chart-deposits" /></div>
        </div>
      </div>
      <div className="card">
        <div className="card-header"><h3>Model Performance</h3></div>
        <div className="chart-container"><canvas id="chart-models" /></div>
      </div>
      <div className="card">
        <div className="card-header"><h3>Recent Activity</h3></div>
        <table className="data-table">
          <thead><tr><th>Type</th><th>Details</th><th>Time</th></tr></thead>
          <tbody>
            {preds.map((p, i) => (
              <tr key={i}><td><span className="tag tag-info">Prediction</span></td><td>{p.model}</td><td>{p.time || 'N/A'}</td></tr>
            ))}
            {lcas.map((m, i) => (
              <tr key={i}><td><span className="tag tag-success">LCA</span></td><td>{m.facility} - {formatNumber(m.carbon)} kg CO2</td><td>{m.time || 'N/A'}</td></tr>
            ))}
            {(preds.length === 0 && lcas.length === 0) && (
              <tr><td colSpan={3} style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>No recent activity</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </>
  );
}