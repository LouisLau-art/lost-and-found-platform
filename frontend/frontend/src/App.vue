<template>
  <div id="app" class="app-container">
    <TheNavbar v-if="authStore.isAuthenticated" />
    <!-- Transition wrapper for page transitions -->
    <main class="app-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- Notification utilities for authenticated users -->
    <NotificationManager v-if="authStore.isAuthenticated" />
    <NotificationDrawer v-if="authStore.isAuthenticated" />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import TheNavbar from '@/components/TheNavbar.vue'
import NotificationManager from '@/components/NotificationManager.vue'
import NotificationDrawer from '@/components/NotificationDrawer.vue'

const authStore = useAuthStore()

onMounted(() => {
  // Initialize auth state from localStorage
  authStore.initAuth()
})
</script>

<style>
/* Base App component styles */
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: var(--bg-base);
}

.app-content {
  flex: 1;
  display: flex;
  flex-direction: column;
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

/* Global dark theme for Element Plus dropdowns and date pickers */
.el-select__popper {
  background-color: var(--bg-surface) !important;
  border: 1px solid var(--border-base) !important;
  color: var(--text-primary) !important;
}

.el-select-dropdown__item {
  color: var(--text-primary) !important;
  background-color: var(--bg-surface) !important;
}

.el-select-dropdown__item:hover {
  background-color: var(--bg-muted) !important;
}

.el-select-dropdown__item.selected {
  color: var(--brand-primary) !important;
  font-weight: 600 !important;
}

.el-picker-panel {
  background-color: var(--bg-surface) !important;
  border: 1px solid var(--border-base) !important;
  color: var(--text-primary) !important;
}

.el-picker-panel__icon-btn,
.el-date-picker__header-label,
.el-date-table th,
.el-date-table td.available {
  color: var(--text-primary) !important;
}

.el-date-table td.current:not(.disabled) span {
  background-color: var(--brand-primary) !important;
  color: white !important;
}

.el-date-table td.today span {
  color: var(--brand-primary) !important;
  font-weight: 600 !important;
}

/* Dark overlay and dialog styling */
.el-overlay {
  background-color: rgba(0, 0, 0, 0.7) !important;
}

.el-dialog {
  background-color: var(--bg-surface) !important;
  border: 1px solid var(--border-base) !important;
  color: var(--text-primary);
}
</style>