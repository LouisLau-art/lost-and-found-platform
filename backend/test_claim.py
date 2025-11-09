import requests
import json

# 登录获取令牌
login_url = "http://localhost:8000/api/auth/login"
login_data = {
    "email": "testuserD@example.com",
    "password": "testpassword123"
}

login_response = requests.post(login_url, json=login_data)
if login_response.status_code != 200:
    print(f"登录失败: {login_response.text}")
    exit(1)

token = login_response.json()["access_token"]
print(f"获取到令牌: {token}")

# 创建认领请求
claim_url = "http://localhost:8000/api/claims"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
claim_data = {
    "post_id": 1,
    "description": "我认领了这个物品"
}

claim_response = requests.post(claim_url, headers=headers, json=claim_data)
print(f"认领请求状态码: {claim_response.status_code}")
print(f"认领请求结果: {claim_response.text}")
