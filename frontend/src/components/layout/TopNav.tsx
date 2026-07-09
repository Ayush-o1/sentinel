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
        <h1 className={styles.pageTitle}>{pageInfo.title}</h1>
        {pageInfo.subtitle && (
          <p className={styles.pageSubtitle}>{pageInfo.subtitle}</p>
        )}
      </div>

      <div className={styles.actions}>
        {/* Status indicator */}
        <div className={styles.statusBadge}>
          <span className={styles.statusDot} />
          <span className={styles.statusText}>System Online</span>
        </div>
      </div>
    </header>
  );
}
