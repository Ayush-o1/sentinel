// SENTINEL Frontend — TypeScript Type Definitions

// ---------------------------------------------------------------------------
// Auth Types
// ---------------------------------------------------------------------------

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'user' | 'admin';
  is_active: boolean;
  created_at: string;
  total_predictions?: number;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

// ---------------------------------------------------------------------------
// Prediction Types
// ---------------------------------------------------------------------------

export type Verdict = 'SPAM' | 'HAM';
export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH';
export type MessageType = 'sms' | 'email' | 'text';

export interface SuspiciousToken {
  token: string;
  weight: number;
}

export interface PredictionExplanation {
  summary: string;
  suspicious_tokens: SuspiciousToken[];
  risk_level: RiskLevel;
}

export interface PredictionResponse {
  prediction_id: string;
  verdict: Verdict;
  confidence: number;
  message_type: MessageType;
  processed_at: string;
  explanation: PredictionExplanation;
}

export interface PredictionSummary {
  id: string;
  verdict: Verdict;
  confidence: number;
  risk_level: RiskLevel;
  message_type: MessageType;
  text_preview: string | null;
  created_at: string;
}

export interface PredictionDetail extends PredictionSummary {
  original_text: string;
  processed_text: string;
  explanation: string;
  suspicious_tokens: SuspiciousToken[];
}

export interface PredictRequest {
  text: string;
  message_type: MessageType;
}

// ---------------------------------------------------------------------------
// Analytics Types
// ---------------------------------------------------------------------------

export interface AnalyticsSummary {
  total_predictions: number;
  spam_count: number;
  ham_count: number;
  spam_rate: number;
  avg_confidence: number;
  high_confidence_spam: number;
  predictions_today: number;
  most_common_spam_tokens: string[];
}

export interface TimelineDataPoint {
  date: string;
  spam: number;
  ham: number;
  total: number;
}

export interface TimelineResponse {
  period: string;
  data: TimelineDataPoint[];
}

export interface ConfidenceBucket {
  range: string;
  count: number;
}

export interface ModelInfo {
  version: string;
  algorithm: string;
  training_date: string;
  training_samples: number;
  accuracy: number;
  precision_spam: number;
  recall_spam: number;
  f1_spam: number;
  status: string;
}

// ---------------------------------------------------------------------------
// Common Types
// ---------------------------------------------------------------------------

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: Record<string, string[]>;
  };
}
