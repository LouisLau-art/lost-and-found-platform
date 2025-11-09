#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库迁移脚本：为users表添加is_admin字段
"""

import os
import sys
import sqlite3
import io

# 设置UTF-8编码环境变量
os.environ["PYTHONIOENCODING"] = "utf-8"

# 配置标准输出为UTF-8
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def get_db_connection(db_path='lostandfound.db'):
    """获取数据库连接"""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        sys.exit(1)

def check_column_exists(conn, table_name, column_name):
    """检查列是否存在"""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns

def add_is_admin_column(conn):
    """为users表添加is_admin字段"""
    print("\n=== 数据库迁移：添加is_admin字段 ===\n")
    
    cursor = conn.cursor()
    
    try:
        # 检查is_admin字段是否已存在
        if check_column_exists(conn, 'users', 'is_admin'):
            print("ℹ️  is_admin 字段已存在，跳过创建")
        else:
            # 添加is_admin字段
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN is_admin INTEGER DEFAULT 0
            """)
            print("✅ 成功添加 is_admin 字段到 users 表")
        
        # 更新admin用户的is_admin字段为1
        cursor.execute("""
            UPDATE users 
            SET is_admin = 1 
            WHERE username = 'admin'
        """)
        affected_rows = cursor.rowcount
        
        if affected_rows > 0:
            print(f"✅ 已将 {affected_rows} 个admin用户的is_admin设置为1")
        else:
            print("⚠️  未找到admin用户，可能需要先运行 init_database.py")
        
        conn.commit()
        
        # 验证迁移结果
        cursor.execute("SELECT username, is_admin FROM users WHERE is_admin = 1")
        admin_users = cursor.fetchall()
        
        print(f"\n📊 当前管理员用户列表:")
        for user in admin_users:
            print(f"   - {user[0]}")
        
        print("\n🎉 数据库迁移完成！")
        
    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        conn.rollback()
        sys.exit(1)

def main():
    """主函数"""
    print("开始数据库迁移...")
    
    # 连接数据库
    conn = get_db_connection()
    
    try:
        # 添加is_admin字段
        add_is_admin_column(conn)
        
        print("\n✅ 所有迁移任务已完成")
        print("\n后续步骤：")
        print("1. 重启后端服务以应用更改")
        print("2. 使用 admin 账号测试管理员权限功能")
        print("3. 验证分类管理和图片删除功能的权限控制")
        
    except Exception as e:
        print(f"\n❌ 数据库迁移过程中发生错误: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    main()
