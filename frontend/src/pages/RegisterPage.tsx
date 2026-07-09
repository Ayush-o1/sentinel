/**
 * SENTINEL — Register Page
 */
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '../services/authService';
import { useAuthStore } from '../store/authStore';
import styles from './AuthPage.module.css';

export default function RegisterPage() {
  const navigate = useNavigate();
  const { setUser } = useAuthStore();
  const [form, setForm] = useState({ email: '', password: '', full_name: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await authService.register(form);
      await authService.login({ email: form.email, password: form.password });
      const user = await authService.getMe();
      setUser(user);
      navigate('/dashboard');
    } catch (err: any) {
      const details = err.response?.data?.error?.details;
      if (details) {
        const msgs = Object.values(details).flat().join(' ');
        setError(msgs);
      } else {
        setError(err.response?.data?.error?.message ?? 'Registration failed.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.bgGrid} aria-hidden />
      <div className={styles.card}>
        <div className={styles.logo}>SENTINEL</div>
        <h1 className={styles.title}>Create Account</h1>
        <p className={styles.subtitle}>Join the threat intelligence platform</p>
        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.field}>
            <label className={styles.label} htmlFor="full_name">Full Name</label>
            <input id="full_name" type="text" required value={form.full_name}
              onChange={e => setForm(f => ({ ...f, full_name: e.target.value }))}
              className={styles.input} placeholder="Your Name" />
          </div>
          <div className={styles.field}>
            <label className={styles.label} htmlFor="email">Email</label>
            <input id="email" type="email" required value={form.email}
              onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
              className={styles.input} placeholder="you@example.com" />
          </div>
          <div className={styles.field}>
            <label className={styles.label} htmlFor="password">Password</label>
            <input id="password" type="password" required value={form.password}
              onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
              className={styles.input} placeholder="Min 8 chars, uppercase & digit" />
          </div>
          {error && <p className={styles.error}>{error}</p>}
          <button type="submit" disabled={loading} className={styles.btnSubmit}>
            {loading ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>
        <p className={styles.switch}>
          Already have an account? <Link to="/login" className={styles.link}>Sign in</Link>
        </p>
      </div>
    </div>
  );
}
