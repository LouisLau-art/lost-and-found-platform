#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
重置管理员密码脚本
"""
import sqlite3
from passlib.context import CryptContext

def reset_admin_password():
    print("重置管理员密码...")
    
    # 使用与后端相同的密码上下文
    pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")
    
    # 新密码
    new_password = "admin123"
    print(f"新密码: {new_password}")
    
    # 确保密码被正确截断（bcrypt限制72字节）
    if len(new_password.encode('utf-8')) > 72:
        new_password = new_password.encode('utf-8')[:72].decode('utf-8', 'ignore')
        print(f"密码已截断: {new_password}")
    
    # 生成新的哈希值
    new_hash = pwd_context.hash(new_password)
    print(f"生成的新哈希值: {new_hash}")
    print(f"哈希长度: {len(new_hash)}")
    
    # 更新数据库中的管理员密码
    try:
        conn = sqlite3.connect('backend/lostandfound.db')
        cursor = conn.cursor()
        
        # 更新管理员密码
        cursor.execute(
            "UPDATE users SET password_hash = ? WHERE username = 'admin'",
            (new_hash,)
        )
        conn.commit()
        
        # 验证更新
        cursor.execute(
            "SELECT COUNT(*) FROM users WHERE username = 'admin' AND password_hash = ?",
            (new_hash,)
        )
        count = cursor.fetchone()[0]
        
        if count > 0:
            print("\n✅ 管理员密码更新成功!")
            
            # 测试新密码验证
            print("\n测试新密码验证:")
            cursor.execute("SELECT password_hash FROM users WHERE username = 'admin'")
            stored_hash = cursor.fetchone()[0]
            is_valid = pwd_context.verify(new_password, stored_hash)
            print(f"验证结果: {'✅ 成功' if is_valid else '❌ 失败'}")
        else:
            print("\n❌ 管理员密码更新失败!")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ 数据库操作错误: {e}")

if __name__ == "__main__":
    reset_admin_password()