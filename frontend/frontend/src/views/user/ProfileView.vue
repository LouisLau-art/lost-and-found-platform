<template>
  <div class="min-h-screen" style="background-color: #f9fafb;">
    <!-- Navigation -->
    <nav class="bg-white/95 backdrop-blur-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <router-link to="/" class="text-xl font-bold text-gray-800 hover:text-indigo-600 transition-all">
              Lost & Found Platform
            </router-link>
          </div>
          <div class="flex items-center space-x-4">
            <router-link to="/forum" class="text-gray-600 hover:text-gray-800 transition-all">
              Forum
            </router-link>
            <router-link to="/dashboard" class="text-gray-600 hover:text-gray-800 transition-all">
              Dashboard
            </router-link>
            <el-button text class="text-gray-600 hover:text-gray-800" @click="handleLogout">
              Sign out
            </el-button>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main content -->
    <div class="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <el-card shadow="hover" class="profile-card">
        <template #header>
          <h1 class="text-2xl font-bold text-gray-800">Profile Settings</h1>
        </template>
        
        <!-- Editable Profile Form -->
        <el-form 
          :model="form" 
          :rules="rules"
          ref="formRef"
          label-position="top"
          size="large"
          @submit.prevent="handleUpdateProfile"
        >
          <el-form-item label="Full Name" prop="name">
            <el-input
              v-model="form.name"
              placeholder="Enter your full name"
              :prefix-icon="User"
            />
          </el-form-item>

          <el-form-item label="Email Address" prop="email">
            <el-input
              v-model="form.email"
              type="email"
              placeholder="Enter your email"
              :prefix-icon="Message"
            />
          </el-form-item>

          <el-form-item label="New Password" prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="Leave blank to keep current password"
              :prefix-icon="Lock"
              show-password
            />
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="userStore.isLoading"
              @click="handleUpdateProfile"
              class="w-full"
            >
              <span v-if="userStore.isLoading">Updating...</span>
              <span v-else>Update Profile</span>
            </el-button>
          </el-form-item>
        </el-form>

        <el-divider />

        <!-- Account Information (Read-only) -->
        <div class="mt-6">
          <h2 class="text-lg font-semibold text-gray-800 mb-4">Account Information</h2>
          <el-descriptions :column="2" border class="account-info">
            <el-descriptions-item label="Credit Score">
              <el-tag type="success" size="large">
                {{ authStore.user?.credit_score || 100 }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="Member Since">
              {{ formatDate(authStore.user?.created_at) }}
            </el-descriptions-item>
            <el-descriptions-item label="Account Status">
              <el-tag :type="authStore.user?.is_active ? 'success' : 'danger'">
                {{ authStore.user?.is_active ? 'Active' : 'Inactive' }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUserStore } from '@/stores/user'
import { User, Message, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()
const userStore = useUserStore()

const formRef = ref()

const form = ref({
  name: '',
  email: '',
  password: ''
})

const rules = {
  name: [
    { required: true, message: 'Please enter your name', trigger: 'blur' },
    { min: 2, max: 50, message: 'Name should be 2-50 characters', trigger: 'blur' }
  ],
  email: [
    { required: true, message: 'Please enter your email', trigger: 'blur' },
    { type: 'email', message: 'Please enter a valid email', trigger: 'blur' }
  ],
  password: [
    { min: 6, max: 50, message: 'Password should be at least 6 characters', trigger: 'blur' }
  ]
}

const handleUpdateProfile = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    userStore.clearError()
    
    const result = await userStore.updateProfile(form.value)
    
    if (result.success) {
      ElMessage.success('Profile updated successfully!')
      // Update auth store with new user data
      await authStore.getCurrentUser()
      // Clear password field
      form.value.password = ''
    } else {
      ElMessage.error(result.error || 'Failed to update profile')
    }
  })
}

const handleLogout = () => {
  authStore.logout()
  router.push('/')
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

onMounted(() => {
  // Initialize form with current user data
  if (authStore.user) {
    form.value.name = authStore.user.name
    form.value.email = authStore.user.email
  }
  
  userStore.clearError()
})
</script>

<style scoped>
/* Profile Card Styling */
.profile-card {
  background: white;
  border: 1px solid #e5e7eb;
}

.profile-card :deep(.el-card__header) {
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.profile-card :deep(.el-form-item__label) {
  color: #1f2937;
  font-weight: 600;
}

.profile-card :deep(.el-input__wrapper) {
  background-color: white;
  border-color: #e5e7eb;
}

.profile-card :deep(.el-input__inner) {
  color: #1f2937;
}

.profile-card :deep(.el-divider) {
  border-color: #e5e7eb;
}

/* Account Info */
.account-info :deep(.el-descriptions__label) {
  color: #6b7280;
  background: #f9fafb;
}

.account-info :deep(.el-descriptions__content) {
  color: #1f2937;
  background: white;
}
</style>