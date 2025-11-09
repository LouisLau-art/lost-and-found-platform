<template>
  <div class="bg-white rounded-lg border p-4 mb-4">
    <h3 class="text-lg font-semibold mb-3">评价统计</h3>
    
    <div v-if="loading" class="flex justify-center py-4">
      <el-skeleton :rows="3" animated />
    </div>
    
    <div v-else-if="error" class="text-center py-4 text-red-500">
      加载评价统计失败
    </div>
    
    <div v-else>
      <!-- 总体评分 -->
      <div class="flex items-center justify-between mb-4">
        <div>
          <div class="text-3xl font-bold">{{ stats.average_score.toFixed(1) }}</div>
          <div class="text-sm text-gray-500">{{ stats.total_count }} 条评价</div>
        </div>
        <div class="flex items-center">
          <el-rate
            v-model="stats.average_score"
            disabled
            show-score
            text-color="#ff9900"
            score-template=""
          />
        </div>
      </div>
      
      <!-- 评分分布 -->
      <div class="mb-4">
        <div v-for="(count, score) in stats.star_distribution" :key="score" class="flex items-center mb-1">
          <div class="w-12 text-sm">{{ score }}星</div>
          <div class="flex-1 mx-2">
            <div class="bg-gray-200 h-2 rounded-full overflow-hidden">
              <div 
                class="bg-yellow-400 h-full" 
                :style="{ width: `${getPercentage(count)}%` }"
              ></div>
            </div>
          </div>
          <div class="w-12 text-right text-sm text-gray-500">{{ count }}</div>
        </div>
      </div>
      
      <!-- 好评率 -->
      <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
        <div class="text-sm text-gray-700">好评率</div>
        <div class="font-semibold">{{ stats.positive_percentage }}%</div>
      </div>
    </div>
    
    <!-- 最近评价 -->
    <div v-if="!loading && !error && stats.recent_ratings.length > 0" class="mt-4">
      <h4 class="text-md font-medium mb-2">最近评价</h4>
      <div class="space-y-3">
        <rating-card 
          v-for="rating in stats.recent_ratings" 
          :key="rating.id" 
          :rating="rating"
          class="border-0 shadow-none p-0 hover:bg-gray-50"
        />
      </div>
      <div v-if="stats.total_count > stats.recent_ratings.length" class="mt-3 text-center">
        <el-button type="primary" link @click="$emit('view-all')">
          查看全部评价
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ratingAPI } from '../api'
import RatingCard from './RatingCard.vue'

const props = defineProps({
  userId: {
    type: [Number, String],
    required: true
  },
  limit: {
    type: Number,
    default: 3
  }
})

defineEmits(['view-all'])

const stats = ref({
  total_count: 0,
  average_score: 0,
  star_distribution: {
    1: 0,
    2: 0,
    3: 0,
    4: 0,
    5: 0
  },
  positive_percentage: 0,
  recent_ratings: []
})

const loading = ref(true)
const error = ref(false)

const getPercentage = (count) => {
  if (stats.value.total_count === 0) return 0
  return (count / stats.value.total_count) * 100
}

const fetchStats = async () => {
  loading.value = true
  error.value = false
  
  try {
    // 尝试调用统计API
    const response = await ratingAPI.getUserRatingStats(props.userId, props.limit)
    stats.value = response.data
  } catch (err) {
    console.error('Failed to fetch rating stats:', err)
    
    // 如果API不存在（404），尝试使用备用方案
    if (err.response?.status === 404) {
      try {
        // 使用现有的getUserRatings API
        const ratingsResponse = await ratingAPI.getUserRatings(props.userId)
        const ratings = ratingsResponse.data || []
        
        // 手动计算统计数据
        stats.value = calculateStats(ratings)
      } catch (fallbackErr) {
        console.error('Fallback API also failed:', fallbackErr)
        error.value = true
      }
    } else {
      error.value = true
    }
  } finally {
    loading.value = false
  }
}

// 手动计算统计数据
const calculateStats = (ratings) => {
  const total = ratings.length
  
  if (total === 0) {
    return {
      total_count: 0,
      average_score: 0,
      star_distribution: { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 },
      positive_percentage: 0,
      recent_ratings: []
    }
  }
  
  // 计算平均分
  const sum = ratings.reduce((acc, r) => acc + r.score, 0)
  const average = sum / total
  
  // 计算星级分布
  const distribution = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 }
  ratings.forEach(r => {
    if (r.score >= 1 && r.score <= 5) {
      distribution[r.score]++
    }
  })
  
  // 计算好评率（4星及以上）
  const positiveCount = (distribution[4] || 0) + (distribution[5] || 0)
  const positivePercentage = Math.round((positiveCount / total) * 100)
  
  // 获取最近的评价
  const recent = ratings
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    .slice(0, props.limit)
  
  return {
    total_count: total,
    average_score: Math.round(average * 10) / 10,
    star_distribution: distribution,
    positive_percentage: positivePercentage,
    recent_ratings: recent
  }
}

onMounted(() => {
  fetchStats()
})
</script>