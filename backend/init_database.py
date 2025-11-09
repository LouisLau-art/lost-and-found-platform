#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
创建失物招领平台所需的所有数据表结构
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
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"数据库连接失败: {e}")
        sys.exit(1)

# 创建所有数据表
def create_tables(conn):
    print("开始创建数据库表...")
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        phone TEXT,
        name TEXT,
        role TEXT DEFAULT 'student',
        is_admin INTEGER DEFAULT 0,
        credit_score INTEGER DEFAULT 80,
        avatar_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP
    )
    ''')
    print("✅ 创建用户表 (users)")
    
    # 创建分类表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    print("✅ 创建分类表 (categories)")
    
    # 创建帖子表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        author_id INTEGER NOT NULL,
        category_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        post_type TEXT NOT NULL,  -- 'lost' 或 'found'
        location TEXT,
        status TEXT DEFAULT 'active',  -- 'active', 'pending', 'resolved', 'closed'
        image_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (author_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE SET NULL
    )
    ''')
    print("✅ 创建帖子表 (posts)")
    
    # 创建认领表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS claims (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        claimer_id INTEGER NOT NULL,
        reason TEXT NOT NULL,
        status TEXT DEFAULT 'pending',  -- 'pending', 'approved', 'rejected', 'canceled'
        processed_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
        FOREIGN KEY (claimer_id) REFERENCES users (id) ON DELETE CASCADE
    )
    ''')
    print("✅ 创建认领表 (claims)")
    
    # 创建评论表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    ''')
    print("✅ 创建评论表 (comments)")
    
    # 创建通知表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        type TEXT NOT NULL,
        content TEXT NOT NULL,
        is_read INTEGER DEFAULT 0,
        related_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    ''')
    print("✅ 创建通知表 (notifications)")
    
    # 创建信用积分记录表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS credit_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        change_amount INTEGER NOT NULL,
        reason TEXT,
        reference_id INTEGER,
        reference_type TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    ''')
    print("✅ 创建信用积分记录表 (credit_records)")
    
    # 创建索引以提高查询性能
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_author_id ON posts(author_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_category_id ON posts(category_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_post_type ON posts(post_type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_status ON posts(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_claims_post_id ON claims(post_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_claims_claimer_id ON claims(claimer_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_claims_status ON claims(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_comments_post_id ON comments(post_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_comments_user_id ON comments(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_credit_records_user_id ON credit_records(user_id)')
    print("✅ 创建索引")
    
    conn.commit()
    print("\n✅ 所有数据库表创建完成！")

# 插入默认管理员用户
def insert_default_admin(conn):
    print("\n开始创建默认管理员账号...")
    cursor = conn.cursor()
    
    # 检查admin用户是否存在
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
    if cursor.fetchone()[0] == 0:
        # 创建admin用户（密码: admin123）
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, phone, name, is_admin, credit_score, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'admin',
            'admin@example.com',
            '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',  # 密码: admin123
            '13800138000',
            '管理员',
            1,
            100,
            datetime.datetime.now(),
            datetime.datetime.now()
        ))
        conn.commit()
        print("✅ 创建默认管理员账号: admin / admin123")
    else:
        print("ℹ️  管理员账号已存在")

# 主函数
def main():
    print("开始初始化数据库...")
    
    # 连接数据库
    conn = get_db_connection()
    
    try:
        # 创建数据表
        create_tables(conn)
        
        # 创建默认管理员
        insert_default_admin(conn)
        
        print("\n🎉 数据库初始化完成！")
        print("\n数据库信息：")
        print("- 数据库文件: lostandfound.db")
        print("- 管理员账号: admin / admin123")
        print("- 后续可运行 generate_test_data.py 导入测试数据")
        
    except Exception as e:
        print(f"\n❌ 数据库初始化失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    main()
