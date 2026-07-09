/**
 * SENTINEL — Dashboard Page
 */
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { analyticsService } from '../services/analyticsService';
import { predictionService } from '../services/predictionService';
import styles from './DashboardPage.module.css';

/* ── SVG metric icons ──────────────────────────────────────────── */
const IconTotal = () => (
  <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24" aria-hidden="true">
    <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
  </svg>
);
const IconSpam = () => (
  <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24" aria-hidden="true">
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
    <path d="M12 8v4m0 4h.01"/>
  </svg>
);
const IconConfidence = () => (
  <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24" aria-hidden="true">
    <circle cx="12" cy="12" r="10"/>
    <path d="M12 6v6l4 2"/>
  </svg>
);
const IconToday = () => (
  <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24" aria-hidden="true">
    <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
  </svg>
);

const METRIC_CONFIG = [
  { key: 'total',      Icon: IconTotal,      label: 'Total Predictions', accent: 'cyan'    },
  { key: 'spam',       Icon: IconSpam,       label: 'Spam Rate',         accent: 'danger'  },
  { key: 'confidence', Icon: IconConfidence, label: 'Avg Confidence',    accent: 'purple'  },
  { key: 'today',      Icon: IconToday,      label: "Today's Volume",    accent: 'success' },
];

/* ── Skeleton Card ─────────────────────────────────────────────── */
function SkeletonMetricCard() {
  return (
    <div className={styles.metricCard} aria-hidden="true">
      <div className={styles.metricHeader}>
        <div className={`${styles.skeletonText} skeleton`} style={{ width: '60%', height: '14px' }} />
        <div className={`skeleton`} style={{ width: '32px', height: '32px', borderRadius: '8px' }} />
      </div>
      <div className={`skeleton`} style={{ width: '50%', height: '36px', marginTop: '8px' }} />
    </div>
  );
}

function SkeletonRecentItem() {
  return (
    <div className={styles.recentItem} aria-hidden="true">
      <div className={styles.recentItemMain}>
        <div className={styles.recentItemHeader}>
          <div className={`skeleton`} style={{ width: '52px', height: '20px', borderRadius: '9999px' }} />
          <div className={`skeleton`} style={{ width: '72px', height: '14px' }} />
        </div>
        <div className={`skeleton`} style={{ width: '85%', height: '14px', marginTop: '6px' }} />
      </div>
      <div className={styles.recentItemMeta} style={{ gap: '6px' }}>
        <div className={`skeleton`} style={{ width: '40px', height: '18px' }} />
        <div className={`skeleton`} style={{ width: '64px', height: '12px' }} />
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const {
    data: summary,
    isLoading: loadingSummary,
    isError: errorSummary,
    refetch: refetchSummary,
  } = useQuery({
    queryKey: ['analytics-summary'],
    queryFn: analyticsService.getSummary,
  });

  const { data: historyData, isLoading: loadingHistory } = useQuery({
    queryKey: ['predictions-recent'],
    queryFn: () => predictionService.getHistory({ page: 1, page_size: 5 }),
  });

  const formatPercentage = (val: number) => `${(val * 100).toFixed(1)}%`;
  const formatDate = (iso: string) => {
    const d = new Date(iso);
    const now = Date.now();
    const diff = now - d.getTime();
    if (diff < 60_000)       return 'Just now';
    if (diff < 3_600_000)    return `${Math.floor(diff / 60_000)}m ago`;
    if (diff < 86_400_000)   return `${Math.floor(diff / 3_600_000)}h ago`;
    return d.toLocaleDateString();
  };

  /* ── Error State ──────────────────────────────────────────────── */
  if (errorSummary) {
    return (
      <div className={styles.errorState}>
        <svg width="40" height="40" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24" aria-hidden="true">
          <circle cx="12" cy="12" r="10"/>
          <path d="M12 8v4m0 4h.01"/>
        </svg>
        <p className={styles.errorTitle}>Failed to load dashboard</p>
        <p className={styles.errorDesc}>Could not reach the analytics service. Check your connection.</p>
        <button className={styles.retryBtn} onClick={() => refetchSummary()}>
          Retry
        </button>
      </div>
    );
  }

  const metricValues = summary
    ? [
        summary.total_predictions.toLocaleString(),
        formatPercentage(summary.spam_rate),
        formatPercentage(summary.avg_confidence),
        summary.predictions_today.toLocaleString(),
      ]
    : ['—', '—', '—', '—'];

  return (
    <div className={styles.container}>
      {/* Metrics Row */}
      <div className={styles.metricsGrid} role="list" aria-label="Key metrics">
        {loadingSummary
          ? METRIC_CONFIG.map((m) => <SkeletonMetricCard key={m.key} />)
          : METRIC_CONFIG.map((m, i) => (
              <div
                key={m.key}
                className={`${styles.metricCard} ${styles[`metricCard_${m.accent}`]}`}
                role="listitem"
              >
                <div className={styles.metricHeader}>
                  <span className={styles.metricTitle}>{m.label}</span>
                  <span className={`${styles.metricIconWrapper} ${styles[`metricIcon_${m.accent}`]}`}>
                    <m.Icon />
                  </span>
                </div>
                <div className={styles.metricValue}>{metricValues[i]}</div>
              </div>
            ))}
      </div>

      <div className={styles.mainGrid}>
        {/* Recent Activity */}
        <div className={styles.recentSection}>
          <div className={styles.sectionHeader}>
            <h2 className={styles.sectionTitle}>Recent Activity</h2>
            <Link to="/history" className={styles.linkViewAll}>View All →</Link>
          </div>
          <div className={styles.recentList} role="list" aria-label="Recent predictions">
            {loadingHistory ? (
              <>
                <SkeletonRecentItem />
                <SkeletonRecentItem />
                <SkeletonRecentItem />
              </>
            ) : !historyData?.items.length ? (
              <div className={styles.emptyState}>
                <svg width="36" height="36" fill="none" stroke="currentColor" strokeWidth="1.2" viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                </svg>
                <p>No predictions yet.</p>
                <Link to="/analyze" className={styles.emptyStateCta}>Analyze your first message →</Link>
              </div>
            ) : (
              historyData.items.map((item) => (
                <div key={item.id} className={styles.recentItem} role="listitem">
                  <div className={styles.recentItemMain}>
                    <div className={styles.recentItemHeader}>
                      <span
                        className={`${styles.verdictBadge} ${item.verdict === 'SPAM' ? styles.badgeSpam : styles.badgeHam}`}
                        aria-label={`Verdict: ${item.verdict}`}
                      >
                        {item.verdict}
                      </span>
                      <span className={styles.confidenceText}>
                        {formatPercentage(item.confidence)} conf.
                      </span>
                    </div>
                    <div className={styles.recentItemText}>
                      {item.text_preview || <span className={styles.noPreview}>No text content available</span>}
                    </div>
                  </div>
                  <div className={styles.recentItemMeta}>
                    <span className={styles.messageType}>{item.message_type.toUpperCase()}</span>
                    <time
                      className={styles.timeAgo}
                      dateTime={item.created_at}
                      title={new Date(item.created_at).toLocaleString()}
                    >
                      {formatDate(item.created_at)}
                    </time>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Side Panel */}
        <div className={styles.sidePanel}>
          {/* Quick Actions */}
          <div className={styles.quickActions}>
            <h2 className={styles.sectionTitle}>Quick Actions</h2>
            <div className={styles.actionButtons}>
              <Link to="/analyze" className={styles.btnPrimary}>
                <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" aria-hidden="true">
                  <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/><path d="M11 8v6M8 11h6"/>
                </svg>
                Analyze New Message
              </Link>
              <Link to="/analytics" className={styles.btnSecondary}>
                <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M3 3v18h18"/><path d="m7 16 4-4 4 4 4-4"/>
                </svg>
                View Full Analytics
              </Link>
            </div>
          </div>

          {/* Top Spam Tokens */}
          <div className={styles.topTokens}>
            <h2 className={styles.sectionTitle}>Top Spam Tokens</h2>
            <div className={styles.tokenList}>
              {loadingSummary ? (
                <>
                  {[1,2,3,4,5].map(i => (
                    <div key={i} className={styles.tokenItem} aria-hidden="true">
                      <div className={`skeleton`} style={{ width: '24px', height: '16px' }} />
                      <div className={`skeleton`} style={{ flex: 1, height: '16px' }} />
                    </div>
                  ))}
                </>
              ) : summary!.most_common_spam_tokens.length > 0 ? (
                summary!.most_common_spam_tokens.map((token, idx) => (
                  <div key={idx} className={styles.tokenItem}>
                    <span className={styles.tokenRank}>#{idx + 1}</span>
                    <span className={styles.tokenName}>{token}</span>
                  </div>
                ))
              ) : (
                <div className={styles.emptyStateSmall}>Not enough data yet.</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
