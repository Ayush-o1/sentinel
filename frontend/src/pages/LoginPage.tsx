/**
 * SENTINEL — Login Page
 * Full implementation to be completed in Phase 3 (Frontend Polish)
 */
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '../services/authService';
import { useAuthStore } from '../store/authStore';
import styles from './AuthPage.module.css';

export default function LoginPage() {
  const navigate = useNavigate();
  const { setUser } = useAuthStore();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

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
      <div className={styles.bgGrid} aria-hidden />
      <div className={styles.card}>
        <div className={styles.logo}>SENTINEL</div>
        <h1 className={styles.title}>Welcome back</h1>
        <p className={styles.subtitle}>Sign in to your threat intelligence platform</p>
        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.field}>
            <label className={styles.label} htmlFor="email">Email</label>
            <input id="email" type="email" required value={email}
              onChange={e => setEmail(e.target.value)}
              className={styles.input} placeholder="you@example.com" />
          </div>
          <div className={styles.field}>
            <label className={styles.label} htmlFor="password">Password</label>
            <input id="password" type="password" required value={password}
              onChange={e => setPassword(e.target.value)}
              className={styles.input} placeholder="••••••••" />
          </div>
          {error && <p className={styles.error}>{error}</p>}
          <button type="submit" disabled={loading} className={styles.btnSubmit}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
        <p className={styles.switch}>
          Don't have an account? <Link to="/register" className={styles.link}>Create one</Link>
        </p>
      </div>
    </div>
  );
}
