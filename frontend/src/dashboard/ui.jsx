import { useEffect, useState } from 'react';

export function formatNumber(n) {
  if (n === null || n === undefined) return 'N/A';
  if (Math.abs(n) >= 1e6) return (n / 1e6).toFixed(2) + 'M';
  if (Math.abs(n) >= 1e3) return (n / 1e3).toFixed(1) + 'K';
  return typeof n === 'number' ? n.toFixed(2) : String(n);
}

export function Loading() {
  return (
    <div style={{ textAlign: 'center', padding: '40px' }}>
      <div className="spinner" />
      <p style={{ marginTop: 12, color: 'var(--text-secondary)' }}>Loading...</p>
    </div>
  );
}

export function ErrorBox({ msg }) {
  return (
    <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
      <p style={{ color: 'var(--danger)', fontSize: 16 }}>{msg}</p>
    </div>
  );
}

export function ToastContainer() {
  const [toasts, setToasts] = useState([]);

  useEffect(() => {
    const handler = (message, type) => {
      const id = Date.now() + Math.random();
      setToasts((prev) => [...prev, { id, message, type }]);
      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
      }, 4000);
    };
    window.__lcaToast = handler;
    return () => {
      delete window.__lcaToast;
    };
  }, []);

  return (
    <div className="toast-container">
      {toasts.map((t) => (
        <div key={t.id} className={`toast toast-${t.type}`}>
          {t.message}
        </div>
      ))}
    </div>
  );
}

export function showToast(message, type = 'info') {
  if (window.__lcaToast) window.__lcaToast(message, type);
}

export function Modal({ title, onClose, children }) {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>{title}</h3>
          <button className="modal-close" onClick={onClose}>
            &times;
          </button>
        </div>
        <div className="modal-body">{children}</div>
      </div>
    </div>
  );
}
