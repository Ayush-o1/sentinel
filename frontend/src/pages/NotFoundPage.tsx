/**
 * SENTINEL — 404 Not Found Page
 */
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import styles from './NotFoundPage.module.css';

export default function NotFoundPage() {
  return (
    <div className={styles.page}>
      {/* Background grid */}
      <div className={styles.bgGrid} role="presentation" aria-hidden="true" />

      {/* Scan line effect */}
      <div className={styles.scanLine} aria-hidden="true" />

      <motion.div
        className={styles.content}
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
      >
        {/* Error code */}
        <div className={styles.codeWrapper} aria-hidden="true">
          <span className={styles.code}>4</span>
          <div className={styles.codeIconWrapper}>
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" className={styles.shieldIcon}>
              <path
                d="M12 2L3 7v5c0 5.25 3.75 10.15 9 11.35C17.25 22.15 21 17.25 21 12V7L12 2z"
                fill="url(#nf404Grad)"
              />
              <path
                d="M9 12l2 2 4-4"
                stroke="rgba(0,0,0,0.4)"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <line x1="8" y1="8" x2="16" y2="16" stroke="rgba(255,51,102,0.8)" strokeWidth="1.5" strokeLinecap="round"/>
              <line x1="16" y1="8" x2="8"  y2="16" stroke="rgba(255,51,102,0.8)" strokeWidth="1.5" strokeLinecap="round"/>
              <defs>
                <linearGradient id="nf404Grad" x1="3" y1="2" x2="21" y2="23">
                  <stop stopColor="#1e3a5f"/>
                  <stop offset="1" stopColor="#162040"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
          <span className={styles.code}>4</span>
        </div>

        {/* Status line */}
        <div className={styles.statusLine} aria-hidden="true">
          <span className={styles.statusTag}>STATUS</span>
          <span className={styles.statusCode}>NOT_FOUND</span>
        </div>

        {/* Message */}
        <h1 className={styles.title}>Page Not Found</h1>
        <p className={styles.description}>
          The resource you requested does not exist or has been moved.
          Return to the dashboard to resume threat analysis.
        </p>

        {/* Actions */}
        <div className={styles.actions}>
          <Link to="/dashboard" className={styles.btnPrimary}>
            <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" aria-hidden="true">
              <rect x="3" y="3" width="7" height="7" rx="1"/>
              <rect x="14" y="3" width="7" height="7" rx="1"/>
              <rect x="3" y="14" width="7" height="7" rx="1"/>
              <rect x="14" y="14" width="7" height="7" rx="1"/>
            </svg>
            Return to Dashboard
          </Link>
          <Link to="/analyze" className={styles.btnGhost}>
            Analyze a Message
          </Link>
        </div>

        {/* Terminal-style error detail */}
        <div className={styles.terminal} aria-hidden="true">
          <span className={styles.terminalPrompt}>sentinel@system:~$</span>
          <span className={styles.terminalCmd}> GET {window.location.pathname}</span>
          <br />
          <span className={styles.terminalError}>→ 404 Not Found — No route matched</span>
        </div>
      </motion.div>
    </div>
  );
}
