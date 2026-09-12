import axios from 'axios'

const baseURL = (import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || '') + '/api'
const api = axios.create({ baseURL, withCredentials: true })
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})
api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) localStorage.removeItem('access_token')
    return Promise.reject(err)
  }
)
export default api