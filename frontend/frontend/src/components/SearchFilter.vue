<template>
  <div class="search-filter-container">
    <el-form :model="filters" label-position="top" size="default" class="modern-filter-form">
      <!-- 第一行：关键词搜索 + 物品类型 -->
      <el-row :gutter="16">
        <el-col :span="24" :sm="12">
          <el-form-item label="关键词搜索">
            <el-input
              v-model="filters.search"
              placeholder="搜索标题或内容..."
              clearable
              @keyup.enter="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-form-item>
        </el-col>
        <el-col :span="24" :sm="12">
          <el-form-item label="物品类型">
            <el-select v-model="filters.item_type" placeholder="请选择类型" clearable class="w-full">
              <el-option label="丢失物品" value="lost" />
              <el-option label="拾到物品" value="found" />
              <el-option label="普通帖子" value="general" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      
      <!-- 第二行：物品分类 + 地点 -->
      <el-row :gutter="16">
        <el-col :span="24" :sm="12">
          <el-form-item label="物品分类">
            <el-select
              v-model="filters.category_id"
              placeholder="请选择分类"
              clearable
              class="w-full"
              :loading="loadingCategories"
            >
              <el-option
                v-for="cat in categories"
                :key="cat.id"
                :label="cat.name"
                :value="cat.id"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="24" :sm="12">
          <el-form-item label="地点">
            <el-input
              v-model="filters.location"
              placeholder="输入地点关键词..."
              clearable
            >
              <template #prefix>
                <el-icon><Location /></el-icon>
              </template>
            </el-input>
          </el-form-item>
        </el-col>
      </el-row>
      
      <!-- 第三行：认领状态 + 时间范围 -->
      <el-row :gutter="16">
        <el-col :span="24" :sm="12">
          <el-form-item label="认领状态">
            <el-select v-model="filters.is_claimed" placeholder="请选择状态" clearable class="w-full">
              <el-option label="未认领" :value="false" />
              <el-option label="已认领" :value="true" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="24" :sm="12">
          <el-form-item label="时间范围">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              class="w-full date-picker"
              size="default"
              @change="handleDateChange"
            />
          </el-form-item>
        </el-col>
      </el-row>
      
      <!-- 操作按钮 -->
      <div class="flex gap-4 mt-4 mb-3">
        <el-button type="primary" class="search-btn" @click="handleSearch">
          <el-icon class="mr-1"><Search /></el-icon>
          搜索
        </el-button>
        <el-button class="reset-btn" @click="resetFilters">
          <el-icon class="mr-1"><RefreshLeft /></el-icon>
          重置
        </el-button>
      </div>
      
      <!-- 当前筛选条件标签 -->
      <div v-if="hasActiveFilters" class="pt-4 border-t border-base">
        <div class="text-sm text-fg-secondary mb-2">当前筛选条件：</div>
        <div class="flex flex-wrap gap-2">
          <el-tag
            v-if="filters.search"
            closable
            @close="filters.search = ''"
            size="small"
          >
            关键词: {{ filters.search }}
          </el-tag>
          <el-tag
            v-if="filters.item_type"
            closable
            @close="filters.item_type = null"
            size="small"
            type="primary"
          >
            类型: {{ getItemTypeLabel(filters.item_type) }}
          </el-tag>
          <el-tag
            v-if="filters.category_id"
            closable
            @close="filters.category_id = null"
            size="small"
            type="warning"
          >
            分类: {{ getCategoryLabel(filters.category_id) }}
          </el-tag>
          <el-tag
            v-if="filters.location"
            closable
            @close="filters.location = ''"
            size="small"
          >
            地点: {{ filters.location }}
          </el-tag>
          <el-tag
            v-if="filters.is_claimed !== null"
            closable
            @close="filters.is_claimed = null"
            size="small"
            :type="filters.is_claimed ? 'success' : 'danger'"
          >
            {{ filters.is_claimed ? '已认领' : '未认领' }}
          </el-tag>
          <el-tag
            v-if="dateRange && dateRange.length === 2"
            closable
            @close="dateRange = null; filters.start_date = null; filters.end_date = null"
            size="small"
            type="info"
          >
            时间范围
          </el-tag>
        </div>
      </div>
    </el-form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { categoryAPI } from '@/api'
import { Search, Location, RefreshLeft } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue', 'search'])

const filters = ref({
  search: '',
  item_type: null,
  category_id: null,
  location: '',
  is_claimed: null,
  start_date: null,
  end_date: null
})

const dateRange = ref(null)
const categories = ref([])
const loadingCategories = ref(false)

// 判断是否有激活的筛选条件
const hasActiveFilters = computed(() => {
  return filters.value.search ||
         filters.value.item_type ||
         filters.value.category_id ||
         filters.value.location ||
         filters.value.is_claimed !== null ||
         (dateRange.value && dateRange.value.length === 2)
})

// 获取分类列表
const fetchCategories = async () => {
  loadingCategories.value = true
  try {
    const response = await categoryAPI.getAll()
    categories.value = response.data
  } catch (error) {
    console.error('Failed to fetch categories:', error)
  } finally {
    loadingCategories.value = false
  }
}

// 处理日期范围变化
const handleDateChange = (dates) => {
  if (dates && dates.length === 2) {
    filters.value.start_date = dates[0].toISOString()
    filters.value.end_date = dates[1].toISOString()
  } else {
    filters.value.start_date = null
    filters.value.end_date = null
  }
}

// 执行搜索
const handleSearch = () => {
  // 移除空值
  const cleanFilters = Object.entries(filters.value).reduce((acc, [key, value]) => {
    if (value !== null && value !== '' && value !== undefined) {
      acc[key] = value
    }
    return acc
  }, {})
  
  emit('update:modelValue', cleanFilters)
  emit('search', cleanFilters)
}

// 重置筛选
const resetFilters = () => {
  filters.value = {
    search: '',
    item_type: null,
    category_id: null,
    location: '',
    is_claimed: null,
    start_date: null,
    end_date: null
  }
  dateRange.value = null
  handleSearch()
}

// 获取物品类型标签
const getItemTypeLabel = (type) => {
  const labels = {
    lost: '丢失物品',
    found: '拾到物品',
    general: '普通帖子'
  }
  return labels[type] || type
}

// 获取分类标签
const getCategoryLabel = (id) => {
  const category = categories.value.find(cat => cat.id === id)
  return category ? `${category.icon} ${category.name}` : `分类 #${id}`
}

onMounted(() => {
  fetchCategories()
})
</script>

<style scoped>
.search-filter-container {
  width: 100%;
  padding: 16px;
  background-color: var(--bg-card);
  border: 1px solid var(--border-base);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}

.modern-filter-form :deep(.el-form-item) {
  margin-bottom: 16px;
}

.modern-filter-form :deep(.el-form-item__label) {
  color: var(--text-primary);
  font-weight: 600;
  margin-bottom: 6px;
  font-size: 14px;
}

.modern-filter-form :deep(.el-input__wrapper),
.modern-filter-form :deep(.el-select .el-input__wrapper),
.modern-filter-form :deep(.el-date-editor .el-input__wrapper) {
  background-color: var(--input-bg-color);
  border-color: var(--input-border-color);
  transition: all 0.3s ease;
}

.modern-filter-form :deep(.el-input__wrapper:hover),
.modern-filter-form :deep(.el-select .el-input__wrapper:hover),
.modern-filter-form :deep(.el-date-editor .el-input__wrapper:hover) {
  border-color: var(--border-base);
}

.modern-filter-form :deep(.el-input__wrapper.is-focus),
.modern-filter-form :deep(.el-select .el-input__wrapper.is-focus),
.modern-filter-form :deep(.el-date-editor .el-input__wrapper.is-focus) {
  border-color: var(--primary);
  box-shadow: 0 0 0 2px rgba(59,130,246,0.15);
}

.modern-filter-form :deep(.el-input__inner) {
  color: var(--text-primary);
  font-size: 14px;
}

.date-picker {
  cursor: pointer;
}

.search-btn,
.reset-btn {
  padding: 10px 20px;
  font-size: 14px;
  transition: all 0.3s ease;
}

.search-btn {
  background-color: var(--primary);
  border-color: var(--primary);
  flex: 2;
}

.search-btn:hover {
  background-color: var(--primary);
  border-color: var(--primary);
}

.reset-btn {
  flex: 1;
}

.reset-btn:hover {
  color: var(--primary);
  border-color: var(--primary);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .search-filter-container {
    padding: 12px;
  }
  
  .modern-filter-form :deep(.el-form-item) {
    margin-bottom: 12px;
  }
  
  .search-btn,
  .reset-btn {
    padding: 8px 16px;
    font-size: 13px;
  }
}
</style>
