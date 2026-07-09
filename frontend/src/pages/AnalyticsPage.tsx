/**
 * SENTINEL — Analytics Page
 */
import { useState, memo } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar
} from 'recharts';
import { analyticsService } from '../services/analyticsService';
import styles from './AnalyticsPage.module.css';

/* Chart theme colors matching CSS design tokens */
const COLORS = {
  spam:         '#ff3366',
  ham:          '#00ff88',
  total:        '#3b82f6',
  grid:         '#1e3a5f',
  text:         '#94a3b8',
  tooltipBg:    '#0f1629',
  tooltipBorder:'#1e3a5f',
};

/* ── Extracted tooltip components (outside parent to avoid re-creation) ── */
const TimelineTooltip = memo(({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className={styles.chartTooltip}>
      <p className={styles.tooltipLabel}>{label}</p>
      {payload.map((entry: any, index: number) => (
        <div key={index} className={styles.tooltipItem} style={{ color: entry.color }}>
          <span>{entry.name}:</span>
          <span>{entry.value}</span>
        </div>
      ))}
    </div>
  );
});
TimelineTooltip.displayName = 'TimelineTooltip';

/* ── Skeleton card for charts ──────────────────────────────────── */
function ChartSkeleton() {
  return (
    <div className={styles.chartSkeletonWrapper} aria-hidden="true">
      <div className={styles.chartSkeletonBars}>
        {[60, 85, 45, 70, 90, 55, 75, 65, 80, 50].map((h, i) => (
          <div
            key={i}
            className={`skeleton ${styles.chartSkeletonBar}`}
            style={{ height: `${h}%` }}
          />
        ))}
      </div>
    </div>
  );
}

export default function AnalyticsPage() {
  const [period, setPeriod] = useState<'7d' | '30d' | '90d'>('30d');

  const { data: timelineData, isLoading: loadingTimeline } = useQuery({
    queryKey: ['analytics-timeline', period],
    queryFn: () => analyticsService.getTimeline(period),
  });

  const { data: distData, isLoading: loadingDist } = useQuery({
    queryKey: ['analytics-confidence-dist'],
    queryFn: analyticsService.getConfidenceDistribution,
  });

  const { data: modelInfo, isLoading: loadingModel } = useQuery({
    queryKey: ['model-info'],
    queryFn: analyticsService.getModelInfo,
  });

  return (
    <div className={styles.container}>
      {/* Period selector */}
      <div className={styles.header}>
        <div
          className={styles.periodSelector}
          role="group"
          aria-label="Select time period"
        >
          {(['7d', '30d', '90d'] as const).map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`${styles.periodBtn} ${period === p ? styles.periodActive : ''}`}
              aria-pressed={period === p}
              aria-label={`Show ${p === '7d' ? '7 days' : p === '30d' ? '30 days' : '90 days'}`}
            >
              {p.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      <div className={styles.gridTop}>
        {/* Timeline Chart */}
        <div className={styles.chartCard}>
          <div className={styles.chartHeader}>
            <h2 className={styles.cardTitle}>Prediction Volume over Time</h2>
            <div className={styles.chartLegend} aria-hidden="true">
              <span className={styles.legendItem}>
                <span className={styles.legendDot} style={{ background: COLORS.spam }} />
                Spam
              </span>
              <span className={styles.legendItem}>
                <span className={styles.legendDot} style={{ background: COLORS.ham }} />
                Ham
              </span>
            </div>
          </div>
          <div className={styles.chartWrapper}>
            {loadingTimeline ? (
              <ChartSkeleton />
            ) : !timelineData?.data.length ? (
              <div className={styles.emptyState}>
                <svg width="32" height="32" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M3 3v18h18"/><path d="m7 16 4-4 4 4 4-4"/>
                </svg>
                No data available for this period.
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={timelineData.data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorSpam" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%"  stopColor={COLORS.spam} stopOpacity={0.35}/>
                      <stop offset="95%" stopColor={COLORS.spam} stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="colorHam" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%"  stopColor={COLORS.ham} stopOpacity={0.35}/>
                      <stop offset="95%" stopColor={COLORS.ham} stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke={COLORS.grid} vertical={false} />
                  <XAxis dataKey="date"  stroke={COLORS.text} fontSize={11} tickLine={false} axisLine={false} />
                  <YAxis               stroke={COLORS.text} fontSize={11} tickLine={false} axisLine={false} />
                  <Tooltip content={<TimelineTooltip />} />
                  <Area type="monotone" dataKey="spam" name="Spam" stroke={COLORS.spam} strokeWidth={2} fillOpacity={1} fill="url(#colorSpam)" />
                  <Area type="monotone" dataKey="ham"  name="Ham"  stroke={COLORS.ham}  strokeWidth={2} fillOpacity={1} fill="url(#colorHam)" />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Model Health */}
        <div className={styles.infoCard}>
          <h2 className={styles.cardTitle}>Model Health</h2>
          {loadingModel ? (
            <div className={styles.infoList}>
              {[1,2,3,4,5,6].map(i => (
                <div key={i} className={styles.infoItem} aria-hidden="true">
                  <div className={`skeleton`} style={{ width: '40%', height: '14px' }} />
                  <div className={`skeleton`} style={{ width: '30%', height: '14px' }} />
                </div>
              ))}
            </div>
          ) : modelInfo ? (
            <div className={styles.infoList}>
              <div className={styles.infoItem}>
                <span className={styles.infoLabel}>Status</span>
                <span className={`${styles.infoValue} ${modelInfo.status === 'ACTIVE' ? styles.statusActive : styles.statusError}`}>
                  <span className={styles.statusPulse} aria-hidden="true" />
                  {modelInfo.status}
                </span>
              </div>
              <div className={styles.infoItem}>
                <span className={styles.infoLabel}>Version</span>
                <span className={styles.infoValueMono}>{modelInfo.version}</span>
              </div>
              <div className={styles.infoItem}>
                <span className={styles.infoLabel}>Accuracy</span>
                <span className={styles.infoValue}>{(modelInfo.accuracy * 100).toFixed(2)}%</span>
              </div>
              <div className={styles.infoItem}>
                <span className={styles.infoLabel}>Precision (Spam)</span>
                <span className={styles.infoValue}>{(modelInfo.precision_spam * 100).toFixed(2)}%</span>
              </div>
              <div className={styles.infoItem}>
                <span className={styles.infoLabel}>Recall (Spam)</span>
                <span className={styles.infoValue}>{(modelInfo.recall_spam * 100).toFixed(2)}%</span>
              </div>
              <div className={styles.infoItem}>
                <span className={styles.infoLabel}>Training Samples</span>
                <span className={styles.infoValue}>{modelInfo.training_samples.toLocaleString()}</span>
              </div>
            </div>
          ) : (
            <div className={styles.emptyState}>Model info unavailable.</div>
          )}
        </div>
      </div>

      {/* Confidence Distribution */}
      <div className={styles.gridBottom}>
        <div className={styles.chartCard}>
          <div className={styles.chartHeader}>
            <h2 className={styles.cardTitle}>Confidence Distribution</h2>
          </div>
          <div className={styles.chartWrapper}>
            {loadingDist ? (
              <ChartSkeleton />
            ) : !distData?.buckets.length ? (
              <div className={styles.emptyState}>
                <svg width="32" height="32" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M3 3v18h18"/><path d="M7 12l4-4 4 4 4-4"/>
                </svg>
                Not enough data to calculate distribution.
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={distData.buckets} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={COLORS.grid} vertical={false} />
                  <XAxis dataKey="range" stroke={COLORS.text} fontSize={11} tickLine={false} axisLine={false} />
                  <YAxis stroke={COLORS.text} fontSize={11} tickLine={false} axisLine={false} allowDecimals={false} />
                  <Tooltip
                    cursor={{ fill: 'rgba(0,212,255,0.05)' }}
                    contentStyle={{
                      backgroundColor: COLORS.tooltipBg,
                      borderColor: COLORS.tooltipBorder,
                      borderRadius: '8px',
                      fontSize: '13px',
                    }}
                    itemStyle={{ color: COLORS.total }}
                  />
                  <Bar dataKey="count" name="Predictions" fill={COLORS.total} radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
