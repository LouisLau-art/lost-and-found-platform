<template>
  <div class="bg-white rounded-lg border p-4 hover:shadow-md transition">
    <!-- 评价者信息 -->
    <div class="flex items-start justify-between mb-3">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center">
          <span class="text-white font-semibold text-sm">
            {{ raterInitial }}
          </span>
        </div>
        <div>
          <div class="font-medium text-gray-900">{{ rating.rater?.name || 'Unknown' }}</div>
          <div class="text-xs text-gray-500">{{ formatDate(rating.created_at) }}</div>
        </div>
      </div>
      
      <!-- 星级评分 -->
      <div class="flex items-center gap-1">
        <el-rate
          v-model="rating.score"
          disabled
          show-score
          text-color="#ff9900"
          score-template="{value}"
          size="small"
        />
      </div>
    </div>

    <!-- 评价内容 -->
    <div v-if="rating.comment" class="bg-gray-50 rounded p-3 mb-2">
      <p class="text-sm text-gray-700 whitespace-pre-wrap">{{ rating.comment }}</p>
    </div>

    <!-- 评分说明 -->
    <div class="flex items-center gap-2 text-xs">
      <el-tag :type="getScoreType(rating.score)" size="small">
        {{ getScoreLabel(rating.score) }}
      </el-tag>
      <span class="text-gray-400">
        {{ getScoreImpact(rating.score) }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  rating: {
    type: Object,
    required: true
  }
})

// 获取评价者首字母
const raterInitial = computed(() => {
  const name = props.rating.rater?.name || 'U'
  return name.charAt(0).toUpperCase()
})

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  
  if (days > 30) {
    return date.toLocaleDateString('zh-CN')
  } else if (days > 0) {
    return `${days}天前`
  } else if (hours > 0) {
    return `${hours}小时前`
  } else if (minutes > 0) {
    return `${minutes}分钟前`
  } else {
    return '刚刚'
  }
}

// 获取评分类型
const getScoreType = (score) => {
  if (score >= 4) return 'success'
  if (score === 3) return ''
  return 'warning'
}

// 获取评分标签
const getScoreLabel = (score) => {
  const labels = {
    5: '非常满意',
    4: '满意',
    3: '一般',
    2: '较差',
    1: '很差'
  }
  return labels[score] || '未知'
}

// 获取评分影响
const getScoreImpact = (score) => {
  if (score >= 4) return '信用分 +5'
  if (score === 3) return '信用分 +0'
  return '信用分 -5'
}
</script>

<style scoped>
:deep(.el-rate) {
  display: inline-flex;
}

:deep(.el-rate__text) {
  font-size: 14px;
  font-weight: 500;
}
</style>
