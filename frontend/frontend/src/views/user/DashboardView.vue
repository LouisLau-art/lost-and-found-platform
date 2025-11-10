<template>
  <div class="dashboard-container">
    <!-- Simple Top Navigation -->
    <nav class="top-nav">
      <div class="nav-content">
        <div class="nav-left">
          <router-link to="/" class="logo-link">
            <el-icon class="logo-icon" :size="28"><Clock /></el-icon>
            <span class="logo-text">Lost & Found</span>
          </router-link>
        </div>
        <div class="nav-right">
          <!-- Theme Toggle Button -->

          
          <!-- Admin Link (Only for Admins) -->
          <router-link 
            v-if="authStore.user?.is_admin" 
            to="/admin/users"
            class="admin-link"
          >
            <el-icon><User /></el-icon>
            <span>管理后台</span>
          </router-link>
          
          <!-- Notifications -->
          <el-badge :value="userStore.unreadCount" :hidden="userStore.unreadCount === 0">
            <el-button circle @click="showNotifications = !showNotifications" class="notification-btn">
              <el-icon><Bell /></el-icon>
            </el-button>
          </el-badge>
          
          <!-- User Dropdown -->
          <el-dropdown trigger="click" @command="handleCommand">
            <el-avatar :size="36" class="user-avatar">
              {{ userInitials }}
            </el-avatar>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  Profile
                </el-dropdown-item>
                <el-dropdown-item v-if="authStore.user?.is_admin" command="admin" divided>
                  <el-icon><User /></el-icon>
                  管理后台
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon>
                  Sign out
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </nav>

    <!-- Main Layout: Sidebar + Content -->
    <div class="main-layout">
      <!-- Left Sidebar -->
      <aside class="sidebar">
        <!-- User Info -->
        <div class="user-info">
          <el-avatar :size="80" class="user-avatar-large">
            <span class="avatar-text">{{ userInitials }}</span>
          </el-avatar>
          <h2 class="user-name">{{ authStore.user?.name || 'Louis' }}</h2>
          <p class="user-email">{{ authStore.user?.email }}</p>
        </div>

        <el-divider class="sidebar-divider" />

        <!-- Credit Score -->
        <div class="credit-score">
          <div class="credit-label">Credit Score</div>
          <div class="credit-value">{{ authStore.user?.credit_score || 100 }}</div>
          <div class="credit-status">
            <el-icon class="status-icon"><CircleCheck /></el-icon>
            <span>Excellent standing</span>
          </div>
        </div>

        <el-divider class="sidebar-divider" />

        <!-- Navigation Menu -->
        <el-menu
          :default-active="activeMenu"
          class="sidebar-menu"
          @select="handleMenuSelect"
        >
          <el-menu-item index="dashboard">
            <el-icon><Monitor /></el-icon>
            <span>Dashboard</span>
          </el-menu-item>
          <el-menu-item index="activity">
            <el-icon><TrendCharts /></el-icon>
            <span>My Activity</span>
          </el-menu-item>
          <el-menu-item index="forum">
            <el-icon><Document /></el-icon>
            <span>Forum</span>
          </el-menu-item>
          <el-menu-item index="profile">
            <el-icon><User /></el-icon>
            <span>Profile Settings</span>
          </el-menu-item>
        </el-menu>
      </aside>

      <!-- Right Content Area -->
      <main class="content-area">
        <!-- Welcome Section -->
        <div class="welcome-section">
          <h1 class="welcome-title">
            Welcome back, {{ authStore.user?.name || 'Louis' }}! 👋
          </h1>
          <p class="welcome-subtitle">
            Manage your lost and found items, participate in the community forum, and help others reunite with their belongings.
          </p>
        </div>

        <!-- Primary CTA Buttons -->
        <div class="cta-section">
          <button class="cta-button cta-lost hover-lift" @click="handleCreatePost('lost')">
            <div class="cta-content">
              <el-icon class="cta-icon" :size="28"><Search /></el-icon>
              <span class="cta-text">I Lost Something</span>
            </div>
          </button>
          <button class="cta-button cta-found cta-found-outlined hover-lift" @click="handleCreatePost('found')">
            <div class="cta-content">
              <el-icon class="cta-icon" :size="28"><Flag /></el-icon>
              <span class="cta-text">I Found Something</span>
            </div>
          </button>
        </div>

        <!-- Admin Panel (Only for Admins) -->
        <div v-if="authStore.user?.is_admin" class="admin-panel">
          <div class="panel-header">
            <el-icon class="panel-icon"><User /></el-icon>
            <span class="panel-title">管理员面板</span>
          </div>
          <div class="admin-buttons">
            <el-button 
              type="warning" 
              size="large" 
              @click="$router.push('/admin/users')" 
              class="admin-btn hover-scale"
              :class="{ 'admin-btn-active': $route.path === '/admin/users' }"
            >
              <div class="btn-content">
                <el-icon class="btn-icon"><User /></el-icon>
                <span>用户管理</span>
              </div>
            </el-button>
            <el-button 
              plain
              type="warning"
              size="large" 
              @click="$router.push('/admin/posts')" 
              class="admin-btn admin-btn-plain hover-scale"
              :class="{ 'admin-btn-active': $route.path === '/admin/posts' }"
            >
              <div class="btn-content">
                <el-icon class="btn-icon"><Document /></el-icon>
                <span>帖子管理</span>
              </div>
            </el-button>
          </div>
        </div>

        <!-- Activity Tabs -->
        <div class="activity-section">
          <el-tabs v-model="activeTab" class="activity-tabs">
            <!-- Tab 1: My Recent Posts -->
            <el-tab-pane name="posts">
              <template #label>
                <span class="tab-label">
                  <el-icon class="tab-icon"><Document /></el-icon>
                  <span>My Recent Posts</span>
                </span>
              </template>
              <div v-if="userPostsCount === 0" class="empty-state">
                <el-empty description="You haven't posted anything yet. Why not report a found item to help someone?">
                  <el-button type="primary" @click="$router.push('/forum/create')">
                    Create Your First Post
                  </el-button>
                </el-empty>
              </div>
              <div v-else class="post-list">
                <div class="list-info">You have <strong>{{ userPostsCount }}</strong> post(s)</div>
                <el-button type="primary" size="default" @click="$router.push('/forum')">
                  <el-icon><Document /></el-icon>
                  View All Posts
                </el-button>
              </div>
            </el-tab-pane>

            <!-- Tab 2: My Recent Claims -->
            <el-tab-pane name="claims">
              <template #label>
                <span class="tab-label">
                  <el-icon class="tab-icon"><Tickets /></el-icon>
                  <span>My Recent Claims</span>
                </span>
              </template>
              <div v-if="claimsCount === 0" class="empty-state">
                <el-empty description="You have no active claims">
                  <el-button type="success" @click="$router.push('/forum')">
                    Browse Items to Claim
                  </el-button>
                </el-empty>
              </div>
              <div v-else class="claim-list">
                <div class="list-info">You have <strong>{{ claimsCount }}</strong> claim(s)</div>
                <el-button type="success" size="default" @click="$router.push('/claims')">
                  <el-icon><Tickets /></el-icon>
                  View All Claims
                </el-button>
              </div>
            </el-tab-pane>

            <!-- Tab 3: Recent Activity -->
            <el-tab-pane name="activity">
              <template #label>
                <span class="tab-label">
                  <el-icon class="tab-icon"><TrendCharts /></el-icon>
                  <span>Recent Activity</span>
                </span>
              </template>
              <div class="activity-feed">
                <el-timeline>
                  <el-timeline-item timestamp="Recently" placement="top">
                    <el-text>New items are being posted on the platform</el-text>
                  </el-timeline-item>
                  <el-timeline-item timestamp="Today" placement="top">
                    <el-text>Community members are actively helping each other</el-text>
                  </el-timeline-item>
                </el-timeline>
                <el-button type="info" text class="explore-btn" @click="$router.push('/forum')">
                  Explore the Community Forum →
                </el-button>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>

        <!-- Forum Link -->
        <div class="forum-link-section">
          <el-link :underline="false" class="forum-link" @click="$router.push('/forum')">
            <span>Explore the Community Forum</span>
            <el-icon class="link-icon"><ArrowRight /></el-icon>
          </el-link>
        </div>
      </main>
    </div>

    <!-- Notifications Drawer -->
    <el-drawer
      v-model="showNotifications"
      title="Notifications"
      direction="rtl"
      size="400px"
    >
      <div v-if="userStore.notifications.length === 0" class="notification-empty">
        <el-empty description="No notifications" />
      </div>
      <div v-else>
        <el-button type="primary" size="small" class="mark-all-btn" @click="markAllAsRead">
          Mark All as Read
        </el-button>
        <div v-for="notification in userStore.notifications" :key="notification.id" class="notification-item">
          <el-card :body-style="{ padding: '12px' }" shadow="hover" @click="markAsRead(notification.id)" class="notification-card">
            <div class="notification-content">
              <el-icon v-if="!notification.is_read" class="unread-icon"><Bell /></el-icon>
              <div class="notification-text">
                <p class="notification-message">{{ notification.content }}</p>
                <p class="notification-time">{{ formatRelativeTime(notification.created_at) }}</p>
              </div>
            </div>
          </el-card>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUserStore } from '@/stores/user'
import { useForumStore } from '@/stores/forum'
import { claimAPI } from '@/api'
import { 
  Clock, Bell, User, SwitchButton, CircleCheck, Document, 
  Tickets, Search, Flag, TrendCharts, ArrowRight, Monitor,
  Sunny, Moon
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()
const userStore = useUserStore()
const forumStore = useForumStore()

const showNotifications = ref(false)
const activeTab = ref('posts')
const activeMenu = ref('dashboard')
const userPostsCount = ref(0)
const claimsCount = ref(0)

const userInitials = computed(() => {
  if (!authStore.user?.name) return 'U'
  return authStore.user.name.split(' ').map(n => n[0]).join('').toUpperCase()
})

const handleCommand = (command) => {
  if (command === 'logout') {
    authStore.logout()
    router.push('/')
  } else if (command === 'profile') {
    router.push('/profile')
  } else if (command === 'admin') {
    router.push('/admin/users')
  }
}

const handleMenuSelect = (index) => {
  activeMenu.value = index
  if (index === 'dashboard') {
    // Stay on current page
  } else if (index === 'activity') {
    router.push('/user/activity')
  } else if (index === 'forum') {
    router.push('/forum')
  } else if (index === 'profile') {
    router.push('/profile')
  }
}

const handleCreatePost = (type) => {
  router.push({
    path: '/forum/create',
    query: { type }
  })
  ElMessage.success(`Creating ${type} post...`)
}

const markAsRead = async (notificationId) => {
  try {
    await userStore.markNotificationRead(notificationId)
  } catch (error) {
    console.error('Failed to mark notification as read:', error)
  }
}

const markAllAsRead = async () => {
  try {
    await userStore.markAllNotificationsRead()
    showNotifications.value = false
  } catch (error) {
    console.error('Failed to mark all notifications as read:', error)
  }
}

const formatRelativeTime = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffInSeconds = Math.floor((now - date) / 1000)
  
  if (diffInSeconds < 60) {
    return `${diffInSeconds}s ago`
  } else if (diffInSeconds < 3600) {
    const minutes = Math.floor(diffInSeconds / 60)
    return `${minutes}m ago`
  } else if (diffInSeconds < 86400) {
    const hours = Math.floor(diffInSeconds / 3600)
    return `${hours}h ago`
  } else if (diffInSeconds < 604800) {
    const days = Math.floor(diffInSeconds / 86400)
    return `${days}d ago`
  } else {
    return date.toLocaleDateString()
  }
}

onMounted(async () => {
  // Dashboard initialization
  
  // Load notifications and unread count
  try {
    await userStore.getNotifications()
    await userStore.getUnreadCount()
  } catch (error) {
    console.error('Failed to load notifications:', error)
  }
  
  // Load user's posts count
  try {
    await forumStore.fetchPosts(1, 100)  // 获取前100个帖子
    // 确保posts是数组
    const posts = Array.isArray(forumStore.posts) ? forumStore.posts : []
    userPostsCount.value = posts.filter(post => post.author_id === authStore.user?.id).length
  } catch (error) {
    console.error('Failed to load posts:', error)
    userPostsCount.value = 0
  }
  
  // Load claims count
  try {
    const response = await claimAPI.getMyClaims()
    claimsCount.value = response.data.length
  } catch (error) {
    console.error('Failed to load claims:', error)
  }
})

onUnmounted(() => {})
</script>

<style scoped>
/* ===== Dashboard Container ===== */
.dashboard-container {
  min-height: 100vh;
  background-color: var(--bg-base);
  color: var(--text-primary);
}

/* ===== Top Navigation ===== */
.top-nav {
  background-color: var(--bg-surface);
  border-bottom: 1px solid var(--border-base);
  backdrop-filter: blur(10px);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
  height: 64px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-left {
  display: flex;
  align-items: center;
}

.logo-link {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: var(--text-primary);
  font-size: 1.25rem;
  font-weight: 700;
  transition: color 0.3s ease;
}

.logo-link:hover {
  color: var(--primary);
}

.logo-icon {
  margin-right: 0.75rem;
}

.logo-text {
  font-size: 1.25rem;
  font-weight: 700;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.theme-toggle-btn {
  background-color: var(--bg-muted);
  border-color: var(--border-base);
}

.admin-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  transition: all 0.3s ease;
}

.admin-link:hover {
  color: var(--primary);
  background-color: var(--bg-muted);
}

.notification-btn {
  background-color: var(--bg-muted);
  border-color: var(--border-base);
}

.user-avatar {
  cursor: pointer;
  background: var(--primary);
  font-weight: 600;
}

/* ===== Main Layout ===== */
.main-layout {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  display: flex;
  gap: 2rem;
}

/* ===== Sidebar ===== */
.sidebar {
  width: 280px;
  flex-shrink: 0;
  background-color: var(--bg-surface);
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.user-info {
  text-align: center;
}

.user-avatar-large {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  margin-bottom: 1rem;
}

.avatar-text {
  font-size: 2rem;
  font-weight: 700;
}

.user-name {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0.5rem 0;
}

.user-email {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin: 0;
}

.sidebar-divider {
  margin: 1.5rem 0;
  border-color: var(--border-base);
}

.credit-score {
  text-align: center;
  margin: 1rem 0;
}

.credit-label {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.credit-value {
  font-size: 3rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.credit-status {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  color: var(--success);
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

.status-icon {
  font-size: 1rem;
}

.sidebar-menu {
  margin-top: 2rem;
}

.sidebar-menu {
  background-color: transparent;
  border: none;
}

.sidebar-menu :deep(.el-menu-item) {
  color: #6b7280;
  border-radius: 0.5rem;
  margin-bottom: 0.5rem;
  transition: all 0.3s ease;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background-color: var(--bg-muted);
  color: var(--text-primary);
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background-color: var(--bg-muted);
  color: var(--primary);
  font-weight: 500;
}

/* ===== Content Area ===== */
.content-area {
  flex: 1;
  min-width: 0;
}

.welcome-section {
  margin-bottom: 2rem;
  animation: slideInDown 0.5s ease-out;
}

.welcome-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.75rem;
}

.welcome-subtitle {
  font-size: 1.125rem;
  color: var(--text-secondary);
  line-height: 1.75;
}

/* ===== CTA Buttons ===== */
.cta-section {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
}

.cta-button {
  height: 120px;
  border-radius: 1rem;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
}

.cta-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.cta-lost {
  background: var(--primary);
  color: var(--text-inverse);
}

.cta-lost:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px -4px rgba(59, 130, 246, 0.4);
}

.cta-found {
  background-color: transparent;
  border: 2px solid var(--success) !important;
  color: var(--success);
}

.cta-found:hover {
  background-color: var(--success);
  color: var(--text-inverse);
  transform: translateY(-4px);
  box-shadow: 0 12px 24px -4px rgba(16, 185, 129, 0.4);
}

.cta-found-outlined {
  border-width: 2px !important;
}

.cta-icon {
  font-size: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cta-text {
  font-size: 1.125rem;
  font-weight: 700;
}

/* ===== Admin Panel ===== */
.admin-panel {
  background-color: #ffffff;
  background-color: var(--bg-surface);
  border-radius: 1rem;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.panel-icon {
  font-size: 1.25rem;
  color: var(--primary);
}

.panel-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
}

.admin-buttons {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.admin-btn {
  width: 100%;
  height: 80px;
  font-size: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease !important;
  border-width: 2px !important;
}

.btn-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.admin-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px -4px rgba(245, 158, 11, 0.4);
}

.admin-btn-plain {
  background-color: var(--bg-color-muted) !important;
  color: var(--text-secondary) !important;
  border-color: var(--border-color-base) !important;
}

.admin-btn-plain .el-icon {
  color: var(--text-secondary) !important;
}

.admin-btn-active {
  background-color: var(--warning) !important;
  border-color: var(--warning) !important;
  color: var(--text-inverse) !important;
}

.admin-btn-active .el-icon {
  color: var(--text-inverse) !important;
}

.btn-icon {
  font-size: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ===== Activity Section ===== */
.activity-section {
  background-color: var(--bg-surface);
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.activity-tabs :deep(.el-tabs__header) {
  background-color: transparent;
  border-bottom: 2px solid var(--border-base);
  margin-bottom: 1.5rem;
}

.activity-tabs :deep(.el-tabs__nav) {
  border: none;
}

.activity-tabs :deep(.el-tabs__item) {
  color: var(--text-muted);
  border: none;
  padding: 1rem 1.5rem;
  font-weight: 500;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.activity-tabs :deep(.el-tabs__item:hover) {
  color: var(--text-secondary);
}

.activity-tabs :deep(.el-tabs__item.is-active) {
  color: var(--primary);
  font-weight: 600;
}

.activity-tabs :deep(.el-tabs__active-bar) {
  background-color: var(--primary);
  height: 3px;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tab-icon {
  font-size: 1.125rem;
}

.empty-state :deep(.el-empty__description) {
  color: var(--text-muted);
}

.list-info {
  color: var(--text-primary);
  font-size: 1rem;
  margin-bottom: 1rem;
  font-weight: 500;
}

.list-info strong {
  color: var(--primary);
  font-size: 1.25rem;
  font-weight: 700;
}

.activity-feed :deep(.el-timeline-item__timestamp) {
  color: var(--text-muted);
}

.activity-feed :deep(.el-text) {
  color: var(--text-primary);
}

.explore-btn {
  margin-top: 1rem;
}

/* ===== Forum Link ===== */
.forum-link-section {
  text-align: center;
  margin-top: 2rem;
}

.forum-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--primary);
  font-size: 1.125rem;
  font-weight: 600;
  transition: all 0.3s ease;
}

.forum-link:hover {
  color: var(--primary);
  transform: translateX(4px);
}

.link-icon {
  font-size: 1.25rem;
}

/* ===== Notifications ===== */
.notification-empty {
  padding: 2rem 0;
  text-align: center;
}

.mark-all-btn {
  width: 100%;
  margin-bottom: 1rem;
}

.notification-list {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.notification-item {
  padding: 1rem;
  border-radius: 0.5rem;
  margin-bottom: 0.75rem;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: var(--bg-muted);
  border: 1px solid var(--border-base);
}

.notification-item.unread {
  background-color: var(--bg-muted);
  border: 1px solid var(--border-base);
}

.notification-item:hover {
  background-color: var(--bg-muted);
}

.notification-card {
  cursor: pointer;
  transition: all 0.3s ease;
}

.notification-card:hover {
  transform: translateX(-4px);
}

.notification-content {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}

.unread-icon {
  margin-top: 0.25rem;
  flex-shrink: 0;
}

.notification-text {
  flex: 1;
}

.notification-message {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.25rem 0;
}

.notification-time {
  font-size: 0.75rem;
  color: var(--text-secondary);
  margin: 0;
}

/* ===== Animations ===== */
@keyframes slideInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ===== Responsive Design ===== */
@media (max-width: 1024px) {
  .main-layout {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .nav-content {
    padding: 0 1rem;
  }
  
  .main-layout {
    padding: 1rem;
  }
  
  .welcome-title {
    font-size: 1.75rem;
  }
  
  .cta-section {
    grid-template-columns: 1fr;
  }
  
  .cta-button {
    height: 100px;
  }
  
  .admin-buttons {
    grid-template-columns: 1fr;
  }
}
</style>

