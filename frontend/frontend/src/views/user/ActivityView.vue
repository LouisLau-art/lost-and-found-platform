<template>
  <div class="min-h-screen" style="background-color: #f9fafb;">
    <!-- Navigation -->
    <nav class="bg-white/95 backdrop-blur-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <router-link to="/" class="text-xl font-bold text-gray-800 hover:text-indigo-600 transition-all">
              Lost & Found Platform
            </router-link>
          </div>
          <div class="flex items-center space-x-4">
            <router-link to="/dashboard" class="text-gray-600 hover:text-gray-800 transition-all">
              Dashboard
            </router-link>
            <router-link to="/forum" class="text-gray-600 hover:text-gray-800 transition-all">
              Forum
            </router-link>
            <el-button text class="text-gray-600 hover:text-gray-800" @click="handleLogout">
              Sign out
            </el-button>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main content -->
    <div class="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <h1 class="text-3xl font-bold text-gray-800 mb-6">My Activity</h1>
      
      <el-tabs v-model="activeTab" type="border-card" class="activity-tabs">
        <!-- My Posts Tab -->
        <el-tab-pane name="posts">
          <template #label>
            <span class="flex items-center">
              <el-icon class="mr-2"><Document /></el-icon>
              My Posts ({{ posts.length }})
            </span>
          </template>
          
          <div v-if="loadingPosts" class="py-8">
            <el-skeleton :rows="5" animated />
          </div>
          
          <div v-else-if="posts.length === 0" class="py-8">
            <el-empty description="You haven't posted anything yet">
              <el-button type="primary" @click="$router.push('/forum/create')">
                Create Your First Post
              </el-button>
            </el-empty>
          </div>
          
          <div v-else class="space-y-4">
            <el-card
              v-for="post in posts"
              :key="post.id"
              class="post-card cursor-pointer"
              shadow="hover"
              @click="$router.push(`/forum/${post.id}`)"
            >
              <div class="flex items-start gap-4">
                <div v-if="post.images && post.images.length > 0" class="flex-shrink-0">
                  <el-image
                    :src="`http://localhost:8000${post.images[0]}`"
                    fit="cover"
                    class="w-24 h-24 rounded-lg"
                  />
                </div>
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-2">
                    <el-tag :type="getTypeColor(post.item_type)" size="small">
                      {{ getTypeLabel(post.item_type) }}
                    </el-tag>
                    <el-tag v-if="post.is_claimed" type="success" size="small">已认领</el-tag>
                  </div>
                  <h3 class="text-lg font-semibold text-gray-800 mb-1">{{ post.title }}</h3>
                  <p class="text-gray-600 text-sm line-clamp-2">{{ post.content }}</p>
                  <div class="flex items-center gap-4 mt-2 text-sm text-gray-500">
                    <span>{{ formatDate(post.created_at) }}</span>
                    <span v-if="post.location">
                      <el-icon><Location /></el-icon> {{ post.location }}
                    </span>
                  </div>
                </div>
              </div>
            </el-card>
          </div>
        </el-tab-pane>

        <!-- My Claims Tab -->
        <el-tab-pane name="claims">
          <template #label>
            <span class="flex items-center">
              <el-icon class="mr-2"><Tickets /></el-icon>
              My Claims ({{ claims.length }})
            </span>
          </template>
          
          <div v-if="loadingClaims" class="py-8">
            <el-skeleton :rows="5" animated />
          </div>
          
          <div v-else-if="claims.length === 0" class="py-8">
            <el-empty description="You have no claims yet">
              <el-button type="primary" @click="$router.push('/forum')">
                Browse Items
              </el-button>
            </el-empty>
          </div>
          
          <div v-else class="space-y-4">
            <el-card
              v-for="claim in claims"
              :key="claim.id"
              class="claim-card"
              shadow="hover"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-2">
                    <el-tag :type="getClaimStatusColor(claim.status)" size="small">
                      {{ getClaimStatusLabel(claim.status) }}
                    </el-tag>
                  </div>
                  <h3 class="text-lg font-semibold text-gray-800 mb-1">
                    Claim for: {{ claim.post?.title }}
                  </h3>
                  <p class="text-gray-400 text-sm mb-2">{{ claim.description }}</p>
                  <div class="text-sm text-gray-500">
                    Submitted: {{ formatDate(claim.created_at) }}
                  </div>
                </div>
                <el-button 
                  v-if="claim.status === 'pending'"
                  type="info" 
                  size="small"
                  @click="viewClaimDetails(claim)"
                >
                  View Details
                </el-button>
              </div>
            </el-card>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useForumStore } from '@/stores/forum'
import { postAPI, claimAPI } from '@/api'
import { Document, Tickets, Location } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()
const forumStore = useForumStore()

const activeTab = ref('posts')
const posts = ref([])
const claims = ref([])
const loadingPosts = ref(false)
const loadingClaims = ref(false)

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

const getClaimStatusLabel = (status) => ({
  pending: 'Pending Review',
  approved: 'Approved',
  rejected: 'Rejected',
  cancelled: 'Cancelled'
})[status] || status

const getClaimStatusColor = (status) => ({
  pending: 'warning',
  approved: 'success',
  rejected: 'danger',
  cancelled: 'info'
})[status] || ''

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const loadMyPosts = async () => {
  loadingPosts.value = true
  try {
    const response = await postAPI.getAll({ skip: 0, limit: 100 })
    const allPosts = response.data.data || response.data
    posts.value = allPosts.filter(post => post.author_id === authStore.user?.id)
  } catch (error) {
    console.error('Failed to load posts:', error)
    ElMessage.error('Failed to load your posts')
  } finally {
    loadingPosts.value = false
  }
}

const loadMyClaims = async () => {
  loadingClaims.value = true
  try {
    const response = await claimAPI.getMyClaims()
    claims.value = response.data
  } catch (error) {
    console.error('Failed to load claims:', error)
    ElMessage.error('Failed to load your claims')
  } finally {
    loadingClaims.value = false
  }
}

const viewClaimDetails = (claim) => {
  if (claim.post?.id) {
    router.push(`/forum/${claim.post.id}`)
  }
}

const handleLogout = () => {
  authStore.logout()
  router.push('/')
}

onMounted(() => {
  loadMyPosts()
  loadMyClaims()
})
</script>

<style scoped>
.activity-tabs {
  background: white;
  border: 1px solid #e5e7eb;
}

.activity-tabs :deep(.el-tabs__header) {
  background: white;
  border-bottom: 1px solid #e5e7eb;
}

.activity-tabs :deep(.el-tabs__item) {
  color: #6b7280;
}

.activity-tabs :deep(.el-tabs__item.is-active) {
  color: #4f46e5;
  background: #f9fafb;
}

.activity-tabs :deep(.el-tabs__content) {
  padding: 24px;
  background: white;
  color: #1f2937;
}

.post-card,
.claim-card {
  background: white;
  border: 1px solid #e5e7eb;
  transition: all 0.3s ease;
}

.post-card:hover,
.claim-card:hover {
  border-color: #4f46e5;
  transform: translateY(-2px);
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
