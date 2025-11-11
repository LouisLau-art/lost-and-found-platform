<template>
  <header class="the-navbar">
    <div class="nav-inner">
      <router-link to="/" class="brand">
        <span class="brand-icon">🧭</span>
        <span class="brand-text">Lost & Found</span>
      </router-link>

      <nav class="links">
        <router-link to="/forum" class="link" active-class="active">论坛</router-link>
        <router-link to="/dashboard" class="link" active-class="active">仪表盘</router-link>
        <router-link to="/claims" class="link" active-class="active">我的认领</router-link>
        <router-link v-if="authStore.user?.is_admin" to="/admin/users" class="link" active-class="active">管理后台</router-link>
      </nav>

      <div class="actions">
        <router-link :to="{ path: '/dashboard', query: { notifications: '1' } }" class="icon-btn" title="通知">
          <el-icon><Bell /></el-icon>
        </router-link>
        <el-dropdown trigger="click">
          <span class="avatar-btn">
            <el-avatar :size="28">{{ initials }}</el-avatar>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="$router.push('/profile')">个人资料</el-dropdown-item>
              <el-dropdown-item @click="$router.push('/claims')">我的认领</el-dropdown-item>
              <el-dropdown-item divided @click="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Bell } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

const initials = computed(() => {
  if (!authStore.user?.name) return 'U'
  return authStore.user.name.split(' ').map(s => s[0]).join('').toUpperCase()
})

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.the-navbar {
  position: sticky;
  top: 0;
  z-index: 50;
  background: var(--bg-surface);
  border-bottom: 1px solid var(--border-base);
  backdrop-filter: blur(8px);
}
.nav-inner {
  max-width: 1280px;
  margin: 0 auto;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
}
.brand {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  color: var(--text-primary);
  font-weight: 700;
}
.brand-icon { font-size: 18px; }
.links { display: flex; gap: 12px; }
.link {
  color: var(--text-secondary);
  text-decoration: none;
  padding: 6px 10px;
  border-radius: 8px;
}
.link:hover { background: var(--bg-muted); color: var(--text-primary); }
.active { color: var(--brand-primary) !important; background: var(--bg-muted); }
.actions { display: flex; align-items: center; gap: 10px; }
.icon-btn { color: var(--text-secondary); text-decoration: none; }
.icon-btn:hover { color: var(--brand-primary); }
.avatar-btn { cursor: pointer; display: inline-flex; align-items: center; }
</style>
