/**
 * SENTINEL — Login Page
 */
import { useState, useId } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '../services/authService';
import { useAuthStore } from '../store/authStore';
import styles from './AuthPage.module.css';

export default function LoginPage() {
  const navigate   = useNavigate();
  const { setUser } = useAuthStore();
  const [email, setEmail]       = useState('');
  const [password, setPassword] = useState('');
  const [error, setError]       = useState('');
  const [loading, setLoading]   = useState(false);
  const errorId = useId();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await authService.login({ email, password });
      const user = await authService.getMe();
      setUser(user);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.error?.message ?? 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.bgGrid} role="presentation" aria-hidden="true" />
      <div className={styles.card}>
        <div className={styles.logo} aria-label="SENTINEL">SENTINEL</div>
        <h1 className={styles.title}>Welcome back</h1>
        <p className={styles.subtitle}>Sign in to your threat intelligence platform</p>

        <form
          onSubmit={handleSubmit}
          className={styles.form}
          aria-describedby={error ? errorId : undefined}
          noValidate
        >
          <div className={styles.field}>
            <label className={styles.label} htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className={styles.input}
              placeholder="you@example.com"
              autoComplete="email"
              disabled={loading}
            />
          </div>

          <div className={styles.field}>
            <label className={styles.label} htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className={styles.input}
              placeholder="••••••••"
              autoComplete="current-password"
              disabled={loading}
            />
          </div>

          {error && (
            <div id={errorId} className={styles.error} role="alert" aria-live="assertive">
              <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" aria-hidden="true">
                <circle cx="12" cy="12" r="10"/><path d="M12 8v4m0 4h.01"/>
              </svg>
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className={styles.btnSubmit}
            aria-label={loading ? 'Signing in…' : 'Sign in'}
          >
            {loading ? (
              <>
                <span className={styles.spinner} aria-hidden="true" />
                Signing in…
              </>
            ) : 'Sign In'}
          </button>
        </form>

        <p className={styles.switch}>
          Don't have an account?{' '}
          <Link to="/register" className={styles.link}>Create one</Link>
        </p>
      </div>
    </div>
  );
}
