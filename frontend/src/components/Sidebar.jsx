import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import './Sidebar.css'

const items = [
  { to: '/dashboard', icon: '📊', label: 'Dashboard' },
  { to: '/logs', icon: '📜', label: 'Logs' },
  { to: '/alerts', icon: '🚨', label: 'Alerts' },
  { to: '/incidents', icon: '📋', label: 'Incidents' },
  { to: '/threats', icon: '🛡️', label: 'Threat Detection' },
]

export default function Sidebar() {
  const { user, logout } = useAuth()
  const location = useLocation()
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <span className="logo">🛡️</span>
        <span className="logo-text">Mini SIEM</span>
      </div>
      <nav className="sidebar-nav">
        {items.map((item) => (
          <Link key={item.to} to={item.to} className={location.pathname === item.to ? 'nav-item active' : 'nav-item'}>
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
          </Link>
        ))}
      </nav>
      <div className="sidebar-footer">
        <div className="user-info">
          <span className="user-avatar">{user?.username?.charAt(0)?.toUpperCase() || 'U'}</span>
          <div className="user-details">
            <span className="user-name">{user?.username}</span>
            <span className="user-role">{user?.role}</span>
          </div>
        </div>
        <button className="logout-btn" onClick={logout}>Logout</button>
      </div>
    </aside>
  )
}