import React, { useEffect, useState } from 'react'
import api from '../services/api'
import { useAuth } from '../context/AuthContext.jsx'
import '../styles.css'
import './Incidents.css'

export default function IncidentsPage() {
  const { user } = useAuth()
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState({ incidents: [], total: 0, page: 1, per_page: 50 })
  const [filters, setFilters] = useState({ severity: '', status: '' })
  const [error, setError] = useState(null)
  const [showModal, setShowModal] = useState(false)
  const [editIncident, setEditIncident] = useState(null)
  const [formData, setFormData] = useState({ title: '', description: '', severity: 'medium', status: 'new' })

  const fetchIncidents = async () => {
    setLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams({ page: data.page, per_page: data.per_page })
      Object.entries(filters).forEach(([k, v]) => { if (v) params.append(k, v) })
      const res = await api.get(`/api/incidents/?${params.toString()}`)
      setData(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load incidents')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchIncidents() }, [data.page])

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

  const openCreateModal = () => {
    setEditIncident(null)
    setFormData({ title: '', description: '', severity: 'medium', status: 'new' })
    setShowModal(true)
  }

  const openEditModal = (incident) => {
    setEditIncident(incident)
    setFormData({ title: incident.title, description: incident.description || '', severity: incident.severity, status: incident.status })
    setShowModal(true)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      if (editIncident) {
        await api.patch(`/api/incidents/${editIncident.id}/status`, { status: formData.status })
      } else {
        await api.post('/api/incidents', { title: formData.title, description: formData.description, severity: formData.severity, status: 'new' })
      }
      setShowModal(false)
      fetchIncidents()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save incident')
    }
  }

  const handleStatusChange = async (incidentId, newStatus) => {
    try {
      await api.patch(`/api/incidents/${incidentId}/status`, { status: newStatus })
      fetchIncidents()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update incident')
    }
  }

  const statusLabels = { new: 'New', investigating: 'Investigating', contained: 'Contained', resolved: 'Resolved' }
  const statusColors = { new: '#38bdf8', investigating: '#f59e0b', contained: '#a855f7', resolved: '#10b981' }
  const severityColors = { critical: '#ef4444', high: '#fb923c', medium: '#fbbf24', low: '#38bdf8' }

  return (
    <div className="incidents-page">
      <div className="page-header">
        <h1 className="page-heading">Incidents</h1>
        <button className="primary-btn" onClick={openCreateModal}>+ Create Incident</button>
      </div>

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
            <option value="new">New</option>
            <option value="investigating">Investigating</option>
            <option value="contained">Contained</option>
            <option value="resolved">Resolved</option>
          </select>
        </div>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="table-wrapper">
        <table className="incidents-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Title</th>
              <th>Severity</th>
              <th>Status</th>
              <th>Assigned To</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {data.incidents.map((inc, i) => (
              <tr key={inc.id}>
                <td>{i + 1}</td>
                <td><strong>{inc.title}</strong>{inc.description && <div className="small-text">({inc.description})</div>}</td>
                <td><span className="status-dot" style={{ background: severityColors[inc.severity] }}></span> {inc.severity}</td>
                <td><span className="status-badge" style={{ background: statusColors[inc.status] }}>{statusLabels[inc.status]}</span></td>
                <td>{inc.username || '-'}</td>
                <td>{new Date(inc.created_at).toLocaleString()}</td>
                <td>
                  {inc.status !== 'resolved' && (
                    <button className="action-btn" onClick={() => handleStatusChange(inc.id, 'investigating')}>Investigate</button>
                  )}
                  {inc.status === 'investigating' && (
                    <button className="action-btn" onClick={() => handleStatusChange(inc.id, 'contained')}>Contain</button>
                  )}
                  {inc.status === 'contained' && (
                    <button className="action-btn" onClick={() => handleStatusChange(inc.id, 'resolved')}>Resolve</button>
                  )}
                </td>
              </tr>
            ))}
            {data.incidents.length === 0 && <tr><td colSpan={7} style={{ textAlign: 'center', color: '#64748b', padding: '2rem' }}>No incidents found</td></tr>}
          </tbody>
        </table>
      </div>

      <div className="pagination">
        <button onClick={() => handlePageChange(data.page - 1)} disabled={data.page === 1 || loading}>Previous</button>
        <span>Page {data.page} of {Math.ceil(data.total / data.per_page)} ({data.total} total)</span>
        <button onClick={() => handlePageChange(data.page + 1)} disabled={data.page >= Math.ceil(data.total / data.per_page) || loading}>Next</button>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>{editIncident ? 'Edit Incident' : 'Create Incident'}</h3>
            <form onSubmit={handleSubmit}>
              <div className="modal-field">
                <label>Title</label>
                <input type="text" value={formData.title} onChange={(e) => setFormData(f => ({ ...f, title: e.target.value }))} required />
              </div>
              <div className="modal-field">
                <label>Description</label>
                <textarea value={formData.description} onChange={(e) => setFormData(f => ({ ...f, description: e.target.value }))} rows={3} />
              </div>
              <div className="modal-field">
                <label>Severity</label>
                <select value={formData.severity} onChange={(e) => setFormData(f => ({ ...f, severity: e.target.value }))}>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>
              {editIncident && (
                <div className="modal-field">
                  <label>Status</label>
                  <select value={formData.status} onChange={(e) => setFormData(f => ({ ...f, status: e.target.value }))}>
                    <option value="new">New</option>
                    <option value="investigating">Investigating</option>
                    <option value="contained">Contained</option>
                    <option value="resolved">Resolved</option>
                  </select>
                </div>
              )}
              <div className="modal-actions">
                <button type="button" className="secondary-btn" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="primary-btn">{editIncident ? 'Update' : 'Create'}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}