# 管理员帖子管理功能 - 快速测试指南

## 🚀 快速开始

### 1. 设置管理员账号

**选择一个现有用户设为管理员**:

```bash
cd backend
python -c "
import sys
from io import TextIOWrapper
sys.stdout = TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from sqlmodel import Session, select
from app.database import engine
from app.models.user import User

with Session(engine) as session:
    # 查找用户 (修改为你的邮箱)
    stmt = select(User).where(User.email == 'userA@example.com')
    user = session.exec(stmt).first()
    
    if user:
        user.is_admin = True
        session.add(user)
        session.commit()
        print(f'✅ {user.name} ({user.email}) 已设为管理员')
    else:
        print('❌ 用户不存在')
"
```

或者直接在数据库中执行:
```sql
UPDATE user SET is_admin = 1 WHERE email = 'userA@example.com';
```

### 2. 启动服务

**后端**:
```bash
cd backend
python start.py
# 访问: http://localhost:8000
```

**前端**:
```bash
cd frontend/frontend
npm run dev
# 访问: http://localhost:5173
```

### 3. 测试访问

1. **登录管理员账号**
   - 访问: http://localhost:5173/login
   - 使用设为管理员的账号登录

2. **访问管理员后台**
   
   **方法 A: 从 Dashboard**
   - 登录后自动跳转到 Dashboard
   - 找到"管理员面板"卡片
   - 点击"帖子管理"按钮
   
   **方法 B: 直接访问**
   - 访问: http://localhost:5173/admin/posts

3. **验证功能**
   - ✅ 看到帖子列表表格
   - ✅ 点击"编辑"按钮,弹出编辑对话框
   - ✅ 点击"删除"按钮,弹出确认对话框
   - ✅ 分页功能正常

---

## 🧪 完整测试清单

### 权限测试

#### 测试 1: 管理员访问
- [ ] 以管理员身份登录
- [ ] 访问 `/admin/posts`
- [ ] **预期**: 成功加载帖子列表

#### 测试 2: 普通用户访问
- [ ] 以普通用户身份登录
- [ ] 尝试访问 `/admin/posts`
- [ ] **预期**: 自动重定向到 `/dashboard`

#### 测试 3: 未登录访问
- [ ] 退出登录
- [ ] 尝试访问 `/admin/posts`
- [ ] **预期**: 自动重定向到 `/login`

#### 测试 4: API 权限
- [ ] 使用普通用户的 Token
- [ ] 调用 `GET /api/admin/posts`
- [ ] **预期**: 返回 `403 Forbidden`

---

### 功能测试

#### 测试 5: 帖子列表
- [ ] 以管理员身份访问 `/admin/posts`
- [ ] **验证**:
  - [ ] 表格显示所有帖子
  - [ ] 列包括: ID、标题、作者、类型、状态、认领状态、创建时间、操作
  - [ ] 每行有"编辑"和"删除"按钮

#### 测试 6: 分页功能
- [ ] 如果帖子超过10条
- [ ] **验证**:
  - [ ] 分页组件显示
  - [ ] 可以切换页码
  - [ ] 可以改变每页显示数量

#### 测试 7: 编辑帖子
- [ ] 点击某个帖子的"编辑"按钮
- [ ] **验证**:
  - [ ] 弹出编辑对话框
  - [ ] 表单预填充当前值
  - [ ] 可以修改标题、内容、类型、状态
- [ ] 修改内容后点击"保存"
- [ ] **验证**:
  - [ ] 显示成功提示
  - [ ] 对话框关闭
  - [ ] 表格自动刷新
  - [ ] 修改已生效

#### 测试 8: 删除帖子
- [ ] 点击某个帖子的"删除"按钮
- [ ] **验证**:
  - [ ] 弹出确认对话框
  - [ ] 显示警告文字
- [ ] 点击"确定"
- [ ] **验证**:
  - [ ] 显示成功提示
  - [ ] 表格自动刷新
  - [ ] 帖子状态变为"已删除"

#### 测试 9: 标题链接
- [ ] 点击某个帖子的标题
- [ ] **预期**: 跳转到帖子详情页

---

### UI 测试

#### 测试 10: 深色主题
- [ ] 访问管理员页面
- [ ] **验证**:
  - [ ] 背景是深色渐变
  - [ ] 卡片是深色
  - [ ] 表格是深色
  - [ ] 文字是浅色
  - [ ] 对话框是深色

#### 测试 11: 响应式布局
- [ ] 在不同屏幕尺寸下测试
- [ ] **桌面 (>1024px)**:
  - [ ] 表格所有列正常显示
- [ ] **平板 (768-1024px)**:
  - [ ] 表格可横向滚动
  - [ ] 操作列固定在右侧
- [ ] **手机 (<768px)**:
  - [ ] 导航栏压缩
  - [ ] 表格可横向滚动

#### 测试 12: 加载状态
- [ ] 访问管理员页面时
- [ ] **验证**: 显示加载动画(骨架屏)
- [ ] 删除或编辑时
- [ ] **验证**: 按钮显示加载状态

---

### 错误处理测试

#### 测试 13: 网络错误
- [ ] 关闭后端服务
- [ ] 尝试访问管理员页面
- [ ] **预期**: 显示友好的错误提示

#### 测试 14: 删除不存在的帖子
- [ ] 尝试删除一个已被删除的帖子
- [ ] **预期**: 显示适当的错误消息

#### 测试 15: 编辑冲突
- [ ] 两个管理员同时编辑同一帖子
- [ ] **验证**: 后提交的覆盖前面的(或有冲突提示)

---

## 🎯 快速验证命令

### 测试后端 API

**1. 获取管理员 Token**:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"userA@example.com","password":"password123"}'
```

保存返回的 `access_token`。

**2. 测试获取帖子列表**:
```bash
curl -X GET "http://localhost:8000/api/admin/posts?skip=0&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**预期**: 返回帖子列表 JSON

**3. 测试删除帖子**:
```bash
curl -X DELETE "http://localhost:8000/api/admin/posts/1" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**预期**: 返回成功消息

**4. 测试编辑帖子**:
```bash
curl -X PUT "http://localhost:8000/api/admin/posts/1" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"title":"管理员修改的标题","content":"管理员修改的内容"}'
```

**预期**: 返回更新后的帖子 JSON

**5. 测试非管理员访问**:
```bash
# 使用普通用户的 Token
curl -X GET "http://localhost:8000/api/admin/posts" \
  -H "Authorization: Bearer NORMAL_USER_TOKEN"
```

**预期**: 返回 `403 Forbidden`

---

## 🐛 常见问题排查

### 问题 1: 管理员面板不显示

**原因**: 用户的 `is_admin` 字段未设置

**解决**:
```sql
-- 检查用户是否为管理员
SELECT id, name, email, is_admin FROM user WHERE email = 'your@email.com';

-- 设置为管理员
UPDATE user SET is_admin = 1 WHERE email = 'your@email.com';
```

### 问题 2: 访问 /admin/posts 重定向

**原因**: 路由守卫检测到用户不是管理员

**检查**:
1. 打开浏览器控制台
2. 输入: `JSON.parse(localStorage.getItem('user'))`
3. 检查 `is_admin` 字段是否为 `true`

**解决**: 重新登录或设置 `is_admin`

### 问题 3: API 返回 403 Forbidden

**原因**: Token 对应的用户不是管理员

**检查**:
1. 解码 JWT Token (使用 jwt.io)
2. 查看 `sub` (用户ID)
3. 在数据库中检查该用户的 `is_admin` 字段

### 问题 4: 帖子列表为空

**原因**: 数据库中没有帖子

**解决**:
```bash
cd backend
python generate_test_data.py
```

### 问题 5: 编辑对话框不显示

**原因**: 可能是Vue响应性问题

**解决**:
1. 检查浏览器控制台是否有错误
2. 刷新页面
3. 清除浏览器缓存

---

## ✅ 验收标准

所有以下测试通过即可验收:

- [x] 后端 3 个 API 端点正常工作
- [x] 前端管理员页面正常显示
- [x] 路由守卫正确阻止非管理员
- [x] 编辑功能正常
- [x] 删除功能正常(带确认)
- [x] 分页功能正常
- [x] 深色主题正确应用
- [x] 响应式布局正常
- [x] 加载状态正常
- [x] 错误处理友好

---

## 📊 测试报告模板

```markdown
# 管理员帖子管理功能测试报告

**测试时间**: 2025-10-23
**测试人员**: [你的名字]
**测试环境**: 
- 后端: http://localhost:8000
- 前端: http://localhost:5173
- 浏览器: Chrome 120

## 测试结果

| 测试项 | 状态 | 备注 |
|--------|------|------|
| 管理员访问 | ✅ | 正常 |
| 普通用户访问 | ✅ | 正确重定向 |
| 帖子列表显示 | ✅ | 正常 |
| 编辑功能 | ✅ | 正常 |
| 删除功能 | ✅ | 正常 |
| 分页功能 | ✅ | 正常 |
| 深色主题 | ✅ | 正常 |
| 响应式布局 | ✅ | 正常 |

## 发现的问题

无

## 建议

建议后续添加搜索和筛选功能。

## 总结

所有核心功能正常,可以投入使用。
```

---

**祝测试顺利!** 🎉
