<template>
  <div class="relative notification-center">
    <button @click="toggleNotifications" class="relative p-2 text-fg-secondary hover-text-primary">
      <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-5 5v-5zM4 19h6v-6H4v6zM4 5h6V1H4v4zM15 1v4h6V1h-6z" />
      </svg>
      <span v-if="userStore.unreadCount > 0" class="absolute -top-1 -right-1 h-4 w-4 text-xs rounded-full flex items-center justify-center" :style="{ backgroundColor: 'var(--danger)', color: 'var(--text-inverse, #fff)' }">
        {{ userStore.unreadCount }}
      </span>
    </button>
    
    <!-- Notifications dropdown -->
    <div v-if="isOpen" class="absolute right-0 mt-2 w-80 rounded-md shadow-lg z-50" :style="{ background: 'var(--bg-card)', border: '1px solid var(--border-base)' }">
      <div class="p-4">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-medium text-fg-primary">通知</h3>
          <button 
            v-if="userStore.notifications.length > 0" 
            @click="markAllAsRead" 
            class="text-xs text-primary hover-text-primary"
          >
            全部标记为已读
          </button>
        </div>
        <div v-if="userStore.notifications.length === 0" class="text-fg-secondary text-sm mt-2">
          暂无通知
        </div>
        <div v-else class="mt-2 space-y-2 max-h-64 overflow-y-auto">
          <div
            v-for="notification in userStore.notifications"
            :key="notification.id"
            :class="[
              'p-3 rounded-md cursor-pointer transition-colors duration-200',
              notification.is_read ? 'bg-surface' : 'bg-muted'
            ]"
            @click="handleNotificationClick(notification)"
          >
            <p class="text-sm text-fg-primary">{{ notification.content }}</p>
            <p class="text-xs text-fg-secondary mt-1">{{ formatDate(notification.created_at) }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const isOpen = ref(false)
const router = useRouter()

// 关闭通知下拉菜单的点击外部事件处理
const handleClickOutside = (event) => {
  const notificationCenter = event.target.closest('.notification-center')
  if (!notificationCenter && isOpen.value) {
    isOpen.value = false
  }
}

const toggleNotifications = () => {
  isOpen.value = !isOpen.value
  if (isOpen.value) refreshNotifications()
}

const refreshNotifications = async () => {
  try {
    await userStore.getNotifications()
    await userStore.getUnreadCount()
  } catch (error) {
    console.error('Failed to refresh notifications:', error)
  }
}

const handleNotificationClick = async (notification) => {
  if (!notification.is_read) {
    await userStore.markNotificationRead(notification.id)
  }
  if (notification.link) {
    router.push(notification.link)
  }
}

const markAllAsRead = async () => {
  try {
    const unreadNotifications = userStore.notifications.filter(n => !n.is_read)
    for (const n of unreadNotifications) {
      await userStore.markNotificationRead(n.id)
    }
  } catch (error) {
    console.error('Failed to mark all notifications as read:', error)
  }
}

const formatDate = (dateString) => new Date(dateString).toLocaleDateString()

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  refreshNotifications()
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
  
  .h-6.w-6 {
    height: 1.5rem;
    width: 1.5rem;
  }
  
  .bg-card {
    background-color: var(--bg-card-dark);
  }
  
  .border-base {
    border-color: var(--border-base-dark);
  }
  
  .text-fg-primary {
    color: var(--text-fg-primary-dark);
  }
  
  .text-fg-secondary {
    color: var(--text-fg-secondary-dark);
  }
  
  .bg-surface {
    background-color: var(--bg-surface-dark);
  }
  
  .bg-muted {
    background-color: var(--bg-muted-dark);
  }
  
  .text-primary {
    color: var(--text-primary-dark);
  }
  
  .hover-text-primary {
    color: var(--hover-text-primary-dark);
  }
}
</style>