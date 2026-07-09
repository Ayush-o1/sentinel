/**
 * SENTINEL — Prediction Service
 */

import api from './api';
import type {
  PaginatedResponse,
  PredictRequest,
  PredictionResponse,
  PredictionSummary,
  PredictionDetail,
} from '../types';

export const predictionService = {
  async analyze(data: PredictRequest): Promise<PredictionResponse> {
    const response = await api.post<PredictionResponse>('/api/v1/predict', data);
    return response.data;
  },

  async getHistory(params: {
    page?: number;
    page_size?: number;
    verdict?: string;
    message_type?: string;
    sort_by?: string;
    sort_order?: string;
  } = {}): Promise<PaginatedResponse<PredictionSummary>> {
    const response = await api.get<PaginatedResponse<PredictionSummary>>(
      '/api/v1/predictions',
      { params }
    );
    return response.data;
  },

  async getById(id: string): Promise<PredictionDetail> {
    const response = await api.get<PredictionDetail>(`/api/v1/predictions/${id}`);
    return response.data;
  },

  async delete(id: string): Promise<void> {
    await api.delete(`/api/v1/predictions/${id}`);
  },
};
