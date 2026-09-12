import React from 'react'
import { useAuth } from '../context/AuthContext.jsx'
import { useNavigate } from 'react-router-dom'
import './Header.css'

export default function Header() {
  const { user } = useAuth()
  const navigate = useNavigate()
  return (
    <header className="header">
      <div className="header-left">
        <h2 className="page-title">Mini SIEM & SOC Dashboard</h2>
      </div>
      <div className="header-right">
        <span className="header-user">{user?.role?.toUpperCase()} · {user?.username}</span>
        <button className="header-btn" onClick={() => navigate('/dashboard')}>🏠 Home</button>
      </div>
    </header>
  )
}