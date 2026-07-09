/**
 * SENTINEL — Zustand Auth Store
 *
 * Global client-side state for authentication.
 * Stores the current user and auth status.
 *
 * Access token is NOT stored here — it lives in the api.ts module
 * as a module-level variable to prevent XSS exposure.
 */

import { create } from 'zustand';
import type { User } from '../types';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;

  // Actions
  setUser: (user: User | null) => void;
  setLoading: (loading: boolean) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,  // True on initial load — we check for an existing session

  setUser: (user) =>
    set({
      user,
      isAuthenticated: user !== null,
      isLoading: false,
    }),

  setLoading: (loading) => set({ isLoading: loading }),

  logout: () =>
    set({
      user: null,
      isAuthenticated: false,
      isLoading: false,
    }),
}));
