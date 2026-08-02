import { useEffect, useState } from 'react';
import { api } from '../api.js';
import { createRadarChart, destroyChart } from '../charts.js';
import { showToast } from '../ui.jsx';

const GRADE_COLORS = {
  'A+': '#34a853', 'A': '#34a853', 'B+': '#1a73e8', 'B': '#1a73e8',
  'C+': '#fbbc04', 'C': '#fbbc04', 'D': '#ea4335', 'F': '#ea4335',
};

export default function SustainabilityPage() {
  const [oreOptions, setOreOptions] = useState([{ key: 'REE', name: 'Rare Earth Elements' }]);
  const [form, setForm] = useState({
    facility_name: 'REE Mine',
    ore_type: 'REE',
    carbon_footprint_kg_co2: 500000,
    water_footprint_m3: 100000,
    energy_consumption_mj: 2000000,
    waste_generation_kg: 5000000,
    recycling_rate: 15,
    community_investment_usd: 50000,
    employees: 200,
    revenue_usd: 50000000,
  });
  const [result, setResult] = useState(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.circularity.oreTypes()
      .then((res) => { if (res.ore_types?.length) setOreOptions(res.ore_types); })
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (!result) return;
    createRadarChart('chart-sus-radar',
      ['Environmental', 'Social', 'Governance', 'Economic', 'Innovation'],
      [{
        label: 'Score',
        data: [result.environmental_score, result.social_score, result.governance_score, result.economic_score, result.innovation_score],
        backgroundColor: 'rgba(26,115,232,0.2)',
        borderColor: '#1a73e8',
      }]);
    return () => destroyChart('chart-sus-radar');
  }, [result]);

  const set = (key, value) => setForm((prev) => ({ ...prev, [key]: value }));

  const handleRun = async () => {
    setRunning(true);
    setError(null);
    setResult(null);
    try {
      const res = await api.circularity.sustainability(form);
      setResult(res);
      showToast('Sustainability score calculated', 'success');
    } catch (err) {
      setError(err.message);
    }
    setRunning(false);
  };

  const gc = result ? (GRADE_COLORS[result.grade] || '#666') : '#666';

  return (
    <>
      <div className="card">
        <div className="card-header"><h3>Sustainability Score</h3></div>
        <div className="form-row-3">
          <div className="form-group">
            <label>Facility Name</label>
            <input type="text" value={form.facility_name} onChange={e => set('facility_name', e.target.value)} />
          </div>
          <div className="form-group">
            <label>Ore / Metal Type</label>
            <select value={form.ore_type} onChange={e => set('ore_type', e.target.value)}>
              {oreOptions.map(o => <option key={o.key} value={o.key}>{o.name}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label>Carbon (kg CO2)</label>
            <input type="number" value={form.carbon_footprint_kg_co2} onChange={e => set('carbon_footprint_kg_co2', parseFloat(e.target.value))} />
          </div>
        </div>
        <div className="form-row-3">
          <div className="form-group">
            <label>Water (m3)</label>
            <input type="number" value={form.water_footprint_m3} onChange={e => set('water_footprint_m3', parseFloat(e.target.value))} />
          </div>
          <div className="form-group">
            <label>Energy (MJ)</label>
            <input type="number" value={form.energy_consumption_mj} onChange={e => set('energy_consumption_mj', parseFloat(e.target.value))} />
          </div>
          <div className="form-group">
            <label>Waste (kg)</label>
            <input type="number" value={form.waste_generation_kg} onChange={e => set('waste_generation_kg', parseFloat(e.target.value))} />
          </div>
        </div>
        <div className="form-row-3">
          <div className="form-group">
            <label>Recycling Rate (%)</label>
            <input type="number" step="1" value={form.recycling_rate} onChange={e => set('recycling_rate', parseFloat(e.target.value))} />
          </div>
          <div className="form-group">
            <label>Community Investment ($)</label>
            <input type="number" value={form.community_investment_usd} onChange={e => set('community_investment_usd', parseFloat(e.target.value))} />
          </div>
          <div className="form-group">
            <label>Employees</label>
            <input type="number" value={form.employees} onChange={e => set('employees', parseInt(e.target.value))} />
          </div>
        </div>
        <div className="form-row">
          <div className="form-group">
            <label>Revenue ($)</label>
            <input type="number" value={form.revenue_usd} onChange={e => set('revenue_usd', parseFloat(e.target.value))} />
          </div>
        </div>
        <button className="btn btn-success" onClick={handleRun} disabled={running}>
          {running ? <><span className="spinner" /> Calculating...</> : 'Calculate Score'}
        </button>
        {error && <p style={{ color: 'var(--danger)', marginTop: 12 }}>Calculation failed: {error}</p>}
        <div id="sustainability-result" style={{ marginTop: 16 }}>
          {result && (
            <>
              <div className="score-display">
                <div className="score-value" style={{ color: gc }}>{result.overall_score.toFixed(1)}</div>
                <div className="score-grade">Grade: <span style={{ color: gc }}>{result.grade}</span></div>
                <div className="score-bar"><div className="score-bar-fill" style={{ width: `${result.overall_score}%`, background: gc }} /></div>
              </div>
              <div className="result-grid">
                <div className="result-item"><div className="label">Environmental</div><div className="value">{result.environmental_score.toFixed(1)}</div></div>
                <div className="result-item"><div className="label">Social</div><div className="value">{result.social_score.toFixed(1)}</div></div>
                <div className="result-item"><div className="label">Governance</div><div className="value">{result.governance_score.toFixed(1)}</div></div>
                <div className="result-item"><div className="label">Economic</div><div className="value">{result.economic_score.toFixed(1)}</div></div>
                <div className="result-item"><div className="label">Innovation</div><div className="value">{result.innovation_score.toFixed(1)}</div></div>
              </div>
              <div className="chart-container" style={{ height: 250, marginTop: 16 }}><canvas id="chart-sus-radar" /></div>
              <div className="card" style={{ marginTop: 16 }}>
                <h4 style={{ marginBottom: 8 }}>Recommendations</h4>
                <ul style={{ paddingLeft: 20 }}>
                  {(result.recommendations || []).map((r, i) => (
                    <li key={i} style={{ marginBottom: 6, fontSize: 14 }}>{r}</li>
                  ))}
                </ul>
              </div>
            </>
          )}
        </div>
      </div>
    </>
  );
}
