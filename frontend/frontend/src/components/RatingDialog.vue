<template>
  <el-dialog
    v-model="dialogVisible"
    title="评价"
    width="500px"
    @close="handleClose"
  >
    <div v-if="claim" class="space-y-4">
      <!-- 评价对象 -->
      <div class="bg-muted rounded p-4">
        <div class="text-sm text-fg-secondary mb-2">评价对象</div>
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-full flex items-center justify-center" style="background: var(--bg-surface);">
            <svg class="w-6 h-6 icon-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          <div>
            <div class="font-medium text-fg-primary">{{ rateeUser?.name }}</div>
            <div class="text-sm text-fg-secondary">信用分：{{ rateeUser?.credit_score }}</div>
          </div>
        </div>
      </div>

      <!-- 星级评分 -->
      <div>
        <label class="block text-sm font-medium text-fg-primary mb-3">
          评分 <span class="text-red-500">*</span>
        </label>
        <div class="flex items-center gap-4">
          <el-rate
            v-model="form.score"
            :texts="rateTexts"
            show-text
            size="large"
          />
        </div>
        <div class="mt-2 text-xs text-fg-secondary">
          <div v-if="form.score >= 4" class="text-success">
            ✓ 好评将为对方增加 5 信用分
          </div>
          <div v-else-if="form.score === 3" class="text-fg-secondary">
            中评不影响信用分
          </div>
          <div v-else-if="form.score > 0" class="text-danger">
            ⚠ 差评将扣除对方 5 信用分
          </div>
        </div>
      </div>

      <!-- 评价标签 -->
      <div>
        <label class="block text-sm font-medium text-fg-primary mb-2">
          评价标签（可选，最多选择3个）
        </label>
        <div class="flex flex-wrap gap-2 mb-3">
          <el-tag 
            v-for="tag in getTagsByScore(form.score)" 
            :key="tag"
            :class="{ 'selected-tag': selectedTags.includes(tag) }"
            class="cursor-pointer hover:opacity-80"
            :type="selectedTags.includes(tag) ? 'primary' : 'info'"
            @click="toggleTag(tag)"
          >
            {{ tag }}
          </el-tag>
        </div>
      </div>

      <!-- 评价内容 -->
      <div>
        <label class="block text-sm font-medium text-fg-primary mb-2">
          评价内容（可选）
        </label>
        <el-input
          v-model="form.comment"
          type="textarea"
          :rows="4"
          :placeholder="getCommentPlaceholder()"
          maxlength="500"
          show-word-limit
        />
      </div>

      <!-- 评价示例 -->
      <div class="bg-muted rounded p-3">
        <div class="text-xs text-primary mb-2">💡 评价建议</div>
        <div class="text-xs text-fg-secondary space-y-1">
          <div>• 好评：态度友好、及时响应、物归原主</div>
          <div>• 中评：沟通一般、基本满意</div>
          <div>• 差评：态度不佳、沟通困难、信息不实</div>
        </div>
      </div>
    </div>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button
          type="primary"
          :loading="submitting"
          :disabled="!form.score"
          @click="handleSubmit"
        >
          提交评价
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { ratingAPI } from '@/api'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  claim: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'rated'])

const authStore = useAuthStore()

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const form = ref({
  score: 0,
  comment: ''
})

const submitting = ref(false)

const rateTexts = ['很差', '较差', '一般', '满意', '非常满意']

// 计算被评价者
const rateeUser = computed(() => {
  if (!props.claim) return null
  
  // 判断当前用户是认领者还是物主
  const isClaimerRating = props.claim.claimer_id === authStore.user?.id
  
  if (isClaimerRating) {
    // 认领者评价物主
    return props.claim.post?.author
  } else {
    // 物主评价认领者
    return props.claim.claimer
  }
})

// 重置表单
const resetForm = () => {
  form.value = {
    score: 0,
    comment: ''
  }
  selectedTags.value = []
}

// 关闭对话框
const handleClose = () => {
  dialogVisible.value = false
  resetForm()
}

// 提交评价
const handleSubmit = async () => {
  if (!form.value.score) {
    ElMessage.warning('请选择评分')
    return
  }

  submitting.value = true
  try {
    await ratingAPI.create({
      claim_id: props.claim.id,
      ratee_id: rateeUser.value.id,
      score: form.value.score,
      comment: form.value.comment || null,
      tags: selectedTags.value.length > 0 ? selectedTags.value.join(',') : null
    })
    
    emit('rated', props.claim.id)
    handleClose()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '提交失败')
  } finally {
    submitting.value = false
  }
}

// 评价标签相关
const selectedTags = ref([])

// 根据评分获取对应标签
const getTagsByScore = (score) => {
  if (score >= 4) {
    return ['态度友好', '及时响应', '物归原主', '沟通顺畅', '诚实守信']
  } else if (score === 3) {
    return ['基本满意', '沟通一般', '过程顺利', '有待改进']
  } else if (score > 0) {
    return ['态度不佳', '沟通困难', '信息不实', '响应缓慢', '不守约定']
  }
  return []
}

// 切换标签选择状态
const toggleTag = (tag) => {
  if (selectedTags.value.includes(tag)) {
    selectedTags.value = selectedTags.value.filter(t => t !== tag)
  } else {
    if (selectedTags.value.length < 3) {
      selectedTags.value.push(tag)
    } else {
      ElMessage.warning('最多只能选择3个标签')
    }
  }
}

// 根据评分和已选标签生成评论占位文本
const getCommentPlaceholder = () => {
  if (selectedTags.value.length > 0) {
    return `你选择了"${selectedTags.value.join('、')}"，可以详细描述一下...`
  }
  return '说说你对这次认领过程的评价...'
}

// 监听评分变化，重置标签
watch(() => form.value.score, () => {
  selectedTags.value = []
})

// 监听claim变化，重置表单
watch(() => props.claim, () => {
  if (props.claim) {
    resetForm()
  }
})
</script>

<style scoped>
:deep(.el-rate) {
  height: 40px;
}

:deep(.el-rate__text) {
  font-size: 16px;
  font-weight: 500;
}
</style>
