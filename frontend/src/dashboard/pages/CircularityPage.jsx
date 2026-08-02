import { useEffect, useState } from 'react';
import { api } from '../api.js';
import { showToast } from '../ui.jsx';

export default function CircularityPage() {
  const [oreOptions, setOreOptions] = useState([{ key: 'REE', name: 'Rare Earth Elements' }]);
  const [form, setForm] = useState({
    facility_name: 'REE Mine',
    ore_type: 'REE',
    ore_processed_tonnes: 100000,
    waste_generated_tonnes: 50000,
    water_used_m3: 100000,
    energy_consumed_mj: 500000,
    recycled_material_tonnes: 500,
    product_output_tonnes: 5000,
  });
  const [result, setResult] = useState(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.circularity.oreTypes()
      .then((res) => { if (res.ore_types?.length) setOreOptions(res.ore_types); })
      .catch(() => {});
  }, []);

  const set = (key, value) => setForm((prev) => ({ ...prev, [key]: value }));

  const handleRun = async () => {
    setRunning(true);
    setError(null);
    setResult(null);
    try {
      const res = await api.circularity.calculate(form);
      setResult(res);
      showToast('Circularity calculated', 'success');
    } catch (err) {
      setError(err.message);
    }
    setRunning(false);
  };

  const scoreColor = result
    ? (result.circularity_score > 50 ? 'var(--accent)' : result.circularity_score > 25 ? 'var(--warning)' : 'var(--danger)')
    : 'var(--primary)';

  return (
    <>
      <div className="card">
        <div className="card-header"><h3>Circularity Assessment</h3></div>
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
            <label>Ore Processed (t)</label>
            <input type="number" value={form.ore_processed_tonnes} onChange={e => set('ore_processed_tonnes', parseFloat(e.target.value))} />
          </div>
        </div>
        <div className="form-row-3">
          <div className="form-group">
            <label>Waste Generated (t)</label>
            <input type="number" value={form.waste_generated_tonnes} onChange={e => set('waste_generated_tonnes', parseFloat(e.target.value))} />
          </div>
          <div className="form-group">
            <label>Water Used (m3)</label>
            <input type="number" value={form.water_used_m3} onChange={e => set('water_used_m3', parseFloat(e.target.value))} />
          </div>
          <div className="form-group">
            <label>Energy (MJ)</label>
            <input type="number" value={form.energy_consumed_mj} onChange={e => set('energy_consumed_mj', parseFloat(e.target.value))} />
          </div>
        </div>
        <div className="form-row-3">
          <div className="form-group">
            <label>Recycled Material (t)</label>
            <input type="number" value={form.recycled_material_tonnes} onChange={e => set('recycled_material_tonnes', parseFloat(e.target.value))} />
          </div>
          <div className="form-group">
            <label>Product Output (t)</label>
            <input type="number" value={form.product_output_tonnes} onChange={e => set('product_output_tonnes', parseFloat(e.target.value))} />
          </div>
        </div>
        <button className="btn btn-success" onClick={handleRun} disabled={running}>
          {running ? <><span className="spinner" /> Calculating...</> : 'Calculate Circularity'}
        </button>
        {error && <p style={{ color: 'var(--danger)', marginTop: 12 }}>Calculation failed: {error}</p>}
        <div id="circularity-result" style={{ marginTop: 16 }}>
          {result && (
            <>
              <div className="score-display">
                <div className="score-value" style={{ color: scoreColor }}>{result.circularity_score}</div>
                <div className="score-grade">Circularity Score ({result.ore_name || 'REE'})</div>
                <div className="score-bar"><div className="score-bar-fill" style={{ width: `${result.circularity_score}%`, background: scoreColor }} /></div>
              </div>
              <div className="result-grid">
                <div className="result-item"><div className="label">Recycling Potential</div><div className="value">{result.recycling_potential}%</div></div>
                <div className="result-item"><div className="label">Resource Efficiency</div><div className="value">{result.resource_efficiency}%</div></div>
                <div className="result-item"><div className="label">Material Recovery</div><div className="value">{result.material_recovery_rate}%</div></div>
                <div className="result-item"><div className="label">Waste Diversion</div><div className="value">{result.waste_diversion_rate}%</div></div>
              </div>
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
