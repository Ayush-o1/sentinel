/**
 * SENTINEL — History Page
 */
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { predictionService } from '../services/predictionService';
import type { PredictionSummary } from '../types';
import styles from './HistoryPage.module.css';

export default function HistoryPage() {
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [verdictFilter, setVerdictFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const pageSize = 10;

  const { data, isLoading, isError } = useQuery({
    queryKey: ['predictions-history', page, verdictFilter, typeFilter],
    queryFn: () => predictionService.getHistory({
      page,
      page_size: pageSize,
      verdict: verdictFilter || undefined,
      message_type: typeFilter || undefined,
    }),
    placeholderData: (prev) => prev, // keep old data while fetching new page
  });

  const deleteMutation = useMutation({
    mutationFn: predictionService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['predictions-history'] });
      queryClient.invalidateQueries({ queryKey: ['analytics-summary'] });
    },
  });

  const handleDelete = (id: string) => {
    if (window.confirm('Are you sure you want to delete this prediction record?')) {
      deleteMutation.mutate(id);
    }
  };

  const handleFilterChange = () => {
    setPage(1); // Reset to first page on filter change
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2 className={styles.title}>Prediction History</h2>
        
        {/* Filters */}
        <div className={styles.filters}>
          <select
            value={verdictFilter}
            onChange={(e) => { setVerdictFilter(e.target.value); handleFilterChange(); }}
            className={styles.select}
          >
            <option value="">All Verdicts</option>
            <option value="SPAM">Spam</option>
            <option value="HAM">Ham</option>
          </select>

          <select
            value={typeFilter}
            onChange={(e) => { setTypeFilter(e.target.value); handleFilterChange(); }}
            className={styles.select}
          >
            <option value="">All Types</option>
            <option value="sms">SMS</option>
            <option value="email">Email</option>
            <option value="text">Text</option>
          </select>
        </div>
      </div>

      <div className={styles.tableContainer}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Date</th>
              <th>Type</th>
              <th>Message Preview</th>
              <th>Verdict</th>
              <th>Confidence</th>
              <th className={styles.colActions}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr>
                <td colSpan={6} className={styles.emptyCell}>Loading history...</td>
              </tr>
            ) : isError ? (
              <tr>
                <td colSpan={6} className={styles.emptyCellError}>Failed to load history.</td>
              </tr>
            ) : data?.items.length === 0 ? (
              <tr>
                <td colSpan={6} className={styles.emptyCell}>No records found matching the criteria.</td>
              </tr>
            ) : (
              data?.items.map((item: PredictionSummary) => (
                <tr key={item.id}>
                  <td className={styles.cellDate}>
                    {new Date(item.created_at).toLocaleString()}
                  </td>
                  <td className={styles.cellType}>
                    <span className={styles.typeTag}>{item.message_type.toUpperCase()}</span>
                  </td>
                  <td className={styles.cellPreview} title={item.text_preview || ''}>
                    {item.text_preview ? (
                      item.text_preview.length > 50 
                        ? `${item.text_preview.substring(0, 50)}...` 
                        : item.text_preview
                    ) : (
                      <span className={styles.noText}>[No text]</span>
                    )}
                  </td>
                  <td>
                    <span className={`${styles.verdictBadge} ${item.verdict === 'SPAM' ? styles.badgeSpam : styles.badgeHam}`}>
                      {item.verdict}
                    </span>
                  </td>
                  <td className={styles.cellConfidence}>
                    {(item.confidence * 100).toFixed(1)}%
                  </td>
                  <td className={styles.colActions}>
                    <button
                      onClick={() => handleDelete(item.id)}
                      className={styles.btnDelete}
                      disabled={deleteMutation.isPending}
                      title="Delete Record"
                    >
                      <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {data && data.total_pages > 1 && (
        <div className={styles.pagination}>
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className={styles.btnPage}
          >
            Previous
          </button>
          <span className={styles.pageInfo}>
            Page {page} of {data.total_pages}
          </span>
          <button
            onClick={() => setPage(p => Math.min(data.total_pages, p + 1))}
            disabled={page === data.total_pages}
            className={styles.btnPage}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
