<template>
  <div class="min-h-screen" style="background-color: var(--bg-base);">
    <el-header class="themed-header shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <router-link to="/" class="text-xl font-bold text-fg-primary">🎯 Lost & Found</router-link>
        <div class="space-x-2">
          <el-button text @click="$router.push('/dashboard')">← 返回Dashboard</el-button>
          <el-button text @click="$router.push('/forum')">论坛</el-button>
        </div>
      </div>
    </el-header>

    <div class="content-wrapper py-8">
      <h1 class="text-3xl font-bold text-fg-primary mb-6">📦 我的认领</h1>

      <el-tabs v-model="activeTab" class="claims-tabs">
        <!-- 我发出的认领 -->
        <el-tab-pane label="我发出的认领" name="submitted">
          <template #label>
            <span class="flex items-center gap-2">
              我发出的认领
              <el-badge v-if="submittedClaims.length > 0" :value="submittedClaims.length" class="ml-2" />
            </span>
          </template>

          <div v-if="loadingSubmitted" class="py-8">
            <el-skeleton :rows="5" animated />
          </div>

          <div v-else-if="submittedClaims.length === 0" class="py-8">
            <el-empty description="你还没有发出任何认领">
              <el-button type="primary" @click="$router.push('/forum')">
                去论坛看看
              </el-button>
            </el-empty>
          </div>

          <div v-else class="space-y-4">
            <el-card v-for="claim in submittedClaims" :key="claim.id" shadow="hover">
              <div class="flex flex-col md:flex-row gap-4">
                <!-- 帖子信息 -->
                <div class="flex-1">
                  <div class="flex items-start justify-between mb-3">
                    <div>
                      <h3
                        v-if="claim.post"
                        class="text-lg font-semibold text-fg-primary mb-1 cursor-pointer hover-text-primary"
                        @click="$router.push(`/forum/${claim.post.id}`)"
                      >
                        {{ claim.post.title }}
                      </h3>
                      <h3 v-else class="text-lg font-semibold text-fg-secondary mb-1">
                        关联的帖子不可用
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
                    :disabled="!claim.post"
                    @click="$router.push(`/forum/${claim.post.id}`)"
                  >
                    查看帖子
                  </el-button>
                </div>
              </div>
            </el-card>
          </div>
        </el-tab-pane>

        <!-- 我收到的认领 -->
        <el-tab-pane label="我收到的认领" name="received">
          <template #label>
            <span class="flex items-center gap-2">
              我收到的认领
              <el-badge v-if="pendingReceived > 0" :value="pendingReceived" type="warning" class="ml-2" />
            </span>
          </template>

          <div v-if="loadingReceived" class="py-8">
            <el-skeleton :rows="5" animated />
          </div>

          <div v-else-if="receivedClaims.length === 0" class="py-8">
            <el-empty description="你的帖子还没有收到任何认领" />
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
                    <p
                      v-if="claim.post"
                      class="text-sm font-medium text-fg-primary cursor-pointer hover-text-primary"
                      @click="$router.push(`/forum/${claim.post.id}`)"
                    >
                      {{ claim.post.title }}
                    </p>
                    <p v-else class="text-sm text-fg-secondary">关联的帖子不可用</p>
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
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import message from '@/utils/message'
import { claimAPI } from '@/api'
import { useAuthStore } from '@/stores/auth'
import RatingDialog from '@/components/RatingDialog.vue'
import { formatRelative as formatRelativeTime } from '@/utils/time'

const route = useRoute()
const activeTab = ref(route.query.tab === 'received' ? 'received' : 'submitted')
const submittedClaims = ref([])
const receivedClaims = ref([])
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
    message.error('加载失败：' + (error.response?.data?.detail || error.message))
  } finally {
    loadingSubmitted.value = false
  }
}

// 加载收到的认领请求
const loadReceivedClaims = async () => {
  console.log('[ClaimsView] Loading received claims...')
  loadingReceived.value = true
  try {
    console.log('[ClaimsView] Calling claimAPI.getReceived()...')
    const response = await claimAPI.getReceived()
    console.log('[ClaimsView] Raw API response:', response)
    console.log('[ClaimsView] Response data:', response.data)
    
    const data = response.data || []
    receivedClaims.value = Array.isArray(data) ? data : []
    
    console.log('[ClaimsView] Processed received claims:', receivedClaims.value)
    console.log('[ClaimsView] Number of received claims:', receivedClaims.value.length)
    
    if (receivedClaims.value.length > 0) {
      console.log('[ClaimsView] First received claim:', receivedClaims.value[0])
    }
  } catch (error) {
    console.error('[ClaimsView] Error loading received claims:', error)
    console.error('[ClaimsView] Error response:', error.response)
    message.error('加载失败：' + (error.response?.data?.detail || error.message))
  } finally {
    loadingReceived.value = false
  }
}

// Tab切换侦听，确保正确加载
watch(activeTab, (tab) => {
  if (tab === 'submitted' && submittedClaims.value.length === 0) {
    loadSubmittedClaims()
  }
  if (tab === 'received' && receivedClaims.value.length === 0) {
    loadReceivedClaims()
  }
})

// 侦听路由查询参数变化，确保与activeTab同步并按需加载
watch(
  () => route.query.tab,
  (tab) => {
    const normalized = tab === 'received' ? 'received' : 'submitted'
    if (activeTab.value !== normalized) {
      activeTab.value = normalized
    }
    if (normalized === 'received' && receivedClaims.value.length === 0) {
      loadReceivedClaims()
    } else if (normalized === 'submitted' && submittedClaims.value.length === 0) {
      loadSubmittedClaims()
    }
  }
)

// 取消认领
const handleCancel = async (claimId) => {
  try {
    await ElMessageBox.confirm('确定要取消这个认领请求吗？', '确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await claimAPI.cancel(claimId)
    message.success('已取消认领')
    loadSubmittedClaims()
  } catch (error) {
    if (error !== 'cancel') {
      message.error(error.response?.data?.detail || '操作失败')
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
    message.success('已确认认领')
    loadReceivedClaims()
  } catch (error) {
    if (error !== 'cancel') {
      message.error(error.response?.data?.detail || '操作失败')
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
    message.success('已拒绝认领')
    loadReceivedClaims()
  } catch (error) {
    if (error !== 'cancel') {
      message.error(error.response?.data?.detail || '操作失败')
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
  message.success('评价成功！')
}

// 检查是否已评价
const hasRated = (claimId) => {
  return ratedClaims.value.has(claimId)
}

// 格式化日期
const formatDate = (dateString) => formatRelativeTime(dateString)

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
  // 预取当前激活tab数据
  if (activeTab.value === 'submitted') {
    loadSubmittedClaims()
  } else {
    loadReceivedClaims()
  }
})
</script>

<style scoped>
.el-header {
  padding: 0;
}

.claims-tabs :deep(.el-tabs__header) {
  background-color: var(--bg-surface);
  border-bottom: 2px solid var(--border-base);
  margin-bottom: 1.5rem;
  padding: 0 1rem;
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
}

.claims-tabs :deep(.el-tabs__nav) {
  border: none;
}

.claims-tabs :deep(.el-tabs__item) {
  color: var(--text-secondary);
  border: none;
  padding: 1rem 1.5rem;
  font-weight: 500;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.claims-tabs :deep(.el-tabs__item:hover) {
  color: var(--text-primary);
}

.claims-tabs :deep(.el-tabs__item.is-active) {
  color: var(--brand-primary);
  font-weight: 600;
}

.claims-tabs :deep(.el-tabs__active-bar) {
  background-color: var(--brand-primary);
  height: 3px;
}

.el-card {
  background-color: var(--bg-card);
  border: 1px solid var(--border-base);
  transition: all 0.3s ease;
}

.el-card:hover {
  border-color: var(--brand-primary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}
</style>
