import React from 'react'
import { useAuth } from '../context/AuthContext.jsx'
import { Navigate } from 'react-router-dom'
export default function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', background: '#0a0f1a', color: '#94a3b8' }}>Loading...</div>
  return user ? children : <Navigate to="/login" replace />
}