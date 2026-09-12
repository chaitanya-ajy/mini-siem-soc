import React, { useEffect, useState } from 'react'
import api from '../services/api'
import '../styles.css'
import './ThreatDetection.css'

export default function ThreatDetectionPage() {
  const [loading, setLoading] = useState(false)
  const [rules, setRules] = useState([])
  const [sampleResults, setSampleResults] = useState([])
  const [error, setError] = useState(null)
  const [showCreate, setShowCreate] = useState(false)
  const [formData, setFormData] = useState({ name: '', condition_field: '', operator: 'contains', value: '', severity: 'medium', enabled: true })

  const fetchRules = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await api.get('/api/threat-detection/rules')
      setRules(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load rules')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchRules() }, [])

  const runSample = async () => {
    try {
      const res = await api.get('/api/threat-detection/sample')
      setSampleResults(res.data.sample_threats || [])
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to run sample')
    }
  }

  const handleCreateRule = async (e) => {
    e.preventDefault()
    try {
      await api.post('/api/threat-detection/rules', formData)
      setShowCreate(false)
      setFormData({ name: '', condition_field: '', operator: 'contains', value: '', severity: 'medium', enabled: true })
      fetchRules()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create rule')
    }
  }

  const handleDeleteRule = async (ruleId) => {
    try {
      await api.delete(`/api/threat-detection/rules?rule_id=${ruleId}`)
      fetchRules()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete rule')
    }
  }

  const toggleRule = async (rule) => {
    try {
      await api.post(`/api/threat-detection/rules/${rule.id}/toggle`, { enabled: !rule.enabled })
      fetchRules()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to toggle rule')
    }
  }

  const operatorLabels = { equals: 'equals', contains: 'contains', regex: 'regex', greater_than: 'greater_than', less_than: 'less_than' }
  const severityColors = { critical: '#ef4444', high: '#fb923c', medium: '#fbbf24', low: '#38bdf8' }

  return (
    <div className="threats-page">
      <div className="page-header">
        <h1 className="page-heading">Threat Detection Rules</h1>
        <button className="primary-btn" onClick={() => setShowCreate(true)}>+ New Rule</button>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="card">
        <h3>Threat Detection Engine</h3>
        <p style={{ color: '#94a3b8', marginBottom: '1rem' }}>Built-in detection rules automatically analyze logs for threats like brute force, SQL injection, port scanning, and suspicious external activity.</p>
        <button className="primary-btn" onClick={runSample}>Run Sample Detection</button>
        {sampleResults.length > 0 && (
          <div className="sample-results" style={{ marginTop: '1rem' }}>
            <h4>Sample Results</h4>
            {sampleResults.map((r, i) => (
              <div key={i} className="sample-result" style={{ borderLeft: `4px solid ${severityColors[r.alert_severity]}` }}>
                <strong>{r.alert_title}</strong>
                <p style={{ color: '#94a3b8', fontSize: '.85rem' }}>{r.alert_description}</p>
                <span className="severity-badge" style={{ background: severityColors[r.alert_severity] }}>{r.alert_severity}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="card" style={{ marginTop: '1rem' }}>
        <h3>Custom Alert Rules</h3>
        {loading && <p style={{ color: '#94a3b8' }}>Loading...</p>}
        {!loading && rules.length === 0 && <p style={{ color: '#64748b' }}>No custom rules configured.</p>}
        <table className="threats-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Field</th>
              <th>Operator</th>
              <th>Value</th>
              <th>Severity</th>
              <th>Enabled</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {rules.map((rule) => (
              <tr key={rule.id}>
                <td><strong>{rule.name}</strong></td>
                <td>{rule.condition_field}</td>
                <td>{operatorLabels[rule.operator] || rule.operator}</td>
                <td><code>{rule.value}</code></td>
                <td><span className="severity-badge" style={{ background: severityColors[rule.severity] }}>{rule.severity}</span></td>
                <td>{rule.enabled ? 'Yes' : 'No'}</td>
                <td>
                  <button className="action-btn" onClick={() => toggleRule(rule)} style={{ marginRight: '.5rem' }}>{rule.enabled ? 'Disable' : 'Enable'}</button>
                  <button className="action-btn" style={{ background: '#7f1d1d', borderColor: '#dc2626', color: '#fca5a5' }} onClick={() => handleDeleteRule(rule.id)}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showCreate && (
        <div className="modal-overlay" onClick={() => setShowCreate(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Create Alert Rule</h3>
            <form onSubmit={handleCreateRule}>
              <div className="modal-field">
                <label>Rule Name</label>
                <input type="text" value={formData.name} onChange={(e) => setFormData(f => ({ ...f, name: e.target.value }))} required />
              </div>
              <div className="modal-field">
                <label>Condition Field</label>
                <select value={formData.condition_field} onChange={(e) => setFormData(f => ({ ...f, condition_field: e.target.value }))} required>
                  <option value="">Select field</option>
                  <option value="source_ip">Source IP</option>
                  <option value="dest_ip">Dest IP</option>
                  <option value="action">Action</option>
                  <option value="protocol">Protocol</option>
                  <option value="severity">Severity</option>
                </select>
              </div>
              <div className="modal-field">
                <label>Operator</label>
                <select value={formData.operator} onChange={(e) => setFormData(f => ({ ...f, operator: e.target.value }))}>
                  <option value="equals">equals</option>
                  <option value="contains">contains</option>
                  <option value="regex">regex</option>
                  <option value="greater_than">greater_than</option>
                  <option value="less_than">less_than</option>
                </select>
              </div>
              <div className="modal-field">
                <label>Value</label>
                <input type="text" value={formData.value} onChange={(e) => setFormData(f => ({ ...f, value: e.target.value }))} required />
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
              <div className="modal-actions">
                <button type="button" className="secondary-btn" onClick={() => setShowCreate(false)}>Cancel</button>
                <button type="submit" className="primary-btn">Create Rule</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}