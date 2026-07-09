/**
 * SENTINEL — Register Page
 */
import { useState, useId } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '../services/authService';
import { useAuthStore } from '../store/authStore';
import styles from './AuthPage.module.css';

/** Returns 0–4 password strength score */
function scorePassword(pw: string): number {
  let score = 0;
  if (pw.length >= 8)  score++;
  if (pw.length >= 12) score++;
  if (/[A-Z]/.test(pw)) score++;
  if (/[0-9]/.test(pw)) score++;
  return score;
}

const STRENGTH_LABELS  = ['', 'Weak', 'Fair', 'Good', 'Strong'];
const STRENGTH_CLASSES = ['', styles.strengthWeak, styles.strengthFair, styles.strengthGood, styles.strengthStrong];

export default function RegisterPage() {
  const navigate    = useNavigate();
  const { setUser } = useAuthStore();
  const [form, setForm] = useState({ email: '', password: '', full_name: '' });
  const [error, setError]     = useState('');
  const [loading, setLoading] = useState(false);
  const errorId = useId();

  const pwStrength = form.password ? scorePassword(form.password) : 0;

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
        const msgs = (Object.values(details) as string[][]).flat().join(' ');
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
      <div className={styles.bgGrid} role="presentation" aria-hidden="true" />
      <div className={styles.card}>
        <div className={styles.logo} aria-label="SENTINEL">SENTINEL</div>
        <h1 className={styles.title}>Create Account</h1>
        <p className={styles.subtitle}>Join the threat intelligence platform</p>

        <form
          onSubmit={handleSubmit}
          className={styles.form}
          aria-describedby={error ? errorId : undefined}
          noValidate
        >
          <div className={styles.field}>
            <label className={styles.label} htmlFor="full_name">Full Name</label>
            <input
              id="full_name"
              type="text"
              required
              value={form.full_name}
              onChange={(e) => setForm((f) => ({ ...f, full_name: e.target.value }))}
              className={styles.input}
              placeholder="Your Name"
              autoComplete="name"
              disabled={loading}
            />
          </div>

          <div className={styles.field}>
            <label className={styles.label} htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              required
              value={form.email}
              onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
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
              value={form.password}
              onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
              className={styles.input}
              placeholder="Min 8 chars, uppercase & digit"
              autoComplete="new-password"
              aria-describedby="pw-strength"
              disabled={loading}
            />

            {/* Password strength indicator */}
            {form.password && (
              <div className={styles.strengthWrapper} id="pw-strength" aria-live="polite">
                <div className={styles.strengthBars}>
                  {[1, 2, 3, 4].map((level) => (
                    <div
                      key={level}
                      className={`${styles.strengthBar} ${
                        pwStrength >= level ? STRENGTH_CLASSES[pwStrength] : ''
                      }`}
                    />
                  ))}
                </div>
                <span className={`${styles.strengthLabel} ${STRENGTH_CLASSES[pwStrength] || ''}`}>
                  {STRENGTH_LABELS[pwStrength]}
                </span>
              </div>
            )}
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
            aria-label={loading ? 'Creating account…' : 'Create account'}
          >
            {loading ? (
              <>
                <span className={styles.spinner} aria-hidden="true" />
                Creating Account…
              </>
            ) : 'Create Account'}
          </button>
        </form>

        <p className={styles.switch}>
          Already have an account?{' '}
          <Link to="/login" className={styles.link}>Sign in</Link>
        </p>
      </div>
    </div>
  );
}
