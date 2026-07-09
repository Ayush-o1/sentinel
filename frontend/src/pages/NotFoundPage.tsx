/**
 * SENTINEL — Not Found Page
 */
export default function NotFoundPage() {
  return (
    <div style={{ padding: '2rem' }}>
      <h2 style={{ fontFamily: 'var(--font-mono)', color: 'var(--color-accent-primary)' }}>
        404 Not Found
      </h2>
      <p style={{ color: 'var(--color-text-secondary)', marginTop: '0.5rem' }}>
        The page you are looking for does not exist.
      </p>
    </div>
  );
}
