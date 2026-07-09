/**
 * SENTINEL — Protected Layout
 *
 * Wraps all authenticated routes with:
 * - Auth guard (redirect to /login if unauthenticated)
 * - Sidebar navigation
 * - Top navigation bar
 * - Page content area
 */

import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import Sidebar from './Sidebar';
import TopNav from './TopNav';
import styles from './ProtectedLayout.module.css';

export default function ProtectedLayout() {
  const { isAuthenticated, isLoading } = useAuthStore();

  if (isLoading) return null;

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className={styles.layout}>
      <Sidebar />
      <div className={styles.main}>
        <TopNav />
        <main className={styles.content}>
          <Outlet />
        </main>
      </div>
    </div>
  );
}
