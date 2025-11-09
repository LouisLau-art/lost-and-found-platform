# 失物招领平台 API 使用指南

## 服务器信息
- **本地开发地址**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs (Swagger UI)
- **备用文档**: http://localhost:8000/redoc (ReDoc)

## 新增 API 端点

### 1. 物品分类 API

#### 获取所有分类
```http
GET /api/categories/
```

**查询参数**:
- `skip` (int, 可选): 跳过的记录数，默认 0
- `limit` (int, 可选): 返回的最大记录数，默认 100
- `show_all` (bool, 可选): 是否显示已禁用的分类，默认 false

**响应示例**:
```json
[
  {
    "id": 1,
    "name": "电子产品",
    "name_en": "electronics",
    "description": "手机、平板、笔记本电脑、耳机、充电器等",
    "icon": "📱",
    "is_active": true,
    "created_at": "2025-10-21T03:48:48.050322"
  }
]
```

#### 获取单个分类
```http
GET /api/categories/{category_id}
```

---

### 2. 图片上传 API

#### 上传单张图片
```http
POST /api/upload/upload
Content-Type: multipart/form-data
Authorization: Bearer {access_token}
```

**表单数据**:
- `file`: 图片文件 (支持 .jpg, .jpeg, .png, .gif, .webp)

**限制**:
- 最大文件大小: 5MB
- 支持格式: JPG, JPEG, PNG, GIF, WEBP

**响应示例**:
```json
{
  "filename": "550e8400-e29b-41d4-a716-446655440000.jpg",
  "url": "/uploads/images/550e8400-e29b-41d4-a716-446655440000.jpg",
  "message": "Image uploaded successfully"
}
```

#### 上传多张图片
```http
POST /api/upload/upload-multiple
Content-Type: multipart/form-data
Authorization: Bearer {access_token}
```

**表单数据**:
- `files`: 多个图片文件（最多 9 张）

**响应示例**:
```json
{
  "files": [
    {
      "filename": "...",
      "url": "/uploads/images/..."
    }
  ],
  "count": 3,
  "message": "3 images uploaded successfully"
}
```

---

### 3. 失物招领帖子 API（已增强）

#### 创建帖子（支持失物招领字段）
```http
POST /api/posts/
Authorization: Bearer {access_token}
```

**请求体**:
```json
{
  "title": "丢失黑色背包",
  "content": "今天下午在图书馆三楼丢失一个黑色双肩背包，里面有笔记本电脑和教材",
  "item_type": "lost",
  "category_id": 6,
  "location": "图书馆三楼",
  "item_time": "2025-10-21T14:30:00",
  "contact_info": "手机: 138****1234, 微信: abc123",
  "images": [
    "/uploads/images/xxx.jpg",
    "/uploads/images/yyy.jpg"
  ]
}
```

**字段说明**:
- `title` (必填): 帖子标题
- `content` (必填): 详细描述
- `item_type` (必填): 物品类型
  - `lost`: 丢失物品
  - `found`: 拾到物品
  - `general`: 普通帖子
- `category_id` (可选): 物品分类 ID
- `location` (可选): 丢失/拾取地点
- `item_time` (可选): 丢失/拾取时间
- `contact_info` (可选): 联系方式
- `images` (可选): 图片 URL 列表

#### 获取帖子列表（支持筛选）
```http
GET /api/posts/
```

**查询参数**:
- `skip` (int): 分页-跳过记录数
- `limit` (int): 分页-每页记录数
- `item_type` (string): 筛选物品类型 (lost/found/general)
- `category_id` (int): 筛选分类
- `is_claimed` (bool): 筛选是否已认领
- `search` (string): 搜索关键词（标题和内容）

**示例**:
```
GET /api/posts/?item_type=lost&category_id=1&is_claimed=false&search=手机
```

#### 智能匹配功能
```http
GET /api/posts/{post_id}/matches
```

**功能说明**:
- 为 "lost" 类型的帖子推荐 "found" 类型的匹配帖子
- 为 "found" 类型的帖子推荐 "lost" 类型的匹配帖子
- 匹配条件：相同分类、相似时间、相似地点

**查询参数**:
- `limit` (int): 最多返回的匹配数，默认 10
- `time_range_days` (int): 时间范围（天），默认 7

**响应**: 返回匹配的帖子列表

#### 高级搜索
```http
GET /api/posts/search/advanced
```

**查询参数**:
- `item_type`: 物品类型
- `category_id`: 分类 ID
- `location`: 地点（模糊匹配）
- `start_date`: 开始时间
- `end_date`: 结束时间
- `is_claimed`: 是否已认领
- `skip`: 分页偏移
- `limit`: 每页数量

---

## 使用流程示例

### 完整的发布失物流程

1. **用户登录**
```bash
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "password123"
}
# 获得 access_token
```

2. **上传物品图片**
```bash
POST /api/upload/upload-multiple
# 上传 2-3 张物品照片
# 获得图片 URL 列表
```

3. **获取分类列表**
```bash
GET /api/categories/
# 选择合适的分类 ID
```

4. **发布失物帖子**
```bash
POST /api/posts/
{
  "title": "丢失 iPhone 14 Pro",
  "content": "黑色 iPhone 14 Pro，带透明保护壳...",
  "item_type": "lost",
  "category_id": 1,
  "location": "东门食堂",
  "item_time": "2025-10-21T12:00:00",
  "contact_info": "微信: abc123",
  "images": ["/uploads/images/xxx.jpg"]
}
```

5. **查看智能匹配**
```bash
GET /api/posts/123/matches
# 查看可能的拾到物品帖子
```

---

## 数据库变更说明

### 新增表
- `category`: 物品分类表

### 更新的表
- `post`: 新增字段
  - `item_type`: 物品类型 (lost/found/general)
  - `category_id`: 分类外键
  - `location`: 地点
  - `item_time`: 丢失/拾取时间
  - `contact_info`: 联系方式
  - `images`: 图片列表 (JSON)
  - `is_claimed`: 是否已认领

---

## 预设分类列表

1. 电子产品 (electronics) - 📱
2. 证件卡类 (documents) - 🪪
3. 钥匙 (keys) - 🔑
4. 书籍文具 (books_stationery) - 📚
5. 衣物配饰 (clothing_accessories) - 👔
6. 包袋箱类 (bags) - 🎒
7. 运动器材 (sports_equipment) - ⚽
8. 生活用品 (daily_items) - ☂️
9. 宠物 (pets) - 🐾
10. 其他 (others) - 📦

---

## 注意事项

1. **图片上传**:
   - 必须先登录获取 token
   - 图片会保存在 `backend/uploads/images/` 目录
   - 图片 URL 可通过 `/uploads/images/{filename}` 访问

2. **智能匹配**:
   - 只对 lost 和 found 类型的帖子有效
   - 匹配算法考虑分类、时间、地点三个维度
   - 时间范围可自定义（1-30 天）

3. **数据库**:
   - 使用 SQLite 本地数据库
   - 数据库文件: `backend/lostandfound.db`
   - 首次启动会自动创建表结构

---

## 测试建议

1. 访问 http://localhost:8000/docs 查看完整 API 文档
2. 使用 Swagger UI 进行交互式测试
3. 创建测试账号并发布不同类型的帖子
4. 测试图片上传和智能匹配功能
