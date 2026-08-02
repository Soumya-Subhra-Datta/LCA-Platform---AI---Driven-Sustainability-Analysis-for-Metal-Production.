import { useEffect, useState } from 'react';
import { api } from '../api.js';
import { createDoughnutChart, createRadarChart, destroyChart } from '../charts.js';
import { showToast, formatNumber } from '../ui.jsx';

const PROCESSING_OPTIONS = [
  { value: 'crushing,grinding,leaching,solvent_extraction', label: 'Full REE Processing' },
  { value: 'crushing,grinding', label: 'Crushing + Grinding Only' },
  { value: 'leaching,solvent_extraction', label: 'Hydromet Only' },
  { value: 'crushing,grinding,flotation,smelting', label: 'Flotation + Smelting' },
  { value: 'crushing,grinding,flotation,smelting,electrorefining', label: 'Full Pyromet + Electro' },
];

export default function LCAPage() {
  const [oreOptions, setOreOptions] = useState([{ key: 'REE', name: 'Rare Earth Elements', description: 'Default' }]);
  const [form, setForm] = useState({
    facility_name: 'REE Processing Plant',
    ore_type: 'REE',
    mining_type: 'Surface',
    resource_tonnes: 100000,
    grade_pct: 5.0,
    transport_distance_km: 200,
    processing_method: 'crushing,grinding,leaching,solvent_extraction',
  });
  const [result, setResult] = useState(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState(null);
  const [benchmarks, setBenchmarks] = useState({});

  useEffect(() => {
    api.environmental.oreTypes()
      .then((res) => { if (res.ore_types?.length) setOreOptions(res.ore_types); })
      .catch(() => {});
    api.environmental.benchmarks()
      .then((res) => setBenchmarks(res))
      .catch(() => setBenchmarks({}));
  }, []);

  useEffect(() => {
    if (!result) return;
    const cf = result.carbon_footprint;
    createDoughnutChart('chart-lca-breakdown',
      ['Mining', 'Processing', 'Transport'],
      [cf.mining_kg_co2 / 1000, cf.processing_kg_co2 / 1000, cf.transport_kg_co2 / 1000]);
    createRadarChart('chart-lca-radar',
      ['Carbon', 'Water', 'Energy', 'Waste', 'Acidification'],
      [{
        label: 'Impact',
        data: [
          Math.min(result.carbon_footprint.intensity_kg_co2_per_t_ore * 5, 100),
          Math.min(result.water_footprint.intensity_m3_per_t_ore * 20, 100),
          Math.min(result.energy_consumption.intensity_mj_per_t_ore * 2, 100),
          Math.min(result.waste_generation.waste_to_ore_ratio * 10, 100),
          Math.min(result.acidification.total_kg_so2_eq * 10, 100),
        ],
        backgroundColor: 'rgba(26,115,232,0.2)',
        borderColor: '#1a73e8',
      }]);
    return () => { destroyChart('chart-lca-breakdown'); destroyChart('chart-lca-radar'); };
  }, [result]);

  const set = (key, value) => setForm((prev) => ({ ...prev, [key]: value }));

  const handleRun = async () => {
    setRunning(true);
    setError(null);
    setResult(null);
    try {
      const res = await api.environmental.assess(form);
      setResult(res);
      showToast('LCA assessment completed', 'success');
    } catch (err) {
      setError(err.message);
    }
    setRunning(false);
  };

  const s = result?.summary;

  return (
    <>
      <div className="card">
        <div className="card-header"><h3>Life Cycle Assessment</h3></div>
        <div className="form-row-3">
          <div className="form-group">
            <label>Facility Name</label>
            <input type="text" value={form.facility_name} onChange={e => set('facility_name', e.target.value)} />
          </div>
          <div className="form-group">
            <label>Ore / Metal Type</label>
            <select value={form.ore_type} onChange={e => set('ore_type', e.target.value)}>
              {oreOptions.map(o => (
                <option key={o.key} value={o.key}>{o.name}{o.description ? ` - ${o.description.substring(0, 50)}...` : ''}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Mining Type</label>
            <select value={form.mining_type} onChange={e => set('mining_type', e.target.value)}>
              <option value="Surface">Surface</option>
              <option value="Underground">Underground</option>
            </select>
          </div>
        </div>
        <div className="form-row-3">
          <div className="form-group">
            <label>Resource (tonnes)</label>
            <input type="number" step="1000" value={form.resource_tonnes} onChange={e => set('resource_tonnes', parseFloat(e.target.value))} />
          </div>
          <div className="form-group">
            <label>Grade (%)</label>
            <input type="number" step="0.1" value={form.grade_pct} onChange={e => set('grade_pct', parseFloat(e.target.value))} />
          </div>
          <div className="form-group">
            <label>Transport Distance (km)</label>
            <input type="number" step="10" value={form.transport_distance_km} onChange={e => set('transport_distance_km', parseFloat(e.target.value))} />
          </div>
        </div>
        <div className="form-row">
          <div className="form-group">
            <label>Processing</label>
            <select value={form.processing_method} onChange={e => set('processing_method', e.target.value)}>
              {PROCESSING_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>
          </div>
        </div>
        <button className="btn btn-success" onClick={handleRun} disabled={running}>
          {running ? <><span className="spinner" /> Running...</> : 'Run Assessment'}
        </button>
        {error && <p style={{ color: 'var(--danger)', marginTop: 12 }}>Assessment failed: {error}</p>}
        <div id="lca-result" style={{ marginTop: 16 }}>
          {result && s && (
            <div className="result-box">
              <h4>
                LCA Results - <span>{s.ore_type || 'REE'}</span> - Impact Grade:{' '}
                <span className={`tag ${s.impact_grade <= 'B' ? 'tag-success' : s.impact_grade <= 'C' ? 'tag-warning' : 'tag-danger'}`}>{s.impact_grade}</span>
              </h4>
              <div className="result-grid" style={{ marginTop: 12 }}>
                <div className="result-item"><div className="label">Total CO2</div><div className="value">{formatNumber(s.total_co2_tonnes)} t</div></div>
                <div className="result-item"><div className="label">Total Water</div><div className="value">{formatNumber(s.total_water_m3)} m3</div></div>
                <div className="result-item"><div className="label">Total Energy</div><div className="value">{formatNumber(s.total_energy_mwh)} MWh</div></div>
                <div className="result-item"><div className="label">Total Waste</div><div className="value">{formatNumber(s.total_waste_tonnes)} t</div></div>
              </div>
              <div className="chart-grid" style={{ marginTop: 16 }}>
                <div><div className="chart-container"><canvas id="chart-lca-breakdown" /></div></div>
                <div><div className="chart-container"><canvas id="chart-lca-radar" /></div></div>
              </div>
            </div>
          )}
        </div>
      </div>
      <div className="card">
        <div className="card-header"><h3>Industry Benchmarks</h3></div>
        <div id="benchmark-display">
          {Object.keys(benchmarks).length === 0 ? (
            <p>Could not load benchmarks.</p>
          ) : (
            <div className="result-grid">
              {Object.entries(benchmarks).map(([category, values]) => (
                <div className="result-item" key={category}>
                  <div className="label" style={{ textTransform: 'capitalize' }}>{category}</div>
                  {Object.entries(values).map(([k, v]) => (
                    <div style={{ fontSize: 13, marginTop: 4 }} key={k}>
                      <strong>{k}:</strong> {typeof v === 'number' ? v.toFixed(4) : v}
                    </div>
                  ))}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
