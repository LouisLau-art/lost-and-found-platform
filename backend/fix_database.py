#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库修复脚本
修复数据库结构不一致问题，并初始化正确的表结构
"""

import os
import sys
import sqlite3
import datetime
import io

# 设置UTF-8编码环境变量
os.environ["PYTHONIOENCODING"] = "utf-8"

# 配置标准输出为UTF-8
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 确保脚本在正确的目录下运行
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 数据库连接函数
def get_db_connection(db_path='lostandfound.db'):
    try:
        # 始终使用与脚本同目录下的数据库文件
        base_dir = os.path.dirname(os.path.abspath(__file__))
        abs_path = db_path if os.path.isabs(db_path) else os.path.join(base_dir, db_path)
        conn = sqlite3.connect(abs_path)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"数据库连接失败: {e}")
        sys.exit(1)

# 检查并修复用户表结构
def fix_users_table(conn):
    print("检查并修复用户表结构...")
    cursor = conn.cursor()
    
    # 检查现有表结构
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    print(f"当前用户表列: {column_names}")
    
    # 检查必要的列是否存在
    required_columns = {
        'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
        'name': 'TEXT',
        'email': 'TEXT UNIQUE',
        'password_hash': 'TEXT',
        'credit_score': 'INTEGER DEFAULT 100',
        'is_active': 'INTEGER DEFAULT 1',
        'is_admin': 'INTEGER DEFAULT 0',
        'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
        'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
    }
    
    # 添加缺失的列
    for column_name, column_def in required_columns.items():
        if column_name not in column_names:
            try:
                if column_name == 'email':
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_def}")
                else:
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_def}")
                print(f"✅ 添加缺失的列: {column_name}")
            except Exception as e:
                print(f"❌ 添加列 {column_name} 失败: {e}")
    
    # 检查并更新现有数据以确保兼容性
    try:
        cursor.execute("UPDATE users SET is_active = 1 WHERE is_active IS NULL")
        cursor.execute("UPDATE users SET credit_score = 100 WHERE credit_score IS NULL")
        print("✅ 更新用户表默认值")
    except Exception as e:
        print(f"❌ 更新用户表默认值失败: {e}")
    
    conn.commit()

# 检查并修复帖子表结构
def fix_posts_table(conn):
    print("检查并修复帖子表结构...")
    cursor = conn.cursor()
    
    # 检查现有表结构
    cursor.execute("PRAGMA table_info(posts)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    print(f"当前帖子表列: {column_names}")
    
    # 检查必要的列是否存在
    required_columns = {
        'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
        'title': 'TEXT',
        'content': 'TEXT',
        'status': 'TEXT DEFAULT "published"',
        'item_type': 'TEXT DEFAULT "general"',
        'location': 'TEXT',
        'item_time': 'TIMESTAMP',
        'contact_info': 'TEXT',
        'images': 'TEXT',  # JSON格式存储图片URL列表
        'is_claimed': 'INTEGER DEFAULT 0',
        'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
        'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
        'author_id': 'INTEGER',
        'category_id': 'INTEGER'
    }
    
    # 添加缺失的列
    for column_name, column_def in required_columns.items():
        if column_name not in column_names:
            try:
                cursor.execute(f"ALTER TABLE posts ADD COLUMN {column_name} {column_def}")
                print(f"✅ 添加缺失的列: {column_name}")
            except Exception as e:
                print(f"❌ 添加列 {column_name} 失败: {e}")
    
    conn.commit()

# 检查并修复认领表结构
def fix_claims_table(conn):
    print("检查并修复认领表结构...")
    cursor = conn.cursor()
    
    # 检查现有表结构
    cursor.execute("PRAGMA table_info(claims)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    print(f"当前认领表列: {column_names}")
    
    # 检查必要的列是否存在
    required_columns = {
        'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
        'status': 'TEXT DEFAULT "pending"',
        'message': 'TEXT',
        'owner_reply': 'TEXT',
        'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
        'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
        'confirmed_at': 'TIMESTAMP',
        'post_id': 'INTEGER',
        'claimer_id': 'INTEGER'
    }
    
    # 添加缺失的列
    for column_name, column_def in required_columns.items():
        if column_name not in column_names:
            try:
                cursor.execute(f"ALTER TABLE claims ADD COLUMN {column_name} {column_def}")
                print(f"✅ 添加缺失的列: {column_name}")
            except Exception as e:
                print(f"❌ 添加列 {column_name} 失败: {e}")
    
    conn.commit()

# 检查并修复分类表结构
def fix_categories_table(conn):
    print("检查并修复分类表结构...")
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(categories)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]

    print(f"当前分类表列: {column_names}")

    required_columns = {
        'name': 'TEXT',
        'name_en': 'TEXT',
        'description': 'TEXT',
        'icon': 'TEXT',
        'is_active': 'INTEGER DEFAULT 1',
        'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
    }

    for column_name, column_def in required_columns.items():
        if column_name not in column_names:
            try:
                cursor.execute(f"ALTER TABLE categories ADD COLUMN {column_name} {column_def}")
                print(f"✅ 添加缺失的列: {column_name}")
            except Exception as e:
                print(f"❌ 添加列 {column_name} 失败: {e}")

    conn.commit()

# 创建索引
def create_indexes(conn):
    print("创建必要的索引...")
    cursor = conn.cursor()
    
    # 用户表索引
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        print("✅ 创建用户邮箱索引")
    except Exception as e:
        print(f"❌ 创建用户邮箱索引失败: {e}")
    
    # 帖子表索引
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_status ON posts(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_item_type ON posts(item_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_is_claimed ON posts(is_claimed)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_category_id ON posts(category_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_author_id ON posts(author_id)")
        print("✅ 创建帖子表索引")
    except Exception as e:
        print(f"❌ 创建帖子表索引失败: {e}")
    
    # 认领表索引
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_claims_status ON claims(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_claims_post_id ON claims(post_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_claims_claimer_id ON claims(claimer_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_claims_created_at ON claims(created_at)")
        print("✅ 创建认领表索引")
    except Exception as e:
        print(f"❌ 创建认领表索引失败: {e}")
    
    conn.commit()

# 插入默认管理员用户
def insert_default_admin(conn):
    print("检查并创建默认管理员账号...")
    cursor = conn.cursor()
    
    # 检查admin用户是否存在
    cursor.execute("SELECT COUNT(*) FROM users WHERE email = 'admin@example.com'")
    if cursor.fetchone()[0] == 0:
        # 创建admin用户（密码: admin123）
        cursor.execute("""
            INSERT INTO users (name, email, password_hash, credit_score, is_active, is_admin, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            '管理员',
            'admin@example.com',
            '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',  # 密码: admin123
            100,
            1,
            1,
            datetime.datetime.now(),
            datetime.datetime.now()
        ))
        conn.commit()
        print("✅ 创建默认管理员账号: admin@example.com / admin123")
    else:
        print("ℹ️  管理员账号已存在")

# 检查数据量并生成测试数据
def check_and_generate_test_data(conn):
    print("检查数据量...")
    cursor = conn.cursor()
    
    # 检查各表数据量
    cursor.execute("SELECT COUNT(*) FROM users")
    users_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM posts")
    posts_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM claims")
    claims_count = cursor.fetchone()[0]
    
    print(f"当前数据量: 用户({users_count}), 帖子({posts_count}), 认领({claims_count})")
    
    # 如果任一表数据量少于10条，生成测试数据
    if users_count < 10 or posts_count < 10 or claims_count < 10:
        print("数据量不足，开始生成测试数据...")
        generate_test_data(conn)
    else:
        print("数据量充足，无需生成测试数据")

# 生成测试数据
def generate_test_data(conn):
    import random
    import string
    from datetime import timedelta
    
    cursor = conn.cursor()
    
    # 生成测试用户
    if cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0] < 10:
        print("生成测试用户...")
        for i in range(20):
            name = f"测试用户{i+1}"
            email = f"user{i+1}@example.com"
            cursor.execute("""
                INSERT OR IGNORE INTO users (name, email, password_hash, credit_score, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                email,
                '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',  # 密码: admin123
                random.randint(60, 100),
                1,
                datetime.datetime.now() - timedelta(days=random.randint(1, 365)),
                datetime.datetime.now()
            ))
        conn.commit()
        print("✅ 生成测试用户完成")
    
    # 生成测试帖子
    if cursor.execute("SELECT COUNT(*) FROM posts").fetchone()[0] < 10:
        print("生成测试帖子...")
        cursor.execute("SELECT id FROM users")
        user_ids = [row[0] for row in cursor.fetchall()]
        
        if not user_ids:
            print("❌ 没有可用用户，无法生成帖子")
            return
            
        locations = ['图书馆', '教学楼A区', '食堂', '宿舍楼', '操场', '实验室']
        item_types = ['lost', 'found', 'general']
        
        for i in range(30):
            title = f"测试帖子 {i+1}"
            content = f"这是一个测试帖子的内容，编号为 {i+1}。" + " " * random.randint(10, 100)
            location = random.choice(locations)
            item_type = random.choice(item_types)
            
            cursor.execute("""
                INSERT INTO posts (title, content, status, item_type, location, is_claimed, author_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                title,
                content,
                'published',
                item_type,
                location,
                0,
                random.choice(user_ids),
                datetime.datetime.now() - timedelta(days=random.randint(1, 30)),
                datetime.datetime.now()
            ))
        conn.commit()
        print("✅ 生成测试帖子完成")
    
    # 生成测试认领
    if cursor.execute("SELECT COUNT(*) FROM claims").fetchone()[0] < 10:
        print("生成测试认领...")
        cursor.execute("SELECT id FROM posts WHERE item_type IN ('lost', 'found')")
        post_ids = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT id FROM users")
        user_ids = [row[0] for row in cursor.fetchall()]
        
        if not post_ids or not user_ids:
            print("❌ 没有可用帖子或用户，无法生成认领")
            return
            
        statuses = ['pending', 'approved', 'rejected']
        
        for i in range(15):
            message = f"认领理由 {i+1}：" + " " * random.randint(10, 50)
            status = random.choice(statuses)
            
            cursor.execute("""
                INSERT INTO claims (status, message, post_id, claimer_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                status,
                message,
                random.choice(post_ids),
                random.choice(user_ids),
                datetime.datetime.now() - timedelta(days=random.randint(1, 15)),
                datetime.datetime.now()
            ))
        conn.commit()
        print("✅ 生成测试认领完成")

# 主函数
def main():
    print("开始修复数据库...")
    
    # 连接数据库
    conn = get_db_connection()
    
    try:
        # 修复各表结构
        fix_users_table(conn)
        fix_posts_table(conn)
        fix_claims_table(conn)
        fix_categories_table(conn)
        
        # 创建索引
        create_indexes(conn)
        
        # 创建默认管理员
        insert_default_admin(conn)
        
        # 检查并生成测试数据
        check_and_generate_test_data(conn)
        
        print("\n🎉 数据库修复完成！")
        print("\n数据库信息：")
        print("- 数据库文件: lostandfound.db")
        print("- 管理员账号: admin@example.com / admin123")
        
    except Exception as e:
        print(f"\n❌ 数据库修复失败: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    main()
