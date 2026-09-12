import React, { useEffect, useState } from 'react'
import api from '../services/api'
import './Logs.css'

export default function LogsPage() {
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState({ logs: [], total: 0, page: 1, per_page: 50 })
  const [filters, setFilters] = useState({ severity: '', source_ip: '', dest_ip: '', protocol: '', start_date: '', end_date: '' })
  const [error, setError] = useState(null)

  const fetchLogs = async () => {
    setLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams({ page: data.page, per_page: data.per_page })
      Object.entries(filters).forEach(([k, v]) => { if (v) params.append(k, v) })
      const res = await api.get(`/logs/?${params.toString()}`)
      setData(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load logs')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchLogs() }, [data.page])

  const handleFilterChange = (e) => {
    const { name, value } = e.target
    setFilters(f => ({ ...f, [name]: value }))
    setData(d => ({ ...d, page: 1 }))
  }

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= Math.ceil(data.total / data.per_page)) {
      setData(d => ({ ...d, page: newPage }))
    }
  }

  const severityColors = { info: '#38bdf8', warning: '#fbbf24', high: '#fb923c', critical: '#ef4444' }

  return (
    <div className="logs-page">
      <h1 className="page-heading">Logs</h1>

      <div className="filters-card">
        <div className="filters-row">
          <select name="severity" value={filters.severity} onChange={handleFilterChange} className="filter-input">
            <option value="">All Severities</option>
            <option value="info">Info</option>
            <option value="warning">Warning</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
          <input type="text" name="source_ip" placeholder="Source IP" value={filters.source_ip} onChange={handleFilterChange} className="filter-input" />
          <input type="text" name="dest_ip" placeholder="Dest IP" value={filters.dest_ip} onChange={handleFilterChange} className="filter-input" />
          <input type="text" name="protocol" placeholder="Protocol" value={filters.protocol} onChange={handleFilterChange} className="filter-input" />
          <input type="date" name="start_date" value={filters.start_date} onChange={handleFilterChange} className="filter-input" />
          <input type="date" name="end_date" value={filters.end_date} onChange={handleFilterChange} className="filter-input" />
        </div>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="table-wrapper">
        <table className="logs-table">
          <thead>
            <tr>
              <th>Time</th>
              <th>Severity</th>
              <th>Source IP</th>
              <th>Dest IP</th>
              <th>Port</th>
              <th>Protocol</th>
              <th>Action</th>
              <th>Raw Log</th>
            </tr>
          </thead>
          <tbody>
            {data.logs.map((log, i) => (
              <tr key={log.id}>
                <td>{new Date(log.timestamp).toLocaleString()}</td>
                <td><span className="severity-badge" style={{ background: severityColors[log.severity] }}>{log.severity}</span></td>
                <td>{log.source_ip}</td>
                <td>{log.dest_ip}</td>
                <td>{log.dest_port || '-'}</td>
                <td>{log.protocol}</td>
                <td>{log.action}</td>
                <td className="raw-log">{log.raw_log}</td>
              </tr>
            ))}
            {!loading && data.logs.length === 0 && (
              <tr><td colSpan={8} style={{ textAlign: 'center', color: '#64748b', padding: '2rem' }}>No logs found</td></tr>
            )}
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