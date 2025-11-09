import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Don't auto-redirect on 401, let the component handle it
    // This prevents page refresh which loses console logs
    if (error.response?.status === 401) {
      // Only clear tokens, don't redirect
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      console.warn('Unauthorized request, tokens cleared')
    }
    return Promise.reject(error)
  }
)

// ========== API Methods ==========

// Categories
export const categoryAPI = {
  getAll: () => api.get('/api/categories/'),
  getById: (id) => api.get(`/api/categories/${id}`)
}

// Upload
export const uploadAPI = {
  uploadSingle: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/api/upload/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  uploadMultiple: (files) => {
    const formData = new FormData()
    files.forEach(file => formData.append('files', file))
    return api.post('/api/upload/upload-multiple', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  deleteImage: (filename) => api.delete(`/api/upload/${filename}`)
}

// Posts (Enhanced)
export const postAPI = {
  getAll: (params) => api.get('/api/posts/', { params }),
  getById: (id) => api.get(`/api/posts/${id}`),
  create: (data) => api.post('/api/posts/', data),
  update: (id, data) => api.put(`/api/posts/${id}`, data),
  delete: (id) => api.delete(`/api/posts/${id}`),
  getMatches: (id, params) => api.get(`/api/posts/${id}/matches`, { params }),
  advancedSearch: (params) => api.get('/api/posts/search/advanced', { params }),
  // Comments
  getComments: (postId) => api.get(`/api/posts/${postId}/comments`),
  createComment: (postId, content) => api.post(`/api/posts/${postId}/comments`, { content }),
  deleteComment: (commentId) => api.delete(`/api/posts/comments/${commentId}`)
}

// Claims
export const claimAPI = {
  create: (data) => api.post('/api/claims/', data),
  getMyClaims: () => api.get('/api/claims/my-claims'),
  getPostClaims: (postId) => api.get(`/api/claims/post/${postId}`),
  approve: (claimId, data) => api.post(`/api/claims/${claimId}/approve`, data),
  reject: (claimId, data) => api.post(`/api/claims/${claimId}/reject`, data),
  cancel: (claimId) => api.delete(`/api/claims/${claimId}`)
}

// Ratings
export const ratingAPI = {
  create: (data) => api.post('/api/ratings/', data),
  getClaimRatings: (claimId) => api.get(`/api/ratings/claim/${claimId}`),
  getUserRatings: (userId) => api.get(`/api/ratings/user/${userId}/received`),
  getUserRatingStats: (userId, limit = 5) => api.get(`/api/ratings/user/${userId}/stats`, { params: { limit } })
}

// Users
// Notifications
export const notificationAPI = {
  getNotifications: () => api.get('/api/users/notifications'),
  getUnreadCount: () => api.get('/api/users/notifications/unread-count'),
  markRead: (notificationId) => api.put(`/api/users/notifications/${notificationId}/read`)
}
export const userAPI = {
  getPublicInfo: (userId) => api.get(`/api/users/${userId}`),
  getUserPosts: (userId, params) => api.get(`/api/users/${userId}/posts`, { params }),
  getUserRatings: (userId, params) => api.get(`/api/users/${userId}/ratings`, { params })
}

export default api

