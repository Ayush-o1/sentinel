/**
 * SENTINEL — Analytics Page
 */
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar
} from 'recharts';
import { analyticsService } from '../services/analyticsService';
import styles from './AnalyticsPage.module.css';

// Chart Theme Colors matching CSS variables
const COLORS = {
  spam: '#ff3366', // accent-danger
  ham: '#00ff88',  // accent-success
  total: '#3b82f6', // accent-info
  grid: '#1e3a5f', // border
  text: '#94a3b8', // text-secondary
  tooltipBg: '#0f1629', // bg-secondary
  tooltipBorder: '#112240', // border-subtle
};

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

  // Custom Tooltip for Timeline
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
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
    }
    return null;
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2 className={styles.title}>Threat Analytics</h2>
        
        {/* Timeline Period Selector */}
        <div className={styles.periodSelector}>
          {(['7d', '30d', '90d'] as const).map(p => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`${styles.periodBtn} ${period === p ? styles.periodActive : ''}`}
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
            <h3 className={styles.cardTitle}>Prediction Volume over Time</h3>
          </div>
          <div className={styles.chartWrapper}>
            {loadingTimeline ? (
              <div className={styles.loadingState}>Loading timeline data...</div>
            ) : timelineData?.data.length === 0 ? (
              <div className={styles.emptyState}>No data available for this period.</div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={timelineData?.data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorSpam" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={COLORS.spam} stopOpacity={0.3}/>
                      <stop offset="95%" stopColor={COLORS.spam} stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="colorHam" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={COLORS.ham} stopOpacity={0.3}/>
                      <stop offset="95%" stopColor={COLORS.ham} stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke={COLORS.grid} vertical={false} />
                  <XAxis dataKey="date" stroke={COLORS.text} fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke={COLORS.text} fontSize={12} tickLine={false} axisLine={false} />
                  <Tooltip content={<CustomTooltip />} />
                  <Area type="monotone" dataKey="spam" name="Spam" stroke={COLORS.spam} fillOpacity={1} fill="url(#colorSpam)" />
                  <Area type="monotone" dataKey="ham" name="Ham" stroke={COLORS.ham} fillOpacity={1} fill="url(#colorHam)" />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Model Health Info */}
        <div className={styles.infoCard}>
          <h3 className={styles.cardTitle}>Model Health</h3>
          {loadingModel ? (
            <div className={styles.loadingState}>Loading model info...</div>
          ) : modelInfo ? (
            <div className={styles.infoList}>
              <div className={styles.infoItem}>
                <span className={styles.infoLabel}>Status</span>
                <span className={`${styles.infoValue} ${modelInfo.status === 'ACTIVE' ? styles.statusActive : styles.statusError}`}>
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

      <div className={styles.gridBottom}>
        {/* Confidence Distribution */}
        <div className={styles.chartCard}>
          <div className={styles.chartHeader}>
            <h3 className={styles.cardTitle}>Confidence Distribution</h3>
          </div>
          <div className={styles.chartWrapper}>
             {loadingDist ? (
              <div className={styles.loadingState}>Loading distribution data...</div>
            ) : distData?.buckets.length === 0 ? (
              <div className={styles.emptyState}>Not enough data to calculate distribution.</div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={distData?.buckets} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={COLORS.grid} vertical={false} />
                  <XAxis dataKey="range" stroke={COLORS.text} fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke={COLORS.text} fontSize={12} tickLine={false} axisLine={false} allowDecimals={false} />
                  <Tooltip
                    cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                    contentStyle={{ backgroundColor: COLORS.tooltipBg, borderColor: COLORS.tooltipBorder, borderRadius: '8px' }}
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
