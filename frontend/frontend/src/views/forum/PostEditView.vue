<template>
  <div class="min-h-screen bg-gray-50">
    <el-header class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <router-link to="/" class="text-xl font-bold text-gray-900">Lost & Found Platform</router-link>
        <div class="space-x-2">
          <el-button text @click="goBack">← 返回详情</el-button>
          <el-button text @click="$router.push('/dashboard')">Dashboard</el-button>
        </div>
      </div>
    </el-header>

    <!-- Main content -->
    <div class="max-w-4xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-6 sm:px-0">
        <el-card>
          <template #header>
            <div class="flex items-center justify-between">
              <span class="text-lg font-semibold">✏️ 编辑信息</span>
              <el-tag :type="getItemTypeColor(form.item_type)" size="large">
                {{ getItemTypeLabel(form.item_type) }}
              </el-tag>
            </div>
          </template>
          
          <el-form :model="form" :rules="rules" ref="formRef" label-position="top" size="large">
            <!-- 物品类型 -->
            <el-form-item label="📌 物品类型" prop="item_type">
              <el-radio-group v-model="form.item_type" size="large" class="w-full">
                <el-radio-button value="lost" class="flex-1">
                  <span class="flex items-center justify-center">
                    🔴 丢失物品
                  </span>
                </el-radio-button>
                <el-radio-button value="found" class="flex-1">
                  <span class="flex items-center justify-center">
                    🟢 拾到物品
                  </span>
                </el-radio-button>
                <el-radio-button value="general" class="flex-1">
                  <span class="flex items-center justify-center">
                    ⚪ 普通帖子
                  </span>
                </el-radio-button>
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
                      <span class="text-xs text-gray-400 ml-2">{{ cat.description }}</span>
                    </el-option>
                  </el-select>
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

            <!-- 标题 -->
            <el-form-item label="📄 标题" prop="title">
              <el-input
                v-model="form.title"
                placeholder="请输入标题，简洁明了地描述物品"
                maxlength="100"
                show-word-limit
              />
            </el-form-item>
            
            <!-- 地点 -->
            <el-form-item label="📍 地点" prop="location">
              <el-input
                v-model="form.location"
                placeholder="请输入具体地点，如：图书馆三楼、东门食堂等"
                maxlength="100"
              >
                <template #prefix>
                  <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  </svg>
                </template>
              </el-input>
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
              />
            </el-form-item>
            
            <!-- 联系方式 -->
            <el-form-item label="📞 联系方式" prop="contact_info">
              <el-input
                v-model="form.contact_info"
                placeholder="请输入联系方式，如：手机号、微信号等"
                maxlength="100"
              >
                <template #prefix>
                  <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                </template>
              </el-input>
            </el-form-item>
            
            <!-- 图片上传 -->
            <el-form-item label="📷 物品图片">
              <ImageUpload v-model="form.images" :max-images="9" />
              <p class="text-xs text-gray-500 mt-2">提示：上传清晰的物品照片有助于快速找回</p>
            </el-form-item>
            
            <el-alert v-if="error" :title="error" type="error" show-icon class="mb-4" />
            
            <div class="flex justify-end space-x-2 pt-4">
              <el-button size="large" @click="goBack">取消</el-button>
              <el-button
                type="primary"
                size="large"
                :loading="isLoading"
                @click="onSubmit"
              >
                <span v-if="!isLoading">保存修改</span>
                <span v-else>保存中...</span>
              </el-button>
            </div>
          </el-form>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { categoryAPI, postAPI } from '@/api'
import { ElMessage } from 'element-plus'
import ImageUpload from '@/components/ImageUpload.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const formRef = ref()
const categories = ref([])
const loadingCategories = ref(false)
const isLoading = ref(false)
const error = ref('')

const postId = computed(() => parseInt(route.params.id))

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
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入详细描述', trigger: 'blur' }],
  item_type: [{ required: true, message: '请选择物品类型', trigger: 'change' }]
}

// 获取物品类型标签
const getItemTypeLabel = (type) => {
  switch(type) {
    case 'lost': return '丢失物品'
    case 'found': return '拾到物品'
    case 'general': return '普通帖子'
    default: return '未知类型'
  }
}

// 获取物品类型颜色
const getItemTypeColor = (type) => {
  switch(type) {
    case 'lost': return 'danger'
    case 'found': return 'success'
    case 'general': return 'info'
    default: return 'default'
  }
}

// 获取时间标签
const getTimeLabel = () => {
  switch(form.value.item_type) {
    case 'lost': return '🕐 丢失时间'
    case 'found': return '🕐 拾取时间'
    default: return '🕐 发生时间'
  }
}

// 加载分类数据
const loadCategories = async () => {
  loadingCategories.value = true
  try {
    const response = await categoryAPI.getAll()
    categories.value = response.data
  } catch (err) {
    ElMessage.error('加载分类失败')
  } finally {
    loadingCategories.value = false
  }
}

// 加载帖子数据
const loadPostData = async () => {
  isLoading.value = true
  error.value = ''
  try {
    const response = await postAPI.get(postId.value)
    const post = response.data
    
    // 检查权限
    if (post.author.id !== authStore.user.id) {
      error.value = '您没有权限编辑此帖子'
      return
    }
    
    // 填充表单数据
    form.value = {
      title: post.title,
      content: post.content,
      item_type: post.item_type,
      category_id: post.category?.id || null,
      location: post.location || '',
      item_time: post.item_time ? new Date(post.item_time) : null,
      contact_info: post.contact_info || '',
      images: post.images || []
    }
  } catch (err) {
    error.value = err.response?.data?.detail || '加载帖子失败'
  } finally {
    isLoading.value = false
  }
}

// 提交表单
const onSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    isLoading.value = true
    error.value = ''
    
    // 转换日期格式
    const submitData = { ...form.value }
    if (submitData.item_time) {
      submitData.item_time = new Date(submitData.item_time).toISOString()
    }
    
    await postAPI.update(postId.value, submitData)
    ElMessage.success('帖子更新成功')
    router.push(`/forum/${postId.value}`)
  } catch (err) {
    error.value = err.response?.data?.detail || '更新失败，请重试'
  } finally {
    isLoading.value = false
  }
}

// 返回详情页
const goBack = () => {
  router.push(`/forum/${postId.value}`)
}

// 初始化
onMounted(() => {
  loadCategories()
  loadPostData()
})
</script>