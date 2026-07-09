/**
 * SENTINEL — Analyze Page
 */
import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { predictionService } from '../services/predictionService';
import type { MessageType, PredictionResponse } from '../types';
import styles from './AnalyzePage.module.css';

const MAX_CHARS = 2000;

export default function AnalyzePage() {
  const [text, setText] = useState('');
  const [messageType, setMessageType] = useState<MessageType>('sms');
  const [result, setResult] = useState<PredictionResponse | null>(null);

  const analyzeMutation = useMutation({
    mutationFn: predictionService.analyze,
    onSuccess: (data) => {
      setResult(data);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) return;
    setResult(null);
    analyzeMutation.mutate({ text, message_type: messageType });
  };

  const handleReset = () => {
    setText('');
    setResult(null);
    analyzeMutation.reset();
  };

  /* Normalize token weights relative to the maximum weight */
  const getTokenBarWidth = (weight: number, tokens: { weight: number }[]) => {
    const maxWeight = Math.max(...tokens.map((t) => t.weight), 0.001);
    return `${Math.min((weight / maxWeight) * 100, 100)}%`;
  };

  const charCount  = text.length;
  const charOver   = charCount > MAX_CHARS;

  return (
    <div className={styles.container}>
      {/* ── Input Form ─────────────────────────────────────────── */}
      <div className={styles.inputSection}>
        <form
          onSubmit={handleSubmit}
          className={styles.form}
          aria-busy={analyzeMutation.isPending}
        >
          {/* Message type selector */}
          <div className={styles.typeSelector} role="group" aria-label="Message type">
            {(['sms', 'email', 'text'] as MessageType[]).map((type) => (
              <label
                key={type}
                className={`${styles.typeLabel} ${messageType === type ? styles.typeActive : ''}`}
              >
                <input
                  type="radio"
                  name="messageType"
                  value={type}
                  checked={messageType === type}
                  onChange={(e) => setMessageType(e.target.value as MessageType)}
                  className={styles.hiddenRadio}
                />
                {type.toUpperCase()}
              </label>
            ))}
          </div>

          {/* Textarea */}
          <div className={styles.textareaWrapper}>
            <textarea
              id="message-input"
              className={`${styles.textarea} ${charOver ? styles.textareaOver : ''}`}
              placeholder="Paste message content here to evaluate its spam probability..."
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={8}
              disabled={analyzeMutation.isPending}
              required
              aria-label="Message content to analyze"
              aria-describedby="char-count"
              maxLength={MAX_CHARS + 500} /* soft limit */
            />
            <div
              id="char-count"
              className={`${styles.charCount} ${charOver ? styles.charCountOver : ''}`}
              aria-live="polite"
              aria-atomic="true"
            >
              {charCount.toLocaleString()} / {MAX_CHARS.toLocaleString()}
            </div>
          </div>

          {/* Actions */}
          <div className={styles.actions}>
            {result && (
              <button
                type="button"
                onClick={handleReset}
                className={styles.btnGhost}
                disabled={analyzeMutation.isPending}
              >
                Clear
              </button>
            )}
            <button
              type="submit"
              className={styles.btnPrimary}
              disabled={analyzeMutation.isPending || !text.trim() || charOver}
              aria-label={analyzeMutation.isPending ? 'Analyzing message…' : 'Analyze message'}
            >
              {analyzeMutation.isPending ? (
                <>
                  <span className={styles.spinner} aria-hidden="true" />
                  Analyzing…
                </>
              ) : (
                <>
                  <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" aria-hidden="true">
                    <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/><path d="M11 8v6M8 11h6"/>
                  </svg>
                  Analyze Message
                </>
              )}
            </button>
          </div>

          {/* Error alert */}
          {analyzeMutation.isError && (
            <div
              className={styles.errorAlert}
              role="alert"
              aria-live="assertive"
            >
              <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" aria-hidden="true">
                <circle cx="12" cy="12" r="10"/><path d="M12 8v4m0 4h.01"/>
              </svg>
              Failed to analyze message. Please check your connection and try again.
            </div>
          )}
        </form>
      </div>

      {/* ── Results ────────────────────────────────────────────── */}
      {result && (
        <div className={styles.resultSection} role="region" aria-label="Analysis results" aria-live="polite">
          {/* Verdict Card */}
          <div
            className={`${styles.verdictCard} ${result.verdict === 'SPAM' ? styles.verdictSpam : styles.verdictHam}`}
          >
            <div className={styles.verdictHeader}>
              <div className={styles.verdictLeft}>
                <div className={styles.verdictIcon} aria-hidden="true">
                  {result.verdict === 'SPAM' ? (
                    <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                      <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
                      <path d="M12 9v4m0 4h.01"/>
                    </svg>
                  ) : (
                    <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                      <path d="M22 11.08V12a10 10 0 11-5.93-9.14"/>
                      <polyline points="22 4 12 14.01 9 11.01"/>
                    </svg>
                  )}
                </div>
                <div>
                  <h2 className={styles.verdictTitle}>
                    {result.verdict === 'SPAM' ? 'SPAM DETECTED' : 'CLEAN MESSAGE'}
                  </h2>
                  <p className={styles.verdictSubtitle}>
                    {result.verdict === 'SPAM' ? 'High spam indicators found' : 'No spam indicators detected'}
                  </p>
                </div>
              </div>
              <div className={styles.confidenceBadge}>
                <span className={styles.confidenceValue}>{(result.confidence * 100).toFixed(1)}%</span>
                <span className={styles.confidenceLabel}>Confidence</span>
              </div>
            </div>

            {/* Confidence bar */}
            <div className={styles.confBarTrack} aria-hidden="true">
              <div
                className={`${styles.confBar} ${result.verdict === 'SPAM' ? styles.confBarSpam : styles.confBarHam}`}
                style={{ width: `${result.confidence * 100}%` }}
              />
            </div>

            <p className={styles.explanationText}>{result.explanation.summary}</p>
          </div>

          {/* LIME Explainability — only shown for SPAM */}
          {result.verdict === 'SPAM' && result.explanation.suspicious_tokens.length > 0 && (
            <div className={styles.explainabilityCard}>
              <h3 className={styles.explainabilityTitle}>LIME Explainability Analysis</h3>
              <p className={styles.explainabilitySubtitle}>
                Tokens contributing most significantly to the spam classification:
              </p>

              <div className={styles.tokenList}>
                {result.explanation.suspicious_tokens.map((token, idx) => (
                  <div key={idx} className={styles.tokenRow}>
                    <span className={styles.tokenString}>{token.token}</span>
                    <div
                      className={styles.tokenBarContainer}
                      role="img"
                      aria-label={`Weight: ${(token.weight).toFixed(2)}`}
                    >
                      <div
                        className={styles.tokenBar}
                        style={{
                          width: getTokenBarWidth(token.weight, result.explanation.suspicious_tokens),
                        }}
                      />
                    </div>
                    <span className={styles.tokenWeight}>{token.weight.toFixed(3)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* HAM — clean message notice */}
          {result.verdict === 'HAM' && (
            <div className={styles.cleanNotice}>
              <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" aria-hidden="true">
                <circle cx="12" cy="12" r="10"/>
                <path d="M12 16v-4m0-4h.01"/>
              </svg>
              No suspicious tokens were identified in this message.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
