/**
 * SENTINEL — History Page
 */
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { predictionService } from '../services/predictionService';
import type { PredictionSummary } from '../types';
import styles from './HistoryPage.module.css';

function formatRelativeDate(iso: string) {
  const d    = new Date(iso);
  const diff = Date.now() - d.getTime();
  if (diff < 60_000)     return 'just now';
  if (diff < 3_600_000)  return `${Math.floor(diff / 60_000)}m ago`;
  if (diff < 86_400_000) return `${Math.floor(diff / 3_600_000)}h ago`;
  if (diff < 604_800_000)return `${Math.floor(diff / 86_400_000)}d ago`;
  return d.toLocaleDateString();
}

function SkeletonRow() {
  return (
    <tr aria-hidden="true" className={styles.skeletonRow}>
      {[180, 60, 260, 60, 60, 36].map((w, i) => (
        <td key={i}><div className={`skeleton ${styles.skeletonCell}`} style={{ width: w }} /></td>
      ))}
    </tr>
  );
}

export default function HistoryPage() {
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [verdictFilter, setVerdictFilter] = useState('');
  const [typeFilter, setTypeFilter]   = useState('');
  const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null);
  const pageSize = 10;

  const { data, isLoading, isError } = useQuery({
    queryKey: ['predictions-history', page, verdictFilter, typeFilter],
    queryFn: () => predictionService.getHistory({
      page,
      page_size: pageSize,
      verdict:      verdictFilter || undefined,
      message_type: typeFilter    || undefined,
    }),
    placeholderData: (prev) => prev,
  });

  const deleteMutation = useMutation({
    mutationFn: predictionService.delete,
    onSuccess: () => {
      setConfirmDeleteId(null);
      queryClient.invalidateQueries({ queryKey: ['predictions-history'] });
      queryClient.invalidateQueries({ queryKey: ['analytics-summary'] });
    },
  });

  const handleFilterChange = (field: 'verdict' | 'type', value: string) => {
    if (field === 'verdict') setVerdictFilter(value);
    else setTypeFilter(value);
    setPage(1);
  };

  return (
    <div className={styles.container}>
      {/* Filters */}
      <div className={styles.filterRow}>
        <div className={styles.filters}>
          <div className={styles.selectWrapper}>
            <select
              value={verdictFilter}
              onChange={(e) => handleFilterChange('verdict', e.target.value)}
              className={styles.select}
              aria-label="Filter by verdict"
            >
              <option value="">All Verdicts</option>
              <option value="SPAM">Spam</option>
              <option value="HAM">Ham</option>
            </select>
            <svg className={styles.selectArrow} width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden="true">
              <polyline points="6 9 12 15 18 9"/>
            </svg>
          </div>

          <div className={styles.selectWrapper}>
            <select
              value={typeFilter}
              onChange={(e) => handleFilterChange('type', e.target.value)}
              className={styles.select}
              aria-label="Filter by message type"
            >
              <option value="">All Types</option>
              <option value="sms">SMS</option>
              <option value="email">Email</option>
              <option value="text">Text</option>
            </select>
            <svg className={styles.selectArrow} width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden="true">
              <polyline points="6 9 12 15 18 9"/>
            </svg>
          </div>
        </div>

        {data && (
          <span className={styles.recordCount} aria-live="polite">
            {data.total.toLocaleString()} record{data.total !== 1 ? 's' : ''}
          </span>
        )}
      </div>

      {/* Table */}
      <div className={styles.tableContainer}>
        <table className={styles.table} aria-label="Prediction history">
          <thead>
            <tr>
              <th scope="col">Date</th>
              <th scope="col">Type</th>
              <th scope="col">Message Preview</th>
              <th scope="col">Verdict</th>
              <th scope="col">Confidence</th>
              <th scope="col" className={styles.colActions}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => <SkeletonRow key={i} />)
            ) : isError ? (
              <tr>
                <td colSpan={6} className={styles.emptyCellError}>
                  <div className={styles.emptyContent}>
                    <svg width="32" height="32" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24" aria-hidden="true">
                      <circle cx="12" cy="12" r="10"/><path d="M12 8v4m0 4h.01"/>
                    </svg>
                    <p>Failed to load history. Please try again.</p>
                  </div>
                </td>
              </tr>
            ) : data?.items.length === 0 ? (
              <tr>
                <td colSpan={6} className={styles.emptyCell}>
                  <div className={styles.emptyContent}>
                    <svg width="32" height="32" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24" aria-hidden="true">
                      <path d="M12 8v4l3 3"/><circle cx="12" cy="12" r="9"/>
                    </svg>
                    <p>No records match the current filters.</p>
                    <Link to="/analyze" className={styles.emptyCta}>Analyze a message →</Link>
                  </div>
                </td>
              </tr>
            ) : (
              data?.items.map((item: PredictionSummary) => (
                <>
                  <tr key={item.id} className={confirmDeleteId === item.id ? styles.rowConfirming : undefined}>
                    <td className={styles.cellDate}>
                      <time
                        dateTime={item.created_at}
                        title={new Date(item.created_at).toLocaleString()}
                      >
                        {formatRelativeDate(item.created_at)}
                      </time>
                    </td>
                    <td className={styles.cellType}>
                      <span className={styles.typeTag}>{item.message_type.toUpperCase()}</span>
                    </td>
                    <td className={styles.cellPreview} title={item.text_preview || ''}>
                      {item.text_preview ? (
                        item.text_preview.length > 60
                          ? `${item.text_preview.substring(0, 60)}…`
                          : item.text_preview
                      ) : (
                        <span className={styles.noText}>[No text]</span>
                      )}
                    </td>
                    <td>
                      <span
                        className={`${styles.verdictBadge} ${item.verdict === 'SPAM' ? styles.badgeSpam : styles.badgeHam}`}
                        aria-label={`Verdict: ${item.verdict}`}
                      >
                        {item.verdict}
                      </span>
                    </td>
                    <td className={styles.cellConfidence}>
                      {(item.confidence * 100).toFixed(1)}%
                    </td>
                    <td className={styles.colActions}>
                      {confirmDeleteId !== item.id ? (
                        <button
                          onClick={() => setConfirmDeleteId(item.id)}
                          className={styles.btnDelete}
                          disabled={deleteMutation.isPending}
                          aria-label={`Delete prediction record`}
                          title="Delete record"
                        >
                          <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" aria-hidden="true">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      ) : (
                        <div className={styles.deleteSpinner} aria-hidden={!deleteMutation.isPending}>
                          {deleteMutation.isPending && (
                            <span className={styles.miniSpinner} aria-label="Deleting…" />
                          )}
                        </div>
                      )}
                    </td>
                  </tr>

                  {/* Inline confirm row */}
                  {confirmDeleteId === item.id && (
                    <tr key={`confirm-${item.id}`} className={styles.confirmRow} role="row">
                      <td colSpan={6}>
                        <div className={styles.confirmContent}>
                          <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" aria-hidden="true">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
                          </svg>
                          <span className={styles.confirmText}>Delete this record permanently?</span>
                          <div className={styles.confirmActions}>
                            <button
                              className={styles.btnConfirmDelete}
                              onClick={() => deleteMutation.mutate(item.id)}
                              disabled={deleteMutation.isPending}
                              aria-label="Confirm deletion"
                            >
                              {deleteMutation.isPending ? 'Deleting…' : 'Delete'}
                            </button>
                            <button
                              className={styles.btnCancelDelete}
                              onClick={() => setConfirmDeleteId(null)}
                              disabled={deleteMutation.isPending}
                              aria-label="Cancel deletion"
                            >
                              Cancel
                            </button>
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {data && data.total_pages > 1 && (
        <div className={styles.pagination} role="navigation" aria-label="Pagination">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className={styles.btnPage}
            aria-label="Previous page"
          >
            ← Previous
          </button>
          <span className={styles.pageInfo} aria-live="polite">
            Page {page} of {data.total_pages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(data.total_pages, p + 1))}
            disabled={page === data.total_pages}
            className={styles.btnPage}
            aria-label="Next page"
          >
            Next →
          </button>
        </div>
      )}
    </div>
  );
}
