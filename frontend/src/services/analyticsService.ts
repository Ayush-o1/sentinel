/**
 * SENTINEL — Analytics Service
 */

import api from './api';
import type {
  AnalyticsSummary,
  ConfidenceBucket,
  ModelInfo,
  TimelineResponse,
} from '../types';

export const analyticsService = {
  async getSummary(): Promise<AnalyticsSummary> {
    const response = await api.get<AnalyticsSummary>('/api/v1/analytics/summary');
    return response.data;
  },

  async getTimeline(period: '7d' | '30d' | '90d' = '30d'): Promise<TimelineResponse> {
    const response = await api.get<TimelineResponse>('/api/v1/analytics/timeline', {
      params: { period },
    });
    return response.data;
  },

  async getConfidenceDistribution(): Promise<{ buckets: ConfidenceBucket[] }> {
    const response = await api.get('/api/v1/analytics/confidence-distribution');
    return response.data;
  },

  async getModelInfo(): Promise<ModelInfo> {
    const response = await api.get<ModelInfo>('/api/v1/model/info');
    return response.data;
  },
};
