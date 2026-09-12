import React, { useEffect, useState } from 'react'
import api from '../services/api'
import { useAuth } from '../context/AuthContext.jsx'
import './Alerts.css'
import '../styles.css'

export default function AlertsPage() {
  const { user } = useAuth()
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState({ alerts: [], total: 0, page: 1, per_page: 50 })
  const [filters, setFilters] = useState({ severity: '', status: '', source_ip: '' })
  const [error, setError] = useState(null)

  const fetchAlerts = async () => {
    setLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams({ page: data.page, per_page: data.per_page })
      Object.entries(filters).forEach(([k, v]) => { if (v) params.append(k, v) })
      const res = await api.get(`/api/alerts/?${params.toString()}`)
      setData(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load alerts')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchAlerts() }, [data.page])

  const handleFilterChange = (e) => {
    const { name, value } = e.target
    setFilters(f => ({ ...f, [name]: value }))
    setData(d => ({ ...d, page: 1 }))
  }

  const handleStatusChange = async (alertId, newStatus) => {
    try {
      await api.patch(`/api/alerts/${alertId}/status`, { status: newStatus })
      fetchAlerts()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update alert')
    }
  }

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= Math.ceil(data.total / data.per_page)) {
      setData(d => ({ ...d, page: newPage }))
    }
  }

  const statusLabels = { open: 'Open', acknowledged: 'Acknowledged', resolved: 'Resolved' }
  const statusColors = { open: '#f59e0b', acknowledged: '#6b7280', resolved: '#10b981' }
  const severityColors = { critical: '#ef4444', high: '#fb923c', medium: '#fbbf24', low: '#38bdf8' }

  return (
    <div className="alerts-page">
      <h1 className="page-heading">Alerts</h1>

      <div className="filters-card">
        <div className="filters-row">
          <select name="severity" value={filters.severity} onChange={handleFilterChange} className="filter-input">
            <option value="">All Severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
          <select name="status" value={filters.status} onChange={handleFilterChange} className="filter-input">
            <option value="">All Statuses</option>
            <option value="open">Open</option>
            <option value="acknowledged">Acknowledged</option>
            <option value="resolved">Resolved</option>
          </select>
          <input type="text" name="source_ip" placeholder="Source IP" value={filters.source_ip} onChange={handleFilterChange} className="filter-input" />
        </div>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="table-wrapper">
        <table className="alerts-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Title</th>
              <th>Severity</th>
              <th>Status</th>
              <th>Source IP</th>
              <th>Assigned To</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {data.alerts.map((alert, i) => (
              <tr key={alert.id}>
                <td>{i + 1}</td>
                <td><strong>{alert.title}</strong>{alert.description && <div className="small-text">({alert.description})</div>}</td>
                <td><span className="status-dot" style={{ background: severityColors[alert.severity] }}></span> {alert.severity}</td>
                <td><span className="status-badge" style={{ background: statusColors[alert.status] }}>{statusLabels[alert.status]}</span></td>
                <td>{alert.source_log_id}</td>
                <td>{alert.username || '-'}</td>
                <td>{new Date(alert.created_at).toLocaleString()}</td>
                <td>
                  {alert.status === 'open' && (
                    <button className="action-btn" onClick={() => handleStatusChange(alert.id, 'acknowledged')}>Acknowledge</button>
                  )}
                  {alert.status === 'acknowledged' && (
                    <button className="action-btn" onClick={() => handleStatusChange(alert.id, 'resolved')}>Resolve</button>
                  )}
                </td>
              </tr>
            ))}
            {data.alerts.length === 0 && <tr><td colSpan={8} style={{ textAlign: 'center', color: '#64748b', padding: '2rem' }}>No alerts found</td></tr>}
          </tbody>
        </table>
      </div>

      <div className="pagination">
        <button onClick={() => handlePageChange(data.page - 1)} disabled={data.page === 1 || loading}>Previous</button>
        <span>Page {data.page} of {Math.ceil(data.total / data.per_page)} ({data.total} total)</span>
        <button onClick={() => handlePageChange(data.page + 1)} disabled={data.page >= Math.ceil(data.total / data.per_page) || loading}>Next</button>
      </div>
    </div>
  )
}