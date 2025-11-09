<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>创建账户</span>
          </div>
        </template>

        <el-form :model="form" :rules="rules" ref="formRef" label-position="top" @submit.prevent>
          <el-form-item label="姓名" prop="name">
            <el-input v-model="form.name" placeholder="请输入姓名" />
          </el-form-item>

          <el-form-item label="邮箱" prop="email">
            <el-input v-model="form.email" type="email" autocomplete="email" placeholder="请输入邮箱" />
          </el-form-item>

          <el-form-item label="密码" prop="password">
            <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
          </el-form-item>

          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input v-model="form.confirmPassword" type="password" placeholder="请再次输入密码" show-password />
          </el-form-item>

          <el-alert v-if="authStore.error" :title="authStore.error" type="error" show-icon class="mb-4" />
          <el-alert v-if="passwordMismatch" title="两次输入的密码不一致" type="warning" show-icon class="mb-4" />

          <el-form-item>
            <el-button type="primary" :loading="authStore.isLoading" class="w-full" @click="onSubmit">
              {{ authStore.isLoading ? '创建中...' : '创建账户' }}
            </el-button>
          </el-form-item>
        </el-form>

        <div class="text-center text-sm text-gray-600">
          已有账号？
          <router-link to="/login" class="text-indigo-600">去登录</router-link>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const formRef = ref()
const form = ref({
  name: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const rules = {
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: ['blur', 'change'] }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (_rule, value, callback) => {
        if (value !== form.value.password) callback(new Error('两次输入的密码不一致'))
        else callback()
      },
      trigger: ['blur', 'change']
    }
  ]
}

const passwordMismatch = computed(() => {
  return form.value.password && form.value.confirmPassword && 
         form.value.password !== form.value.confirmPassword
})

const onSubmit = async () => {
  await formRef.value?.validate(async (valid) => {
    if (!valid) return
    authStore.clearError()
    const result = await authStore.register({
      name: form.value.name,
      email: form.value.email,
      password: form.value.password
    })
    if (result.success) {
      const loginResult = await authStore.login({
        email: form.value.email,
        password: form.value.password
      })
      if (loginResult.success) router.push('/dashboard')
    }
  })
}

onMounted(() => {
  authStore.clearError()
})
</script>

