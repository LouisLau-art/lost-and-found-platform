#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
三大任务完成情况验证脚本
验证编码问题修复、SECRET_KEY更新、权限控制实现
"""

import os
import sys
import io
from pathlib import Path

# 设置UTF-8编码
os.environ["PYTHONIOENCODING"] = "utf-8"

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def print_header(title):
    """打印标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def print_result(passed, message):
    """打印测试结果"""
    status = "✅" if passed else "❌"
    print(f"{status} {message}")
    return passed

# 任务1：编码问题修复验证
def verify_encoding_fix():
    """验证编码问题修复"""
    print_header("任务1：编码问题修复验证")
    
    all_passed = True
    root_dir = Path(__file__).parent.parent
    
    # 检查关键文件
    files_to_check = [
        "backend/init_database.py",
        "backend/generate_test_data.py"
    ]
    
    for file_path in files_to_check:
        full_path = root_dir / file_path
        if not full_path.exists():
            all_passed &= print_result(False, f"文件不存在: {file_path}")
            continue
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否包含UTF-8编码设置
        has_pythonioencoding = 'PYTHONIOENCODING' in content
        has_textwrapper = 'TextIOWrapper' in content
        has_utf8_comment = '# -*- coding: utf-8 -*-' in content
        
        if has_pythonioencoding and has_textwrapper and has_utf8_comment:
            all_passed &= print_result(True, f"{file_path}: UTF-8编码配置完整")
        else:
            all_passed &= print_result(False, f"{file_path}: 缺少UTF-8编码配置")
            if not has_pythonioencoding:
                print(f"   ⚠️  缺少: PYTHONIOENCODING环境变量设置")
            if not has_textwrapper:
                print(f"   ⚠️  缺少: TextIOWrapper输出配置")
    
    return all_passed

# 任务2：SECRET_KEY安全更新验证
def verify_secret_key_update():
    """验证SECRET_KEY更新"""
    print_header("任务2：SECRET_KEY安全更新验证")
    
    all_passed = True
    root_dir = Path(__file__).parent.parent
    
    # 检查.env文件
    env_file = root_dir / "backend" / ".env"
    env_example_file = root_dir / "backend" / ".env.example"
    
    if not env_file.exists():
        all_passed &= print_result(False, ".env 文件不存在")
    else:
        with open(env_file, 'r', encoding='utf-8') as f:
            env_content = f.read()
        
        # 检查SECRET_KEY
        if 'SECRET_KEY=' in env_content:
            # 提取SECRET_KEY值
            for line in env_content.split('\n'):
                if line.startswith('SECRET_KEY='):
                    secret_key = line.split('=', 1)[1].strip()
                    
                    # 检查是否为默认值
                    if secret_key == 'your-secret-key-change-in-production':
                        all_passed &= print_result(False, "SECRET_KEY仍为默认值，存在安全风险")
                    elif len(secret_key) < 32:
                        all_passed &= print_result(False, f"SECRET_KEY长度不足 (当前:{len(secret_key)}, 建议:≥32)")
                    else:
                        all_passed &= print_result(True, f"SECRET_KEY已更新 (长度:{len(secret_key)})")
                    break
        else:
            all_passed &= print_result(False, ".env文件中未找到SECRET_KEY配置")
    
    # 检查.env.example文件
    if env_example_file.exists():
        all_passed &= print_result(True, ".env.example 示例文件已创建")
    else:
        all_passed &= print_result(False, ".env.example 示例文件不存在")
    
    # 检查ACCESS_TOKEN_EXPIRE_MINUTES
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            env_content = f.read()
        
        if 'ACCESS_TOKEN_EXPIRE_MINUTES=1440' in env_content:
            all_passed &= print_result(True, "TOKEN过期时间已更新为24小时")
        elif 'ACCESS_TOKEN_EXPIRE_MINUTES=30' in env_content:
            print_result(False, "TOKEN过期时间仍为30分钟（建议改为1440）")
    
    return all_passed

# 任务3：权限控制系统验证
def verify_permission_system():
    """验证权限控制系统"""
    print_header("任务3：权限控制系统实现验证")
    
    all_passed = True
    root_dir = Path(__file__).parent.parent
    
    # 1. 检查User模型中的is_admin字段
    user_model_file = root_dir / "backend" / "app" / "models" / "user.py"
    if user_model_file.exists():
        with open(user_model_file, 'r', encoding='utf-8') as f:
            user_content = f.read()
        
        if 'is_admin' in user_content and 'Field(default=False)' in user_content:
            all_passed &= print_result(True, "User模型: is_admin字段已添加")
        else:
            all_passed &= print_result(False, "User模型: is_admin字段未正确添加")
    else:
        all_passed &= print_result(False, "User模型文件不存在")
    
    # 2. 检查deps.py中的权限依赖函数
    deps_file = root_dir / "backend" / "app" / "core" / "deps.py"
    if deps_file.exists():
        with open(deps_file, 'r', encoding='utf-8') as f:
            deps_content = f.read()
        
        if 'get_current_admin_user' in deps_content:
            all_passed &= print_result(True, "权限依赖: get_current_admin_user函数已创建")
        else:
            all_passed &= print_result(False, "权限依赖: get_current_admin_user函数未创建")
    else:
        all_passed &= print_result(False, "deps.py文件不存在")
    
    # 3. 检查4处TODO权限检查实现
    todo_checks = [
        ("backend/app/api/categories.py", "create_category", "创建分类"),
        ("backend/app/api/categories.py", "update_category", "更新分类"),
        ("backend/app/api/categories.py", "delete_category", "删除分类"),
        ("backend/app/api/upload.py", "delete_image", "删除图片")
    ]
    
    print("\n📋 TODO权限检查实现情况:")
    for file_path, function_name, description in todo_checks:
        full_path = root_dir / file_path
        if not full_path.exists():
            all_passed &= print_result(False, f"{description}: 文件不存在")
            continue
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否使用了get_current_admin_user或权限检查逻辑
        has_admin_check = 'get_current_admin_user' in content or 'is_admin' in content
        has_todo = f'# TODO' in content and function_name in content
        
        if has_admin_check and not (has_todo and '权限检查' in content):
            all_passed &= print_result(True, f"{description}: 权限检查已实现")
        else:
            all_passed &= print_result(False, f"{description}: TODO未完成或权限检查缺失")
    
    # 4. 检查数据库迁移
    print("\n📊 数据库迁移状态:")
    db_file = root_dir / "backend" / "lostandfound.db"
    if db_file.exists():
        import sqlite3
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # 检查users表的is_admin字段
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'is_admin' in columns:
            all_passed &= print_result(True, "数据库: users表is_admin字段已存在")
            
            # 检查是否有管理员用户
            cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = 1")
            admin_count = cursor.fetchone()[0]
            
            if admin_count > 0:
                all_passed &= print_result(True, f"数据库: 已有{admin_count}个管理员用户")
            else:
                all_passed &= print_result(False, "数据库: 未找到管理员用户")
        else:
            all_passed &= print_result(False, "数据库: users表缺少is_admin字段")
        
        conn.close()
    else:
        print_result(False, "数据库文件不存在（可能需要先运行 init_database.py）")
    
    return all_passed

# 生成总结报告
def generate_summary_report(task1_passed, task2_passed, task3_passed):
    """生成总结报告"""
    print_header("📊 任务完成情况总结")
    
    total_tasks = 3
    completed_tasks = sum([task1_passed, task2_passed, task3_passed])
    
    print(f"\n总任务数: {total_tasks}")
    print(f"已完成: {completed_tasks}")
    print(f"未完成: {total_tasks - completed_tasks}")
    print(f"完成率: {completed_tasks/total_tasks*100:.1f}%\n")
    
    print("详细状态:")
    print(f"  {'✅' if task1_passed else '❌'} 任务1: 编码问题修复 - {'完成' if task1_passed else '未完成'}")
    print(f"  {'✅' if task2_passed else '❌'} 任务2: SECRET_KEY安全更新 - {'完成' if task2_passed else '未完成'}")
    print(f"  {'✅' if task3_passed else '❌'} 任务3: 权限控制系统实现 - {'完成' if task3_passed else '未完成'}")
    
    if completed_tasks == total_tasks:
        print("\n🎉 所有任务已完成！系统已准备就绪。")
        print("\n建议的后续步骤:")
        print("  1. 重启后端服务: cd backend && python start_sqlite.py")
        print("  2. 运行完整测试: python system_test.py")
        print("  3. 检查测试仪表板: python tools/test_dashboard_generator.py")
        print("  4. 验证管理员权限功能")
        return True
    else:
        print("\n⚠️  仍有任务未完成，请检查上述错误信息。")
        return False

def main():
    """主函数"""
    print("="*60)
    print("  三大关键任务完成情况验证")
    print("="*60)
    print(f"\n开始时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 执行验证
        task1_passed = verify_encoding_fix()
        task2_passed = verify_secret_key_update()
        task3_passed = verify_permission_system()
        
        # 生成总结报告
        all_passed = generate_summary_report(task1_passed, task2_passed, task3_passed)
        
        print(f"\n完成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        sys.exit(0 if all_passed else 1)
        
    except Exception as e:
        print(f"\n❌ 验证过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
