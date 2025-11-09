import requests
import json

# 登录Test User A（帖子所有者）
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

# 拒绝认领请求（有效pending状态claim_id=1）
claim_id = 1
reject_url = f"http://localhost:8000/api/claims/{claim_id}/reject"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

reject_data = {
    "owner_reply": "你的认领请求不符合要求，已拒绝"
}

reject_response = requests.post(reject_url, headers=headers, json=reject_data)
print(f"拒绝请求状态码: {reject_response.status_code}")
print(f"拒绝请求结果: {reject_response.text}")
