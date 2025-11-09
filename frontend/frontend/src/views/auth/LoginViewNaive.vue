<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <n-card class="w-full max-w-md" title="登录到失物招领平台">
      <n-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-placement="left"
        label-width="auto"
        require-mark-placement="right-hanging"
        size="large"
        @submit.prevent="handleLogin"
      >
        <n-form-item label="邮箱" path="email">
          <n-input
            v-model:value="form.email"
            placeholder="请输入邮箱地址"
            type="email"
            :input-props="{ autocomplete: 'email' }"
          />
        </n-form-item>
        
        <n-form-item label="密码" path="password">
          <n-input
            v-model:value="form.password"
            placeholder="请输入密码"
            type="password"
            show-password-on="click"
            :input-props="{ autocomplete: 'current-password' }"
          />
        </n-form-item>

        <n-form-item v-if="authStore.error">
          <n-alert type="error" :show-icon="false">
            {{ authStore.error }}
          </n-alert>
        </n-form-item>

        <n-form-item>
          <n-button
            type="primary"
            size="large"
            block
            :loading="authStore.isLoading"
            @click="handleLogin"
          >
            {{ authStore.isLoading ? '登录中...' : '登录' }}
          </n-button>
        </n-form-item>

        <n-divider>或</n-divider>

        <n-form-item>
          <n-button
            type="info"
            size="large"
            block
            @click="$router.push('/register')"
          >
            注册新账户
          </n-button>
        </n-form-item>
      </n-form>
    </n-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  NCard,
  NForm,
  NFormItem,
  NInput,
  NButton,
  NAlert,
  NDivider,
  useMessage
} from 'naive-ui'

const router = useRouter()
const authStore = useAuthStore()
const message = useMessage()

const formRef = ref(null)
const form = ref({
  email: '',
  password: ''
})

const rules = {
  email: [
    {
      required: true,
      message: '请输入邮箱地址',
      trigger: ['input', 'blur']
    },
    {
      type: 'email',
      message: '请输入有效的邮箱地址',
      trigger: ['input', 'blur']
    }
  ],
  password: [
    {
      required: true,
      message: '请输入密码',
      trigger: ['input', 'blur']
    },
    {
      min: 6,
      message: '密码长度至少6位',
      trigger: ['input', 'blur']
    }
  ]
}

const handleLogin = async () => {
  try {
    await formRef.value?.validate()
    authStore.clearError()
    
    const result = await authStore.login(form.value)
    
    if (result.success) {
      message.success('登录成功！')
      router.push('/dashboard')
    } else {
      message.error(result.error || '登录失败')
    }
  } catch (error) {
    console.error('Form validation failed:', error)
  }
}
</script>

