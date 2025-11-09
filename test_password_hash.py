#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试密码哈希验证
"""
import sqlite3
from passlib.context import CryptContext

def test_password_hash():
    # 使用与后端相同的密码上下文
    pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")
    
    # 从数据库获取管理员密码哈希
    try:
        conn = sqlite3.connect('backend/lostandfound.db')
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE username = 'admin'")
        result = cursor.fetchone()
        conn.close()
        
        if result:
            hashed_password = result[0]
            print(f"获取到的密码哈希: {hashed_password}")
            
            # 测试密码验证
            test_password = "admin123"
            print(f"\n测试密码 '{test_password}' 验证:")
            is_valid = pwd_context.verify(test_password, hashed_password)
            print(f"验证结果: {'✅ 成功' if is_valid else '❌ 失败'}")
            
            # 测试手动生成的哈希
            print("\n生成新的哈希值用于测试:")
            new_hash = pwd_context.hash(test_password)
            print(f"新哈希值: {new_hash}")
            print(f"新哈希长度: {len(new_hash)}")
            print(f"原哈希长度: {len(hashed_password)}")
            
            # 测试新哈希的验证
            is_valid_new = pwd_context.verify(test_password, new_hash)
            print(f"新哈希验证结果: {'✅ 成功' if is_valid_new else '❌ 失败'}")
            
            # 检查算法差异
            if hashed_password.startswith('$2b$'):
                print("\n原哈希使用的是 bcrypt 算法")
            elif hashed_password.startswith('$argon2'):
                print("\n原哈希使用的是 argon2 算法")
            else:
                print(f"\n未知的哈希算法前缀: {hashed_password[:5]}")
                
        else:
            print("未找到管理员用户")
            
    except Exception as e:
        print(f"数据库错误: {e}")

if __name__ == "__main__":
    test_password_hash()