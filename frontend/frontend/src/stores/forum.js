import { defineStore } from 'pinia'
import api from '@/api'

export const useForumStore = defineStore('forum', {
  state: () => ({
    posts: [],
    currentPost: null,
    comments: [],
    pagination: {
      page: 1,
      limit: 10,
      total: 0
    },
    isLoading: false,
    error: null
  }),

  actions: {
    async fetchPosts(page = 1, limit = 10) {
      this.isLoading = true
      this.error = null
      
      try {
        const skip = (page - 1) * limit
        const response = await api.get(`/api/posts?skip=${skip}&limit=${limit}`)
        
        // 处理新的响应格式 {data: [...], total: number}
        if (response.data && response.data.data) {
          this.posts = response.data.data
          this.pagination.total = response.data.total
        } else {
          // 兼容旧格式
          this.posts = Array.isArray(response.data) ? response.data : []
          this.pagination.total = this.posts.length
        }
        
        this.pagination.page = page
        this.pagination.limit = limit
        return this.posts
      } catch (error) {
        console.error('fetchPosts error:', error)
        this.error = error.response?.data?.detail || 'Failed to fetch posts'
        this.posts = []  // 确保posts是数组
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async fetchPost(postId) {
      this.isLoading = true
      this.error = null
      
      try {
        const response = await api.get(`/api/posts/${postId}`)
        this.currentPost = response.data
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to fetch post'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async createPost(postData) {
      this.isLoading = true
      this.error = null
      
      try {
        const response = await api.post('/api/posts', postData)
        this.posts.unshift(response.data) // Add to beginning of list
        return { success: true, post: response.data }
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to create post'
        return { success: false, error: this.error }
      } finally {
        this.isLoading = false
      }
    },

    async updatePost(postId, postData) {
      this.isLoading = true
      this.error = null
      
      try {
        const response = await api.put(`/api/posts/${postId}`, postData)
        
        // Update in posts list
        const index = this.posts.findIndex(p => p.id === postId)
        if (index !== -1) {
          this.posts[index] = response.data
        }
        
        // Update current post if it's the same
        if (this.currentPost && this.currentPost.id === postId) {
          this.currentPost = response.data
        }
        
        return { success: true, post: response.data }
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to update post'
        return { success: false, error: this.error }
      } finally {
        this.isLoading = false
      }
    },

    async deletePost(postId) {
      this.isLoading = true
      this.error = null
      
      try {
        await api.delete(`/api/posts/${postId}`)
        
        // Remove from posts list
        this.posts = this.posts.filter(p => p.id !== postId)
        
        // Clear current post if it's the same
        if (this.currentPost && this.currentPost.id === postId) {
          this.currentPost = null
        }
        
        return { success: true }
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to delete post'
        return { success: false, error: this.error }
      } finally {
        this.isLoading = false
      }
    },

    async fetchComments(postId) {
      try {
        const response = await api.get(`/api/posts/${postId}/comments`)
        this.comments = response.data
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to fetch comments'
        throw error
      }
    },

    async createComment(postId, commentData) {
      this.isLoading = true
      this.error = null
      
      try {
        const response = await api.post(`/api/posts/${postId}/comments`, commentData)
        this.comments.push(response.data)
        return { success: true, comment: response.data }
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to create comment'
        return { success: false, error: this.error }
      } finally {
        this.isLoading = false
      }
    },

    async deleteComment(commentId) {
      this.isLoading = true
      this.error = null
      
      try {
        await api.delete(`/api/posts/comments/${commentId}`)
        this.comments = this.comments.filter(c => c.id !== commentId)
        return { success: true }
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to delete comment'
        return { success: false, error: this.error }
      } finally {
        this.isLoading = false
      }
    },

    clearError() {
      this.error = null
    },

    clearCurrentPost() {
      this.currentPost = null
      this.comments = []
    }
  }
})

