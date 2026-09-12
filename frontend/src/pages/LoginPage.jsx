import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

export default function LoginPage() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(username, password)
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>🔒 SIEM Dashboard</h1>
        <p style={styles.subtitle}>Sign in to your account</p>
        {error && <div style={styles.error}>{error}</div>}
        <form onSubmit={handleSubmit} style={styles.form}>
          <div style={styles.field}>
            <label style={styles.label}>Username</label>
            <input
              style={styles.input}
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              placeholder="admin"
            />
          </div>
          <div style={styles.field}>
            <label style={styles.label}>Password</label>
            <input
              style={styles.input}
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="••••••••"
            />
          </div>
          <button type="submit" style={styles.button} disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
        <p style={styles.hint}>Default admin: admin / admin123</p>
      </div>
    </div>
  )
}

const styles = {
  container: { display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', background: '#0a0f1a' },
  card: { background: '#1a1f2e', borderRadius: '12px', padding: '2rem', width: '360px', boxShadow: '0 4px 24px rgba(0,0,0,.5)' },
  title: { fontSize: '1.5rem', textAlign: 'center', marginBottom: '.5rem', color: '#38bdf8' },
  subtitle: { textAlign: 'center', color: '#94a3b8', marginBottom: '1.5rem' },
  error: { background: '#7f1d1d', color: '#fca5a5', padding: '.6rem .8rem', borderRadius: '6px', marginBottom: '1rem', fontSize: '.85rem' },
  form: { display: 'flex', flexDirection: 'column', gap: '1rem' },
  field: { display: 'flex', flexDirection: 'column', gap: '.3rem' },
  label: { color: '#94a3b8', fontSize: '.85rem', fontWeight: 600 },
  input: { background: '#0f172a', border: '1px solid #334155', borderRadius: '6px', padding: '.6rem .8rem', color: '#e2e8f0', fontSize: '.9rem', outline: 'none' },
  button: { background: '#38bdf8', color: '#0a0f1a', fontWeight: 700, padding: '.7rem', borderRadius: '6px', border: 'none', fontSize: '1rem', marginTop: '.5rem', opacity: 0.9 },
  hint: { textAlign: 'center', color: '#64748b', fontSize: '.75rem', marginTop: '1rem' }
}