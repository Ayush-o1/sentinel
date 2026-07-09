/**
 * SENTINEL — Root Application Component
 *
 * Configures React Router, protected route infrastructure,
 * and initial session restoration (via refresh token cookie).
 */

import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import { authService } from './services/authService';
import { setAccessToken } from './services/api';

// Layouts
import ProtectedLayout from './components/layout/ProtectedLayout';

// Public Pages
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';

// Protected Pages
import DashboardPage from './pages/DashboardPage';
import AnalyzePage from './pages/AnalyzePage';
import HistoryPage from './pages/HistoryPage';
import AnalyticsPage from './pages/AnalyticsPage';
import NotFoundPage from './pages/NotFoundPage';

export default function App() {
  const { setUser, setLoading, isAuthenticated, isLoading } = useAuthStore();

  /**
   * Session Restoration
   *
   * On app load, attempt to get a new access token via the refresh
   * token cookie. If successful, load the user profile.
   * This provides a seamless "stay logged in" experience across
   * page refreshes without storing the access token in localStorage.
   */
  useEffect(() => {
    const restoreSession = async () => {
      try {
        await authService.refresh();
        const user = await authService.getMe();
        setUser(user);
      } catch {
        // No valid refresh token — user needs to log in
        setAccessToken(null);
        setUser(null);
      }
    };

    restoreSession();
  }, [setUser, setLoading]);

  // Show a minimal loading screen while restoring session
  if (isLoading) {
    return (
      <div className="sentinel-boot-screen">
        <div className="sentinel-boot-logo">SENTINEL</div>
        <div className="sentinel-boot-spinner" />
      </div>
    );
  }

  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route
          path="/"
          element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <LandingPage />}
        />
        <Route
          path="/login"
          element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <LoginPage />}
        />
        <Route
          path="/register"
          element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <RegisterPage />}
        />

        {/* Protected Routes — wrapped in ProtectedLayout (sidebar + topnav) */}
        <Route element={<ProtectedLayout />}>
          <Route path="/dashboard"  element={<DashboardPage />} />
          <Route path="/analyze"    element={<AnalyzePage />} />
          <Route path="/history"    element={<HistoryPage />} />
          <Route path="/analytics"  element={<AnalyticsPage />} />
        </Route>

        {/* 404 */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
}
