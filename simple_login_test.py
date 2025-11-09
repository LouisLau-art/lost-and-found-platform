#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单的登录测试脚本，用于调试
"""
import requests
import json

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/auth/login"

def test_direct_request():
    print("=== 直接使用requests发送登录请求 ===")
    
    # 管理员凭据
    data = {
        "email": "admin@example.com",
        "password": "admin123"
    }
    
    # 添加详细的请求头
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    print(f"请求URL: {LOGIN_URL}")
    print(f"请求头: {json.dumps(headers, indent=2)}")
    print(f"请求体: {json.dumps(data, indent=2)}")
    
    try:
        # 发送请求
        response = requests.post(
            LOGIN_URL,
            json=data,
            headers=headers,
            timeout=10
        )
        
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应头: {json.dumps(dict(response.headers), indent=2)}")
        print(f"响应体: {response.text}")
        
        # 尝试使用data参数而不是json参数
        print("\n=== 使用data参数发送请求 ===")
        response2 = requests.post(
            LOGIN_URL,
            data=json.dumps(data),
            headers=headers,
            timeout=10
        )
        
        print(f"响应状态码: {response2.status_code}")
        print(f"响应体: {response2.text}")
        
    except Exception as e:
        print(f"\n请求异常: {e}")

if __name__ == "__main__":
    test_direct_request()