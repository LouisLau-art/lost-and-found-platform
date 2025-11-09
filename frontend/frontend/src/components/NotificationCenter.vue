<template>
  <div class="relative">
    <button @click="toggleNotifications" class="relative p-2 text-gray-700 hover:text-gray-900">
      <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-5 5v-5zM4 19h6v-6H4v6zM4 5h6V1H4v4zM15 1v4h6V1h-6z" />
      </svg>
      <span v-if="userStore.unreadCount > 0" class="absolute -top-1 -right-1 h-4 w-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
        {{ userStore.unreadCount }}
      </span>
    </button>
    
    <!-- Notifications dropdown -->
    <div v-if="isOpen" class="absolute right-0 mt-2 w-80 bg-white rounded-md shadow-lg z-50">
      <div class="p-4">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-medium text-gray-900">通知</h3>
          <button 
            v-if="userStore.notifications.length > 0" 
            @click="markAllAsRead" 
            class="text-xs text-blue-600 hover:text-blue-800"
          >
            全部标记为已读
          </button>
        </div>
        <div v-if="userStore.notifications.length === 0" class="text-gray-500 text-sm mt-2">
          暂无通知
        </div>
        <div v-else class="mt-2 space-y-2 max-h-64 overflow-y-auto">
          <div
            v-for="notification in userStore.notifications"
            :key="notification.id"
            :class="[
              'p-3 rounded-md cursor-pointer transition-colors duration-200',
              notification.is_read ? 'bg-gray-50' : 'bg-blue-50'
            ]"
            @click="handleNotificationClick(notification)"
          >
            <p class="text-sm text-gray-900">{{ notification.content }}</p>
            <p class="text-xs text-gray-500 mt-1">{{ formatDate(notification.created_at) }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const isOpen = ref(false)

// 关闭通知下拉菜单的点击外部事件处理
const handleClickOutside = (event) => {
  const notificationCenter = event.target.closest('.notification-center')
  if (!notificationCenter && isOpen.value) {
    isOpen.value = false
  }
}

const toggleNotifications = () => {
  isOpen.value = !isOpen.value
  
  // 如果打开通知，则刷新通知列表
  if (isOpen.value) {
    refreshNotifications()
  }
}

const refreshNotifications = async () => {
  try {
    await userStore.getNotifications()
    await userStore.getUnreadCount()
  } catch (error) {
    console.error('Failed to refresh notifications:', error)
  }
}

import { useRouter } from 'vue-router'

const router = useRouter()

const handleNotificationClick = async (notification) => {
  if (!notification.is_read) {
    await userStore.markNotificationRead(notification.id)
  }
  
  // 如果通知有关联链接，导航到相关页面
  if (notification.link) {
    router.push(notification.link)
  }
} {
    // 可以使用router导航到相关页面
    // router.push(notification.link)
  }
}

const markAllAsRead = async () => {
  try {
    // 获取所有未读通知
    const unreadNotifications = userStore.notifications.filter(n => !n.is_read)
    
    // 逐个标记为已读
    for (const notification of unreadNotifications) {
      await userStore.markNotificationRead(notification.id)
    }
  } catch (error) {
    console.error('Failed to mark all notifications as read:', error)
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString()
}

import { ref, onMounted, onUnmounted, watch } from 'vue'

// 新增WebSocket连接逻辑
const ws = ref(null)

const connectWebSocket = () => {
  ws.value = new WebSocket('ws://localhost:8000/ws/notifications')
  ws.value.onmessage = (event) => {
    const data = JSON.parse(event.data)
    if (data.type === 'new_notification') {
      userStore.notifications.unshift(data.payload)
      userStore.unreadCount++
    }
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  refreshNotifications()
  connectWebSocket()
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  if (ws.value) ws.value.close()
})


onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.notification-center {
  position: relative;
}

/* 移动端响应式样式 */
@media (max-width: 768px) {
  .absolute.right-0.mt-2.w-80 {
    width: 90vw;
    right: 5vw;
  }
  
  button.relative.p-2.text-gray-700.hover\:text-gray-900 {
    padding: 1rem;
  }
  
  .h-6.w-6 {
    height: 1.5rem;
    width: 1.5rem;
  }
}
</style>