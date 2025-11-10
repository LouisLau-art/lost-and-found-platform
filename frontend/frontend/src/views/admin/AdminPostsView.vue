<template>
  <div class="min-h-screen" style="background-color: var(--bg-base);">
    <!-- 导航栏 -->
    <nav class="themed-header backdrop-blur-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <router-link to="/" class="text-xl font-bold text-fg-primary hover-text-primary transition-all">
              Lost & Found - Admin
            </router-link>
          </div>
          <div class="flex items-center space-x-4">
            <router-link to="/dashboard" class="text-fg-secondary hover-text-primary transition-all">
              返回用户面板
            </router-link>
            <el-button text class="text-fg-secondary hover-text-primary" @click="handleLogout">
              退出登录
            </el-button>
          </div>
        </div>
      </div>
    </nav>

    <!-- 主要内容区域 -->
    <div class="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <!-- 页面标题 -->
      <div class="page-title-section">
        <h1 class="admin-page-title">
          <el-icon class="mr-2" :size="32"><Document /></el-icon>
          帖子管理
        </h1>
        <p class="admin-page-subtitle">管理所有用户发布的帖子</p>
      </div>

      <!-- 帖子列表 -->
      <el-card shadow="hover" class="admin-card">
        <template #header>
          <div class="card-header">
            <div class="flex items-center">
              <el-icon class="mr-2" :size="24"><Document /></el-icon>
              <span class="header-title">帖子列表</span>
            </div>
          </div>
        </template>
        
        <el-table
          :data="posts"
          v-loading="loading"
          stripe
          style="width: 100%"
          class="admin-table enhanced-table"
          :header-cell-style="{ background: 'var(--bg-muted)', color: 'var(--text-primary)' }"
        >
          <el-table-column prop="id" label="ID" width="80" />
          
          <el-table-column prop="title" label="标题" min-width="200">
            <template #default="{ row }">
              <router-link :to="`/forum/${row.id}`" class="text-primary hover-text-primary">
                {{ row.title }}
              </router-link>
            </template>
          </el-table-column>
          
          <el-table-column label="作者" width="150">
            <template #default="{ row }">
              <div class="flex items-center">
                <el-avatar :size="24" class="mr-2">
                  {{ row.author?.name?.charAt(0) || '?' }}
                </el-avatar>
                <span>{{ row.author?.name || '未知' }}</span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="类型" width="120">
            <template #default="{ row }">
              <el-tag :type="getTypeColor(row.item_type)" size="small">
                {{ getTypeLabel(row.item_type) }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="状态" width="120">
            <template #default="{ row }">
              <el-tag :type="getStatusColor(row.status)" size="small">
                {{ getStatusLabel(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="是否认领" width="100">
            <template #default="{ row }">
              <el-tag :type="row.is_claimed ? 'success' : 'info'" size="small">
                {{ row.is_claimed ? '已认领' : '未认领' }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="创建时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button
                  size="small"
                  type="primary"
                  @click="handleEdit(row)"
                  class="action-btn"
                >
                  <el-icon class="mr-1"><Edit /></el-icon>
                  编辑
                </el-button>
                <el-popconfirm
                  title="确定要删除这个帖子吗？此操作不可撤销！"
                  confirm-button-text="确定"
                  cancel-button-text="取消"
                  @confirm="handleDelete(row.id)"
                >
                  <template #reference>
                    <el-button
                      size="small"
                      type="danger"
                      class="action-btn"
                    >
                      <el-icon class="mr-1"><Delete /></el-icon>
                      删除
                    </el-button>
                  </template>
                </el-popconfirm>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="mt-6 flex justify-center">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            background
            @current-change="loadPosts"
            @size-change="loadPosts"
          />
        </div>
      </el-card>
    </div>

    <!-- 编辑对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑帖子"
      width="600px"
      class="edit-dialog"
    >
      <el-form
        v-if="editingPost"
        :model="editForm"
        label-position="top"
        size="large"
      >
        <el-form-item label="标题">
          <el-input v-model="editForm.title" />
        </el-form-item>
        
        <el-form-item label="内容">
          <el-input
            v-model="editForm.content"
            type="textarea"
            :rows="6"
          />
        </el-form-item>
        
        <el-form-item label="物品类型">
          <el-select v-model="editForm.item_type" class="w-full">
            <el-option label="丢失" value="lost" />
            <el-option label="拾到" value="found" />
            <el-option label="普通" value="general" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="状态">
          <el-select v-model="editForm.status" class="w-full">
            <el-option label="已发布" value="published" />
            <el-option label="已删除" value="deleted" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveEdit" :loading="saving">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const router = useRouter()
const authStore = useAuthStore()

const posts = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const editDialogVisible = ref(false)
const editingPost = ref(null)
const editForm = ref({
  title: '',
  content: '',
  item_type: '',
  status: ''
})
const saving = ref(false)

// 获取帖子列表
const loadPosts = async () => {
  loading.value = true
  try {
    const skip = (currentPage.value - 1) * pageSize.value
    const response = await api.get('/api/admin/posts', {
      params: {
        skip,
        limit: pageSize.value
      }
    })
    
    posts.value = response.data.data
    total.value = response.data.total
  } catch (error) {
    console.error('Failed to load posts:', error)
    if (error.response?.status === 403) {
      ElMessage.error('需要管理员权限')
      router.push('/dashboard')
    } else {
      ElMessage.error('加载帖子失败: ' + (error.response?.data?.detail || error.message))
    }
  } finally {
    loading.value = false
  }
}

// 删除帖子
const handleDelete = async (postId) => {
  try {
    await api.delete(`/api/admin/posts/${postId}`)
    ElMessage.success('删除成功')
    loadPosts()
  } catch (error) {
    console.error('Failed to delete post:', error)
    ElMessage.error('删除失败: ' + (error.response?.data?.detail || error.message))
  }
}

// 打开编辑对话框
const handleEdit = (post) => {
  editingPost.value = post
  editForm.value = {
    title: post.title,
    content: post.content,
    item_type: post.item_type,
    status: post.status
  }
  editDialogVisible.value = true
}

// 保存编辑
const handleSaveEdit = async () => {
  if (!editingPost.value) return
  
  saving.value = true
  try {
    await api.put(`/api/admin/posts/${editingPost.value.id}`, editForm.value)
    ElMessage.success('更新成功')
    editDialogVisible.value = false
    loadPosts()
  } catch (error) {
    console.error('Failed to update post:', error)
    ElMessage.error('更新失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

// 退出登录
const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

// 获取类型标签
const getTypeLabel = (type) => ({
  lost: '丢失',
  found: '拾到',
  general: '普通'
})[type] || type

const getTypeColor = (type) => ({
  lost: 'danger',
  found: 'success',
  general: 'info'
})[type] || ''

// 获取状态标签
const getStatusLabel = (status) => ({
  published: '已发布',
  deleted: '已删除',
  draft: '草稿'
})[status] || status

const getStatusColor = (status) => ({
  published: 'success',
  deleted: 'danger',
  draft: 'warning'
})[status] || ''

// 格式化日期
import { formatLocal } from '@/utils/time'
const formatDate = (dateString) => {
  if (!dateString) return '-'
  return formatLocal(dateString)
}

onMounted(() => {
  loadPosts()
})
</script>

<style scoped>
/* Page Title Section */
.page-title-section {
  margin-bottom: var(--spacing-xl);
  animation: fadeIn 0.5s ease-out;
}

.admin-page-title {
  display: flex;
  align-items: center;
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: var(--spacing-sm);
}

.admin-page-subtitle {
  font-size: 1.125rem;
  color: var(--text-secondary);
  font-weight: 500;
}

/* Card Header */
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
}

/* 浅色主题 */
.admin-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-base);
}

.admin-card :deep(.el-card__header) {
  background: var(--bg-surface);
  border-bottom: 1px solid var(--border-base);
  padding: var(--spacing-lg);
}

.admin-card :deep(.el-card__body) {
  padding: var(--spacing-lg);
}

/* Enhanced Table */
.enhanced-table {
  --el-table-bg-color: var(--bg-surface);
  --el-table-tr-bg-color: var(--bg-surface);
  --el-table-row-hover-bg-color: var(--bg-muted);
  --el-table-text-color: var(--text-primary);
  --el-table-border-color: var(--border-base);
}

.enhanced-table :deep(.el-table__header th) {
  background: var(--bg-muted) !important;
  color: var(--text-primary);
  font-weight: 700;
  font-size: 0.95rem;
  padding: var(--spacing-md) var(--spacing-sm) !important;
}

.enhanced-table :deep(.el-table__body tr) {
  background: transparent;
  border-bottom: 1px solid var(--border-base);
  transition: all 0.3s ease;
}

.enhanced-table :deep(.el-table__body tr:hover) {
  background: var(--bg-muted) !important;
}

.enhanced-table :deep(.el-table__body td) {
  border-color: var(--border-base);
  color: var(--text-primary);
  padding: var(--spacing-md) var(--spacing-sm) !important;
}

.enhanced-table :deep(.el-table__row--striped td) {
  background: var(--bg-muted);
}

/* Action Buttons */
.action-buttons {
  display: flex;
  gap: var(--spacing-sm);
  align-items: center;
}

.action-btn {
  font-weight: 600;
  transition: all 0.3s ease;
}

.action-btn:hover {
  transform: translateY(-1px);
}

/* 对话框样式 */
.edit-dialog :deep(.el-dialog) {
  background: var(--bg-surface);
  border: 1px solid var(--border-base);
}

.edit-dialog :deep(.el-dialog__header) {
  background: var(--bg-surface);
  border-bottom: 1px solid var(--border-base);
}

.edit-dialog :deep(.el-dialog__title) {
  color: var(--text-primary);
  font-weight: 700;
}

.edit-dialog :deep(.el-form-item__label) {
  color: var(--text-primary);
  font-weight: 600;
}

.edit-dialog :deep(.el-input__wrapper) {
  background-color: var(--input-bg-color);
  border-color: var(--input-border-color);
}

.edit-dialog :deep(.el-input__inner),
.edit-dialog :deep(.el-textarea__inner) {
  color: var(--input-text-color);
  background-color: var(--input-bg-color);
}

/* 分页样式 */
:deep(.el-pagination) {
  --el-text-color-primary: var(--text-primary);
  --el-text-color-regular: var(--text-secondary);
  padding: var(--spacing-lg) 0;
  background-color: var(--bg-surface);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
}

:deep(.el-pagination.is-background .btn-next),
:deep(.el-pagination.is-background .btn-prev),
:deep(.el-pagination.is-background .el-pager li) {
  background-color: var(--bg-muted);
  color: var(--text-primary);
  transition: all 0.3s ease;
  border: 1px solid var(--border-base);
}

:deep(.el-pagination.is-background .el-pager li:hover) {
  color: var(--primary);
  transform: translateY(-1px);
}

:deep(.el-pagination.is-background .el-pager li.is-active) {
  background-color: var(--primary);
  color: var(--text-inverse);
  font-weight: 700;
  border-color: var(--primary);
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
</style>
