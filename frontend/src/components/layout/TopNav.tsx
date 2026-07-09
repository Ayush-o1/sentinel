/**
 * SENTINEL — Top Navigation Bar
 */

import { useLocation } from 'react-router-dom';
import styles from './TopNav.module.css';

const PAGE_TITLES: Record<string, { title: string; subtitle: string }> = {
  '/dashboard':  { title: 'Overview', subtitle: 'Threat intelligence summary' },
  '/analyze':    { title: 'Analyze', subtitle: 'Submit a message for analysis' },
  '/history':    { title: 'History', subtitle: 'Past prediction records' },
  '/analytics':  { title: 'Analytics', subtitle: 'Aggregate statistics & charts' },
};

export default function TopNav() {
  const { pathname } = useLocation();
  const pageInfo = PAGE_TITLES[pathname] ?? { title: 'SENTINEL', subtitle: '' };

  return (
    <header className={styles.topnav}>
      <div className={styles.pageInfo}>
        <h1 className={styles.pageTitle} aria-live="polite" aria-atomic="true">
          {pageInfo.title}
        </h1>
        {pageInfo.subtitle && (
          <p className={styles.pageSubtitle}>{pageInfo.subtitle}</p>
        )}
      </div>

      <div className={styles.actions}>
        {/* System status indicator */}
        <div
          className={styles.statusBadge}
          role="status"
          aria-label="System status: online"
        >
          <span className={styles.statusDot} aria-hidden="true" />
          <span className={styles.statusText}>System Online</span>
        </div>
      </div>
    </header>
  );
}
