/**
 * SENTINEL Frontend — Axios API Client
 *
 * Configures the Axios instance with:
 * - Base URL from environment variables
 * - Authorization header injection from in-memory token store
 * - Automatic token refresh on 401 responses
 * - Standardized error handling
 */

import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import type { TokenResponse } from '../types';

// ---------------------------------------------------------------------------
// In-Memory Token Store
//
// Access tokens are stored in memory (a module-level variable), NOT in
// localStorage. This prevents XSS attacks from stealing the token.
// The token is lost on page refresh — users will seamlessly get a new
// one via the refresh token cookie (HttpOnly, invisible to JS).
// ---------------------------------------------------------------------------
let _accessToken: string | null = null;

export const setAccessToken = (token: string | null): void => {
  _accessToken = token;
};

export const getAccessToken = (): string | null => _accessToken;

// ---------------------------------------------------------------------------
// Axios Instance
// ---------------------------------------------------------------------------
const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  withCredentials: true, // Required to send/receive HttpOnly cookies (refresh token)
});

// ---------------------------------------------------------------------------
// Request Interceptor — Inject Authorization Header
// ---------------------------------------------------------------------------
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    if (_accessToken) {
      config.headers.Authorization = `Bearer ${_accessToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ---------------------------------------------------------------------------
// Response Interceptor — Automatic Token Refresh
// ---------------------------------------------------------------------------
let _isRefreshing = false;
let _failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: unknown) => void;
}> = [];

const _processQueue = (error: unknown, token: string | null) => {
  _failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token!);
    }
  });
  _failedQueue = [];
};

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Only attempt refresh on 401 and non-refresh endpoints
    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !originalRequest.url?.includes('/auth/refresh') &&
      !originalRequest.url?.includes('/auth/login')
    ) {
      if (_isRefreshing) {
        // Queue concurrent requests during refresh
        return new Promise((resolve, reject) => {
          _failedQueue.push({ resolve, reject });
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return api(originalRequest);
        });
      }

      originalRequest._retry = true;
      _isRefreshing = true;

      try {
        const { data } = await api.post<TokenResponse>('/api/v1/auth/refresh');
        const newToken = data.access_token;
        setAccessToken(newToken);
        _processQueue(null, newToken);
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return api(originalRequest);
      } catch (refreshError) {
        _processQueue(refreshError, null);
        // Refresh failed — clear token and redirect to login
        setAccessToken(null);
        window.location.href = '/login';
        return Promise.reject(refreshError);
      } finally {
        _isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default api;
