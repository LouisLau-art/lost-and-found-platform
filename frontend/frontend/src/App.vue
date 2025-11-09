<template>
  <n-message-provider>
    <n-notification-provider>
      <div id="app">
        <!-- Transition wrapper for page transitions -->
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
        
        <!-- Notification manager for authenticated users -->
        <NotificationManager v-if="authStore.isAuthenticated" />
      </div>
    </n-notification-provider>
  </n-message-provider>
</template>

<script setup>
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { NMessageProvider, NNotificationProvider } from 'naive-ui'
import { useAuthStore } from '@/stores/auth'
import NotificationManager from '@/components/NotificationManager.vue'

const authStore = useAuthStore()

onMounted(() => {
  // Initialize auth state from localStorage
  authStore.initAuth()
})
</script>

<style>
/* Base App component styles */
#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: var(--el-bg-color-page);
}

/* Page transition animations */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>