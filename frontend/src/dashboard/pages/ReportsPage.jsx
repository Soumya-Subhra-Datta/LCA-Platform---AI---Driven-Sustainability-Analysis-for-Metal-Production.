import { useEffect, useState } from 'react';
import { api } from '../api.js';
import { showToast } from '../ui.jsx';

const REPORT_TYPES = [
  { value: 'comprehensive', label: 'Comprehensive Report' },
  { value: 'lca_summary', label: 'LCA Summary' },
  { value: 'sustainability', label: 'Sustainability Summary' },
  { value: 'predictions', label: 'Predictions Summary' },
];

export default function ReportsPage() {
  const [type, setType] = useState('comprehensive');
  const [title, setTitle] = useState('Analysis Report');
  const [generating, setGenerating] = useState(false);
  const [generated, setGenerated] = useState(null);
  const [error, setError] = useState(null);
  const [reports, setReports] = useState([]);

  const loadReports = () => {
    api.reports.list()
      .then((res) => setReports(res.reports || []))
      .catch(() => setReports([]));
  };

  useEffect(() => { loadReports(); }, []);

  const handleGenerate = async () => {
    setGenerating(true);
    setError(null);
    setGenerated(null);
    try {
      const res = await api.reports.generate(type, title);
      setGenerated(res);
      showToast('Report generated', 'success');
      loadReports();
    } catch (err) {
      setError(err.message);
    }
    setGenerating(false);
  };

  return (
    <>
      <div className="card">
        <div className="card-header"><h3>Generate Report</h3></div>
        <div className="form-row">
          <div className="form-group">
            <label>Report Type</label>
            <select value={type} onChange={e => setType(e.target.value)}>
              {REPORT_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label>Title</label>
            <input type="text" value={title} onChange={e => setTitle(e.target.value)} />
          </div>
        </div>
        <button className="btn btn-primary" onClick={handleGenerate} disabled={generating}>
          {generating ? <><span className="spinner" /> Generating...</> : 'Generate Report'}
        </button>
        {error && <p style={{ color: 'var(--danger)', marginTop: 12 }}>Generation failed: {error}</p>}
        <div id="report-result" style={{ marginTop: 16 }}>
          {generated && (
            <div className="result-box">
              <h4>Report Generated: {generated.title}</h4>
              <pre style={{ whiteSpace: 'pre-wrap', fontSize: 13, marginTop: 8, maxHeight: 400, overflowY: 'auto' }}>
                {JSON.stringify(generated.content, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </div>
      <div className="card">
        <div className="card-header"><h3>Previous Reports</h3></div>
        <div id="reports-list">
          {reports.length === 0 ? (
            <p style={{ color: 'var(--text-secondary)' }}>No reports generated yet.</p>
          ) : (
            <table className="data-table">
              <thead><tr><th>Title</th><th>Type</th><th>Status</th><th>Date</th></tr></thead>
              <tbody>
                {reports.map((r, i) => (
                  <tr key={i}>
                    <td>{r.title}</td>
                    <td><span className="tag tag-info">{r.type}</span></td>
                    <td>{r.status}</td>
                    <td>{r.created_at || 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </>
  );
}
