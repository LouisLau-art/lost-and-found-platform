import { defineStore } from 'pinia'
import { notificationAPI, userAPI } from '@/api'

export const useUserStore = defineStore('user', {
  state: () => ({
    profile: null,
    notifications: [],
    unreadCount: 0,
    isLoading: false,
    error: null
  }),

  actions: {
    async updateProfile(profileData) {
      this.isLoading = true
      this.error = null
      
      try {
        // 这里应该使用userAPI，但目前api中没有定义updateProfile方法
        // 暂时实现一个直接的API调用
        const api = await import('@/api').then(module => module.default)
        const response = await api.put('/api/users/profile', profileData)
        this.profile = response.data
        return { success: true, profile: response.data }
      } catch (error) {
        this.error = error.response?.data?.detail || 'Profile update failed'
        console.error('Profile update error:', error)
        return { success: false, error: this.error }
      } finally {
        this.isLoading = false
      }
    },

    async getNotifications() {
      try {
        const response = await notificationAPI.getNotifications()
        this.notifications = response.data || []
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to fetch notifications'
        console.error('Get notifications error:', error)
        // 不抛出错误，让轮询继续进行
        return []
      }
    },

    async getUnreadCount() {
      try {
        const response = await notificationAPI.getUnreadCount()
        this.unreadCount = response.data.unread_count
        return response.data.unread_count
      } catch (error) {
        console.error('Failed to fetch unread count:', error)
        return 0
      }
    },

    async markNotificationRead(notificationId) {
      try {
        await notificationAPI.markRead(notificationId)
        // Update local state
        const notification = this.notifications.find(n => n.id === notificationId)
        if (notification) {
          notification.is_read = true
        }
        this.unreadCount = Math.max(0, this.unreadCount - 1)
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to mark notification as read'
        console.error('Mark notification read error:', error)
        // 不抛出错误，让用户体验更流畅
      }
    },

    clearError() {
      this.error = null
    }
  }
})

