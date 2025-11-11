# 校园失物招领平台 (Campus Lost & Found Platform)

[![Vue.js](https://img.shields.io/badge/Vue.js-4FC08D?style=flat&logo=vuedotjs&logoColor=white)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Element Plus](https://img.shields.io/badge/Element%20Plus-409EFF?style=flat&logo=element&logoColor=white)](https://element-plus.org/)

一个基于现代Web技术栈构建的智能校园失物招领平台，提供高效的物品匹配、用户交互和社区功能。

## 📌 项目概述

本项目是一个面向校园环境的失物招领平台，旨在通过技术手段提高失物招领的效率和用户体验。平台采用前后端分离架构，后端基于Python FastAPI框架，前端使用Vue 3构建，数据库采用SQLite（开发环境）和PostgreSQL（生产环境）。

## ✨ 主要功能

### 核心功能
- **用户认证**：支持邮箱/密码注册与登录，JWT令牌认证
- **用户管理**：个人资料管理、通知系统和信用评分系统
- **社区论坛**：发布帖子、评论互动、点赞收藏
- **实时通知**：评论、认领状态变更等实时提醒
- **响应式设计**：适配桌面和移动端的现代化UI界面

### 失物招领特色功能
- **智能分类**：支持多种物品分类（电子设备、证件、钥匙等）
- **智能匹配**：基于内容的推荐系统，自动匹配失物与招领信息
- **多图上传**：支持多张图片上传，展示物品详情
- **高级搜索**：按分类、地点、时间、状态等多维度筛选
- **认领系统**：完整的认领流程，包括申请、审核、确认
- **互评系统**：物品所有人与认领人之间的相互评价
- **信用积分**：基于用户行为的信用评分系统
- **详细信息**：记录物品位置、时间、联系方式等关键信息

## 🚀 技术栈

### 后端技术
- **FastAPI**：高性能Python Web框架，自动生成API文档
- **SQLModel**：结合SQLAlchemy和Pydantic的类型安全ORM
- **SQLite/PostgreSQL**：轻量级文件数据库/企业级关系型数据库
- **JWT**：基于JSON Web Token的认证机制
- **Alembic**：数据库迁移工具
- **Uvicorn**：ASGI服务器，支持异步请求处理
- **Scikit-learn**：用于智能匹配算法
- **Python-Levenshtein**：字符串相似度计算

### 前端技术
- **Vue 3**：渐进式JavaScript框架，采用Composition API
- **Pinia**：Vue的现代化状态管理库
- **Vue Router**：Vue.js官方路由管理器
- **Axios**：基于Promise的HTTP客户端
- **Element Plus**：基于Vue 3的桌面端组件库
- **Tailwind CSS**：实用优先的CSS框架
- **Vite**：下一代前端构建工具
- **Day.js**：轻量级日期处理库

## 📁 项目结构

```
lost-and-found-platform/
├── backend/                 # 后端代码
│   ├── app/                # 应用主目录
│   │   ├── api/            # API路由
│   │   │   ├── v1/         # API版本1
│   │   │   └── deps.py     # 依赖注入
│   │   ├── core/           # 核心功能
│   │   │   ├── config.py   # 配置管理
│   │   │   └── security.py # 安全相关
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic模型
│   │   └── services/       # 业务逻辑
│   ├── tests/              # 测试代码
│   ├── alembic/            # 数据库迁移
│   ├── scripts/            # 实用脚本
│   ├── requirements.txt     # Python依赖
│   └── start.py            # 启动脚本
│
└── frontend/               # 前端代码
    └── frontend/           # Vue项目
        ├── public/         # 静态资源
        └── src/
            ├── api/        # API请求
            ├── assets/     # 资源文件
            ├── components/ # 公共组件
            ├── router/     # 路由配置
            ├── stores/     # Pinia状态管理
            ├── utils/      # 工具函数
            └── views/      # 页面组件
```

## 🔄 最近更新

### 前端优化 (2024-01-15)
- 统一使用`content-wrapper`包装主要视图，确保一致的页面布局
- 创建`message`工具函数，统一管理消息提示
- 优化通知中心，使用`router-link`实现页面跳转
- 修复了多个视图中的消息提示和布局问题

### 数据库优化 (2024-01-10)
- 优化了数据库查询性能
- 添加了数据库备份和恢复脚本
- 修复了数据一致性问题

## 🚧 开发进展

### 已完成功能
- [x] 用户认证（注册、登录、JWT）
- [x] 物品发布与管理
- [x] 图片上传与展示
- [x] 认领流程实现
- [x] 用户评价系统
- [x] 通知系统
- [x] 响应式布局

### 进行中
- [ ] 智能推荐算法优化
- [ ] 后台管理系统
- [ ] 数据统计与分析
- [ ] 多语言支持

## 🛠️ 开发指南

### 环境要求
- Python 3.9+
- Node.js 18+
- SQLite/PostgreSQL

### 快速开始

1. **克隆仓库**
   ```bash
   git clone https://github.com/yourusername/lost-and-found-platform.git
   cd lost-and-found-platform
   ```

2. **后端设置**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或 venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

3. **前端设置**
   ```bash
   cd ../frontend/frontend
   npm install
   ```

4. **启动开发服务器**
   ```bash
   # 启动后端
   cd ../../backend
   uvicorn app.main:app --reload
   
   # 启动前端 (新终端)
   cd ../frontend/frontend
   npm run dev
   ```

5. 访问 `http://localhost:5173`

## 🤝 贡献指南

欢迎提交Issue和Pull Request。请确保：
1. 遵循项目的代码风格
2. 添加适当的测试
3. 更新相关文档

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)

## 📞 联系方式

如有任何问题或建议，请通过以下方式联系我们：
- 邮箱：your.email@example.com
- GitHub Issues: [提交问题](https://github.com/yourusername/lost-and-found-platform/issues)

### Core Features
- **User Authentication**: Email/password registration and login with JWT tokens
- **User Management**: Profile management, notifications, and credit scoring system
- **Community Forum**: Create posts, comment on posts, and engage with the community
- **Real-time Notifications**: Get notified about comments and other activities
- **Responsive Design**: Modern, mobile-friendly UI built with Tailwind CSS

### Lost & Found Features ✨
- **Item Categories**: Organize lost and found items by category (electronics, documents, keys, etc.)
- **Smart Matching**: Intelligent recommendation system to match lost and found items
- **Image Upload**: Support multiple image uploads for item posts
- **Advanced Search**: Filter by category, location, time, and claimed status
- **Claim System**: Complete claim workflow with approval/rejection
- **Rating System**: Mutual rating between item owners and claimers
- **Credit Score**: Automatic credit score updates based on ratings
- **Detailed Information**: Track item location, time, and contact information

## Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLModel**: Type-safe ORM that combines SQLAlchemy and Pydantic
- **PostgreSQL**: Robust, open-source relational database
- **JWT**: Secure authentication with JSON Web Tokens
- **Alembic**: Database migration tool

### Frontend
- **Vue 3**: Progressive JavaScript framework with Composition API
- **Pinia**: State management for Vue applications
- **Vue Router**: Official router for Vue.js
- **Axios**: HTTP client for API communication
- **Tailwind CSS**: Utility-first CSS framework

## Project Structure

```
lost-and-found-platform/
├── backend/
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── core/          # Core functionality (security, config)
│   │   ├── models/        # SQLModel database models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── database.py    # Database configuration
│   │   └── main.py        # FastAPI application
│   ├── requirements.txt   # Python dependencies
│   └── start.py          # Startup script
├── frontend/
│   └── frontend/
│       ├── src/
│       │   ├── api/       # API client configuration
│       │   ├── components/ # Vue components
│       │   ├── stores/    # Pinia stores
│       │   ├── views/     # Vue pages
│       │   └── router/    # Vue Router configuration
│       └── package.json   # Node.js dependencies
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. Start the backend server:
   ```bash
   python start.py
   ```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:5173`

### Create an Admin User

To create an administrator account for the platform:

```bash
cd backend
python create_admin.py
```

The script will interactively prompt you for:
- Username
- Full Name  
- Email
- Password (with confirmation)

The created user will have admin privileges and can access the admin panel at `/admin`.

### Seed the Database with Test Data

To quickly populate the database with realistic test data (users, posts, claims, comments, ratings):

1. **BACKUP YOUR DATABASE FIRST** (optional but recommended):
   ```bash
   cd backend
   ./backup_database.sh
   ```

2. Ensure backend dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the seeding script:
   ```bash
   python seed_database.py
   # Type 'yes' when prompted to confirm
   ```

**⚠️ WARNING:** This script is DESTRUCTIVE and will:
- Delete ALL existing data (users, posts, claims, comments, etc.)
- Create fresh test data with Faker
- Create a default admin account (`admin@example.com` / `admin123`)

Notes:
- The script requires typing 'yes' to proceed as a safety measure
- Uses the DATABASE_URL from environment or falls back to SQLite
- Creates ~20 users, ~50 posts, ~30 claims, and related data

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user info

### Users
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update user profile
- `GET /api/users/notifications` - Get user notifications
- `PUT /api/users/notifications/{id}/read` - Mark notification as read

### Categories
- `GET /api/categories/` - List all categories
- `GET /api/categories/{id}` - Get category detail

### Posts (Lost & Found)
- `GET /api/posts` - List posts (with filtering)
- `POST /api/posts` - Create post
- `GET /api/posts/{id}` - Get post detail
- `PUT /api/posts/{id}` - Update post
- `DELETE /api/posts/{id}` - Delete post
- `GET /api/posts/{id}/matches` - Get smart matches for a post
- `GET /api/posts/search/advanced` - Advanced search
- `POST /api/posts/{id}/comments` - Add comment
- `GET /api/posts/{id}/comments` - List comments
- `DELETE /api/posts/comments/{id}` - Delete comment

### Claims ✨
- `POST /api/claims/` - Create claim request
- `GET /api/claims/my-claims` - Get my claim requests
- `GET /api/claims/post/{id}` - Get claims for a post
- `POST /api/claims/{id}/approve` - Approve a claim
- `POST /api/claims/{id}/reject` - Reject a claim
- `DELETE /api/claims/{id}` - Cancel a claim

### Ratings ✨
- `POST /api/ratings/` - Create rating
- `GET /api/ratings/claim/{id}` - Get ratings for a claim
- `GET /api/ratings/user/{id}/received` - Get ratings received by user

### Users ✨
- `GET /api/users/{id}` - Get user public information
- `GET /api/users/{id}/posts` - Get user's posts
- `GET /api/users/{id}/ratings` - Get user's ratings

### Upload
- `POST /api/upload/upload` - Upload single image
- `POST /api/upload/upload-multiple` - Upload multiple images
- `DELETE /api/upload/{filename}` - Delete image

## Database Schema

The application uses the following main entities:

- **Users**: User accounts with authentication, profile information, and credit scores
- **Categories**: Item categories (electronics, documents, keys, books, etc.)
- **Posts**: Forum posts with lost/found item information
- **Comments**: Comments on posts
- **Notifications**: System notifications for users
- **Claims** ✨: Claim requests for lost and found items
- **Ratings** ✨: User ratings after successful claims

## Admin Setup

To create an administrator account, run the admin creation script:

```bash
cd backend
source .venv/bin/activate  # Activate virtual environment
python3 create_admin.py
```

The script will prompt you to enter:
- Username
- Full Name
- Email
- Password (minimum 6 characters)

Once created, you can login with these credentials and access admin features including:
- User management (`/admin/users`)
- Post moderation (`/admin/posts`)
- System-wide content management

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend/frontend
npm run test
```

### Database Migrations

```bash
cd backend
alembic upgrade head
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Documentation

- **[Claim System Complete Guide](./docs/features/claim/CLAIM_SYSTEM_COMPLETE.md)** - Complete implementation report of the claim system
- **[User Profile Feature](./docs/features/user-profile/USER_PROFILE_COMPLETE.md)** - User profile and rating display feature
- **[Testing Checklist](./docs/testing/TESTING_CHECKLIST.md)** - Comprehensive testing guide
- **[Development Summary](./docs/reports/DEVELOPMENT_SUMMARY.md)** - Development completion summary

## Current Status

### Completed Features (≈ 90%)
- ✅ User authentication and authorization
- ✅ User profile management
- ✅ Forum system with posts and comments
- ✅ Notification system
- ✅ Item categories
- ✅ Image upload (single and multiple)
- ✅ Advanced search and filtering
- ✅ Smart matching algorithm
- ✅ **Claim system** (NEW)
- ✅ **Rating system** (NEW)
- ✅ **Credit score system** (NEW)
- ✅ **User profile page** (NEW) ✨

### Optional Enhancements
- ⚠️ Admin dashboard
- ⚠️ Real-time messaging
- ⚠️ Email notifications
- ⚠️ Data analytics and reports

## License

This project is licensed under the MIT License.

