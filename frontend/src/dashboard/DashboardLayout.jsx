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
  { key: 'about', label: 'About' },
  { key: 'settings', label: 'Settings' },
];

export default function DashboardLayout({ onLogout }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [currentPage, setCurrentPage] = useState(() => location.pathname.slice(1) || 'dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [apiStatus, setApiStatus] = useState('Connected');
  const [user, setUser] = useState(null);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const healthCheckRef = useRef(null);
  const userMenuRef = useRef(null);

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

  useEffect(() => {
    if (!userMenuOpen) return undefined;
    const onClick = (e) => {
      if (userMenuRef.current && !userMenuRef.current.contains(e.target)) setUserMenuOpen(false);
    };
    const onKey = (e) => {
      if (e.key === 'Escape') setUserMenuOpen(false);
    };
    document.addEventListener('mousedown', onClick);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('mousedown', onClick);
      document.removeEventListener('keydown', onKey);
    };
  }, [userMenuOpen]);

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
          <button
            type="button"
            className="logo-link"
            onClick={() => handleNavClick('dashboard')}
            aria-label="Go to Dashboard"
          >
            <h2 className="logo">LCA<span>Platform</span></h2>
          </button>
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
            <div className="user-menu" ref={userMenuRef}>
              <button
                type="button"
                className="user-info"
                id="user-display"
                onClick={() => setUserMenuOpen((o) => !o)}
                aria-haspopup="menu"
                aria-expanded={userMenuOpen}
              >
                {user?.full_name || user?.username || 'Guest'}
                <span className="user-caret">&#9662;</span>
              </button>
              {userMenuOpen && (
                <div className="user-dropdown" role="menu">
                  <button
                    type="button"
                    role="menuitem"
                    onClick={() => { setUserMenuOpen(false); handleNavClick('settings'); }}
                  >
                    Profile
                  </button>
                  <button type="button" role="menuitem" onClick={handleLogout}>
                    Log Out
                  </button>
                </div>
              )}
            </div>
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