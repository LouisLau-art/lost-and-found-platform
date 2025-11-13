<template>
  <el-drawer
    v-model="drawerVisible"
    title="Notifications"
    direction="rtl"
    size="400px"
  >
    <div v-if="userStore.notifications.length === 0" class="notification-empty">
      <el-empty description="No notifications" />
    </div>
    <div v-else>
      <el-button type="primary" size="small" class="mark-all-btn" @click="markAllAsRead">
        Mark All as Read
      </el-button>
      <div
        v-for="notification in userStore.notifications"
        :key="notification.id"
        class="notification-item"
        @click="openNotification(notification)"
      >
        <el-card :body-style="{ padding: '12px' }" shadow="hover" class="notification-card notification-link">
          <div class="notification-content">
            <el-icon v-if="!notification.is_read" class="unread-icon"><Bell /></el-icon>
            <div class="notification-text">
              <p class="notification-message">{{ notification.content }}</p>
              <p class="notification-time">{{ formatRelativeTime(notification.created_at) }}</p>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </el-drawer>
</template>

<script setup>
import { computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { formatRelative as formatRelativeTime } from '@/utils/time'
import { Bell } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const drawerVisible = computed({
  get: () => userStore.notificationsDrawerOpen,
  set: (val) => userStore.setNotificationsDrawer(val)
})

const notificationLink = (notification) => {
  if (!notification) return null

  if (notification.link) return notification.link

  const extra = notification.extra_data || {}
  if (extra.link) return extra.link

  if (notification.related_post_id) {
    const hash = notification.related_comment_id ? `#comment-${notification.related_comment_id}` : ''
    return `/forum/${notification.related_post_id}${hash}`
  }

  if (notification.related_claim_id) {
    const t = (notification.type || '').toLowerCase()
    if (t.includes('claim_created')) return { path: '/claims', query: { tab: 'received' } }
    if (t.includes('claim_approved') || t.includes('claim_rejected') || t.includes('claim_cancelled')) {
      return { path: '/claims', query: { tab: 'submitted' } }
    }
    return { path: '/claims' }
  }

  if (extra.new_post_id) return `/forum/${extra.new_post_id}`
  if (extra.matched_post_id) return `/forum/${extra.matched_post_id}`

  return null
}

const openNotification = async (notification) => {
  try {
    await userStore.markNotificationRead(notification.id)
  } catch (error) {
    console.warn('Failed to mark notification as read:', error)
  }

  const target = notificationLink(notification)
  if (!target) return

  userStore.setNotificationsDrawer(false)
  router.push(target).catch((err) => {
    if (!err || err.name === 'NavigationDuplicated' || err.message?.includes('Avoided redundant navigation')) {
      return
    }
    console.error('Failed to navigate to notification target:', err)
  })
}

const markAllAsRead = async () => {
  try {
    await userStore.markAllNotificationsRead()
    userStore.setNotificationsDrawer(false)
  } catch (error) {
    console.error('Failed to mark all notifications as read:', error)
  }
}

const maybeOpenDrawerFromRoute = () => {
  const flag = route.query.openNotifications
  if (flag === '1' || flag === 1 || flag === true) {
    userStore.setNotificationsDrawer(true)
    const { openNotifications, ...rest } = route.query
    router.replace({ path: route.path, query: { ...rest } }).catch(() => {})
  }
}

onMounted(async () => {
  try {
    await userStore.getNotifications()
    await userStore.getUnreadCount()
  } catch (error) {
    console.error('Failed to initialize notifications:', error)
  }

  maybeOpenDrawerFromRoute()
})

watch(() => route.query.openNotifications, () => {
  maybeOpenDrawerFromRoute()
})
</script>

<style scoped>
.notification-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}

.mark-all-btn {
  margin-bottom: 1rem;
}

.notification-item + .notification-item {
  margin-top: 0.75rem;
}

.notification-card {
  cursor: pointer;
  border: 1px solid var(--border-base);
  transition: transform 0.2s ease;
  background: var(--bg-surface);
}

.notification-card:hover {
  transform: translateX(-2px);
  border-color: var(--primary);
}

.notification-content {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
}

.unread-icon {
  color: var(--primary);
  font-size: 1.1rem;
  margin-top: 0.25rem;
}

.notification-text {
  flex: 1;
}

.notification-message {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.25rem 0;
}

.notification-time {
  font-size: 0.75rem;
  color: var(--text-tertiary);
  margin: 0;
}

:deep(.el-drawer__header) {
  margin: 0;
  padding: 16px 20px;
  background-color: var(--bg-surface);
  border-bottom: 1px solid var(--border-base);
  color: var(--text-primary);
}

:deep(.el-drawer__title) {
  font-weight: 600;
  font-size: 1rem;
  color: inherit;
}

:deep(.el-drawer__close-btn) {
  color: var(--text-secondary);
  transition: color 0.2s ease;
}

:deep(.el-drawer__close-btn:hover) {
  color: var(--brand-primary);
}
</style>
