/**
 * SENTINEL — Dashboard Page
 */
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { analyticsService } from '../services/analyticsService';
import { predictionService } from '../services/predictionService';
import styles from './DashboardPage.module.css';

export default function DashboardPage() {
  const { data: summary, isLoading: loadingSummary, isError: errorSummary } = useQuery({
    queryKey: ['analytics-summary'],
    queryFn: analyticsService.getSummary,
  });

  const { data: historyData, isLoading: loadingHistory } = useQuery({
    queryKey: ['predictions-recent'],
    queryFn: () => predictionService.getHistory({ page: 1, page_size: 5 }),
  });

  const formatPercentage = (val: number) => `${(val * 100).toFixed(1)}%`;
  const formatConfidence = (val: number) => `${(val * 100).toFixed(1)}%`;

  if (loadingSummary) {
    return <div className={styles.loading}>Loading dashboard data...</div>;
  }

  if (errorSummary || !summary) {
    return <div className={styles.error}>Failed to load dashboard data.</div>;
  }

  return (
    <div className={styles.container}>
      {/* Metrics Row */}
      <div className={styles.metricsGrid}>
        <div className={styles.metricCard}>
          <div className={styles.metricHeader}>
            <span className={styles.metricTitle}>Total Predictions</span>
            <span className={styles.metricIcon}>📊</span>
          </div>
          <div className={styles.metricValue}>{summary.total_predictions.toLocaleString()}</div>
        </div>
        <div className={styles.metricCard}>
          <div className={styles.metricHeader}>
            <span className={styles.metricTitle}>Spam Rate</span>
            <span className={styles.metricIcon}>🛡️</span>
          </div>
          <div className={styles.metricValue}>{formatPercentage(summary.spam_rate)}</div>
        </div>
        <div className={styles.metricCard}>
          <div className={styles.metricHeader}>
            <span className={styles.metricTitle}>Avg Confidence</span>
            <span className={styles.metricIcon}>🎯</span>
          </div>
          <div className={styles.metricValue}>{formatConfidence(summary.avg_confidence)}</div>
        </div>
        <div className={styles.metricCard}>
          <div className={styles.metricHeader}>
            <span className={styles.metricTitle}>Today's Volume</span>
            <span className={styles.metricIcon}>⚡</span>
          </div>
          <div className={styles.metricValue}>{summary.predictions_today.toLocaleString()}</div>
        </div>
      </div>

      <div className={styles.mainGrid}>
        {/* Recent Activity */}
        <div className={styles.recentSection}>
          <div className={styles.sectionHeader}>
            <h2 className={styles.sectionTitle}>Recent Activity</h2>
            <Link to="/history" className={styles.linkViewAll}>View All</Link>
          </div>
          <div className={styles.recentList}>
            {loadingHistory ? (
              <div className={styles.loadingSmall}>Loading recent activity...</div>
            ) : historyData?.items.length === 0 ? (
              <div className={styles.emptyState}>No predictions yet.</div>
            ) : (
              historyData?.items.map((item) => (
                <div key={item.id} className={styles.recentItem}>
                  <div className={styles.recentItemMain}>
                    <div className={styles.recentItemHeader}>
                      <span className={`${styles.verdictBadge} ${item.verdict === 'SPAM' ? styles.badgeSpam : styles.badgeHam}`}>
                        {item.verdict}
                      </span>
                      <span className={styles.confidenceText}>
                        {formatConfidence(item.confidence)} conf.
                      </span>
                    </div>
                    <div className={styles.recentItemText}>
                      {item.text_preview || 'No text content available'}
                    </div>
                  </div>
                  <div className={styles.recentItemMeta}>
                    <span className={styles.messageType}>{item.message_type.toUpperCase()}</span>
                    <span className={styles.timeAgo}>
                      {new Date(item.created_at).toLocaleDateString()}
                    </span>
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
                Analyze New Message
              </Link>
              <Link to="/analytics" className={styles.btnSecondary}>
                View Full Analytics
              </Link>
            </div>
          </div>

          {/* Top Spam Tokens */}
          <div className={styles.topTokens}>
            <h2 className={styles.sectionTitle}>Top Spam Tokens</h2>
            <div className={styles.tokenList}>
              {summary.most_common_spam_tokens.length > 0 ? (
                summary.most_common_spam_tokens.map((token, idx) => (
                  <div key={idx} className={styles.tokenItem}>
                    <span className={styles.tokenRank}>#{idx + 1}</span>
                    <span className={styles.tokenName}>{token}</span>
                  </div>
                ))
              ) : (
                <div className={styles.emptyState}>Not enough data yet.</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
