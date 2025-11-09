import requests
import json

# 登录Test User A获取令牌（帖子所有者）
login_url = "http://localhost:8000/api/auth/login"
login_data = {
    "email": "testuserA@example.com",
    "password": "testpassword"
}

login_response = requests.post(login_url, json=login_data)
if login_response.status_code != 200:
    print(f"Test User A登录失败: {login_response.text}")
    exit(1)

token = login_response.json()["access_token"]
print(f"Test User A令牌: {token}")

# 批准认领请求（id=2）
approve_url = "http://localhost:8000/api/claims/2/approve"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

approve_response = requests.post(approve_url, headers=headers)
print(f"批准请求状态码: {approve_response.status_code}")
print(f"批准请求结果: {approve_response.text}")
