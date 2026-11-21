import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  withCredentials: true, // Sends session cookies
});

// Interceptor to automatically append JWT Bearer Token and Anti-CSRF Header
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  const csrfToken = localStorage.getItem('csrf_token');

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  // Attach Anti-CSRF Header for state-changing calls
  if (csrfToken && ['post', 'put', 'delete', 'patch'].includes(config.method.toLowerCase())) {
    config.headers['X-CSRF-Token'] = csrfToken;
  }

  return config;
}, (error) => {
  return Promise.reject(error);
});

export default api;