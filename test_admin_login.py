#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试管理员登录功能的简单脚本
"""
import requests
import json

# 配置
BASE_URL = "http://localhost:8000"
LOGIN_ENDPOINT = "/api/auth/login"

# 管理员凭据
ADMIN_CREDENTIALS = {
    "email": "admin@example.com",
    "password": "admin123"
}

def test_login():
    print(f"测试管理员登录: {ADMIN_CREDENTIALS['email']}")
    print(f"请求URL: {BASE_URL}{LOGIN_ENDPOINT}")
    print(f"请求数据: {json.dumps(ADMIN_CREDENTIALS)}")
    
    try:
        # 发送登录请求
        response = requests.post(
            f"{BASE_URL}{LOGIN_ENDPOINT}",
            json=ADMIN_CREDENTIALS
        )
        
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            print("\n✅ 登录成功!")
            data = response.json()
            print(f"访问令牌: {data.get('access_token')[:20]}...")
            return True
        else:
            print("\n❌ 登录失败")
            return False
            
    except Exception as e:
        print(f"\n❌ 请求异常: {e}")
        return False

if __name__ == "__main__":
    test_login()