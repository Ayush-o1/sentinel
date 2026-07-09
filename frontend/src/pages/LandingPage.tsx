/**
 * SENTINEL — Landing Page
 */

import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import styles from './LandingPage.module.css';

const FEATURES = [
  {
    icon: '🛡️',
    title: 'ML-Powered Detection',
    desc: 'TF-IDF + Logistic Regression trained on 5,500+ messages with 98.7% accuracy.',
  },
  {
    icon: '🔍',
    title: 'Explainable AI',
    desc: 'LIME-powered token attribution shows exactly why a message was flagged.',
  },
  {
    icon: '📊',
    title: 'Threat Analytics',
    desc: 'Real-time dashboards, confidence distributions, and spam trend analysis.',
  },
  {
    icon: '⚡',
    title: 'Real-Time Analysis',
    desc: 'Sub-500ms inference with async ML pipeline and connection pooling.',
  },
  {
    icon: '🔐',
    title: 'Secure by Design',
    desc: 'JWT dual-token auth, bcrypt hashing, rate limiting, and HttpOnly cookies.',
  },
  {
    icon: '📜',
    title: 'Full Audit Trail',
    desc: 'Every prediction is logged with full history, pagination, and filtering.',
  },
];

export default function LandingPage() {
  return (
    <div className={styles.page}>
      {/* Background grid */}
      <div className={styles.bgGrid} aria-hidden />

      {/* Nav */}
      <nav className={styles.nav}>
        <div className={styles.navLogo}>
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
            <path d="M12 2L3 7v5c0 5.25 3.75 10.15 9 11.35C17.25 22.15 21 17.25 21 12V7L12 2z" fill="url(#lg1)"/>
            <path d="M9 12l2 2 4-4" stroke="#0a0e1a" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <defs>
              <linearGradient id="lg1" x1="3" y1="2" x2="21" y2="23">
                <stop stopColor="#00d4ff"/><stop offset="1" stopColor="#7c3aed"/>
              </linearGradient>
            </defs>
          </svg>
          <span>SENTINEL</span>
        </div>
        <div className={styles.navActions}>
          <Link to="/login" className={styles.btnGhost}>Sign In</Link>
          <Link to="/register" className={styles.btnPrimary}>Get Started</Link>
        </div>
      </nav>

      {/* Hero */}
      <section className={styles.hero}>
        <motion.div
          className={styles.heroBadge}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <span className={styles.badgeDot} />
          AI-Powered Threat Intelligence
        </motion.div>

        <motion.h1
          className={styles.heroTitle}
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          Detect Spam.
          <br />
          <span className={styles.gradientText}>Understand Why.</span>
        </motion.h1>

        <motion.p
          className={styles.heroSubtitle}
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          Enterprise-grade spam detection powered by NLP and Machine Learning.
          Every prediction is explained with token-level attribution.
        </motion.p>

        <motion.div
          className={styles.heroActions}
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <Link to="/register" className={styles.btnHeroPrimary}>
            Launch SENTINEL →
          </Link>
          <Link to="/login" className={styles.btnHeroGhost}>
            Sign in
          </Link>
        </motion.div>

        {/* Stats bar */}
        <motion.div
          className={styles.statsBar}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.5 }}
        >
          {[
            { value: '98.7%', label: 'Accuracy' },
            { value: '< 500ms', label: 'Inference Time' },
            { value: '5,500+', label: 'Training Samples' },
            { value: '11-Stage', label: 'NLP Pipeline' },
          ].map((stat) => (
            <div key={stat.label} className={styles.statItem}>
              <span className={styles.statValue}>{stat.value}</span>
              <span className={styles.statLabel}>{stat.label}</span>
            </div>
          ))}
        </motion.div>
      </section>

      {/* Features */}
      <section className={styles.features}>
        <h2 className={styles.sectionTitle}>Built for Production</h2>
        <p className={styles.sectionSubtitle}>
          Not a demo. A full-stack platform with enterprise architecture.
        </p>
        <div className={styles.featureGrid}>
          {FEATURES.map((feat, i) => (
            <motion.div
              key={feat.title}
              className={styles.featureCard}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.08 }}
            >
              <div className={styles.featureIcon}>{feat.icon}</div>
              <h3 className={styles.featureTitle}>{feat.title}</h3>
              <p className={styles.featureDesc}>{feat.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className={styles.cta}>
        <h2>Ready to Analyze?</h2>
        <p>Start detecting spam with explainable AI in seconds.</p>
        <Link to="/register" className={styles.btnHeroPrimary}>
          Create Free Account →
        </Link>
      </section>

      <footer className={styles.footer}>
        <span className={styles.footerLogo}>SENTINEL</span>
        <span className={styles.footerText}>
          AI-Powered Spam Detection & Threat Intelligence Platform
        </span>
      </footer>
    </div>
  );
}
