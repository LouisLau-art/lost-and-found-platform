import { defineStore } from 'pinia'
import api from '@/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('access_token'),
    isLoading: false,
    error: null
  }),

  getters: {
    isAuthenticated: (state) => !!state.token && !!state.user,
    userInfo: (state) => state.user
  },

  actions: {
    async login(credentials) {
      this.isLoading = true
      this.error = null
      
      try {
        const response = await api.post('/api/auth/login', credentials)
        const { access_token } = response.data
        
        this.token = access_token
        localStorage.setItem('access_token', access_token)
        
        // Get user info
        await this.getCurrentUser()
        
        return { success: true }
      } catch (error) {
        this.error = error.response?.data?.detail || 'Login failed'
        return { success: false, error: this.error }
      } finally {
        this.isLoading = false
      }
    },

    async register(userData) {
      this.isLoading = true
      this.error = null
      
      try {
        const response = await api.post('/api/auth/register', userData)
        return { success: true, user: response.data }
      } catch (error) {
        this.error = error.response?.data?.detail || 'Registration failed'
        return { success: false, error: this.error }
      } finally {
        this.isLoading = false
      }
    },

    async getCurrentUser() {
      try {
        const response = await api.get('/api/auth/me')
        this.user = response.data
        localStorage.setItem('user', JSON.stringify(response.data))
        console.log('User info loaded:', this.user)
        return response.data
      } catch (error) {
        console.error('Failed to get current user:', error)
        this.logout()
        throw error
      }
    },

    logout() {
      this.user = null
      this.token = null
      this.error = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
    },

    clearError() {
      this.error = null
    },

    // Initialize auth state from localStorage
    initAuth() {
      const token = localStorage.getItem('access_token')
      const user = localStorage.getItem('user')
      
      if (token && user) {
        this.token = token
        this.user = JSON.parse(user)
      }
    }
  }
})

