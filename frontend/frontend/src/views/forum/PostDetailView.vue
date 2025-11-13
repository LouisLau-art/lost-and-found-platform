<template>
  <div class="min-h-screen bg-page">
    <el-header class="fixed w-full z-10 themed-header">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <router-link to="/" class="text-xl font-bold text-primary flex items-center gap-2">
          <el-icon><Target /></el-icon> Lost & Found
        </router-link>
        <div class="space-x-2">
          <el-button text @click="$router.push('/forum')" class="text-fg-primary">
            <el-icon><ArrowLeft /></el-icon> 返回列表
          </el-button>
          <el-button v-if="authStore.isAuthenticated" text @click="$router.push('/dashboard')">Dashboard</el-button>
          <el-button v-else type="primary" @click="$router.push('/login')">登录</el-button>
        </div>
      </div>
    </el-header>

    <div class="content-wrapper py-24">
      <!-- Loading -->
      <div v-if="loading" class="py-12">
        <el-skeleton :rows="8" animated class="rounded-lg overflow-hidden" />
      </div>

      <!-- Error -->
      <el-alert v-else-if="error" :title="error" type="error" show-icon class="mb-6" />
      

      <!-- Content -->
      <div v-else-if="post" class="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fade-in">
        <!-- 主内容区 -->
        <div class="lg:col-span-2 space-y-6">
          <!-- 帖子主体 -->
          <el-card class="shadow-md hover:shadow-lg transition-shadow duration-300 post-detail-card">
            <!-- 清晰的头部 -->
            <div class="post-header">
              <h1 class="post-main-title">
                {{ post.title }}
              </h1>
              
              <!-- 标签栏 -->
              <div class="flex items-center flex-wrap gap-3 mt-4">
                <el-tag :type="getTypeColor(post.item_type)" size="large" class="font-semibold">
                  {{ getTypeLabel(post.item_type) }}
                </el-tag>
                <el-tag v-if="post.category" type="info" size="large" class="font-semibold">
                  <el-icon><Category /></el-icon> {{ post.category.name }}
                </el-tag>
                <el-tag v-if="post.is_claimed" type="success" size="large" class="font-semibold">
                  <el-icon><Check /></el-icon> 已认领
                </el-tag>
              </div>
            </div>

            <!-- 元信息和操作 -->
            <div class="post-meta">
              <div class="flex flex-wrap items-center gap-4">
                <span class="meta-item" @click="$router.push(`/users/${post.author?.id}`)">
                  <el-icon><User /></el-icon>
                  {{ post.author?.name || 'Unknown' }}
                </span>
                <span class="meta-item">
                  <el-icon><Time /></el-icon>
                  {{ formatDate(post.created_at) }}
                </span>
                <span v-if="post.updated_at" class="meta-item meta-muted">
                  <el-icon><Edit /></el-icon>
                  (已编辑)
                </span>
              </div>
            </div>
            <!-- 编辑按钮 - 仅作者可见 -->
            <div v-if="isAuthor" class="flex items-center gap-2 mb-4">
              <el-button 
                @click="editPost" 
                type="primary"
                size="small"
                class="transition-all duration-300"
              >
                <el-icon><Edit /></el-icon>
                编辑帖子
              </el-button>
            </div>

            <!-- 详细信息卡片 -->
            <div v-if="hasDetails" class="details-card">
              <h3 class="details-title">
                <el-icon><Document /></el-icon>
                详细信息
              </h3>
              <el-descriptions :column="2" border size="large" class="custom-descriptions">
                <el-descriptions-item v-if="post.location" label="地点">
                  <el-icon class="icon-primary"><Location /></el-icon>
                  <span class="ml-2">{{ post.location }}</span>
                </el-descriptions-item>
                <el-descriptions-item v-if="post.item_time" :label="post.item_type === 'lost' ? '丢失时间' : '拾取时间'">
                  <el-icon class="icon-primary"><Time /></el-icon>
                  <span class="ml-2">{{ formatDateTime(post.item_time) }}</span>
                </el-descriptions-item>
                <el-descriptions-item v-if="post.contact_info && canViewContact" label="联系方式" :span="2">
                  <el-icon class="icon-primary"><Phone /></el-icon>
                  <span class="ml-2">{{ post.contact_info }}</span>
                </el-descriptions-item>
              </el-descriptions>
            </div>

            <!-- 内容 -->
            <div class="mb-6">
              <p class="content-text whitespace-pre-wrap text-base leading-relaxed">{{ post.content }}</p>
            </div>

            <!-- 图片画廊 -->
            <div v-if="post.images && post.images.length > 0" class="mb-6">
              <ImageGallery :images="post.images" />
            </div>

            <!-- 操作按钮 -->
            <div class="flex flex-wrap items-center justify-between mt-6 pt-6 card-footer gap-4">
              <div class="flex gap-2">
                <el-button
                  v-if="post.is_claimed"
                  type="success"
                  disabled
                  size="large"
                >
                  <el-icon><Check /></el-icon>
                  已认领
                </el-button>
                <el-button
                  v-else-if="hasApprovedClaim"
                  type="success"
                  disabled
                  size="large"
                >
                  <el-icon><Check /></el-icon>
                  认领已通过
                </el-button>
                <el-button
                  v-else-if="hasPendingClaim"
                  type="warning"
                  disabled
                  size="large"
                >
                  <el-icon><Time /></el-icon>
                  已提交认领，请等待物主确认
                </el-button>
                <el-button
                  v-else-if="hasRejectedClaim"
                  type="info"
                  disabled
                  size="large"
                >
                  <el-icon><InfoFilled /></el-icon>
                  认领请求已被拒绝
                </el-button>
                <el-button
                  v-else-if="canClaim"
                  type="primary"
                  size="large"
                  @click="handleClaim"
                  class="hover:shadow-md transition-all duration-300"
                >
                  <el-icon><Check /></el-icon>
                  我要认领
                </el-button>
                <el-button
                  v-if="isAuthor && !post.is_claimed"
                  text
                  type="info"
                  @click="showClaimRequests = true"
                  class="hover:bg-info/10 transition-colors"
                >
                  <el-icon><Document /></el-icon>
                  认领请求 ({{ claimRequests.length }})
                </el-button>
              </div>
              <div v-if="isAuthor" class="flex gap-2">
                <el-button text type="primary" @click="editPost" class="hover:bg-primary/10 transition-colors">编辑</el-button>
                <el-button text type="danger" @click="deletePost" class="hover:bg-danger/10 transition-colors">删除</el-button>
              </div>
            </div>
            
            <!-- 认领状态信息 -->
            <div v-if="post.is_claimed && claimedBy" class="mt-6 p-4 claimed-box rounded-lg shadow-sm">
              <div class="flex items-center gap-2 claimed-box-title">
                <el-icon class="text-lg"><Check /></el-icon>
                <h3 class="font-semibold">该物品已被认领</h3>
              </div>
              <div class="mt-2 claimed-box-text">
                <p>认领者：{{ claimedBy.name }}</p>
                <p v-if="claimedAt" class="text-sm claimed-box-time">认领时间：{{ formatDateTime(claimedAt) }}</p>
              </div>
            </div>
          </el-card>

          <!-- 评论区 -->
          <el-card class="shadow-md hover:shadow-lg transition-shadow duration-300">
            <h2 class="text-xl font-semibold mb-4 flex items-center gap-2 text-[var(--text-primary)]">
              <el-icon><ChatDotRound /></el-icon>
              评论 ({{ comments.length }})
            </h2>

            <!-- 评论表单 -->
            <div v-if="authStore.isAuthenticated" class="mb-6">
              <el-input
                v-model="commentContent"
                type="textarea"
                :rows="3"
                placeholder="发表你的看法..."
                class="mb-3"
                :border="true"
              />
              <div class="flex justify-end">
                <el-button type="primary" :loading="submittingComment" @click="submitComment" class="shadow hover:shadow-md transition-all">
                  <el-icon><Send /></el-icon>
                  发表评论
                </el-button>
              </div>
            </div>
            <el-alert v-else title="登录后才能发表评论" type="info" show-icon class="mb-6" />

            <!-- 评论列表 -->
            <div v-if="comments.length > 0" class="space-y-4">
              <div v-for="comment in comments" :key="comment.id" class="border-l-2 comment-border pl-4 hover-border-primary transition-colors animate-fade-in">
                <div class="flex items-start justify-between">
                  <div class="flex-1">
                    <div class="flex items-center gap-2 mb-2">
                      <el-icon class="icon-muted"><User /></el-icon>
                      <span class="font-medium">{{ comment.author?.name }}</span>
                      <span class="text-xs text-muted">{{ formatDate(comment.created_at) }}</span>
                    </div>
                    <p class="content-text">{{ comment.content }}</p>
                  </div>
                  <el-button
                    v-if="authStore.user?.id === comment.author_id"
                    text
                    type="danger"
                    size="small"
                    @click="deleteComment(comment.id)"
                    class="hover:bg-danger/10 transition-colors"
                  >
                    <el-icon><Delete /></el-icon>
                    删除
                  </el-button>
                </div>
              </div>
            </div>
            <div v-else class="text-center py-10 text-fg-muted">
              <el-empty description="暂无评论，快来抢沙发吧！" />
            </div>
          </el-card>
        </div>

        <!-- 侧边栏 -->
        <div class="lg:col-span-1 space-y-6">
          <!-- 智能匹配推荐 -->
          <el-card v-if="matchedPosts.length > 0" class="shadow-md sticky top-20 hover:shadow-lg transition-shadow duration-300">
            <template #header>
              <div class="flex items-center gap-2">
                <el-icon class="icon-primary"><RefreshRight /></el-icon>
                <span class="font-semibold">智能匹配推荐</span>
              </div>
            </template>
            <div class="space-y-3">
              <div
                v-for="matched in matchedPosts"
                :key="matched.id"
                class="border rounded p-3 cursor-pointer hover-card transition-all hover:shadow-sm animate-fade-in"
                @click="$router.push(`/forum/${matched.id}`)"
              >
                <div class="flex items-start gap-2 mb-1">
                  <el-tag :type="getTypeColor(matched.item_type)" size="small">
                    {{ getTypeLabel(matched.item_type) }}
                  </el-tag>
                </div>
                <h4 class="font-medium text-sm mb-1 line-clamp-2">{{ matched.title }}</h4>
                <p class="text-xs text-muted line-clamp-1 flex items-center gap-1">
                  <el-icon class="w-3 h-3 icon-primary"><Location /></el-icon>
                  {{ matched.location }}
                </p>
              </div>
            </div>
          </el-card>

          <!-- 发布者信息 -->
          <el-card v-if="post.author" class="shadow-md hover:shadow-lg transition-shadow duration-300">
            <template #header>
              <span class="font-semibold">发布者</span>
            </template>
            <div class="text-center cursor-pointer hover-card transition-all rounded p-2 hover:shadow-sm"
                 @click="$router.push(`/users/${post.author.id}`)">
              <div class="w-16 h-16 author-avatar rounded-full mx-auto mb-3 flex items-center justify-center shadow-sm hover:scale-105 transition-transform">
                  <el-icon class="w-8 h-8 icon-primary"><User /></el-icon>
                </div>
              <h3 class="font-semibold mb-1">{{ post.author.name }}</h3>
              <div v-if="post.author.credit_score" class="mt-3 text-sm">
                <span class="text-muted">信用分：</span>
                <span class="font-semibold text-primary">{{ post.author.credit_score }}</span>
              </div>
              <el-button type="primary" size="small" class="mt-3 shadow hover:shadow-md transition-all">
                <el-icon><User /></el-icon>
                查看主页
              </el-button>
            </div>
          </el-card>
        </div>
      </div>

      <!-- Not Found -->
      <div v-else class="text-center py-16">
        <el-empty description="帖子不存在">
          <el-button type="primary" @click="$router.push('/forum')" class="shadow hover:shadow-md transition-all">
            <el-icon><ArrowLeft /></el-icon>
            返回列表
          </el-button>
        </el-empty>
      </div>
    </div>
    
    <!-- 认领请求管理对话框 -->
    <el-dialog
      v-model="showClaimRequests"
      title="认领请求管理"
      width="700px"
      :close-on-click-modal="false"
      class="animate-fade-in"
    >
      <div v-if="claimRequests.length === 0" class="text-center py-10 text-fg-muted">
        暂无认领请求
      </div>
      
      <div v-else class="space-y-4">
        <div
          v-for="claim in claimRequests"
          :key="claim.id"
          class="p-4 border rounded-lg hover:bg-muted transition"
        >
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-full flex items-center justify-center author-avatar">
              <el-icon class="w-4 h-4 icon-primary"><User /></el-icon>
            </div>
              <div>
                <div class="font-medium">{{ claim.requester.name }}</div>
                <div class="text-xs text-fg-secondary">
                  {{ formatDateTime(claim.created_at) }}
                  <span v-if="claim.requester.credit_score" class="ml-2">
                    信用分：{{ claim.requester.credit_score }}
                  </span>
                </div>
              </div>
            </div>
            <el-tag :type="getStatusType(claim.status)">
              {{ getStatusLabel(claim.status) }}
            </el-tag>
          </div>
          
          <div v-if="claim.message" class="mb-3">
            <div class="text-xs text-fg-secondary mb-1">认领理由：</div>
            <div class="text-fg-primary whitespace-pre-wrap">{{ claim.message }}</div>
          </div>
          
          <div v-if="claim.owner_reply" class="mb-3">
            <div class="text-xs text-fg-secondary mb-1">我的回复：</div>
            <div class="text-fg-primary whitespace-pre-wrap">{{ claim.owner_reply }}</div>
          </div>
          
          <div v-if="claim.status === 'pending'" class="flex gap-2 justify-end">
            <el-button
              type="primary"
              size="small"
              @click="handleApproveClaim(claim.id)"
              :loading="handlingClaim"
            >
              批准
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleRejectClaim(claim.id)"
              :loading="handlingClaim"
            >
              拒绝
            </el-button>
          </div>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="showClaimRequests = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { postAPI, claimAPI } from '@/api'
import { ElMessageBox } from 'element-plus'
import message from '@/utils/message'
import { formatRelative as formatRelativeTime, formatLocal } from '@/utils/time'
import ImageGallery from '@/components/ImageGallery.vue'
// 动态导入Element Plus图标组件
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// 注册所有图标
const icons = {
  Target: ElementPlusIconsVue.Target,
  ArrowLeft: ElementPlusIconsVue.ArrowLeft,
  User: ElementPlusIconsVue.User,
  Time: ElementPlusIconsVue.Time,
  Edit: ElementPlusIconsVue.Edit,
  Document: ElementPlusIconsVue.Document,
  Location: ElementPlusIconsVue.Location,
  Phone: ElementPlusIconsVue.Phone,
  Check: ElementPlusIconsVue.Check,
  ChatDotRound: ElementPlusIconsVue.ChatDotRound,
  Send: ElementPlusIconsVue.Send,
  Delete: ElementPlusIconsVue.Delete,
  Category: ElementPlusIconsVue.Category
}

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const post = ref(null)
const comments = ref([])
const matchedPosts = ref([])
const claimRequests = ref([])
const showClaimRequests = ref(false)
const claimedBy = ref(null)
const claimedAt = ref(null)
const loading = ref(false)
const error = ref(null)
const commentContent = ref('')
const submittingComment = ref(false)
const handlingClaim = ref(false)
const myClaim = ref(null)

// 计算属性
const isAuthor = computed(() => {
  return authStore.user?.id === post.value?.author_id
})

// 编辑帖子 - 函数定义在文件后续部分

const canClaim = computed(() => {
  if (!authStore.isAuthenticated || isAuthor.value) return false
  if (post.value?.item_type !== 'found') return false
  if (myClaim.value && ['pending', 'approved'].includes(myClaim.value.status)) {
    return false
  }
  return true
})

const canViewContact = computed(() => {
  return authStore.isAuthenticated
})

const hasPendingClaim = computed(() => myClaim.value?.status === 'pending')
const hasApprovedClaim = computed(() => myClaim.value?.status === 'approved')
const hasRejectedClaim = computed(() => myClaim.value?.status === 'rejected')

const hasDetails = computed(() => {
  return post.value?.location || post.value?.item_time || (post.value?.contact_info && canViewContact.value)
})

// 方法
const getStatusType = (status) => ({
  pending: 'warning',
  approved: 'success',
  rejected: 'danger',
  cancelled: 'info'
})[status] || ''

const getStatusLabel = (status) => ({
  pending: '待处理',
  approved: '已批准',
  rejected: '已拒绝',
  cancelled: '已取消'
})[status] || status

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

const formatDate = (date) => formatRelativeTime(date)
const formatDateTime = (date) => formatLocal(date)

const loadPost = async () => {
  loading.value = true
  error.value = null
  try {
    const postId = parseInt(route.params.id)
    const [postRes, commentsRes] = await Promise.all([
      postAPI.getById(postId),
      postAPI.getComments(postId)
    ])
    post.value = postRes.data
    comments.value = commentsRes.data
    
    // 加载认领信息
    if (post.value.is_claimed && post.value.claimer) {
      claimedBy.value = post.value.claimer
      claimedAt.value = post.value.claimed_at
    } else {
      claimedBy.value = null
      claimedAt.value = null
    }

    // 如果是作者，加载认领请求
    if (isAuthor.value && !post.value.is_claimed) {
      try {
        const claimsRes = await claimAPI.getPostClaims(postId)
        claimRequests.value = claimsRes.data
      } catch (err) {
        console.error('Failed to load claim requests:', err)
      }
    } else {
      claimRequests.value = []
    }

    if (authStore.isAuthenticated && !isAuthor.value) {
      await refreshMyClaim()
    } else {
      myClaim.value = null
    }

    // 加载匹配推荐
    if (post.value.item_type !== 'general') {
      try {
        const matchRes = await postAPI.getMatches(postId, { limit: 5 })
        matchedPosts.value = matchRes.data
      } catch (err) {
        console.error('Failed to load matches:', err)
      }
    }
  } catch (err) {
    error.value = err.response?.data?.detail || '加载失败'
  } finally {
    loading.value = false
  }
}

const submitComment = async () => {
  if (!commentContent.value.trim()) return
  submittingComment.value = true
  try {
    await postAPI.createComment(post.value.id, commentContent.value)
    message.success('评论成功')
    commentContent.value = ''
    await loadPost()
  } catch (err) {
    message.error(err.response?.data?.detail || '评论失败')
  } finally {
    submittingComment.value = false
  }
}

const deleteComment = async (commentId) => {
  try {
    await ElMessageBox.confirm('确认删除该评论？', '提示', { type: 'warning' })
    await postAPI.deleteComment(commentId)
    message.success('删除成功')
    await loadPost()
  } catch (err) {
    if (err !== 'cancel') {
      message.error('删除失败')
    }
  }
}

const handleClaim = async () => {
  try {
    const { value: claimMessage } = await ElMessageBox.prompt(
      '请描述你的认领理由（可选）',
      '提交认领请求',
      {
        confirmButtonText: '提交',
        cancelButtonText: '取消',
        inputType: 'textarea',
        inputPlaceholder: '例如：这是我的物品，我可以描述更多细节...'
      }
    )
    
    await claimAPI.create({
      post_id: post.value.id,
      message: claimMessage || null
    })

    message.success('认领请求已提交，等待物主确认')
    await refreshMyClaim()
    await loadPost()
  } catch (err) {
    if (err !== 'cancel') {
      const detail = err?.response?.data?.detail
      if (typeof detail === 'string' && detail.toLowerCase().includes('already have a pending')) {
        message.warning('已提交认领请求，请等待物主确认')
        await refreshMyClaim()
      } else {
        message.error(detail || '提交失败')
      }
    }
  }
}

const refreshMyClaim = async () => {
  if (!authStore.isAuthenticated || isAuthor.value || !post.value?.id) {
    myClaim.value = null
    return
  }

  try {
    const res = await claimAPI.getMyClaims()
    myClaim.value = res.data.find(claim => claim.post_id === post.value.id && claim.status !== 'cancelled') || null
  } catch (err) {
    console.error('Failed to load user claim status:', err)
  }
}

const handleApproveClaim = async (claimId) => {
  try {
    const { value: reply } = await ElMessageBox.prompt(
      '请输入回复信息（可选）',
      '批准认领请求',
      {
        confirmButtonText: '批准',
        cancelButtonText: '取消',
        inputType: 'textarea',
        inputPlaceholder: '例如：已验证身份，批准认领'
      }
    )
    
    handlingClaim.value = true
    await claimAPI.approve(claimId, { owner_reply: reply || null })
    message.success('已批准认领请求')
    await loadPost()
    showClaimRequests.value = false
  } catch (err) {
    if (err !== 'cancel') {
      message.error(err.response?.data?.detail || '操作失败')
    }
  } finally {
    handlingClaim.value = false
  }
}

const handleRejectClaim = async (claimId) => {
  try {
    await ElMessageBox.confirm(
      '确定要拒绝该认领请求吗？',
      '拒绝认领请求',
      {
        confirmButtonText: '拒绝',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const { value: reply } = await ElMessageBox.prompt(
      '请输入拒绝理由（可选）',
      '拒绝认领请求',
      {
        confirmButtonText: '确认拒绝',
        cancelButtonText: '取消',
        inputType: 'textarea',
        inputPlaceholder: '例如：描述的物品特征不符'
      }
    )
    
    handlingClaim.value = true
    await claimAPI.reject(claimId, { owner_reply: reply || null })
    message.success('已拒绝认领请求')
    await loadPost()
  } catch (err) {
    if (err !== 'cancel') {
      message.error(err.response?.data?.detail || '操作失败')
    }
  } finally {
    handlingClaim.value = false
  }
}

const editPost = () => {
  router.push(`/forum/${route.params.id}/edit`)
}

const deletePost = async () => {
  try {
    await ElMessageBox.confirm('确认删除该帖子？', '提示', { type: 'warning' })
    await postAPI.delete(post.value.id)
    message.success('删除成功')
    router.push('/forum')
  } catch (err) {
    if (err !== 'cancel') {
      message.error('删除失败')
    }
  }
}

onMounted(() => loadPost())
</script>

<style scoped>
/* Post Detail Card */
.post-detail-card :deep(.el-card__body) {
  padding: var(--spacing-2xl) !important;
}

/* Themed header using variables */
.themed-header {
  background-color: var(--bg-surface);
  border-bottom: 1px solid var(--border-base);
}

.post-header {
  margin-bottom: var(--spacing-xl);
  padding-bottom: var(--spacing-xl);
  border-bottom: 1px solid var(--border-base);
}

.post-main-title {
  font-size: 2.25rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.3;
  margin-bottom: 0;
}

.post-meta {
  padding: var(--spacing-md) 0;
  margin-bottom: var(--spacing-lg);
  border-bottom: 1px solid var(--border-base);
}

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-secondary);
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: color 0.3s ease;
}

.meta-item:hover {
  color: var(--brand-primary);
}

.meta-muted {
  color: var(--text-tertiary);
  cursor: default;
}

.meta-muted:hover {
  color: var(--text-tertiary);
}

/* Details Card */
.details-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-base);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
}

.details-title {
  color: var(--text-primary);
  font-size: 1.125rem;
  font-weight: 700;
  margin-bottom: var(--spacing-md);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.custom-descriptions :deep(.el-descriptions__label) {
  color: var(--text-secondary);
  font-weight: 600;
  background-color: var(--bg-surface);
}

.custom-descriptions :deep(.el-descriptions__content) {
  color: var(--text-primary);
  font-weight: 500;
  font-size: 0.95rem;
}

.custom-descriptions :deep(.el-descriptions__cell) {
  padding: var(--spacing-md) var(--spacing-lg) !important;
}

/* Generic text colors */
.content-text { color: var(--text-primary); }
.text-muted { color: var(--text-secondary); }
.text-primary { color: var(--brand-primary); }
.icon-muted { color: var(--text-muted); }
.icon-primary { color: var(--brand-primary); }

/* Footer and dividers */
.card-footer {
  border-top: 1px solid var(--border-base);
}

/* Claimed status panel */
.claimed-box { background-color: var(--bg-muted); border: 1px solid var(--border-base); }
.claimed-box-title { color: var(--success-color); }
.claimed-box-text { color: var(--text-primary); }
.claimed-box-time { color: var(--text-secondary); }

/* Comments */
.comment-border { border-color: var(--border-base); }
.hover-border-primary:hover { border-color: var(--brand-primary); }

/* Sidebar hover cards and avatar */
.hover-card { background-color: var(--bg-card); border: 1px solid var(--border-base); }
.hover-card:hover { background-color: var(--bg-muted); }
.author-avatar { background-color: var(--bg-muted); }

/* 动画效果 */
.animate-fade-in {
  animation: fadeIn 0.5s ease-in-out;
}

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

/* 响应式调整 */
@media (max-width: 768px) {
  .max-w-7xl {
    padding-left: 1rem;
    padding-right: 1rem;
  }
  
  .post-main-title {
    font-size: 1.75rem !important;
  }
  
  .el-card {
    margin-bottom: 1rem;
  }
  
  .post-detail-card :deep(.el-card__body) {
    padding: var(--spacing-lg) !important;
  }
}

/* 卡片样式增强 */
.el-card {
  border-radius: var(--radius-lg);
  overflow: hidden;
  background-color: var(--bg-card) !important;
  border: 1px solid var(--border-base) !important;
  box-shadow: var(--shadow-sm);
}

/* 按钮增强 */
.el-button {
  border-radius: var(--radius-md);
  transition: all 0.3s ease;
  font-weight: 500;
}

.el-button:hover {
  transform: translateY(-1px);
}

/* 标签增强 */
.el-tag {
  border-radius: var(--radius-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  font-weight: 500;
  border: none;
}

/* 表单元素增强 */
.el-input__wrapper {
  border-radius: var(--radius-md);
}

/* 滚动条美化 */
:deep(.el-scrollbar__thumb) {
  background-color: var(--brand-primary);
  border-radius: var(--radius-sm);
}

/* 侧边栏粘性定位调整 */
.sticky {
  position: sticky;
  top: 80px;
}

/* 交互反馈增强 */
.cursor-pointer {
  transition: all 0.2s ease;
}

.cursor-pointer:hover {
  transform: translateY(-1px);
}

/* 文本截断工具类 */
.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>