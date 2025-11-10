<template>
  <div class="rounded-lg p-4 mb-4" style="background: var(--bg-card); border: 1px solid var(--border-base);">
    <h3 class="text-lg font-semibold mb-3" style="color: var(--text-primary);">筛选评价</h3>
    
    <div class="space-y-4">
      <!-- 评分筛选 -->
      <div>
        <label class="block text-sm font-medium text-fg-primary mb-2">评分</label>
        <div class="flex flex-wrap gap-2">
          <el-tag
            v-for="score in [5, 4, 3, 2, 1]"
            :key="score"
            :type="filters.score === score ? 'primary' : 'info'"
            class="cursor-pointer"
            @click="toggleScoreFilter(score)"
          >
            {{ score }} 星
          </el-tag>
          <el-tag
            v-if="filters.score"
            type="danger"
            class="cursor-pointer"
            @click="filters.score = null"
          >
            清除
          </el-tag>
        </div>
      </div>
      
      <!-- 时间筛选 -->
      <div>
        <label class="block text-sm font-medium text-fg-primary mb-2">时间范围</label>
        <el-select v-model="filters.timeRange" class="w-full">
          <el-option label="全部时间" value="" />
          <el-option label="最近一周" value="week" />
          <el-option label="最近一个月" value="month" />
          <el-option label="最近三个月" value="quarter" />
          <el-option label="最近一年" value="year" />
        </el-select>
      </div>
      
      <!-- 排序方式 -->
      <div>
        <label class="block text-sm font-medium text-fg-primary mb-2">排序方式</label>
        <el-select v-model="filters.sortBy" class="w-full">
          <el-option label="最新优先" value="newest" />
          <el-option label="最早优先" value="oldest" />
          <el-option label="评分从高到低" value="score_desc" />
          <el-option label="评分从低到高" value="score_asc" />
        </el-select>
      </div>
      
      <!-- 应用筛选按钮 -->
      <div class="flex justify-end">
        <el-button type="primary" @click="applyFilters">应用筛选</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

const props = defineProps({
  initialFilters: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['filter'])

const filters = reactive({
  score: props.initialFilters.score || null,
  timeRange: props.initialFilters.timeRange || '',
  sortBy: props.initialFilters.sortBy || 'newest'
})

const toggleScoreFilter = (score) => {
  filters.score = filters.score === score ? null : score
}

const applyFilters = () => {
  emit('filter', { ...filters })
}
</script>