import { useEffect, useState } from 'react';
import { api } from '../api.js';
import { showToast, formatNumber, Loading, ErrorBox, Modal } from '../ui.jsx';

export default function DatasetsPage() {
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [detail, setDetail] = useState(null);

  const load = () => {
    setLoading(true);
    api.datasets.list()
      .then(res => { setDatasets(res.datasets); setLoading(false); })
      .catch(err => { setError(err.message); setLoading(false); showToast('Failed to load datasets: ' + err.message, 'error'); });
  };

  useEffect(() => { load(); }, []);

  const openDetail = async (name) => {
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
      setDetail({
        title: `Dataset: ${name}`,
        body: (
          <>
            <p><strong>Rows:</strong> {info.rows} | <strong>Columns:</strong> {info.columns} | <strong>Memory:</strong> {(info.memory_mb || 0).toFixed(1)} MB</p>
            <h4 style={{ margin: '16px 0 8px' }}>Sample Data</h4>
            <div dangerouslySetInnerHTML={{ __html: tableHtml }} />
          </>
        )
      });
    } catch (err) { showToast('Failed to load dataset details: ' + err.message, 'error'); }
  };

  const handleReload = async () => {
    try { await api.post('/datasets/reload'); showToast('Datasets reloaded', 'success'); load(); }
    catch (err) { showToast('Reload failed: ' + err.message, 'error'); }
  };

  if (loading) return <Loading />;
  if (error) return <ErrorBox msg={error} />;

  return (
    <>
      <div className="card">
        <div className="card-header">
          <h3>All Datasets ({datasets.length})</h3>
          <button className="btn btn-primary" onClick={handleReload}>Reload</button>
        </div>
        <table className="data-table">
          <thead><tr><th>Name</th><th>Rows</th><th>Columns</th><th>Size</th><th>Status</th></tr></thead>
          <tbody>
            {datasets.map(d => (
              <tr key={d.name} onClick={() => openDetail(d.name)} style={{ cursor: 'pointer' }}>
                <td><strong>{d.name}</strong></td>
                <td>{d.rows}</td>
                <td>{d.columns}</td>
                <td>{(d.memory_mb || 0).toFixed(1)} MB</td>
                <td><span className={`tag ${d.status === 'loaded' ? 'tag-success' : 'tag-danger'}`}>{d.status}</span></td>
              </tr>
            ))}
            {datasets.length === 0 && <tr><td colSpan={5} style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>No datasets loaded</td></tr>}
          </tbody>
        </table>
      </div>

      {detail && (
        <Modal title={detail.title} onClose={() => setDetail(null)}>
          {detail.body}
        </Modal>
      )}
    </>
  );
}