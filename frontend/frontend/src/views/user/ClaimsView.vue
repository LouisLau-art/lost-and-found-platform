<template>
  <div class="min-h-screen bg-page">
    <el-header class="themed-header shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <router-link to="/" class="text-xl font-bold text-fg-primary">🎯 Lost & Found</router-link>
        <div class="space-x-2">
          <el-button text @click="$router.push('/dashboard')">← 返回Dashboard</el-button>
          <el-button text @click="$router.push('/forum')">论坛</el-button>
        </div>
      </div>
    </el-header>

    <div class="max-w-7xl mx-auto py-8 px-4">
      <h1 class="text-3xl font-bold text-fg-primary mb-6">📦 我的认领</h1>

      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <!-- 我提交的认领 -->
        <el-tab-pane label="我提交的认领" name="submitted">
          <template #label>
            <span class="flex items-center gap-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
              我提交的认领
              <el-badge v-if="submittedClaims.length > 0" :value="submittedClaims.length" class="ml-2" />
            </span>
          </template>

          <div v-if="loadingSubmitted" class="py-8">
            <el-skeleton :rows="5" animated />
          </div>

          <div v-else-if="submittedClaims.length === 0" class="text-center py-16">
            <svg class="w-16 h-16 mx-auto icon-muted mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
            </svg>
            <p class="text-fg-secondary">你还没有提交过任何认领请求</p>
            <el-button type="primary" class="mt-4" @click="$router.push('/forum')">
              去论坛看看
            </el-button>
          </div>

          <div v-else class="space-y-4">
            <el-card v-for="claim in submittedClaims" :key="claim.id" shadow="hover">
              <div class="flex flex-col md:flex-row gap-4">
                <!-- 帖子信息 -->
                <div class="flex-1">
                  <div class="flex items-start justify-between mb-3">
                    <div>
                      <h3 class="text-lg font-semibold text-fg-primary mb-1 cursor-pointer hover-text-primary"
                          @click="$router.push(`/forum/${claim.post.id}`)">
                        {{ claim.post.title }}
                      </h3>
                      <div class="flex items-center gap-2 text-sm text-fg-secondary">
                        <el-tag :type="getStatusType(claim.status)" size="small">
                          {{ getStatusLabel(claim.status) }}
                        </el-tag>
                        <span>{{ formatDate(claim.created_at) }}</span>
                      </div>
                    </div>
                  </div>

                  <!-- 我的留言 -->
                  <div v-if="claim.message" class="bg-muted rounded p-3 mb-3">
                    <div class="text-xs text-fg-secondary mb-1">我的留言：</div>
                    <p class="text-sm text-fg-primary">{{ claim.message }}</p>
                  </div>

                  <!-- 物主回复 -->
                  <div v-if="claim.owner_reply" class="bg-muted rounded p-3 mb-3">
                    <div class="text-xs text-primary mb-1">物主回复：</div>
                    <p class="text-sm text-fg-primary">{{ claim.owner_reply }}</p>
                  </div>

                  <!-- 时间信息 -->
                  <div class="flex flex-wrap gap-4 text-xs text-fg-muted">
                    <span v-if="claim.updated_at">更新于 {{ formatDate(claim.updated_at) }}</span>
                    <span v-if="claim.confirmed_at" class="text-success">确认于 {{ formatDate(claim.confirmed_at) }}</span>
                  </div>
                </div>

                <!-- 操作按钮 -->
                <div class="flex flex-col gap-2 md:w-32">
                  <el-button
                    v-if="claim.status === 'pending'"
                    size="small"
                    type="danger"
                    plain
                    @click="handleCancel(claim.id)"
                  >
                    取消认领
                  </el-button>
                  <el-button
                    v-if="claim.status === 'approved' && !hasRated(claim.id)"
                    size="small"
                    type="primary"
                    @click="handleRate(claim)"
                  >
                    评价物主
                  </el-button>
                  <el-button
                    size="small"
                    @click="$router.push(`/forum/${claim.post.id}`)"
                  >
                    查看帖子
                  </el-button>
                </div>
              </div>
            </el-card>
          </div>
        </el-tab-pane>

        <!-- 收到的认领请求 -->
        <el-tab-pane label="收到的认领请求" name="received">
          <template #label>
            <span class="flex items-center gap-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
              收到的认领请求
              <el-badge v-if="pendingReceived > 0" :value="pendingReceived" type="warning" class="ml-2" />
            </span>
          </template>

          <div v-if="loadingReceived" class="py-8">
            <el-skeleton :rows="5" animated />
          </div>

          <div v-else-if="receivedClaims.length === 0" class="text-center py-16">
            <svg class="w-16 h-16 mx-auto icon-muted mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p class="text-fg-secondary">还没有人认领你的帖子</p>
          </div>

          <div v-else class="space-y-4">
            <el-card v-for="claim in receivedClaims" :key="claim.id" shadow="hover">
              <div class="flex flex-col md:flex-row gap-4">
                <!-- 认领信息 -->
                <div class="flex-1">
                  <div class="flex items-start justify-between mb-3">
                    <div>
                      <h3 class="text-lg font-semibold text-fg-primary mb-1">
                        来自 <span class="text-primary">{{ claim.claimer.name }}</span> 的认领请求
                      </h3>
                      <div class="flex items-center gap-2 text-sm text-fg-secondary">
                        <el-tag :type="getStatusType(claim.status)" size="small">
                          {{ getStatusLabel(claim.status) }}
                        </el-tag>
                        <span>{{ formatDate(claim.created_at) }}</span>
                      </div>
                    </div>
                  </div>

                  <!-- 帖子信息 -->
                  <div class="bg-muted rounded p-3 mb-3">
                    <div class="text-xs text-fg-secondary mb-1">关于帖子：</div>
                    <p class="text-sm font-medium text-fg-primary cursor-pointer hover-text-primary"
                       @click="$router.push(`/forum/${claim.post.id}`)">
                      {{ claim.post.title }}
                    </p>
                  </div>

                  <!-- 认领者留言 -->
                  <div v-if="claim.message" class="bg-muted rounded p-3 mb-3">
                    <div class="text-xs text-primary mb-1">认领者留言：</div>
                    <p class="text-sm text-fg-primary">{{ claim.message }}</p>
                  </div>

                  <!-- 我的回复 -->
                  <div v-if="claim.owner_reply" class="bg-muted rounded p-3 mb-3">
                    <div class="text-xs text-fg-secondary mb-1">我的回复：</div>
                    <p class="text-sm text-fg-primary">{{ claim.owner_reply }}</p>
                  </div>

                  <!-- 认领者信用分 -->
                  <div class="flex items-center gap-2 text-sm">
                    <span class="text-fg-secondary">认领者信用分：</span>
                    <el-tag :type="getCreditType(claim.claimer.credit_score)" size="small">
                      {{ claim.claimer.credit_score }} 分
                    </el-tag>
                    <el-button
                      text
                      type="primary"
                      size="small"
                      @click="$router.push(`/users/${claim.claimer.id}`)"
                    >
                      查看用户
                    </el-button>
                  </div>
                </div>

                <!-- 操作按钮 -->
                <div class="flex flex-col gap-2 md:w-32">
                  <template v-if="claim.status === 'pending'">
                    <el-button
                      size="small"
                      type="success"
                      @click="handleApprove(claim)"
                    >
                      ✓ 确认
                    </el-button>
                    <el-button
                      size="small"
                      type="danger"
                      plain
                      @click="handleReject(claim)"
                    >
                      ✗ 拒绝
                    </el-button>
                  </template>
                  <el-button
                    v-if="claim.status === 'approved' && !hasRated(claim.id)"
                    size="small"
                    type="primary"
                    @click="handleRate(claim)"
                  >
                    评价认领者
                  </el-button>
                  <el-button
                    size="small"
                    @click="$router.push(`/forum/${claim.post.id}`)"
                  >
                    查看帖子
                  </el-button>
                </div>
              </div>
            </el-card>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 评价对话框 -->
    <RatingDialog
      v-model="showRatingDialog"
      :claim="selectedClaim"
      @rated="handleRated"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { claimAPI, postAPI } from '@/api'
import { useAuthStore } from '@/stores/auth'
import RatingDialog from '@/components/RatingDialog.vue'

const activeTab = ref('submitted')
const submittedClaims = ref([])
const receivedClaims = ref([])
const receivedClaimsByPost = ref({})
const loadingSubmitted = ref(false)
const loadingReceived = ref(false)
const showRatingDialog = ref(false)
const selectedClaim = ref(null)
const ratedClaims = ref(new Set())

// 计算待处理的认领请求数量
const pendingReceived = computed(() => {
  return receivedClaims.value.filter(c => c.status === 'pending').length
})

// 加载我提交的认领
const loadSubmittedClaims = async () => {
  loadingSubmitted.value = true
  try {
    const response = await claimAPI.getMyClaims()
    submittedClaims.value = response.data
  } catch (error) {
    ElMessage.error('加载失败：' + (error.response?.data?.detail || error.message))
  } finally {
    loadingSubmitted.value = false
  }
}

// 加载收到的认领请求
const loadReceivedClaims = async () => {
  loadingReceived.value = true
  try {
    // 获取我的所有帖子
    const postsResponse = await postAPI.getAll()
    const allPosts = postsResponse.data.posts || postsResponse.data
    
    // 从authStore获取当前用户ID
    const authStore = useAuthStore()
    const myPosts = allPosts.filter(post => post.author_id === authStore.user?.id)
    
    // 获取每个帖子的认领请求
    const claimsPromises = myPosts.map(post => 
      claimAPI.getPostClaims(post.id).catch(() => ({ data: [] }))
    )
    const claimsResponses = await Promise.all(claimsPromises)
    
    // 合并所有认领请求
    const allClaims = []
    claimsResponses.forEach((response, index) => {
      const claims = response.data || []
      claims.forEach(claim => {
        claim.post = myPosts[index] // 添加帖子信息
        allClaims.push(claim)
      })
    })
    
    receivedClaims.value = allClaims.sort((a, b) => 
      new Date(b.created_at) - new Date(a.created_at)
    )
  } catch (error) {
    ElMessage.error('加载失败：' + (error.response?.data?.detail || error.message))
  } finally {
    loadingReceived.value = false
  }
}

// Tab切换
const handleTabChange = (tab) => {
  if (tab === 'submitted' && submittedClaims.value.length === 0) {
    loadSubmittedClaims()
  } else if (tab === 'received' && receivedClaims.value.length === 0) {
    loadReceivedClaims()
  }
}

// 取消认领
const handleCancel = async (claimId) => {
  try {
    await ElMessageBox.confirm('确定要取消这个认领请求吗？', '确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await claimAPI.cancel(claimId)
    ElMessage.success('已取消认领')
    loadSubmittedClaims()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '操作失败')
    }
  }
}

// 确认认领
const handleApprove = async (claim) => {
  try {
    const { value: reply } = await ElMessageBox.prompt(
      '确认这是认领者的物品吗？你可以留言给对方：',
      '确认认领',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        inputType: 'textarea',
        inputPlaceholder: '例如：确认是你的，请联系我领取...'
      }
    )
    
    await claimAPI.approve(claim.id, { owner_reply: reply || '' })
    ElMessage.success('已确认认领')
    loadReceivedClaims()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '操作失败')
    }
  }
}

// 拒绝认领
const handleReject = async (claim) => {
  try {
    const { value: reply } = await ElMessageBox.prompt(
      '请说明拒绝的原因（可选）：',
      '拒绝认领',
      {
        confirmButtonText: '确定拒绝',
        cancelButtonText: '取消',
        inputType: 'textarea',
        inputPlaceholder: '例如：抱歉，经核实不是你的物品...'
      }
    )
    
    await claimAPI.reject(claim.id, { owner_reply: reply || '' })
    ElMessage.success('已拒绝认领')
    loadReceivedClaims()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '操作失败')
    }
  }
}

// 评价
const handleRate = (claim) => {
  selectedClaim.value = claim
  showRatingDialog.value = true
}

// 评价完成
const handleRated = (claimId) => {
  ratedClaims.value.add(claimId)
  showRatingDialog.value = false
  ElMessage.success('评价成功！')
}

// 检查是否已评价
const hasRated = (claimId) => {
  return ratedClaims.value.has(claimId)
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  
  if (days > 7) {
    return date.toLocaleDateString('zh-CN')
  } else if (days > 0) {
    return `${days}天前`
  } else if (hours > 0) {
    return `${hours}小时前`
  } else if (minutes > 0) {
    return `${minutes}分钟前`
  } else {
    return '刚刚'
  }
}

// 状态标签
const getStatusLabel = (status) => {
  const labels = {
    pending: '待处理',
    approved: '已确认',
    rejected: '已拒绝',
    cancelled: '已取消'
  }
  return labels[status] || status
}

const getStatusType = (status) => {
  const types = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger',
    cancelled: 'info'
  }
  return types[status] || ''
}

// 信用分标签
const getCreditType = (score) => {
  if (score >= 80) return 'success'
  if (score >= 60) return ''
  if (score >= 40) return 'warning'
  return 'danger'
}

onMounted(() => {
  loadSubmittedClaims()
})
</script>

<style scoped>
.el-header {
  padding: 0;
}
</style>
