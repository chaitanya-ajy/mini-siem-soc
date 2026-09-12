import React, { useEffect, useState } from 'react'
import api from '../services/api'
import { useAuth } from '../context/AuthContext.jsx'
import './Dashboard.css'

export default function DashboardPage() {
  const { user } = useAuth()
  const [loading, setLoading] = useState(true)
  const [summary, setSummary] = useState(null)
  const [logsTrend, setLogsTrend] = useState([])
  const [alertsTrend, setAlertsTrend] = useState([])
  const [topIps, setTopIps] = useState([])
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [res1, res2, res3, res4] = await Promise.all([
          api.get('/dashboard/summary'),
          api.get('/dashboard/logs/trend?days=7'),
          api.get('/dashboard/alerts/trend?days=7'),
          api.get('/dashboard/top-ips?limit=5&days=7')
        ])
        setSummary(res1.data)
        setLogsTrend(res2.data)
        setAlertsTrend(res3.data)
        setTopIps(res4.data)
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to load dashboard')
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  if (loading) return <div style={{ textAlign: 'center', padding: '3rem', color: '#94a3b8' }}>Loading dashboard...</div>
  if (error) return <div style={{ color: '#fca5a5', padding: '1rem' }}>Error: {error}</div>

  return (
    <div className="dashboard">
      <h1 className="page-heading">Dashboard</h1>
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📜</div>
          <div className="stat-value">{summary?.total_logs || 0}</div>
          <div className="stat-label">Total Logs</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🚨</div>
          <div className="stat-value">{summary?.total_alerts || 0}</div>
          <div className="stat-label">Total Alerts</div>
        </div>
        <div className="stat-card highlight-red">
          <div className="stat-icon">🔴</div>
          <div className="stat-value">{summary?.critical_alerts || 0}</div>
          <div className="stat-label">Critical</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">📋</div>
          <div className="stat-value">{summary?.total_incidents || 0}</div>
          <div className="stat-label">Incidents</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">⚠️</div>
          <div className="stat-value">{summary?.open_alerts || 0}</div>
          <div className="stat-label">Open Alerts</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🔒</div>
          <div className="stat-value">{summary?.active_incidents || 0}</div>
          <div className="stat-label">Active Incidents</div>
        </div>
      </div>

      <div className="charts-row">
        <div className="chart-card">
          <h3>Logs Trend (7 days)</h3>
          <div className="chart">{renderBarChart(logsTrend)}</div>
        </div>
        <div className="chart-card">
          <h3>Alerts Trend (7 days)</h3>
          <div className="chart">{renderBarChart(alertsTrend)}</div>
        </div>
      </div>

      <div className="chart-card full-width">
        <h3>Top Source IPs</h3>
        <div className="ips-table">
          {topIps.map((ip, i) => (
            <div key={i} className="ip-row">
              <span className="ip-rank">{i + 1}</span>
              <span className="ip-address">{ip.source_ip}</span>
              <span className="ip-count">{ip.count} logs</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function renderBarChart(data) {
  if (!data?.length) return <div style={{ color: '#64748b', padding: '1rem' }}>No data</div>
  const max = Math.max(...data.map(d => d.count), 1)
  return (
    <div className="bar-chart">
      {data.map((d, i) => (
        <div key={i} className="bar-item">
          <div className="bar" style={{ height: `${(d.count / max) * 100}%` }} />
          <span className="bar-label">{d.date.slice(5)}</span>
          <span className="bar-value">{d.count}</span>
        </div>
      ))}
    </div>
  )
}