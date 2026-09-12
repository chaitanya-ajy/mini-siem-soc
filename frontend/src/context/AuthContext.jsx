import React, { createContext, useContext, useState, useEffect } from 'react'
import api from '../services/api'
const AuthContext = createContext()
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  useEffect(() => {
    const loadUser = async () => {
      try {
        const res = await api.get('/auth/me')
        setUser(res.data)
      } catch (err) {
        setUser(null)
      } finally { setLoading(false) }
    }
    loadUser()
  }, [])
  const login = async (username, password) => {
      const res = await api.post('/auth/login', { username, password })
      localStorage.setItem('access_token', res.data.access_token)
      // Fetch user info after login
      const userRes = await api.get('/auth/me')
      setUser(userRes.data)
      return res.data
    }
  const logout = async () => {
    await api.post('/auth/logout')
    localStorage.removeItem('access_token')
    setUser(null)
  }
  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}
export const useAuth = () => useContext(AuthContext)