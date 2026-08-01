import { Routes, Route, Navigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import LoginPage from './auth/LoginPage.jsx';
import authService from './auth/authService.js';
import './auth/auth.css';

function PlaceholderHome({ onLogout }) {
  const user = authService.getUser();
  return (
    <div className="auth-page home-placeholder">
      <div className="home-card">
        <p className="home-greeting">Welcome, {user?.full_name || user?.username || 'Guest'}!</p>
        <p className="home-message">
          You are signed in. The dashboard and analysis tools will be added here next.
        </p>
        <button type="button" className="btn btn-primary" onClick={onLogout}>
          Sign Out
        </button>
      </div>
    </div>
  );
}

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(() => authService.isAuthenticated());

  const handleLogout = () => {
    authService.logout();
    setIsAuthenticated(false);
  };

  useEffect(() => {
    setIsAuthenticated(authService.isAuthenticated());
  }, []);

  return (
    <Routes>
      <Route
        path="/login"
        element={isAuthenticated ? <Navigate to="/" replace /> : <LoginPage onAuthenticated={() => setIsAuthenticated(true)} />}
      />
      <Route
        path="/"
        element={isAuthenticated ? <PlaceholderHome onLogout={handleLogout} /> : <Navigate to="/login" replace />}
      />
      <Route path="*" element={<Navigate to={isAuthenticated ? '/' : '/login'} replace />} />
    </Routes>
  );
}
