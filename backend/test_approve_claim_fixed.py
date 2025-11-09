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

# 批准认领请求（假设认领ID为2，可根据实际情况调整）
claim_id = 2
approve_url = f"http://localhost:8000/api/claims/{claim_id}/approve"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

approve_response = requests.post(approve_url, headers=headers, json={"owner_reply": "已批准认领"})
print(f"批准请求状态码: {approve_response.status_code}")
print(f"批准请求结果: {approve_response.text}")
