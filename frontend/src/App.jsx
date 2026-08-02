import { Routes, Route, Navigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import LoginPage from './auth/LoginPage.jsx';
import DashboardLayout from './dashboard/DashboardLayout.jsx';
import DashboardPage from './dashboard/pages/DashboardPage.jsx';
import DatasetsPage from './dashboard/pages/DatasetsPage.jsx';
import PredictionsPage from './dashboard/pages/PredictionsPage.jsx';
import LCAPage from './dashboard/pages/LCAPage.jsx';
import CircularityPage from './dashboard/pages/CircularityPage.jsx';
import SustainabilityPage from './dashboard/pages/SustainabilityPage.jsx';
import ReportsPage from './dashboard/pages/ReportsPage.jsx';
import SettingsPage from './dashboard/pages/SettingsPage.jsx';
import authService from './auth/authService.js';
import './auth/auth.css';
import './dashboard/dashboard.css';

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
        element={
          isAuthenticated ? <Navigate to="/" replace /> : <LoginPage onAuthenticated={() => setIsAuthenticated(true)} />
        }
      />
      <Route element={isAuthenticated ? <DashboardLayout onLogout={handleLogout} /> : <Navigate to="/login" replace />}>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/datasets" element={<DatasetsPage />} />
        <Route path="/predictions" element={<PredictionsPage />} />
        <Route path="/lca" element={<LCAPage />} />
        <Route path="/circularity" element={<CircularityPage />} />
        <Route path="/sustainability" element={<SustainabilityPage />} />
        <Route path="/reports" element={<ReportsPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Route>
    </Routes>
  );
}
