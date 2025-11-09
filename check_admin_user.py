#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查数据库中的管理员用户信息
"""
import sqlite3
import os

db_path = os.path.join('backend', 'lostandfound.db')

def check_admin_user():
    print(f"检查数据库: {db_path}")
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查询所有用户表结构
        print("\n用户表结构:")
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} - {col[2]}")
        
        # 查询管理员用户信息
        print("\n管理员用户信息:")
        cursor.execute("SELECT * FROM users WHERE username = 'admin' OR email LIKE '%admin%'")
        admin_users = cursor.fetchall()
        
        if admin_users:
            print(f"找到 {len(admin_users)} 个管理员用户")
            
            # 获取列名
            column_names = [desc[0] for desc in cursor.description]
            
            for i, user in enumerate(admin_users):
                print(f"\n管理员 #{i+1}:")
                for j, value in enumerate(user):
                    # 不显示完整的密码哈希，只显示前20个字符
                    if column_names[j] == 'password_hash' and value:
                        value = value[:20] + "..."
                    print(f"  {column_names[j]}: {value}")
        else:
            print("未找到管理员用户")
            
            # 显示所有用户的基本信息
            print("\n所有用户列表:")
            cursor.execute("SELECT id, username, email, is_admin FROM users LIMIT 10")
            users = cursor.fetchall()
            for user in users:
                print(f"  ID: {user[0]}, 用户名: {user[1]}, 邮箱: {user[2]}, 管理员: {user[3]}")
        
        conn.close()
        
    except Exception as e:
        print(f"数据库操作错误: {e}")

if __name__ == "__main__":
    check_admin_user()