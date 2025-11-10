<template>
  <div class="min-h-screen" style="background-color: var(--bg-page);">
    <!-- Header with navigation -->
    <el-header class="themed-header backdrop-blur-sm sticky top-0 z-10">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <router-link to="/" class="text-2xl font-bold text-fg-primary hover-text-primary transition-all flex items-center">
          Lost & Found Platform
        </router-link>
        <div class="space-x-4">
          <el-button text class="text-fg-secondary hover-text-primary" @click="$router.push('/dashboard')">
            Dashboard
          </el-button>
          <el-button text class="text-fg-secondary hover-text-primary" @click="$router.push('/forum')">
            Forum
          </el-button>
          <el-button text type="danger" @click="handleLogout" class="text-fg-secondary hover-text-primary">
            Sign out
          </el-button>
        </div>
      </div>
    </el-header>

    <!-- Main content area -->
    <main class="flex-grow container mx-auto px-4 py-8">
      <div class="max-w-5xl mx-auto">
        <!-- Steps -->
        <el-card shadow="hover" class="form-card mb-6 steps-card">
          <el-steps :active="currentStep" finish-status="success" align-center class="enhanced-steps">
            <el-step title="核心信息" description="物品类型、分类、标题、描述" />
            <el-step title="地点与时间" description="发生地点和时间" />
            <el-step title="图片与联系方式" description="上传图片和填写联系方式" />
          </el-steps>
        </el-card>

        <el-card shadow="hover" class="form-card">
          <template #header>
            <div class="flex items-center justify-between">
              <h2 class="text-xl font-bold text-fg-primary flex items-center">
                发布信息
              </h2>
              <el-tag 
                :type="getItemTypeColor(form.item_type)" 
                size="large"
              >
                {{ getItemTypeLabel(form.item_type) }}
              </el-tag>
            </div>
          </template>
          
          <el-form 
            :model="form" 
            :rules="rules" 
            ref="formRef" 
            label-position="top" 
            size="large"
          >
            <!-- 步骤1：核心信息 -->
            <div v-show="currentStep === 0" class="step-content">
              <h3 class="step-title">📌 步骤 1: 核心信息</h3>
              
              <!-- 物品类型组 -->
              <div class="form-group">
                <h4 class="group-title">物品类型与分类</h4>
                <!-- 物品类型 -->
                <el-form-item label="📌 物品类型" prop="item_type">
                <el-radio-group v-model="form.item_type" size="large" class="w-full">
                  <el-row :gutter="16">
                    <el-col :span="8">
                      <el-radio-button value="lost" class="w-full">
                        <span class="flex items-center justify-center py-3">
                          🔴 丢失物品
                        </span>
                      </el-radio-button>
                    </el-col>
                    <el-col :span="8">
                      <el-radio-button value="found" class="w-full">
                        <span class="flex items-center justify-center py-3">
                          🟢 拾到物品
                        </span>
                      </el-radio-button>
                    </el-col>
                    <el-col :span="8">
                      <el-radio-button value="general" class="w-full">
                        <span class="flex items-center justify-center py-3">
                          ⚪ 普通帖子
                        </span>
                      </el-radio-button>
                    </el-col>
                  </el-row>
                </el-radio-group>
              </el-form-item>

              <el-row :gutter="16">
                <el-col :span="12">
                  <!-- 物品分类 -->
                  <el-form-item label="🏷️ 物品分类" prop="category_id">
                    <el-select
                      v-model="form.category_id"
                      placeholder="请选择分类"
                      class="w-full"
                      :loading="loadingCategories"
                    >
                      <el-option
                        v-for="cat in categories"
                        :key="cat.id"
                        :label="`${cat.icon} ${cat.name}`"
                        :value="cat.id"
                      >
                        <span>{{ cat.icon }} {{ cat.name }}</span>
                        <span class="text-xs text-fg-muted ml-2">{{ cat.description }}</span>
                      </el-option>
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>
              </div>

              <!-- 标题与描述组 -->
              <div class="form-group">
                <h4 class="group-title">详细信息</h4>
              <!-- 标题 -->
              <el-form-item label="📄 标题" prop="title">
                <el-input
                  v-model="form.title"
                  placeholder="请输入标题，简洁明了地描述物品"
                  maxlength="100"
                  show-word-limit
                />
              </el-form-item>
              
              <!-- 详细描述 -->
              <el-form-item label="📝 详细描述" prop="content">
                <el-input
                  v-model="form.content"
                  type="textarea"
                  :rows="6"
                  placeholder="请详细描述物品特征、颜色、品牌等信息，有助于物品找回"
                  maxlength="1000"
                  show-word-limit
                  class="resize-none"
                />
                <div class="text-xs text-fg-muted mt-1">提示：详细的描述能大大提高物品找回几率</div>
              </el-form-item>
              </div>
            </div>

            <!-- 步骤2：地点与时间 -->
            <div v-show="currentStep === 1" class="step-content">
              <h3 class="step-title">📍 步骤 2: 地点与时间</h3>
              
              <el-row :gutter="16">
                <el-col :span="12">
                  <!-- 地点 -->
                  <el-form-item label="📍 地点" prop="location">
                    <el-input
                      v-model="form.location"
                      placeholder="请输入具体地点，如：图书馆三楼、东门食堂等"
                      maxlength="100"
                    />
                  </el-form-item>
                </el-col>
                
                <el-col :span="12">
                  <!-- 时间 -->
                  <el-form-item :label="getTimeLabel()" prop="item_time">
                    <el-date-picker
                      v-model="form.item_time"
                      type="datetime"
                      placeholder="选择时间"
                      class="w-full"
                      format="YYYY-MM-DD HH:mm"
                    />
                  </el-form-item>
                </el-col>
              </el-row>
            </div>

            <!-- 步骤3：图片与联系方式 -->
            <div v-show="currentStep === 2" class="step-content">
              <h3 class="step-title">📷 步骤 3: 图片与联系方式</h3>
              
              <!-- 联系方式 -->
              <el-form-item label="📞 联系方式" prop="contact_info">
                <el-input
                  v-model="form.contact_info"
                  placeholder="请输入联系方式，如：手机号、微信号等"
                  maxlength="100"
                />
              </el-form-item>
              
              <!-- 图片上传 -->
              <el-form-item label="📸 上传物品照片 (关键信息)">
                <div class="upload-hint mb-3 p-3 bg-muted border rounded-lg" style="border-color: var(--border-base);">
                  <div class="flex items-start">
                    <el-icon class="icon-primary mt-1 mr-2"><InfoFilled /></el-icon>
                    <div class="text-sm text-fg-secondary">
                      <p>提示：上传清晰的物品照片有助于快速找回</p>
                      <p class="text-xs mt-1 text-fg-muted">支持 JPG、PNG、GIF 格式，最多 9 张，每张不超过 5MB</p>
                    </div>
                  </div>
                </div>
                <ImageUpload v-model="form.images" :max-images="9" />
              </el-form-item>
            </div>
            
            <!-- Error display -->
            <el-alert 
              v-if="forumStore.error" 
              :title="forumStore.error" 
              type="error" 
              show-icon 
              class="mb-4"
              :closable="false"
            />
            
            <!-- Form actions -->
            <div class="form-actions">
              <el-button 
                v-if="currentStep > 0"
                size="large" 
                @click="currentStep--"
                class="action-btn"
              >
                <el-icon class="mr-1"><ArrowLeft /></el-icon>
                上一步
              </el-button>
              <div class="flex-1"></div>
              <el-button 
                v-if="currentStep < 2"
                type="primary"
                size="large" 
                @click="nextStep"
                class="action-btn next-btn"
              >
                下一步
                <el-icon class="ml-1"><ArrowRight /></el-icon>
              </el-button>
              <el-button
                v-else
                type="primary"
                size="large"
                :loading="forumStore.isLoading"
                @click="onSubmit"
                class="action-btn submit-btn"
              >
                <span v-if="!forumStore.isLoading">🚀 发布信息</span>
                <span v-else>发布中...</span>
              </el-button>
            </div>
          </el-form>
        </el-card>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useForumStore } from '@/stores/forum'
import { categoryAPI, postAPI } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import ImageUpload from '@/components/ImageUpload.vue'
import { InfoFilled, ArrowLeft, ArrowRight } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const forumStore = useForumStore()

const formRef = ref()
const categories = ref([])
const loadingCategories = ref(false)
const currentStep = ref(0)

const form = ref({
  title: '',
  content: '',
  item_type: 'lost',
  category_id: null,
  location: '',
  item_time: null,
  contact_info: '',
  images: []
})

const rules = {
  title: [
    { required: true, message: '请输入标题', trigger: 'blur' },
    { min: 5, max: 100, message: '标题长度应在 5 到 100 个字符之间', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入详细描述', trigger: 'blur' },
    { min: 10, max: 1000, message: '描述长度应在 10 到 1000 个字符之间', trigger: 'blur' }
  ],
  item_type: [{ required: true, message: '请选择物品类型', trigger: 'change' }],
  category_id: [{ required: true, message: '请选择物品分类', trigger: 'change' }],
  location: [
    { required: true, message: '请输入地点', trigger: 'blur' },
    { min: 2, max: 100, message: '地点长度应在 2 到 100 个字符之间', trigger: 'blur' }
  ],
  contact_info: [
    { required: true, message: '请输入联系方式', trigger: 'blur' },
    { min: 2, max: 100, message: '联系方式长度应在 2 到 100 个字符之间', trigger: 'blur' }
  ]
}

// 获取物品类型标签
const getItemTypeLabel = (type) => {
  const labels = {
    lost: '丢失物品',
    found: '拾到物品',
    general: '普通帖子'
  }
  return labels[type] || '未知类型'
}

// 获取物品类型颜色
const getItemTypeColor = (type) => {
  const colors = {
    lost: 'danger',
    found: 'success',
    general: 'info'
  }
  return colors[type] || ''
}

// 获取时间标签
const getTimeLabel = () => {
  if (form.value.item_type === 'lost') return '🕐 丢失时间'
  if (form.value.item_type === 'found') return '🕐 拾取时间'
  return '🕐 时间'
}

// 获取分类列表
const fetchCategories = async () => {
  loadingCategories.value = true
  try {
    const response = await categoryAPI.getAll()
    categories.value = response.data
  } catch (error) {
    console.error('Failed to fetch categories:', error)
    ElMessage.error('获取分类失败')
  } finally {
    loadingCategories.value = false
  }
}

// 自动填充当前时间
const setCurrentTime = () => {
  const now = new Date()
  form.value.item_time = now
}

// 下一步
const nextStep = async () => {
  // 验证当前步骤的字段
  const fieldsToValidate = [
    ['item_type', 'category_id', 'title', 'content'], // 步骤1
    ['location'], // 步骤2
    ['contact_info'] // 步骤3
  ][currentStep.value]
  
  let valid = true
  for (const field of fieldsToValidate) {
    try {
      await formRef.value?.validateField(field)
    } catch (error) {
      valid = false
      break
    }
  }
  
  if (valid) {
    currentStep.value++
  }
}

// 提交表单
const onSubmit = async () => {
  await formRef.value?.validate(async (valid) => {
    if (!valid) {
      ElMessage.warning('请完善表单信息')
      return
    }
    
    forumStore.clearError()
    
    try {
      // 准备数据
      const postData = {
        ...form.value,
        item_time: form.value.item_time ? new Date(form.value.item_time).toISOString() : null
      }
      
      const response = await postAPI.create(postData)
      
      ElMessage.success('发布成功！')
      // 添加延迟，让用户看到成功提示
      setTimeout(() => {
        router.push(`/forum/${response.data.id}`)
      }, 1000)
    } catch (error) {
      console.error('Create post error:', error)
      const errorMsg = error.response?.data?.detail || '发布失败，请重试'
      ElMessage.error(errorMsg)
      forumStore.setError(errorMsg)
    }
  })
}

// 确认退出登录
const handleLogout = () => {
  ElMessageBox.confirm(
    '确定要退出登录吗？',
    '确认退出',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    authStore.logout()
    router.push('/')
    ElMessage.success('已退出登录')
  }).catch(() => {
    // 取消退出
  })
}

onMounted(() => {
  fetchCategories()
  setCurrentTime()
  
  // 自动填充用户联系方式（如果有）
  if (authStore.user) {
    form.value.contact_info = authStore.user.phone || authStore.user.email || ''
  }
  
  // 根据URL查询参数设置物品类型
  if (route.query.type && ['lost', 'found', 'general'].includes(route.query.type)) {
    form.value.item_type = route.query.type
  }
})
</script>

<style scoped>
/* 浅色主题 */
.form-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-base);
}

.form-card :deep(.el-card__header) {
  background: var(--bg-muted);
  border-bottom: 1px solid var(--border-base);
}

.form-card :deep(.el-form-item__label) {
  color: var(--text-primary);
  font-weight: 600;
  font-size: 0.95rem;
}

.form-card :deep(.el-input__wrapper) {
  background-color: var(--input-bg-color);
  border-color: var(--input-border-color);
}

.form-card :deep(.el-input__inner) {
  color: var(--input-text-color);
}

.form-card :deep(.el-textarea__inner) {
  background-color: var(--input-bg-color);
  border-color: var(--input-border-color);
  color: var(--input-text-color);
}

.form-card :deep(.el-select .el-input__wrapper) {
  background-color: var(--input-bg-color);
  border-color: var(--input-border-color);
}

.form-card :deep(.el-radio-button__inner) {
  background-color: var(--input-bg-color);
  border-color: var(--input-border-color);
  color: var(--text-primary);
}

.form-card :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background-color: var(--primary);
  border-color: var(--primary);
  color: var(--text-inverse);
}

/* Enhanced Steps Component */
.steps-card {
  padding: var(--spacing-lg);
  margin-bottom: var(--spacing-xl) !important;
}

.enhanced-steps :deep(.el-step__icon) {
  width: 48px !important;
  height: 48px !important;
  font-size: 20px !important;
  border-width: 2px !important;
  transition: all 0.3s ease !important;
}

.enhanced-steps :deep(.el-step__icon.is-text) {
  transform: scale(1.2);
  border-width: 3px !important;
}

.enhanced-steps :deep(.el-step__title) {
  color: var(--text-primary) !important;
  font-weight: 600;
  font-size: 1rem;
}

.enhanced-steps :deep(.el-step__title.is-wait) {
  color: var(--text-secondary) !important;
}

.enhanced-steps :deep(.el-step__title.is-process) {
  color: var(--primary) !important;
  font-weight: 700;
}

.enhanced-steps :deep(.el-step__description) {
  color: var(--text-secondary) !important;
  font-size: 0.875rem;
}

.enhanced-steps :deep(.el-step__description.is-wait) {
  color: var(--text-muted) !important;
}

/* Form Grouping */
.form-group {
  background: var(--bg-muted);
  border: 1px solid var(--border-base);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
}

.group-title {
  color: var(--text-primary);
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: var(--spacing-md);
  padding-bottom: var(--spacing-sm);
  border-bottom: 2px solid var(--primary);
}

.step-title {
  color: var(--text-primary);
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: var(--spacing-lg);
  padding-bottom: var(--spacing-md);
  border-bottom: 2px solid var(--border-base);
}

.step-content {
  min-height: 400px;
  animation: fadeIn 0.3s ease-in;
  padding: var(--spacing-md) 0;
}

/* Form Actions */
.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: var(--spacing-xl);
  margin-top: var(--spacing-xl);
  border-top: 2px solid var(--border-base);
}

.action-btn {
  min-width: 120px;
  height: 48px;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.3s ease;
}

.next-btn,
.submit-btn {
  min-width: 150px;
}

.submit-btn {
  background: var(--success) !important;
  font-size: 1.1rem;
}

.submit-btn:hover {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 10px 20px rgba(16, 185, 129, 0.4) !important;
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

/* 按钮效果增强 */
:deep(.el-button--primary) {
  background: linear-gradient(135deg, var(--el-color-primary), var(--el-color-primary-light-3));
  border: none;
}

:deep(.el-button--primary:hover:not(:disabled)) {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(45, 140, 240, 0.4);
}

/* Steps 样式 */
:deep(.el-step__title) {
  color: var(--text-primary);
}

:deep(.el-step__description) {
  color: var(--text-secondary);
}

:deep(.el-step__head.is-finish) {
  color: var(--success);
  border-color: var(--success);
}

:deep(.el-step__head.is-process) {
  color: var(--primary);
  border-color: var(--primary);
}

/* 响应式设计调整 */
@media (max-width: 768px) {
  .el-header {
    padding: 0 16px;
  }
  
  .el-header .text-2xl {
    font-size: 1.5rem;
  }
  
  .el-card {
    border-radius: 8px;
    margin: 0 -16px;
  }
  
  .form-group {
    padding: var(--spacing-md);
  }
  
  .action-btn {
    min-width: 100px;
    height: 44px;
    font-size: 0.9rem;
  }
}
</style>

