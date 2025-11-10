<template>
  <div class="login-wrapper">
    <el-card class="login-card" shadow="hover">
      <template #header>
        <div class="card-header">登录到失物招领平台</div>
      </template>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" size="large" @submit.prevent>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" type="email" autocomplete="email" placeholder="请输入邮箱地址" />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" show-password autocomplete="current-password" placeholder="请输入密码" />
        </el-form-item>

        <el-alert v-if="authStore.error" :title="authStore.error" type="error" show-icon class="mb-2" />

        <el-button type="primary" size="large" class="w-full" :loading="authStore.isLoading" @click="handleLogin">
          {{ authStore.isLoading ? '登录中...' : '登录' }}
        </el-button>

        <div class="divider">或</div>

        <el-button type="info" size="large" class="w-full" @click="$router.push('/register')">注册新账户</el-button>
      </el-form>
    </el-card>
  </div>
 </template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

const formRef = ref(null)
const form = ref({ email: '', password: '' })

const rules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: ['blur', 'change'] },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: ['blur', 'change'] }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: ['blur', 'change'] },
    { min: 6, message: '密码长度至少6位', trigger: ['blur', 'change'] }
  ]
}

const handleLogin = async () => {
  try {
    await formRef.value?.validate()
    authStore.clearError()
    const result = await authStore.login(form.value)
    if (result.success) {
      ElMessage.success('登录成功！')
      router.push('/dashboard')
    } else {
      ElMessage.error(result.error || '登录失败')
    }
  } catch (error) {
    // ignore
  }
}
</script>

<style scoped>
.login-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-base);
  padding: 16px;
}
.login-card {
  width: 100%;
  max-width: 400px;
  background: var(--bg-surface);
  border: 1px solid var(--border-base);
}
.card-header {
  font-weight: 800;
  color: var(--text-primary);
}
.divider {
  text-align: center;
  color: var(--text-tertiary);
  margin: 12px 0;
}
</style>