import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
// 全部使用路由懒加载
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // Redirect root to forum
    {
      path: '/',
      redirect: '/forum'
    },
    {
      path: '/home',
      name: 'home',
      component: () => import('../views/HomeView.vue')
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue')
    },
    // Auth routes
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/auth/LoginView.vue'),
      meta: { requiresGuest: true }
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/auth/RegisterView.vue'),
      meta: { requiresGuest: true }
    },
    // User routes
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('../views/user/DashboardView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/user/ProfileView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/user/activity',
      name: 'user-activity',
      component: () => import('../views/user/ActivityView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/claims',
      name: 'claims',
      component: () => import('../views/user/ClaimsView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/users/:id',
      name: 'user-profile',
      component: () => import('../views/user/UserProfileView.vue')
    },
    // Forum routes
    {      
      path: '/forum',
      name: 'forum',
      component: () => import('../views/forum/ForumListView.vue')
    },
    {
      path: '/forum/create',
      name: 'create-post',
      component: () => import('../views/forum/CreatePostView.vue')
    },
    {
      path: '/forum/:id',
      name: 'post-detail',
      component: () => import('../views/forum/PostDetailView.vue')
    },
    {
      path: '/forum/:id/edit',
      name: 'edit-post',
      component: () => import('../views/forum/CreatePostView.vue')
    },
    // Admin routes
    {
      path: '/admin/users',
      name: 'user-management',
      component: () => import('../views/admin/UserManagementView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/admin/posts',
      name: 'admin-posts',
      component: () => import('../views/admin/AdminPostsView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    // Test route
    {
      path: '/test',
      name: 'test',
      component: () => import('../views/TestView.vue')
    },
    // Redirect all other routes to test view for troubleshooting
    {
      path: '/:pathMatch(.*)*',
      redirect: '/test'
    },
    // Legacy routes for backward compatibility
    {
      path: '/posts',
      redirect: '/forum'
    },
    {
      path: '/posts/new',
      redirect: '/forum/create'
    }
  ]
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Initialize auth state if not already done
  if (!authStore.user && localStorage.getItem('access_token')) {
    try {
      await authStore.getCurrentUser()
    } catch (error) {
      // If token is invalid, it will be cleared by getCurrentUser
      console.error('Failed to get current user:', error)
    }
  }
  
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiresGuest = to.matched.some(record => record.meta.requiresGuest)
  const requiresAdmin = to.matched.some(record => record.meta.requiresAdmin)
  
  // 检查是否需要认证
  if (requiresAuth && !authStore.isAuthenticated) {
    next('/login')
    return
  }
  
  // 检查是否需要管理员权限
  if (requiresAdmin) {
    console.log('Checking admin access:', {
      isAuthenticated: authStore.isAuthenticated,
      user: authStore.user,
      is_admin: authStore.user?.is_admin
    })
    
    if (!authStore.user?.is_admin) {
      // 如果已登录但不是管理员,返回dashboard
      if (authStore.isAuthenticated) {
        console.warn('User is not admin, redirecting to dashboard')
        next('/dashboard')
      } else {
        next('/login')
      }
      return
    }
  }
  
  // 已登录用户不能访问guest页面
  if (requiresGuest && authStore.isAuthenticated) {
    next('/dashboard')
    return
  }
  
  next()
})

export default router
