<template>
  <div class="image-gallery">
    <!-- 缩略图网格 -->
    <div v-if="images && images.length > 0" class="thumbnail-grid">
      <div
        v-for="(img, index) in images"
        :key="index"
        class="thumbnail-item"
        @click="openGallery(index)"
      >
        <img :src="getImageUrl(img)" :alt="`Image ${index + 1}`" />
        <div class="overlay">
          <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
          </svg>
        </div>
      </div>
    </div>

    <!-- 全屏画廊弹窗 -->
    <el-dialog
      v-model="showGallery"
      :fullscreen="true"
      :show-close="false"
      class="image-gallery-dialog"
    >
      <div class="gallery-container">
        <!-- 关闭按钮 -->
        <button class="close-btn" @click="closeGallery">
          <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        <!-- 左箭头 -->
        <button
          v-if="images.length > 1"
          class="nav-btn nav-btn-left"
          @click="prevImage"
        >
          <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </button>

        <!-- 当前图片 -->
        <div class="image-viewer">
          <img
            :src="getImageUrl(images[currentIndex])"
            :alt="`Image ${currentIndex + 1}`"
            class="current-image"
          />
          <div class="image-counter">
            {{ currentIndex + 1 }} / {{ images.length }}
          </div>
        </div>

        <!-- 右箭头 -->
        <button
          v-if="images.length > 1"
          class="nav-btn nav-btn-right"
          @click="nextImage"
        >
          <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>

        <!-- 缩略图导航栏 -->
        <div v-if="images.length > 1" class="thumbnail-nav">
          <div
            v-for="(img, index) in images"
            :key="index"
            class="thumbnail-nav-item"
            :class="{ active: index === currentIndex }"
            @click="currentIndex = index"
          >
            <img :src="getImageUrl(img)" :alt="`Thumb ${index + 1}`" />
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  images: {
    type: Array,
    default: () => []
  }
})

const showGallery = ref(false)
const currentIndex = ref(0)

const getImageUrl = (url) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return `http://localhost:8000${url}`
}

const openGallery = (index) => {
  currentIndex.value = index
  showGallery.value = true
}

const closeGallery = () => {
  showGallery.value = false
}

const nextImage = () => {
  currentIndex.value = (currentIndex.value + 1) % props.images.length
}

const prevImage = () => {
  currentIndex.value = (currentIndex.value - 1 + props.images.length) % props.images.length
}

// 键盘导航
const handleKeydown = (e) => {
  if (!showGallery.value) return
  if (e.key === 'ArrowRight') nextImage()
  if (e.key === 'ArrowLeft') prevImage()
  if (e.key === 'Escape') closeGallery()
}

if (typeof window !== 'undefined') {
  window.addEventListener('keydown', handleKeydown)
}
</script>

<style scoped>
.thumbnail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 12px;
  margin-top: 16px;
}

.thumbnail-item {
  position: relative;
  width: 100%;
  padding-bottom: 100%;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
}

.thumbnail-item:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.thumbnail-item img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.thumbnail-item:hover .overlay {
  opacity: 1;
}

.overlay .icon {
  width: 32px;
  height: 32px;
  color: white;
}

/* 画廊弹窗样式 */
.gallery-container {
  position: relative;
  width: 100%;
  height: 100vh;
  background: rgba(0, 0, 0, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 1000;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 50%;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: white;
  transition: all 0.3s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.1);
}

.nav-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 50%;
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: white;
  transition: all 0.3s;
  z-index: 100;
}

.nav-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-50%) scale(1.1);
}

.nav-btn-left {
  left: 40px;
}

.nav-btn-right {
  right: 40px;
}

.image-viewer {
  position: relative;
  max-width: 90%;
  max-height: 85vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.current-image {
  max-width: 100%;
  max-height: 85vh;
  object-fit: contain;
  border-radius: 4px;
}

.image-counter {
  position: absolute;
  bottom: -40px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
}

.thumbnail-nav {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 8px;
  padding: 12px;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 8px;
  max-width: 80%;
  overflow-x: auto;
}

.thumbnail-nav-item {
  width: 60px;
  height: 60px;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.3s;
  flex-shrink: 0;
}

.thumbnail-nav-item:hover {
  border-color: rgba(255, 255, 255, 0.5);
}

.thumbnail-nav-item.active {
  border-color: white;
  box-shadow: 0 0 12px rgba(255, 255, 255, 0.5);
}

.thumbnail-nav-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 覆盖 Element Plus Dialog 样式 */
:deep(.el-dialog__body) {
  padding: 0 !important;
}

:deep(.el-dialog) {
  background: transparent !important;
}
</style>
