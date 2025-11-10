<template>
  <div class="min-h-screen" style="background-color: var(--bg-base);">
    <!-- Navigation -->
    <nav class="themed-header backdrop-blur-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <router-link to="/" class="flex items-center text-xl font-bold text-fg-primary hover:text-primary transition-all">
              <el-icon class="mr-2" :size="28"><User /></el-icon>
              用户管理
            </router-link>
          </div>
          <div class="flex items-center space-x-4">
            <el-button text class="text-fg-secondary hover:text-primary" @click="$router.push('/dashboard')">
              <el-icon><Monitor /></el-icon> Dashboard
            </el-button>
            <el-button text class="text-fg-secondary hover:text-primary" @click="$router.push('/forum')">
              <el-icon><List /></el-icon> Forum
            </el-button>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <!-- Page Title -->
      <div class="page-title-section">
        <h1 class="admin-page-title">
          <el-icon class="mr-2" :size="32"><UserFilled /></el-icon>
          用户管理
        </h1>
        <p class="admin-page-subtitle">管理所有用户账户、权限和状态</p>
      </div>
      
      <el-card shadow="hover" class="admin-card">
        <template #header>
          <div class="card-header">
            <div class="flex items-center">
              <el-icon class="mr-2" :size="24"><UserFilled /></el-icon>
              <span class="header-title">用户列表</span>
            </div>
            <div class="flex items-center gap-4">
              <el-input
                v-model="searchQuery"
                placeholder="搜索用户名或邮箱..."
                :prefix-icon="Search"
                class="search-input"
                style="width: 320px;"
                @input="handleSearch"
                clearable
              />
              <el-button type="primary" @click="fetchUsers" class="refresh-btn">
                <el-icon><Refresh /></el-icon> 刷新
              </el-button>
            </div>
          </div>
        </template>

        <!-- Users Table -->
        <el-table
          :data="users"
          v-loading="loading"
          stripe
          class="users-table enhanced-table"
          :header-cell-style="{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }"
          :row-style="{ cursor: 'pointer' }"
        >
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column label="用户信息" width="300">
            <template #default="{ row }">
              <div class="user-info-cell">
                <el-avatar :size="40" class="mr-3">
                  {{ row.name.charAt(0).toUpperCase() }}
                </el-avatar>
                <div>
                  <div class="font-semibold text-fg-primary">{{ row.name }}</div>
                  <div class="text-sm text-fg-secondary">{{ row.email }}</div>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="credit_score" label="信用分" width="100">
            <template #default="{ row }">
              <el-tag :type="getCreditScoreType(row.credit_score)" size="large">
                {{ row.credit_score }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="120">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'danger'">
                {{ row.is_active ? '正常' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="角色" width="120">
            <template #default="{ row }">
              <el-tag :type="row.is_admin ? 'warning' : 'info'">
                {{ row.is_admin ? '管理员' : '普通用户' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="注册时间" width="180">
            <template #default="{ row }">
              <div class="text-fg-secondary">
                {{ formatDate(row.created_at) }}
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="220" fixed="right">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button size="small" @click="viewUser(row)" class="action-btn">
                  <el-icon><View /></el-icon>
                  查看
                </el-button>
                <el-button 
                  size="small" 
                  type="danger"
                  link
                  @click="toggleUserStatus(row)"
                  class="action-btn"
                >
                  {{ row.is_active ? '禁用' : '启用' }}
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <!-- Pagination -->
        <div class="mt-6 flex justify-center">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="fetchUsers"
            @current-change="fetchUsers"
            background
          />
        </div>
      </el-card>
    </div>

    <!-- User Detail Dialog -->
    <el-dialog
      v-model="dialogVisible"
      title="用户详情"
      width="600px"
      :close-on-click-modal="false"
    >
      <div v-if="selectedUser" class="user-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="用户ID">{{ selectedUser.id }}</el-descriptions-item>
          <el-descriptions-item label="用户名">{{ selectedUser.name }}</el-descriptions-item>
          <el-descriptions-item label="邮箱" :span="2">{{ selectedUser.email }}</el-descriptions-item>
          <el-descriptions-item label="信用分">
            <el-tag :type="getCreditScoreType(selectedUser.credit_score)">
              {{ selectedUser.credit_score }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="selectedUser.is_active ? 'success' : 'danger'">
              {{ selectedUser.is_active ? '正常' : '禁用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="角色" :span="2">
            <el-tag :type="selectedUser.is_admin ? 'warning' : 'info'">
              {{ selectedUser.is_admin ? '管理员' : '普通用户' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="注册时间" :span="2">
            {{ formatDate(selectedUser.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="最后更新" :span="2">
            {{ selectedUser.updated_at ? formatDate(selectedUser.updated_at) : '从未更新' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="dialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  User, UserFilled, Monitor, List, Search, Refresh, View 
} from '@element-plus/icons-vue'
import axios from 'axios'
import { formatLocal } from '@/utils/time'

const router = useRouter()
const users = ref([])
const loading = ref(false)
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const dialogVisible = ref(false)
const selectedUser = ref(null)

const fetchUsers = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    const response = await axios.get('http://localhost:8000/api/users/admin/list', {
      headers: { Authorization: `Bearer ${token}` },
      params: {
        skip: (currentPage.value - 1) * pageSize.value,
        limit: pageSize.value,
        search: searchQuery.value || undefined
      }
    })
    
    if (response.data && response.data.data) {
      users.value = response.data.data
      total.value = response.data.total
    } else {
      users.value = response.data
      total.value = response.data.length
    }
  } catch (error) {
    console.error('Failed to fetch users:', error)
    ElMessage.error('获取用户列表失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchUsers()
}

const getCreditScoreType = (score) => {
  if (score >= 90) return 'success'
  if (score >= 70) return 'warning'
  return 'danger'
}

const formatDate = (dateString) => (dateString ? formatLocal(dateString) : '')

const viewUser = (user) => {
  selectedUser.value = user
  dialogVisible.value = true
}

const toggleUserStatus = async (user) => {
  try {
    await ElMessageBox.confirm(
      `确定要${user.is_active ? '禁用' : '启用'}用户 ${user.name} 吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    ElMessage.success(`用户 ${user.name} 已${user.is_active ? '禁用' : '启用'}`)
    // TODO: 实现实际的API调用
    // user.is_active = !user.is_active
  } catch {
    ElMessage.info('操作已取消')
  }
}

onMounted(() => {
  fetchUsers()
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
  flex-wrap: wrap;
  gap: var(--spacing-md);
}

.header-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
}

.search-input :deep(.el-input__wrapper) {
  background: var(--input-bg-color);
  border-color: var(--input-border-color);
  transition: all 0.3s ease;
}

.search-input :deep(.el-input__wrapper):hover {
  border-color: var(--primary);
}

.search-input :deep(.el-input__inner) {
  color: var(--input-text-color);
}

.refresh-btn {
  font-weight: 600;
}

/* Admin Card */
.admin-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-base);
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
}

.admin-card :deep(.el-card__header) {
  background: var(--bg-surface);
  border-bottom: 1px solid var(--border-base);
  padding: var(--spacing-lg);
}

/* Enhanced Table */
.enhanced-table {
  --el-table-bg-color: var(--bg-surface);
  --el-table-tr-bg-color: var(--bg-surface);
  --el-table-row-hover-bg-color: var(--bg-muted);
  --el-table-striped-row-bg-color: var(--bg-surface);
  --el-table-header-bg-color: var(--bg-surface);
  --el-table-text-color: var(--text-primary);
  --el-table-border-color: var(--border-base);
}

.enhanced-table :deep(.el-table__body tr) {
  background-color: var(--bg-surface);
  transition: all 0.3s ease;
}

.enhanced-table :deep(.el-table__body tr:hover > td) {
  background-color: var(--bg-muted) !important;
}

.enhanced-table :deep(.el-table__header th) {
  font-weight: 700;
  font-size: 0.95rem;
  padding: var(--spacing-md) var(--spacing-sm) !important;
}

.enhanced-table :deep(.el-table__body td) {
  padding: var(--spacing-md) var(--spacing-sm) !important;
  vertical-align: middle !important;
  color: var(--text-primary);
}

/* User Info Cell - Ensure Perfect Vertical Alignment */
.user-info-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

/* Action Buttons */
.action-buttons {
  display: flex;
  gap: var(--spacing-xs);
  align-items: center;
}

.action-btn {
  font-weight: 600;
  transition: all 0.3s ease;
}

.action-btn:hover {
  transform: translateY(-1px);
}

/* Pagination */
:deep(.el-pagination) {
  --el-text-color-primary: var(--text-primary);
  --el-text-color-regular: var(--text-secondary);
  padding: var(--spacing-lg) 0;
}

:deep(.el-pagination.is-background .btn-next),
:deep(.el-pagination.is-background .btn-prev),
:deep(.el-pagination.is-background .el-pager li) {
  background-color: var(--bg-muted);
  color: var(--text-primary);
  border: 1px solid var(--border-base);
  transition: all 0.3s ease;
}

:deep(.el-pagination.is-background .el-pager li:hover) {
  color: var(--primary);
  border-color: var(--primary);
  transform: translateY(-1px);
}

:deep(.el-pagination.is-background .el-pager li.is-active) {
  background-color: var(--primary);
  color: var(--text-inverse);
  border-color: var(--primary);
  font-weight: 700;
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
