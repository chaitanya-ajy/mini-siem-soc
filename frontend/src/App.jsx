import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext.jsx'
import ProtectedRoute from './components/ProtectedRoute.jsx'
import LoginPage from './pages/LoginPage.jsx'
import DashboardPage from './pages/DashboardPage.jsx'
import LogsPage from './pages/LogsPage.jsx'
import AlertsPage from './pages/AlertsPage.jsx'
import IncidentsPage from './pages/IncidentsPage.jsx'
import ThreatDetectionPage from './pages/ThreatDetectionPage.jsx'
import Sidebar from './components/Sidebar.jsx'
import Header from './components/Header.jsx'
import './App.css'

function Layout() {
  const { user, loading } = useAuth()
  if (loading) return <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', background: '#0a0f1a', color: '#94a3b8' }}>Loading...</div>
  if (!user) return <Navigate to="/login" replace />
  return (
    <div className="app-layout">
      <Sidebar />
      <div className="main-area">
        <Header />
        <main className="content">
          <Routes>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/logs" element={<LogsPage />} />
            <Route path="/alerts" element={<AlertsPage />} />
            <Route path="/incidents" element={<IncidentsPage />} />
            <Route path="/threats" element={<ThreatDetectionPage />} />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/*" element={<Layout />} />
      </Routes>
    </AuthProvider>
  )
}