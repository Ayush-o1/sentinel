/**
 * SENTINEL — Analyze Page
 */
import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { predictionService } from '../services/predictionService';
import type { MessageType, PredictionResponse } from '../types';
import styles from './AnalyzePage.module.css';

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
    setResult(null); // Clear previous results
    analyzeMutation.mutate({ text, message_type: messageType });
  };

  const handleReset = () => {
    setText('');
    setResult(null);
    analyzeMutation.reset();
  };

  return (
    <div className={styles.container}>
      <div className={styles.inputSection}>
        <div className={styles.header}>
          <h2 className={styles.title}>Threat Analysis Engine</h2>
          <p className={styles.subtitle}>
            Submit a message to evaluate its spam probability using the NLP pipeline.
          </p>
        </div>

        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.typeSelector}>
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

          <textarea
            className={styles.textarea}
            placeholder="Paste message content here..."
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={8}
            disabled={analyzeMutation.isPending}
            required
          />

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
              disabled={analyzeMutation.isPending || !text.trim()}
            >
              {analyzeMutation.isPending ? 'Analyzing...' : 'Analyze Message'}
            </button>
          </div>

          {analyzeMutation.isError && (
            <div className={styles.errorAlert}>
              Failed to analyze message. Please try again.
            </div>
          )}
        </form>
      </div>

      {result && (
        <div className={styles.resultSection}>
          {/* Verdict Card */}
          <div className={`${styles.verdictCard} ${result.verdict === 'SPAM' ? styles.verdictSpam : styles.verdictHam}`}>
            <div className={styles.verdictHeader}>
              <h3 className={styles.verdictTitle}>
                {result.verdict === 'SPAM' ? '⚠️ SPAM DETECTED' : '✅ CLEAN (HAM)'}
              </h3>
              <div className={styles.confidenceBadge}>
                {(result.confidence * 100).toFixed(1)}% Confidence
              </div>
            </div>
            <p className={styles.explanationText}>
              {result.explanation.summary}
            </p>
          </div>

          {/* Explainability / Suspicious Tokens */}
          {result.verdict === 'SPAM' && result.explanation.suspicious_tokens.length > 0 && (
            <div className={styles.explainabilityCard}>
              <h4 className={styles.explainabilityTitle}>LIME Explainability Analysis</h4>
              <p className={styles.explainabilitySubtitle}>
                Tokens contributing most significantly to the spam classification:
              </p>
              
              <div className={styles.tokenList}>
                {result.explanation.suspicious_tokens.map((token, idx) => (
                  <div key={idx} className={styles.tokenRow}>
                    <span className={styles.tokenString}>{token.token}</span>
                    <div className={styles.tokenBarContainer}>
                      <div
                        className={styles.tokenBar}
                        style={{ width: `${token.weight * 100}%` }}
                      />
                    </div>
                    <span className={styles.tokenWeight}>
                      {(token.weight).toFixed(2)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
