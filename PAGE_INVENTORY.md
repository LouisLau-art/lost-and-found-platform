# 项目页面完整清单

## 📊 页面总览

**总计**: 22个页面（不含404和重定向）

---

## 🏠 公共页面 (3个)

### 1. 首页
- **路径**: `/` → 重定向到 `/forum`
- **文件**: `views/HomeView.vue`
- **状态**: ✅ 存在
- **权限**: 无需登录

### 2. 关于页面
- **路径**: `/about`
- **文件**: `views/AboutView.vue`
- **状态**: ✅ 存在
- **权限**: 无需登录

### 3. 测试页面
- **路径**: `/test`
- **文件**: `views/TestView.vue`
- **状态**: ✅ 存在
- **权限**: 无需登录
- **用途**: 开发测试和问题排查

---

## 🔐 认证页面 (2个)

### 1. 登录页面
- **路径**: `/login`
- **文件**: `views/auth/LoginView.vue`
- **状态**: ✅ 存在
- **权限**: 仅访客（已登录用户会被重定向）
- **功能**: 
  - 邮箱/密码登录
  - 表单验证
  - 错误提示（不刷新页面）
  - 登录后重定向到dashboard

### 2. 注册页面
- **路径**: `/register`
- **文件**: `views/auth/RegisterView.vue`
- **状态**: ✅ 存在
- **权限**: 仅访客
- **功能**: 新用户注册

---

## 👤 用户中心页面 (5个)

### 1. 用户仪表盘 ⭐
- **路径**: `/dashboard`
- **文件**: `views/user/DashboardView.vue`
- **状态**: ✅ 存在
- **权限**: 需要登录
- **功能**:
  - 用户信息展示（头像、姓名、邮箱、信用分）
  - 左侧导航菜单（Dashboard、My Activity、Forum、Profile Settings）
  - 快捷操作按钮（I Lost Something、I Found Something）
  - **管理员面板**（仅管理员可见）:
    - 用户管理按钮 → `/admin/users`
    - 帖子管理按钮 → `/admin/posts`
  - 我的帖子统计
  - 我的认领统计
  - 通知中心

### 2. 个人资料设置
- **路径**: `/profile`
- **文件**: `views/user/ProfileView.vue`
- **状态**: ✅ 存在
- **权限**: 需要登录
- **功能**: 编辑个人信息

### 3. 我的活动
- **路径**: `/user/activity`
- **文件**: `views/user/ActivityView.vue`
- **状态**: ✅ 存在
- **权限**: 需要登录
- **功能**: 查看用户活动记录

### 4. 我的认领
- **路径**: `/claims`
- **文件**: `views/user/ClaimsView.vue`
- **状态**: ✅ 存在
- **权限**: 需要登录
- **功能**: 管理我的认领请求

### 5. 用户公开主页
- **路径**: `/users/:id`
- **文件**: `views/user/UserProfileView.vue`
- **状态**: ✅ 存在
- **权限**: 无需登录
- **功能**: 查看其他用户的公开信息

---

## 📝 论坛页面 (4个)

### 1. 论坛列表
- **路径**: `/forum`
- **文件**: `views/forum/ForumListView.vue`
- **状态**: ✅ 存在
- **权限**: 无需登录
- **功能**:
  - 浏览所有帖子
  - 搜索和筛选（按类型、分类、地点、时间）
  - 分页显示

### 2. 发布帖子
- **路径**: `/forum/create`
- **文件**: `views/forum/CreatePostView.vue`
- **状态**: ✅ 存在
- **权限**: 需要登录
- **功能**:
  - 创建lost（丢失）或found（拾到）帖子
  - 分步骤表单（使用el-steps）
  - 上传图片（最多9张）
  - 选择分类、地点、时间
  - 添加联系方式

### 3. 帖子详情
- **路径**: `/forum/:id`
- **文件**: `views/forum/PostDetailView.vue`
- **状态**: ✅ 存在
- **权限**: 无需登录
- **功能**:
  - 查看帖子完整信息
  - 智能匹配推荐（相同地点、分类、时间的帖子）
  - 评论功能
  - 认领功能
  - 联系方式显示

### 4. 编辑帖子
- **路径**: `/forum/:id/edit`
- **文件**: `views/forum/PostEditView.vue`
- **状态**: ✅ 存在
- **权限**: 需要登录且是帖子作者
- **功能**: 编辑自己发布的帖子

---

## 👑 管理员页面 (2个)

### 1. 用户管理 ⭐
- **路径**: `/admin/users`
- **路由名称**: `user-management`
- **文件**: `views/admin/UserManagementView.vue`
- **状态**: ✅ 存在
- **权限**: 需要管理员权限
- **功能**:
  - 查看所有用户列表
  - 用户信息管理
  - 权限管理
  - 用户状态管理
- **访问方式**:
  - Dashboard中的"用户管理"按钮
  - 顶部导航的"管理后台"
  - 直接访问 `/admin/users`

### 2. 帖子管理 ⭐
- **路径**: `/admin/posts`
- **路由名称**: `admin-posts`
- **文件**: `views/admin/AdminPostsView.vue`
- **状态**: ✅ 存在
- **权限**: 需要管理员权限
- **功能**:
  - 查看所有帖子（包括已删除的）
  - 使用el-table展示帖子列表
  - 编辑任意帖子
  - 删除帖子（带确认提示）
  - 分页显示
  - 状态筛选
- **访问方式**:
  - Dashboard中的"帖子管理"按钮
  - 顶部导航的"管理后台"（默认跳转到用户管理）
  - 直接访问 `/admin/posts`

---

## 🔒 权限说明

### 访客（未登录）
可访问:
- ✅ 首页、关于、测试页面
- ✅ 登录、注册页面
- ✅ 论坛列表、帖子详情
- ✅ 用户公开主页

无法访问:
- ❌ 用户中心所有页面
- ❌ 发布/编辑帖子
- ❌ 管理员页面

### 普通用户（已登录）
可访问:
- ✅ 所有访客可访问的页面
- ✅ 用户中心所有页面
- ✅ 发布/编辑帖子
- ✅ 认领功能

无法访问:
- ❌ 管理员页面（会被重定向到dashboard）
- ❌ 登录、注册页面（会被重定向到dashboard）

### 管理员（已登录且is_admin=true）
可访问:
- ✅ 所有普通用户可访问的页面
- ✅ 用户管理页面
- ✅ 帖子管理页面

---

## 📍 路由重定向

| 原路径 | 重定向到 |
|--------|----------|
| `/` | `/forum` |
| `/posts` | `/forum` |
| `/posts/new` | `/forum/create` |
| 404 (所有未匹配路径) | `/test` |

---

## 🎨 Dashboard管理员面板详情

在 [`DashboardView.vue`](file://c:\Users\Louis\Desktop\lost-and-found-platform\frontend\frontend\src\views\user\DashboardView.vue) 中，管理员可以看到特殊的管理员面板：

```vue
<!-- Admin Panel (Only for Admins) -->
<el-card v-if="authStore.user?.is_admin" shadow="hover" class="activity-card mb-6">
  <template #header>
    <div class="text-white font-semibold flex items-center">
      <el-icon class="mr-2"><User /></el-icon>
      管理员面板
    </div>
  </template>
  <div class="grid grid-cols-2 gap-4">
    <el-button type="warning" size="large" @click="$router.push('/admin/users')" class="admin-btn">
      <el-icon class="mr-2"><User /></el-icon>
      用户管理
    </el-button>
    <el-button type="info" size="large" @click="$router.push('/admin/posts')" class="admin-btn">
      <el-icon class="mr-2"><Document /></el-icon>
      帖子管理
    </el-button>
  </div>
</el-card>
```

**显示条件**: `authStore.user?.is_admin === true`

如果您看不到管理员面板，请：
1. 确认已登录
2. 检查控制台，查看用户信息中的 `is_admin` 字段
3. 确保已重新登录（更新权限后需要重新登录）

---

## 🚀 导航入口

### 顶部导航栏
- **管理后台链接**（仅管理员可见）: 
  ```vue
  <router-link 
    v-if="authStore.user?.is_admin" 
    to="/admin/users"
    class="..."
  >
    管理后台
  </router-link>
  ```

### 用户下拉菜单
- Profile（个人资料）
- 管理后台（仅管理员）
- Sign out（登出）

### Dashboard左侧菜单
- Dashboard（当前页）
- My Activity
- Forum
- Profile Settings

### Dashboard管理员面板（仅管理员）
- 用户管理按钮
- 帖子管理按钮

---

## 📝 页面功能对照表

| 页面类型 | 已实现 | 缺失 |
|---------|--------|------|
| 认证功能 | ✅ 登录、注册 | - |
| 用户中心 | ✅ Dashboard、Profile、Activity、Claims、UserProfile | - |
| 论坛功能 | ✅ 列表、详情、发布、编辑 | - |
| 管理功能 | ✅ 用户管理、帖子管理 | ❌ 分类管理、统计分析、系统设置 |
| 通知系统 | ✅ 通知列表、未读提示 | - |
| 智能匹配 | ✅ 基于地点、分类、时间 | 💡 文本相似度匹配（建议添加） |

---

## 💡 建议添加的功能

### 1. 文本相似度匹配（高优先级）
**当前状态**: 智能匹配基于分类、时间、地点三个维度  
**建议优化**: 添加基于物品描述的文本相似度匹配

**实现方案**:
```python
# backend/app/services/text_similarity.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import jieba  # 中文分词

def calculate_text_similarity(text1: str, text2: str) -> float:
    """计算两段文本的相似度（0-1之间）"""
    # 分词
    words1 = ' '.join(jieba.cut(text1))
    words2 = ' '.join(jieba.cut(text2))
    
    # 计算TF-IDF向量
    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform([words1, words2])
    
    # 计算余弦相似度
    similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    return similarity

# 在智能匹配中使用
def get_matching_posts_enhanced(post_id: int, session: Session):
    # 获取原帖
    original_post = session.get(Post, post_id)
    
    # 基础匹配（现有逻辑）
    base_matches = get_matching_posts(post_id, session)
    
    # 文本相似度排序
    for match in base_matches:
        similarity = calculate_text_similarity(
            original_post.content, 
            match.content
        )
        match.similarity_score = similarity
    
    # 按相似度排序
    base_matches.sort(key=lambda x: x.similarity_score, reverse=True)
    return base_matches
```

**需要的依赖**:
```bash
pip install jieba scikit-learn
```

### 2. 分类管理页面
- 路径: `/admin/categories`
- 功能: 添加、编辑、删除物品分类

### 3. 统计分析Dashboard
- 路径: `/admin/dashboard`
- 功能: 数据可视化、趋势分析

### 4. 系统设置页面
- 路径: `/admin/settings`
- 功能: 系统参数配置

---

## 🔍 如何验证页面是否存在

### 方法1: 检查文件系统
```bash
# 查看所有视图文件
ls frontend/frontend/src/views/**/*.vue
```

### 方法2: 检查路由配置
查看 [`router/index.js`](file://c:\Users\Louis\Desktop\lost-and-found-platform\frontend\frontend\src\router\index.js) 中的路由定义

### 方法3: 浏览器访问
- 打开浏览器控制台（F12）
- 访问相应URL
- 如果页面存在但无权限，会看到重定向日志
- 如果页面不存在，会重定向到 `/test`

---

## 📱 移动端适配

所有页面都使用了响应式设计，支持以下断点：
- `xs`: < 768px（手机）
- `sm`: 768px - 992px（平板）
- `md`: 992px - 1200px（小屏电脑）
- `lg`: 1200px+（大屏电脑）

---

**最后更新**: 2025-10-24  
**文档状态**: ✅ 完整准确
