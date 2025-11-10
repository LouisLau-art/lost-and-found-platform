<template>
  <div class="admin-layout">
    <aside class="admin-sidebar">
      <div class="sidebar-header">Admin</div>
      <nav class="sidebar-nav">
        <router-link to="/admin/users" class="nav-link" active-class="active">用户管理</router-link>
        <router-link to="/admin/posts" class="nav-link" active-class="active">帖子管理</router-link>
      </nav>
    </aside>
    <main class="admin-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 240px 1fr;
  background: var(--bg-base);
  color: var(--text-primary);
}
.admin-sidebar {
  background: var(--bg-surface);
  border-right: 1px solid var(--border-base);
  padding: 1rem;
}
.sidebar-header {
  font-weight: 800;
  font-size: 1.25rem;
  margin-bottom: 1rem;
}
.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.nav-link {
  color: var(--text-secondary);
  text-decoration: none;
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
}
.nav-link:hover {
  background: var(--bg-muted);
  color: var(--text-primary);
}
.active {
  background: var(--bg-muted);
  color: var(--brand-primary) !important;
  font-weight: 600;
}
.admin-content {
  padding: 1.5rem;
}
</style>
