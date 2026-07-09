/**
 * SENTINEL — Auth Service
 * API calls for authentication endpoints
 */

import api, { setAccessToken } from './api';
import type { LoginRequest, RegisterRequest, TokenResponse, User } from '../types';

export const authService = {
  async register(data: RegisterRequest): Promise<User> {
    const response = await api.post<User>('/api/v1/auth/register', data);
    return response.data;
  },

  async login(data: LoginRequest): Promise<TokenResponse> {
    const response = await api.post<TokenResponse>('/api/v1/auth/login', data);
    setAccessToken(response.data.access_token);
    return response.data;
  },

  async logout(): Promise<void> {
    await api.post('/api/v1/auth/logout');
    setAccessToken(null);
  },

  async getMe(): Promise<User> {
    const response = await api.get<User>('/api/v1/auth/me');
    return response.data;
  },

  async refresh(): Promise<TokenResponse> {
    const response = await api.post<TokenResponse>('/api/v1/auth/refresh');
    setAccessToken(response.data.access_token);
    return response.data;
  },
};
