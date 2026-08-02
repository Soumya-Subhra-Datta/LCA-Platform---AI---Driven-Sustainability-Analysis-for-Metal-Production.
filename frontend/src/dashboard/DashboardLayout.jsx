import { useState, useEffect, useRef } from 'react';
import { NavLink, Outlet, useNavigate, useLocation } from 'react-router-dom';
import { api } from './api.js';
import { ToastContainer } from './ui.jsx';
import './dashboard.css';

const NAV_ITEMS = [
  { key: 'dashboard', label: 'Dashboard' },
  { key: 'datasets', label: 'Datasets' },
  { key: 'predictions', label: 'AI Predictions' },
  { key: 'lca', label: 'LCA Analysis' },
  { key: 'circularity', label: 'Circularity' },
  { key: 'sustainability', label: 'Sustainability' },
  { key: 'reports', label: 'Reports' },
  { key: 'settings', label: 'Settings' },
];

export default function DashboardLayout({ onLogout }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [currentPage, setCurrentPage] = useState(() => location.pathname.slice(1) || 'dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [apiStatus, setApiStatus] = useState('Connected');
  const [user, setUser] = useState(null);
  const healthCheckRef = useRef(null);

  useEffect(() => {
    const token = localStorage.getItem('lca_access_token');
    const userData = localStorage.getItem('lca_user');
    if (userData) setUser(JSON.parse(userData));
    if (!token) { navigate('/login', { replace: true }); return; }
    checkHealth();
    healthCheckRef.current = setInterval(checkHealth, 30000);

    const onUnauthorized = () => handleLogout();
    window.addEventListener('lca:unauthorized', onUnauthorized);
    return () => {
      if (healthCheckRef.current) clearInterval(healthCheckRef.current);
      window.removeEventListener('lca:unauthorized', onUnauthorized);
    };
  }, [navigate]);

  const checkHealth = async () => {
    try {
      await api.health();
      setApiStatus('Connected');
    } catch {
      setApiStatus('Disconnected');
    }
  };

  const handleNavClick = (page) => {
    setCurrentPage(page);
    navigate(`/${page}`);
    if (window.innerWidth < 768) setSidebarOpen(false);
  };

  const handleLogout = () => {
    onLogout();
    navigate('/login', { replace: true });
  };

  const isActive = (page) => currentPage === page;

  return (
    <div id="app">
      <nav className={`sidebar ${sidebarOpen ? 'open' : ''}`} id="sidebar">
        <div className="sidebar-header">
          <h2 className="logo">LCA<span>Platform</span></h2>
        </div>
        <ul className="nav-menu">
          {NAV_ITEMS.map(({ key, label }) => (
            <li key={key} className={`nav-item ${isActive(key) ? 'active' : ''}`} data-page={key}>
              <NavLink to={`/${key}`} onClick={() => handleNavClick(key)}>{label}</NavLink>
            </li>
          ))}
        </ul>
      </nav>

      <main className="main-content">
        <header className="top-bar">
          <button className="menu-toggle" onClick={() => setSidebarOpen(!sidebarOpen)}>&#9776;</button>
          <h1 id="page-title">
            {NAV_ITEMS.find(i => i.key === currentPage)?.label || 'Dashboard'}
          </h1>
          <div className="top-bar-actions">
            <span className={`status-badge ${apiStatus === 'Connected' ? '' : 'disconnected'}`} id="api-status">
              {apiStatus}
            </span>
            <span className="user-info" id="user-display">
              {user?.full_name || user?.username || 'Guest'}
            </span>
          </div>
        </header>

        <div className="content-area" id="content-area">
          <Outlet context={{ onLogout: handleLogout }} />
        </div>
      </main>

      <ToastContainer />
    </div>
  );
}