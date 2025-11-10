<template>
  <div class="user-profile-page">
    <!-- Top Navigation -->
    <nav class="top-nav">
      <div class="nav-content">
        <router-link to="/" class="logo-link">
          <el-icon class="logo-icon" :size="28"><Compass /></el-icon>
          <span class="logo-text">Lost & Found</span>
        </router-link>
        <div class="nav-actions">
          <el-button text class="nav-btn" @click="$router.back()">
            <el-icon><ArrowLeft /></el-icon>
            <span>返回</span>
          </el-button>
          <el-button v-if="authStore.isAuthenticated" text class="nav-btn" @click="$router.push('/dashboard')">
            <el-icon><Monitor /></el-icon>
            <span>仪表盘</span>
          </el-button>
        </div>
      </div>
    </nav>

    <!-- Main Content Container -->
    <main class="main-container">
      <!-- Loading State -->
      <div v-if="loading" class="loading-wrapper">
        <el-skeleton :rows="8" animated />
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="error-wrapper">
        <el-result icon="error" title="加载失败" :sub-title="error">
          <template #extra>
            <el-button type="primary" @click="loadUserInfo">
              <el-icon><Refresh /></el-icon>
              重试
            </el-button>
          </template>
        </el-result>
      </div>

      <!-- User Profile Content -->
      <div v-else-if="userInfo" class="profile-content">
        <!-- Profile Header Card -->
        <el-card class="profile-header-card" shadow="hover">
          <div class="header-layout">
            <!-- Left: Avatar -->
            <div class="avatar-section">
              <el-avatar :size="120" class="user-avatar-large">
                <span class="avatar-text">{{ userInitial }}</span>
              </el-avatar>
            </div>

            <!-- Right: User Info -->
            <div class="user-info-section">
              <h1 class="user-name">{{ userInfo.name }}</h1>
              
              <!-- Credit Score Tag -->
              <div class="credit-score-wrapper">
                <span class="credit-label">信用分:</span>
                <el-tag :type="getCreditType(userInfo.credit_score)" size="large" class="credit-tag" effect="light">
                  {{ userInfo.credit_score }}
                </el-tag>
              </div>

              <!-- User Stats using el-descriptions -->
              <el-descriptions :column="4" border class="user-stats-desc">
                <el-descriptions-item label="发布帖子" label-align="center" align="center">
                  <span class="stat-value">{{ postsCount }}</span>
                </el-descriptions-item>
                <el-descriptions-item label="收到评价" label-align="center" align="center">
                  <span class="stat-value">{{ ratingsCount }}</span>
                </el-descriptions-item>
                <el-descriptions-item label="平均评分" label-align="center" align="center">
                  <span class="stat-value">{{ averageRating }}</span>
                </el-descriptions-item>
                <el-descriptions-item label="加入时间" label-align="center" align="center">
                  <span class="stat-value-small">{{ formatJoinDate(userInfo.created_at) }}</span>
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </div>
        </el-card>

        <!-- Main Content Tabs -->
        <el-tabs v-model="activeTab" class="profile-tabs">
          <!-- Tab 1: 发布的帖子 -->
          <el-tab-pane name="posts">
            <template #label>
              <span class="tab-label">
                <el-icon><Document /></el-icon>
                <span>发布的帖子</span>
                <el-badge v-if="postsCount > 0" :value="postsCount" class="tab-badge" />
              </span>
            </template>

            <!-- Loading -->
            <div v-if="loadingPosts" class="tab-loading">
              <el-skeleton :rows="5" animated />
            </div>

            <!-- Empty State -->
            <el-empty v-else-if="posts.length === 0" description="该用户还没有发布任何帖子">
              <template #image>
                <el-icon :size="80" class="empty-icon"><Document /></el-icon>
              </template>
            </el-empty>

            <!-- Posts List -->
            <div v-else class="posts-grid">
              <el-card
                v-for="post in posts"
                :key="post.id"
                shadow="hover"
                class="post-card"
                @click="$router.push(`/forum/${post.id}`)"
              >
                <div class="post-content">
                  <!-- Post Thumbnail -->
                  <div v-if="post.images && post.images.length > 0" class="post-thumbnail">
                    <el-image
                      :src="`http://localhost:8000${post.images[0]}`"
                      :alt="post.title"
                      fit="cover"
                      class="thumbnail-image"
                    />
                  </div>

                  <!-- Post Info -->
                  <div class="post-info">
                    <!-- Tags -->
                    <div class="post-tags">
                      <el-tag :type="getTypeColor(post.item_type)" size="small">
                        {{ getTypeLabel(post.item_type) }}
                      </el-tag>
                      <el-tag v-if="post.category" type="info" size="small">
                        {{ post.category.name }}
                      </el-tag>
                      <el-tag v-if="post.is_claimed" type="success" size="small">
                        已认领
                      </el-tag>
                    </div>
                    
                    <!-- Title -->
                    <h3 class="post-title">{{ post.title }}</h3>
                    
                    <!-- Description -->
                    <p class="post-description">{{ post.content }}</p>
                    
                    <!-- Meta -->
                    <div class="post-meta">
                      <span v-if="post.location" class="meta-item">
                        <el-icon><Location /></el-icon>
                        {{ post.location }}
                      </span>
                      <span class="meta-item">
                        <el-icon><Clock /></el-icon>
                        {{ formatDate(post.created_at) }}
                      </span>
                    </div>
                  </div>
                </div>
              </el-card>
            </div>
          </el-tab-pane>

          <!-- Tab 2: 收到的评价 -->
          <el-tab-pane name="ratings">
            <template #label>
              <span class="tab-label">
                <el-icon><Star /></el-icon>
                <span>收到的评价</span>
                <el-badge v-if="ratingsCount > 0" :value="ratingsCount" class="tab-badge" />
              </span>
            </template>

            <!-- Loading -->
            <div v-if="loadingRatings" class="tab-loading">
              <el-skeleton :rows="5" animated />
            </div>

            <!-- Empty State -->
            <el-empty v-else-if="ratings.length === 0" description="该用户还没有收到任何评价">
              <template #image>
                <el-icon :size="80" class="empty-icon"><Star /></el-icon>
              </template>
            </el-empty>

            <!-- Ratings List -->
            <div v-else class="ratings-list">
              <RatingCard
                v-for="rating in ratings"
                :key="rating.id"
                :rating="rating"
                class="rating-item"
              />
            </div>
          </el-tab-pane>

          <!-- Tab 3: 信用记录 -->
          <el-tab-pane name="credit">
            <template #label>
              <span class="tab-label">
                <el-icon><TrendCharts /></el-icon>
                <span>信用记录</span>
              </span>
            </template>

            <!-- Credit Score Info -->
            <el-card class="credit-info-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <el-icon><InfoFilled /></el-icon>
                  <span>信用分说明</span>
                </div>
              </template>
              
              <el-descriptions :column="1" border>
                <el-descriptions-item label="信用优秀">
                  <el-tag type="success">80分以上</el-tag>
                  <span class="ml-2">表现出色，值得信赖</span>
                </el-descriptions-item>
                <el-descriptions-item label="信用良好">
                  <el-tag>60-79分</el-tag>
                  <span class="ml-2">表现良好，可以信任</span>
                </el-descriptions-item>
                <el-descriptions-item label="信用一般">
                  <el-tag type="warning">40-59分</el-tag>
                  <span class="ml-2">需要改进，谨慎交易</span>
                </el-descriptions-item>
                <el-descriptions-item label="信用较差">
                  <el-tag type="danger">40分以下</el-tag>
                  <span class="ml-2">信用堪忧，建议避免交易</span>
                </el-descriptions-item>
              </el-descriptions>
            </el-card>

            <!-- Credit History Timeline (Placeholder) -->
            <el-card class="credit-history-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <el-icon><TrendCharts /></el-icon>
                  <span>信用变更历史</span>
                </div>
              </template>
              
              <el-empty description="信用变更历史功能即将推出">
                <template #image>
                  <el-icon :size="60" class="empty-icon"><TrendCharts /></el-icon>
                </template>
                <template #extra>
                  <p class="text-sm text-fg-secondary">未来将显示用户信用分的变更记录</p>
                </template>
              </el-empty>
            </el-card>
          </el-tab-pane>
        </el-tabs>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  Compass, 
  ArrowLeft, 
  Monitor, 
  InfoFilled,
  Document,
  Star,
  TrendCharts,
  Location,
  Clock,
  Refresh
} from '@element-plus/icons-vue'
import { userAPI } from '@/api'
import { useAuthStore } from '@/stores/auth'
import RatingCard from '@/components/RatingCard.vue'

const route = useRoute()
const authStore = useAuthStore()

const loading = ref(true)
const error = ref(null)
const userInfo = ref(null)
const posts = ref([])
const ratings = ref([])
const loadingPosts = ref(false)
const loadingRatings = ref(false)
const activeTab = ref('posts')

// 统计数据
const postsCount = computed(() => posts.value.length)
const ratingsCount = computed(() => ratings.value.length)
const averageRating = computed(() => {
  if (ratings.value.length === 0) return 0
  const sum = ratings.value.reduce((acc, r) => acc + r.score, 0)
  return Math.round((sum / ratings.value.length) * 10) / 10
})

// 用户首字母
const userInitial = computed(() => {
  if (!userInfo.value?.name) return 'U'
  return userInfo.value.name.charAt(0).toUpperCase()
})

// 加载用户信息
const loadUserInfo = async () => {
  loading.value = true
  error.value = null
  try {
    const userId = route.params.id
    const response = await userAPI.getPublicInfo(userId)
    userInfo.value = response.data
  } catch (err) {
    error.value = err.response?.data?.detail || '加载用户信息失败'
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}

// 加载用户帖子
const loadUserPosts = async () => {
  loadingPosts.value = true
  try {
    const userId = route.params.id
    const response = await userAPI.getUserPosts(userId)
    posts.value = response.data
  } catch (err) {
    ElMessage.error('加载帖子失败')
  } finally {
    loadingPosts.value = false
  }
}

// 加载用户评价
const loadUserRatings = async () => {
  loadingRatings.value = true
  try {
    const userId = route.params.id
    const response = await userAPI.getUserRatings(userId)
    ratings.value = response.data
  } catch (err) {
    ElMessage.error('加载评价失败')
  } finally {
    loadingRatings.value = false
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days > 30) {
    return date.toLocaleDateString('zh-CN')
  } else if (days > 0) {
    return `${days}天前`
  } else {
    const hours = Math.floor(diff / (1000 * 60 * 60))
    if (hours > 0) return `${hours}小时前`
    const minutes = Math.floor(diff / (1000 * 60))
    if (minutes > 0) return `${minutes}分钟前`
    return '刚刚'
  }
}

// 格式化加入日期
const formatJoinDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
}

// 信用分类型
const getCreditType = (score) => {
  if (score >= 80) return 'success'
  if (score >= 60) return ''
  if (score >= 40) return 'warning'
  return 'danger'
}

// 帖子类型颜色
const getTypeColor = (type) => {
  const colors = {
    lost: 'danger',
    found: 'success',
    general: ''
  }
  return colors[type] || ''
}

// 帖子类型标签
const getTypeLabel = (type) => {
  const labels = {
    lost: '丢失',
    found: '拾取',
    general: '一般'
  }
  return labels[type] || type
}

onMounted(async () => {
  await loadUserInfo()
  await Promise.all([
    loadUserPosts(),
    loadUserRatings()
  ])
})
</script>

<style scoped>
/* ===== Global Page Styles ===== */
.user-profile-page {
  min-height: 100vh;
  background-color: var(--bg-page);
  color: var(--text-primary);
}

/* ===== Top Navigation ===== */
.top-nav {
  background-color: rgba(255, 255, 255, 0.95);
  border-bottom: 1px solid var(--border-base);
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(8px);
}

.nav-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--spacing-lg);
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo-link {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  color: var(--text-primary);
  text-decoration: none;
  font-size: 1.5rem;
  font-weight: 700;
  transition: color 0.3s ease;
}

.logo-link:hover {
  color: var(--brand-primary);
}

.logo-icon {
  color: var(--brand-primary);
}

.logo-text {
  font-weight: 700;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.nav-btn {
  color: var(--text-secondary);
  font-weight: 500;
}

.nav-btn:hover {
  color: var(--text-primary);
}

/* ===== Main Container ===== */
.main-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--spacing-2xl) var(--spacing-lg);
}

.loading-wrapper,
.error-wrapper {
  padding: var(--spacing-3xl) 0;
}

/* ===== Profile Content ===== */
.profile-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2xl);
}

/* ===== Profile Header Card ===== */
.profile-header-card {
  background-color: var(--bg-card) !important;
  border: 1px solid var(--border-base) !important;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}

.profile-header-card :deep(.el-card__body) {
  padding: var(--spacing-2xl) !important;
}

.header-layout {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: var(--spacing-2xl);
  align-items: start;
}

/* Avatar Section */
.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.user-avatar-large {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  font-weight: 700;
  transition: transform 0.3s ease;
  border: 3px solid var(--border-base);
}

.user-avatar-large:hover {
  transform: scale(1.05);
}

.avatar-text {
  font-size: 3rem;
  color: white;
}

/* User Info Section */
.user-info-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.user-name {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.2;
}

.credit-score-wrapper {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.credit-label {
  font-size: 1.125rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.credit-tag {
  font-size: 1.25rem;
  font-weight: 700;
  padding: var(--spacing-sm) var(--spacing-lg);
  border-radius: var(--radius-full);
}

/* User Stats Descriptions */
.user-stats-desc {
  margin-top: var(--spacing-md);
}

.user-stats-desc :deep(.el-descriptions__label) {
  background-color: var(--bg-surface) !important;
  color: var(--text-secondary) !important;
  font-weight: 600;
  font-size: 0.875rem;
}

.user-stats-desc :deep(.el-descriptions__content) {
  background-color: var(--bg-card) !important;
  color: var(--text-primary) !important;
}

.user-stats-desc :deep(.el-descriptions__cell) {
  border-color: var(--border-base) !important;
  padding: var(--spacing-md) !important;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--brand-primary);
}

.stat-value-small {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
}

/* ===== Profile Tabs ===== */
.profile-tabs {
  background-color: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  border: 1px solid var(--border-base);
  box-shadow: var(--shadow-sm);
}

.profile-tabs :deep(.el-tabs__header) {
  margin-bottom: var(--spacing-xl);
  border-bottom: 2px solid var(--border-base);
}

.profile-tabs :deep(.el-tabs__item) {
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 1rem;
  padding: var(--spacing-md) var(--spacing-lg);
  transition: all 0.3s ease;
}

.profile-tabs :deep(.el-tabs__item:hover) {
  color: var(--text-primary);
}

.profile-tabs :deep(.el-tabs__item.is-active) {
  color: var(--brand-primary);
}

.profile-tabs :deep(.el-tabs__active-bar) {
  background-color: var(--brand-primary);
  height: 3px;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.tab-badge {
  margin-left: var(--spacing-xs);
}

.tab-loading {
  padding: var(--spacing-xl) 0;
}

/* ===== Posts Grid ===== */
.posts-grid {
  display: grid;
  gap: var(--spacing-lg);
}

.post-card {
  background-color: var(--bg-card) !important;
  border: 1px solid var(--border-base) !important;
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: var(--shadow-sm);
}

.post-card:hover {
  border-color: var(--brand-primary) !important;
  transform: translateY(-2px);
  box-shadow: var(--shadow-md) !important;
}

.post-content {
  display: flex;
  gap: var(--spacing-lg);
}

.post-thumbnail {
  width: 120px;
  height: 120px;
  flex-shrink: 0;
  border-radius: var(--radius-md);
  overflow: hidden;
  background-color: var(--bg-surface);
}

.thumbnail-image {
  width: 100%;
  height: 100%;
  transition: transform 0.3s ease;
}

.post-card:hover .thumbnail-image {
  transform: scale(1.1);
}

.post-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.post-tags {
  display: flex;
  gap: var(--spacing-xs);
  flex-wrap: wrap;
}

.post-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.4;
}

.post-description {
  font-size: 0.95rem;
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-meta {
  display: flex;
  gap: var(--spacing-lg);
  margin-top: auto;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  color: var(--text-tertiary);
  font-size: 0.875rem;
}

/* ===== Ratings List ===== */
.ratings-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.rating-item {
  animation: fadeIn 0.5s ease-in-out;
}

/* ===== Credit Info Cards ===== */
.credit-info-card,
.credit-history-card {
  background-color: var(--bg-card) !important;
  border: 1px solid var(--border-base) !important;
  border-radius: var(--radius-lg);
  margin-bottom: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
}

.card-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  color: var(--text-primary);
  font-size: 1.125rem;
  font-weight: 600;
}

.credit-info-card :deep(.el-descriptions__label),
.credit-history-card :deep(.el-descriptions__label) {
  background-color: var(--bg-surface) !important;
  color: var(--text-secondary) !important;
  font-weight: 600;
}

.credit-info-card :deep(.el-descriptions__content),
.credit-history-card :deep(.el-descriptions__content) {
  background-color: var(--bg-card) !important;
  color: var(--text-primary) !important;
}

.credit-info-card :deep(.el-descriptions__cell),
.credit-history-card :deep(.el-descriptions__cell) {
  border-color: var(--border-base) !important;
  padding: var(--spacing-md) var(--spacing-lg) !important;
}

/* ===== Empty States ===== */
.empty-icon {
  color: var(--text-tertiary);
}

:deep(.el-empty__description) {
  color: var(--text-secondary);
  font-size: 1rem;
}

:deep(.el-empty) {
  padding: var(--spacing-3xl) 0;
}

/* ===== Animations ===== */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ===== Responsive Design ===== */
@media (max-width: 768px) {
  .header-layout {
    grid-template-columns: 1fr;
    gap: var(--spacing-lg);
    text-align: center;
  }
  
  .avatar-section {
    justify-content: center;
  }
  
  .user-info-section {
    align-items: center;
  }
  
  .user-name {
    font-size: 2rem;
  }
  
  .user-stats-desc :deep(.el-descriptions) {
    grid-template-columns: repeat(2, 1fr) !important;
  }
  
  .post-content {
    flex-direction: column;
  }
  
  .post-thumbnail {
    width: 100%;
    height: 200px;
  }
  
  .nav-content {
    padding: 0 var(--spacing-md);
  }
  
  .main-container {
    padding: var(--spacing-lg) var(--spacing-md);
  }
}
</style>