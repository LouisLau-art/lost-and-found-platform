#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Lost and Found Platform System Test Script
Includes database preparation, system startup and functional testing phases
"""
import sys

import os
import sys
import time
import json
import sqlite3
import requests
import subprocess
import datetime
import logging
import io
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

# Configure logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("system_test.log", encoding="utf-8"),
        logging.StreamHandler(io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8'))
    ]
)
logger = logging.getLogger(__name__)

# Global configuration
BASE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = BASE_DIR / "backend"
FRONTEND_DIR = BASE_DIR / "frontend" / "frontend"
DB_PATH = BACKEND_DIR / "lostandfound.db"
API_BASE_URL = "http://localhost:8000"
TEST_REPORT_PATH = BASE_DIR / "test_report.md"

# Set environment variable for UTF-8 encoding
os.environ["PYTHONIOENCODING"] = "utf-8"

# 测试数据
TEST_USER = {"username": "testuser", "password": "admin123"}
TEST_ADMIN = {"username": "admin", "password": "admin123"}

# 测试结果统计
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "errors": [],
    "performance": []
}

# 辅助函数
def get_db_connection():
    """获取数据库连接"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        sys.exit(1)

def run_command(cmd, cwd=None, shell=True):
    """运行命令并返回输出"""
    try:
        result = subprocess.run(
            cmd, 
            cwd=cwd, 
            shell=shell, 
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Command execution failed: {e}")
        logger.error(f"Error output: {e.stderr}")
        return None

def api_request(method, endpoint, data=None, token=None, expected_status=200):
    """发送API请求并记录性能"""
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    url = f"{API_BASE_URL}{endpoint}"
    start_time = time.time()
    
    try:
        if method.lower() == "get":
            response = requests.get(url, headers=headers)
        elif method.lower() == "post":
            response = requests.post(url, json=data, headers=headers)
        elif method.lower() == "put":
            response = requests.put(url, json=data, headers=headers)
        elif method.lower() == "delete":
            response = requests.delete(url, headers=headers)
        else:
            logger.error(f"不支持的HTTP方法: {method}")
            return None
        
        elapsed_time = time.time() - start_time
        test_results["performance"].append({
            "endpoint": endpoint,
            "method": method,
            "status_code": response.status_code,
            "response_time": elapsed_time
        })
        
        if response.status_code != expected_status:
            logger.warning(f"API请求状态码不匹配: 预期 {expected_status}, 实际 {response.status_code}")
            logger.warning(f"响应内容: {response.text}")
        
        return response
    except Exception as e:
        logger.error(f"API请求失败: {e}")
        return None

def login_user(username, password):
    """登录用户并返回token"""
    # 管理员用户使用固定邮箱格式
    email = "admin@example.com" if username == "admin" else f"{username}@example.com"
    response = api_request(
        "post", 
        "/api/auth/login", 
        data={"email": email, "password": password}
    )
    if response and response.status_code == 200:
        return response.json().get("access_token")
    return None

def run_test(test_name, test_func, *args, **kwargs):
    """运行测试并记录结果"""
    logger.info(f"开始测试: {test_name}")
    test_results["total"] += 1
    
    try:
        start_time = time.time()
        result = test_func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        
        if result:
            logger.info(f"测试通过: {test_name} (耗时: {elapsed_time:.2f}秒)")
            test_results["passed"] += 1
        else:
            logger.error(f"测试失败: {test_name} (耗时: {elapsed_time:.2f}秒)")
            test_results["failed"] += 1
            test_results["errors"].append({
                "test": test_name,
                "error": "测试断言失败"
            })
        
        return result
    except Exception as e:
        logger.error(f"测试出错: {test_name} - {str(e)}")
        test_results["failed"] += 1
        test_results["errors"].append({
            "test": test_name,
            "error": str(e)
        })
        return False

# 阶段1: 数据库准备
def prepare_database():
    """准备测试数据库"""
    logger.info("=== 阶段1: 数据库准备 ===")
    
    # 终止占用8000端口的进程
    try:
        netstat_output = subprocess.check_output("netstat -ano | findstr :8000", shell=True, text=True)
        for line in netstat_output.splitlines():
            if "LISTENING" in line:
                parts = line.split()
                pid = parts[-1]
                subprocess.run(f"taskkill /PID {pid} /F", shell=True)
                logger.info(f"已终止占用端口的进程: PID={pid}")
    except subprocess.CalledProcessError:
        logger.info("无占用8000端口的进程")
    
    # 检查数据库文件是否存在，如果存在则备份
    if DB_PATH.exists():
        backup_path = DB_PATH.with_suffix('.db.bak')
        # 如果备份文件已存在，先删除它
        if backup_path.exists():
            backup_path.unlink()
        DB_PATH.rename(backup_path)
        logger.info(f"已备份原数据库到 {backup_path}")
    
    # 初始化数据库
    logger.info("初始化数据库...")
    output = run_command("python init_database.py", cwd=BACKEND_DIR)
    if output is None:
        logger.error("数据库初始化失败")
        return False
    
    # 生成测试数据
    logger.info("生成测试数据...")
    output = run_command("python generate_test_data.py", cwd=BACKEND_DIR)
    if output is None:
        logger.error("测试数据生成失败")
        return False
    
    # 验证数据是否正确导入
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查用户表
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    logger.info(f"用户表记录数: {user_count}")
    
    # 检查帖子表
    cursor.execute("SELECT COUNT(*) FROM posts")
    post_count = cursor.fetchone()[0]
    logger.info(f"帖子表记录数: {post_count}")
    
    # 检查认领表
    cursor.execute("SELECT COUNT(*) FROM claims")
    claim_count = cursor.fetchone()[0]
    logger.info(f"认领表记录数: {claim_count}")
    
    conn.close()
    
    return user_count > 0 and post_count > 0

# 阶段2: 系统启动
def start_system():
    """启动系统服务"""
    logger.info("=== 阶段2: 系统启动 ===")
    
    # 启动后端服务
    logger.info("启动后端服务...")
    backend_process = subprocess.Popen(
        "python start_sqlite.py", 
        cwd=BACKEND_DIR,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # 等待后端服务启动
    time.sleep(5)
    
    # 检查后端服务是否正常运行
    try:
        response = requests.get(f"{API_BASE_URL}/docs")
        if response.status_code == 200:
            logger.info("后端服务启动成功")
        else:
            logger.error(f"后端服务状态异常: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"后端服务连接失败: {e}")
        return False
    
    return True

# 阶段3: 功能测试
def test_crud_operations():
    """测试CRUD操作"""
    logger.info("=== 阶段3: 功能测试 - CRUD操作 ===")
    
    # 登录获取token
    admin_token = login_user(TEST_ADMIN["username"], TEST_ADMIN["password"])
    if not admin_token:
        logger.error("管理员登录失败，无法继续测试")
        return False
    
    # 测试用例1: 创建帖子(Create)
    def test_create_post():
        new_post = {
            "title": "测试帖子",
            "description": "这是一个测试帖子",
            "post_type": "lost",
            "category_id": 1,
            "location": "图书馆"
        }
        
        response = api_request(
            "post", 
            "/api/posts/", 
            data=new_post,
            token=admin_token,
            expected_status=201
        )
        
        if not response or response.status_code != 201:
            return False
        
        post_id = response.json().get("id")
        return post_id is not None
    
    # 测试用例2: 读取帖子(Read)
    def test_read_posts():
        # 测试获取帖子列表
        response = api_request("get", "/api/posts/")
        if not response or response.status_code != 200:
            return False
        
        posts = response.json()
        if not isinstance(posts, list) or len(posts) == 0:
            return False
        
        # 测试获取单个帖子
        post_id = posts[0].get("id")
        response = api_request("get", f"/api/posts/{post_id}")
        
        if not response or response.status_code != 200:
            return False
        
        post = response.json()
        return post.get("id") == post_id
    
    # 测试用例3: 更新帖子(Update)
    def test_update_post():
        # 先获取一个帖子
        response = api_request("get", "/api/posts/")
        if not response or response.status_code != 200:
            return False
        
        posts = response.json()
        if not isinstance(posts, list) or len(posts) == 0:
            return False
        
        # 找到管理员创建的帖子
        admin_post = None
        for post in posts:
            author = post.get("author", {})
            if author.get("username") == TEST_ADMIN["username"]:
                admin_post = post
                break
        
        if not admin_post:
            logger.warning("未找到管理员创建的帖子，无法测试更新")
            return False
        
        post_id = admin_post.get("id")
        update_data = {
            "title": f"更新的帖子 {datetime.datetime.now()}",
            "description": "这是更新后的描述"
        }
        
        response = api_request(
            "put", 
            f"/api/posts/{post_id}", 
            data=update_data,
            token=admin_token
        )
        
        if not response or response.status_code != 200:
            return False
        
        # 验证更新是否成功
        response = api_request("get", f"/api/posts/{post_id}")
        if not response or response.status_code != 200:
            return False
        
        updated_post = response.json()
        return updated_post.get("title") == update_data["title"]
    
    # 测试用例4: 删除帖子(Delete)
    def test_delete_post():
        # 创建一个新帖子用于删除
        new_post = {
            "title": "待删除帖子",
            "description": "这个帖子将被删除",
            "post_type": "lost",
            "category_id": 1,
            "location": "食堂"
        }
        
        response = api_request(
            "post", 
            "/api/posts/", 
            data=new_post,
            token=admin_token,
            expected_status=201
        )
        
        if not response or response.status_code != 201:
            return False
        
        post_id = response.json().get("id")
        
        # 删除帖子
        response = api_request(
            "delete", 
            f"/api/posts/{post_id}", 
            token=admin_token
        )
        
        if not response or response.status_code != 200:
            return False
        
        # 验证删除是否成功
        response = api_request(
            "get", 
            f"/api/posts/{post_id}", 
            expected_status=404
        )
        
        return response and response.status_code == 404
    
    # 运行CRUD测试
    create_result = run_test("创建帖子", test_create_post)
    read_result = run_test("读取帖子", test_read_posts)
    update_result = run_test("更新帖子", test_update_post)
    delete_result = run_test("删除帖子", test_delete_post)
    
    return create_result and read_result and update_result and delete_result

def test_claim_flow():
    """测试认领流程"""
    logger.info("=== 阶段3: 功能测试 - 认领流程 ===")
    
    # 登录两个用户
    admin_token = login_user(TEST_ADMIN["username"], TEST_ADMIN["password"])
    if not admin_token:
        logger.error("管理员登录失败，无法继续测试")
        return False
    
    # 创建一个测试用户
    test_user_data = {
        "username": f"testuser_{int(time.time())}",
        "password": "testpass123",
        "email": f"test{int(time.time())}@example.com",
        "name": "测试用户",
        "phone": "13800138000"
    }
    
    # 注册测试用户
    response = api_request(
        "post", 
        "/api/auth/register", 
        data=test_user_data
    )
    
    if not response or response.status_code != 201:
        logger.error("创建测试用户失败")
        return False
    
    # 登录测试用户
    test_token = login_user(test_user_data["username"], test_user_data["password"])
    if not test_token:
        logger.error("测试用户登录失败")
        return False
    
    # 测试用例1: 管理员创建帖子
    new_post = {
        "title": "测试认领流程帖子",
        "description": "这是用于测试认领流程的帖子",
        "post_type": "found",
        "category_id": 1,
        "location": "图书馆"
    }
    
    response = api_request(
        "post", 
        "/api/posts/", 
        data=new_post,
        token=admin_token,
        expected_status=201
    )
    
    if not response or response.status_code != 201:
        logger.error("创建测试帖子失败")
        return False
    
    post_id = response.json().get("id")
    
    # 测试用例2: 测试用户提交认领请求
    claim_data = {
        "post_id": post_id,
        "reason": "这是我的物品，我可以描述它的特征"
    }
    
    response = api_request(
        "post", 
        "/api/claims/", 
        data=claim_data,
        token=test_token,
        expected_status=201
    )
    
    if not response or response.status_code != 201:
        logger.error("提交认领请求失败")
        return False
    
    claim_id = response.json().get("id")
    
    # 测试用例3: 管理员查看认领请求
    response = api_request(
        "get", 
        f"/api/claims/post/{post_id}", 
        token=admin_token
    )
    
    if not response or response.status_code != 200:
        logger.error("查看认领请求失败")
        return False
    
    claims = response.json()
    if not isinstance(claims, list) or len(claims) == 0:
        logger.error("未找到认领请求")
        return False
    
    # 测试用例4: 管理员批准认领请求
    response = api_request(
        "put", 
        f"/api/claims/{claim_id}/approve", 
        data={"message": "认领已批准，请联系我领取"},
        token=admin_token
    )
    
    if not response or response.status_code != 200:
        logger.error("批准认领请求失败")
        return False
    
    # 测试用例5: 验证帖子状态已更新
    response = api_request("get", f"/api/posts/{post_id}")
    if not response or response.status_code != 200:
        logger.error("获取帖子信息失败")
        return False
    
    post = response.json()
    if post.get("status") != "resolved":
        logger.error(f"帖子状态未更新为resolved，当前状态: {post.get('status')}")
        return False
    
    return True

# 生成测试报告
def generate_test_report():
    """生成测试报告"""
    logger.info("=== 生成测试报告 ===")
    
    report = f"""# 失物招领平台系统测试报告

## 测试概述

- **测试时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **测试环境**: 本地开发环境
- **测试数据**: 随机生成的测试数据，包含正常值、边界值和异常值

## 测试结果统计

- **总测试用例**: {test_results['total']}
- **通过**: {test_results['passed']} ({test_results['passed']/test_results['total']*100 if test_results['total'] > 0 else 0:.2f}%)
- **失败**: {test_results['failed']}
- **跳过**: {test_results['skipped']}

## 性能指标

| 接口 | 方法 | 状态码 | 响应时间(秒) |
|------|------|--------|------------|
"""
    
    for perf in test_results["performance"]:
        report += f"| {perf['endpoint']} | {perf['method']} | {perf['status_code']} | {perf['response_time']:.4f} |\n"
    
    report += """
## 测试失败详情

"""
    
    if test_results["errors"]:
        for error in test_results["errors"]:
            report += f"- **{error['test']}**: {error['error']}\n"
    else:
        report += "- 无测试失败\n"
    
    report += """
## 测试覆盖范围

1. **数据库操作**
   - 数据库初始化
   - 测试数据生成与导入
   - 数据完整性验证

2. **系统启动**
   - 后端服务启动
   - 服务健康检查

3. **功能测试**
   - CRUD操作测试
     - 创建帖子
     - 读取帖子
     - 更新帖子
     - 删除帖子
   - 认领流程测试
     - 创建认领请求
     - 查看认领请求
     - 批准认领请求
     - 验证状态更新

## 结论与建议

"""
    
    if test_results["failed"] == 0:
        report += "系统测试全部通过，功能运行正常。\n"
    else:
        report += f"系统测试存在{test_results['failed']}个失败项，需要进一步修复。\n"
    
    # 写入报告文件
    with open(TEST_REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)
    
    logger.info(f"测试报告已生成: {TEST_REPORT_PATH}")
    return True

# 主函数
def main():
    """主函数"""
    logger.info("开始系统测试...")
    
    try:
        # 阶段1: 数据库准备（可通过命令行参数跳过）
        skip_db_prep = len(sys.argv) > 1 and sys.argv[1] == "--skip-db-prep"
        
        if skip_db_prep:
            logger.info("跳过数据库准备阶段")
        elif not run_test("数据库准备", prepare_database):
            logger.error("数据库准备失败，终止测试")
            return
        
        # 阶段2: 系统启动（如果跳过数据库准备，则也跳过系统启动）
        if skip_db_prep:
            logger.info("跳过系统启动阶段")
        elif not run_test("系统启动", start_system):
            logger.error("系统启动失败，终止测试")
            return
        
        # 阶段3: 功能测试
        run_test("CRUD操作测试", test_crud_operations)
        run_test("认领流程测试", test_claim_flow)
        
        # 生成测试报告
        generate_test_report()
        
        logger.info(f"测试完成: 总计 {test_results['total']} 个测试, "
                   f"通过 {test_results['passed']}, "
                   f"失败 {test_results['failed']}, "
                   f"跳过 {test_results['skipped']}")
        
    except Exception as e:
        logger.error(f"测试过程中发生错误: {e}")
    finally:
        # 确保后端服务被关闭
        try:
            requests.get(f"{API_BASE_URL}/api/shutdown")
        except:
            pass

if __name__ == "__main__":
    main()