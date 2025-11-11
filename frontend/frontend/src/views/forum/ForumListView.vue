<template>
  <div class="min-h-screen flex flex-col" style="background-color: var(--bg-page);">
    <!-- Header with navigation -->
    <el-header class="themed-header backdrop-blur-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <router-link to="/" class="text-2xl font-bold text-fg-primary hover-text-primary transition-all flex items-center">
          <el-icon class="mr-2" :size="28"><Compass /></el-icon>
          Lost & Found Platform
        </router-link>
        <div class="flex gap-2">
          <el-button v-if="authStore.isAuthenticated" text class="text-fg-secondary hover-text-primary" @click="$router.push('/dashboard')">
            <el-icon><Monitor /></el-icon> 仪表盘
          </el-button>
          <el-button v-if="authStore.isAuthenticated" type="primary" @click="$router.push('/forum/create')">
            <el-icon><Plus /></el-icon> 发布信息
          </el-button>
          <el-button v-else type="primary" @click="$router.push('/login')">登录</el-button>
        </div>
      </div>
    </el-header>

    <!-- Main Content -->
    <main class="flex-1 pt-20 pb-12 px-4 sm:px-6 lg:px-8">
      <div class="content-wrapper">
        <div class="grid grid-cols-1 lg:grid-cols-4 gap-8">
            <!-- Left sidebar for filters -->
            <div class="lg:col-span-1">
              <el-card shadow="hover" class="sticky top-20 filter-card">
                <template #header>
                  <div class="filter-header">
                    <el-icon class="mr-2"><Filter /></el-icon>
                    <h2 class="filter-title">搜索筛选</h2>
                  </div>
                </template>
              <SearchFilter v-model="filters" @search="handleSearch" />
            </el-card>
          </div>

          <!-- Right content for posts list -->
          <div class="lg:col-span-3">
            <!-- Page header -->
            <div class="page-header">
              <div>
                <h1 class="page-title">失物招领</h1>
                <p class="page-subtitle">找到 <strong class="highlight-count">{{ total }}</strong> 条相关信息</p>
              </div>
            </div>

            <!-- Loading -->
            <div v-if="loading" class="py-16 loading-container">
              <el-skeleton :rows="5" animated />
            </div>

            <!-- Error message -->
            <el-alert v-else-if="error" :title="error" type="error" show-icon class="mb-4" />

            <!-- Posts list -->
            <div v-else-if="posts.length > 0" class="space-y-6">
              <el-card
                v-for="post in posts"
                :key="post.id"
                class="post-card hover-lift"
                shadow="hover"
              >
                <div @click="$router.push(`/forum/${post.id}`)" class="cursor-pointer">
                  <div class="flex flex-col md:flex-row gap-6">
                    <div v-if="post.images && post.images.length > 0" class="md:w-1/4">
                      <el-image
                        :src="`http://localhost:8000${post.images[0]}`"
                        fit="cover"
                        class="w-full h-48 object-cover rounded-lg transition-transform duration-300 hover:scale-105"
                        placeholder="暂无图片"
                        :preview-src-list="toFullUrls(post.images)"
                      />
                    </div>
                    <div class="flex-1">
                      <div class="card-tags-row">
                        <el-tag :type="getTypeColor(post.item_type)" size="small" effect="dark">
                          {{ getTypeLabel(post.item_type) }}
                        </el-tag>
                        <el-tag v-if="post.category" type="info" size="small" effect="dark">
                          {{ post.category.icon }} {{ post.category.name }}
                        </el-tag>
                        <el-tag v-if="post.is_claimed" type="success" size="small" effect="dark">已认领</el-tag>
                      </div>
                      <h3 class="post-title">
                        {{ post.title }}
                      </h3>
                      <p class="post-content">{{ post.content }}</p>
                      
                      <!-- Additional images -->
                      <div v-if="post.images && post.images.length > 1" class="flex gap-2 mb-4">
                        <img
                          v-for="(img, idx) in post.images.slice(1, 4)"
                          :key="idx"
                          :src="`http://localhost:8000${img}`"
                          class="w-16 h-16 object-cover rounded transition-transform duration-300 hover:scale-110"
                        />
                        <div v-if="post.images.length > 4" class="w-16 h-16 bg-muted rounded flex items-center justify-center text-fg-secondary">
                          +{{ post.images.length - 4 }}
                        </div>
                      </div>
                      
                      <!-- Metadata Tags -->
                      <div class="metadata-tags">
                        <el-tag size="small" type="info" effect="dark" v-if="post.location">
                          <el-icon><Location /></el-icon> {{ post.location }}
                        </el-tag>
                        <el-tag size="small" effect="dark" v-if="post.item_time">
                          <el-icon><Calendar /></el-icon> {{ formatDate(post.item_time) }}
                        </el-tag>
                      </div>
                      
                      <!-- Card Footer: Author & Stats -->
                      <div class="card-footer">
                        <div class="footer-left">
                          <el-avatar 
                            :size="32" 
                            class="cursor-pointer hover:scale-110 transition-transform duration-300"
                          >
                            {{ post.author?.name?.charAt(0) || '?' }}
                          </el-avatar>
                          <span class="author-name">
                            {{ post.author?.name || '匿名用户' }}
                          </span>
                        </div>
                        <div class="footer-right">
                          <span class="stat-item">
                            <el-icon class="mr-1"><Message /></el-icon>
                            <span>{{ post.comments?.length || 0 }}</span>
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </el-card>
            </div>

            <!-- No posts -->
            <div v-else class="no-results">
              <img src="https://example.com/friendly-no-results.png" alt="未找到相关信息" class="no-results-image">
              <p class="no-results-text">未找到相关信息！试试调整筛选条件或稍后再来~</p>
            </div>

            <!-- Pagination -->
            <div v-if="posts.length > 0" class="mt-10 flex justify-center">
              <el-pagination
                v-model:current-page="currentPage"
                :page-size="pageSize"
                :total="total"
                layout="total, sizes, prev, pager, next, jumper"
                :page-sizes="[10, 20, 50, 100]"
                @current-change="loadPosts"
                @size-change="handleSizeChange"
                background
                small
              />
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { formatLocal } from '@/utils/time'
import { useAuthStore } from '@/stores/auth'
import { postAPI } from '@/api'
import SearchFilter from '@/components/SearchFilter.vue'
import { 
  Compass, Monitor, Plus, Filter, Location, 
  Calendar, Message 
} from '@element-plus/icons-vue'

const authStore = useAuthStore()
const posts = ref([])
const loading = ref(false)
const error = ref(null)
const filters = ref({})
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// Normalize images to an absolute URL array for ElImage preview
const toFullUrls = (imgs) => {
  if (!imgs) return []
  let arr = imgs
  if (typeof imgs === 'string') {
    try {
      arr = JSON.parse(imgs)
    } catch (e) {
      console.warn('Invalid images string, expected JSON array:', imgs)
      arr = []
    }
  }
  if (!Array.isArray(arr)) return []
  return arr.map(img => `http://localhost:8000${img}`)
}

const getTypeLabel = (type) => ({
  lost: '🔴 丢失',
  found: '🟢 拾到',
  general: '⚪ 普通'
})[type] || type

const getTypeColor = (type) => ({
  lost: 'danger',
  found: 'success',
  general: 'info'
})[type] || ''

const formatDate = (date) => (date ? formatLocal(date) : '')

const loadPosts = async () => {
  loading.value = true
  error.value = null
  try {
    const params = {
      ...filters.value,
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    const response = await postAPI.getAll(params)
    
    // 后端现在返回 { data: [...], total: number }
    if (response.data && response.data.data) {
      posts.value = response.data.data
      total.value = response.data.total
    } else {
      // 兼容旧的返回格式
      posts.value = response.data
      total.value = response.data.length
    }
  } catch (err) {
    console.error('Failed to load posts:', err)
    error.value = err.message || '加载帖子失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

const handleSearch = (newFilters) => {
  filters.value = newFilters
  currentPage.value = 1
  loadPosts()
}

// Pagination size change handler (remove warning and reload)
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadPosts()
}

onMounted(() => loadPosts())
</script>

<style scoped>
/* 浅色主题样式 */
.filter-card {
  background: var(--bg-card);
  border: 1px solid var(--border-base);
  border-radius: var(--radius-lg);
}

.filter-card :deep(.el-card__header) {
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-base);
  padding: var(--spacing-lg);
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
}

.filter-header {
  display: flex;
  align-items: center;
}

.filter-title {
  color: var(--text-primary);
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0;
}

/* Page Header */
.page-header {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-2xl);
  animation: fadeIn 0.5s ease-out;
}

@media (min-width: 640px) {
  .page-header {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
}

.page-title {
  font-size: clamp(1.75rem, 3vw, 2.5rem);
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: var(--spacing-sm);
}

.page-subtitle {
  color: var(--text-secondary);
  font-size: 1.125rem;
  font-weight: 500;
}

.highlight-count {
  color: var(--brand-primary);
  font-size: 1.5rem;
  font-weight: 700;
}

.create-btn {
  font-size: 1rem;
  font-weight: 600;
  height: 48px;
  padding: 0 var(--spacing-xl);
}

/* Post Cards */
.post-card {
  background: var(--bg-card);
  border: 1px solid var(--border-base);
  border-radius: var(--radius-lg);
  transition: all 0.3s ease;
  margin-bottom: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
}

.post-card:hover {
  border-color: var(--brand-primary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.post-title {
  font-size: 1.375rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: var(--spacing-sm);
  transition: color 0.3s ease;
  line-height: 1.4;
}

.post-title:hover {
  color: var(--brand-primary);
}

.post-content {
  color: var(--text-secondary);
  font-size: 1rem;
  line-height: 1.6;
  margin-bottom: var(--spacing-md);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Card Tags Row */
.card-tags-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: var(--spacing-sm);
  flex-wrap: wrap;
}

/* Metadata Tags */
.metadata-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: var(--spacing-md);
}

/* Footer Metadata */
.card-footer {
  color: var(--text-secondary);
}

/* Card Footer */
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: var(--spacing-md);
  margin-top: var(--spacing-md);
  border-top: 1px solid var(--border-base);
}

.footer-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.footer-right {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.stat-item {
  display: flex;
  align-items: center;
  color: var(--text-secondary);
  cursor: pointer;
  transition: color 0.3s ease;
}

.stat-item:hover {
  color: var(--brand-primary);
}

.author-name {
  color: var(--text-primary);
  font-weight: 600;
  font-size: 0.95rem;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Element Plus 组件浅色主题覆盖 */
:deep(.el-skeleton) {
  background: var(--bg-surface);
  border-radius: var(--radius-md);
}

:deep(.el-pagination) {
  --el-text-color-primary: var(--text-primary);
  --el-text-color-regular: var(--text-secondary);
}

:deep(.el-pagination.is-background .btn-next),
:deep(.el-pagination.is-background .btn-prev),
:deep(.el-pagination.is-background .el-pager li) {
  background-color: var(--bg-card);
  color: var(--text-primary);
  border: 1px solid var(--border-base);
}

:deep(.el-pagination.is-background .el-pager li:hover) {
  color: var(--brand-primary);
  border-color: var(--brand-primary);
}

:deep(.el-pagination.is-background .el-pager li.is-active) {
  background-color: var(--brand-primary);
  color: white;
  border-color: var(--brand-primary);
}

/* 无结果状态样式 */
.no-results {
  text-align: center;
  padding: 60px 20px;
  background-color: var(--bg-card);
  border-radius: var(--radius-lg);
  margin: 24px 0;
  border: 1px solid var(--border-base);
  box-shadow: var(--shadow-sm);
}

.no-results-image {
  width: 180px;
  height: auto;
  margin-bottom: 24px;
  max-width: 100%;
  transition: transform 0.3s ease;
}

.no-results-image:hover {
  transform: scale(1.05);
}

.no-results-text {
  font-size: 16px;
  color: var(--text-secondary);
  margin: 0;
  font-weight: 500;
  line-height: 1.6;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .no-results {
    padding: 40px 16px;
  }
  
  .no-results-image {
    width: 140px;
  }
  
  .no-results-text {
    font-size: 14px;
  }
}
</style>