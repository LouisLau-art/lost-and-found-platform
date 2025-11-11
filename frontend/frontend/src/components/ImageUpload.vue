<template>
  <div class="image-upload-container">
    <div class="upload-area">
      <input
        ref="fileInput"
        type="file"
        multiple
        accept="image/jpeg,image/jpg,image/png,image/gif,image/webp"
        @change="handleFileSelect"
        class="hidden"
      />
      
      <!-- 图片预览区域 -->
      <div v-if="imageList.length > 0" class="image-preview-grid">
        <div
          v-for="(img, index) in imageList"
          :key="index"
          class="image-preview-item"
        >
          <img :src="getImageUrl(img)" :alt="`Image ${index + 1}`" />
          <div class="image-overlay">
            <button @click="removeImage(index)" class="delete-btn">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        
        <!-- 添加更多按钮 -->
        <div
          v-if="imageList.length < maxImages"
          @click="triggerFileInput"
          class="add-more-btn"
        >
          <svg class="w-8 h-8 icon-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          <span class="text-sm text-fg-secondary">添加图片</span>
        </div>
      </div>
      
      <!-- 上传按钮 -->
      <div
        v-else
        @click="triggerFileInput"
        class="upload-placeholder"
      >
        <svg class="w-12 h-12 icon-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <p class="mt-2 text-sm text-fg-secondary">点击上传图片</p>
        <p class="mt-1 text-xs text-fg-muted">支持 JPG、PNG、GIF，最多 {{ maxImages }} 张，每张不超过 5MB</p>
      </div>
      
      <!-- 上传进度提示 -->
      <div v-if="uploading" class="upload-progress">
        <div class="spinner"></div>
        <span class="ml-2 text-sm text-fg-secondary">上传中...</span>
      </div>
    </div>
    
    <!-- 提示信息 -->
    <p v-if="imageList.length > 0" class="mt-2 text-xs text-fg-muted">
      已上传 {{ imageList.length }} / {{ maxImages }} 张图片
    </p>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { uploadAPI } from '@/api'
import message from '@/utils/message'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  maxImages: {
    type: Number,
    default: 9
  }
})

const emit = defineEmits(['update:modelValue'])

const fileInput = ref(null)
const imageList = ref([...props.modelValue])
const uploading = ref(false)

// 监听外部值变化
watch(() => props.modelValue, (newVal) => {
  imageList.value = [...newVal]
})

// 触发文件选择
const triggerFileInput = () => {
  fileInput.value?.click()
}

// 获取图片完整 URL
const getImageUrl = (url) => {
  if (url.startsWith('http')) {
    return url
  }
  return `http://localhost:8000${url}`
}

// 处理文件选择
const handleFileSelect = async (event) => {
  const files = Array.from(event.target.files)
  
  if (files.length === 0) return
  
  // 检查数量限制
  if (imageList.value.length + files.length > props.maxImages) {
    message.warning(`最多只能上传 ${props.maxImages} 张图片`)
    return
  }
  
  // 检查文件大小
  const maxSize = 5 * 1024 * 1024 // 5MB
  const oversizedFiles = files.filter(file => file.size > maxSize)
  if (oversizedFiles.length > 0) {
    message.error('部分图片超过 5MB 限制')
    return
  }
  
  // 上传图片
  uploading.value = true
  try {
    const response = await uploadAPI.uploadMultiple(files)
    const uploadedUrls = response.data.files.map(file => file.url)
    
    imageList.value = [...imageList.value, ...uploadedUrls]
    emit('update:modelValue', imageList.value)
    
    message.success(`成功上传 ${files.length} 张图片`)
  } catch (error) {
    console.error('Upload error:', error)
    message.error(error.response?.data?.detail || '上传失败，请重试')
  } finally {
    uploading.value = false
    // 清空 input，允许重复选择同一文件
    event.target.value = ''
  }
}

// 删除图片
const removeImage = (index) => {
  imageList.value.splice(index, 1)
  emit('update:modelValue', imageList.value)
}
</script>

<style scoped>
.image-upload-container {
  width: 100%;
}

.upload-area {
  position: relative;
}

.hidden {
  display: none;
}

.image-preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 12px;
}

.image-preview-item {
  position: relative;
  width: 100%;
  padding-bottom: 100%;
  border-radius: 8px;
  overflow: hidden;
  border: 2px solid var(--border-base);
  cursor: pointer;
  transition: all 0.2s;
}

.image-preview-item:hover {
  border-color: var(--brand-primary);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.4);
}

.image-preview-item img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
}

.image-preview-item:hover .image-overlay {
  opacity: 1;
}

.delete-btn {
  background: var(--danger);
  color: var(--text-inverse, #fff);
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.delete-btn:hover {
  background: var(--danger);
  transform: scale(1.1);
}

.add-more-btn {
  position: relative;
  width: 100%;
  padding-bottom: 100%;
  border: 2px dashed var(--border-base);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  background: var(--bg-muted);
}

.add-more-btn:hover {
  border-color: var(--brand-primary);
  background: var(--bg-surface);
}

.add-more-btn > * {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.add-more-btn span {
  top: 65%;
}

.upload-placeholder {
  width: 180px;
  height: 180px;
  border: 2px dashed var(--border-base);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background: var(--bg-muted);
}

.upload-placeholder:hover {
  border-color: var(--brand-primary);
  background: var(--bg-surface);
}

.upload-progress {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(17, 24, 39, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
}

.spinner {
  border: 3px solid var(--border-base);
  border-top: 3px solid var(--brand-primary);
  border-radius: 50%;
  width: 24px;
  height: 24px;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
