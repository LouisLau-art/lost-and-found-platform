#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
详细的登录调试脚本
"""
import sqlite3
import requests
import json

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/auth/login"

def check_database_admin():
    print("=== 检查数据库中的管理员信息 ===")
    
    try:
        conn = sqlite3.connect('backend/lostandfound.db')
        cursor = conn.cursor()
        
        # 获取管理员用户的所有信息
        cursor.execute("SELECT * FROM users WHERE username = 'admin' OR email LIKE '%admin%'")
        admin_users = cursor.fetchall()
        
        # 获取所有列名
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        print(f"找到 {len(admin_users)} 个匹配的管理员用户")
        
        for i, user in enumerate(admin_users):
            print(f"\n用户 #{i+1}:")
            for col, val in zip(columns, user):
                # 对于敏感信息，只显示部分
                if col == 'password_hash':
                    print(f"  {col}: {val[:20]}...")
                else:
                    print(f"  {col}: {val}")
                    # 特别注意email字段的精确值
                    if col == 'email':
                        print(f"  email长度: {len(val)}")
                        print(f"  email类型: {type(val)}")
                        print(f"  email转义表示: {repr(val)}")
        
        conn.close()
        
    except Exception as e:
        print(f"数据库错误: {e}")

def test_different_email_formats():
    print("\n=== 测试不同的email格式 ===")
    
    # 要测试的各种email格式
    test_emails = [
        "admin@example.com",
        "ADMIN@EXAMPLE.COM",  # 大写
        "admin@example.com ",  # 尾部空格
        " admin@example.com",  # 头部空格
        "admin@example.com\n",  # 换行符
        "admin123@example.com"   # 错误email
    ]
    
    password = "admin123"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    for email in test_emails:
        data = {"email": email, "password": password}
        print(f"\n测试email: {repr(email)}")
        
        try:
            response = requests.post(
                LOGIN_URL,
                json=data,
                headers=headers,
                timeout=10
            )
            print(f"  状态码: {response.status_code}")
            print(f"  响应: {response.text}")
        except Exception as e:
            print(f"  请求错误: {e}")

def test_manual_direct_query():
    print("\n=== 直接在数据库中验证查询条件 ===")
    
    try:
        conn = sqlite3.connect('backend/lostandfound.db')
        cursor = conn.cursor()
        
        # 模拟登录API中的查询
        test_emails = ["admin@example.com", "ADMIN@EXAMPLE.COM"]
        
        for email in test_emails:
            print(f"\n查询email: {repr(email)}")
            cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?", (email,))
            count = cursor.fetchone()[0]
            print(f"  精确匹配结果: {count} 个用户")
            
            # 测试大小写不敏感的查询
            cursor.execute("SELECT COUNT(*) FROM users WHERE LOWER(email) = LOWER(?)", (email,))
            count_lower = cursor.fetchone()[0]
            print(f"  大小写不敏感匹配结果: {count_lower} 个用户")
        
        conn.close()
        
    except Exception as e:
        print(f"数据库错误: {e}")

if __name__ == "__main__":
    check_database_admin()
    test_different_email_formats()
    test_manual_direct_query()