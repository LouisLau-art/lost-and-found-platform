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

# 获取帖子ID=2的所有认领请求
claims_url = "http://localhost:8000/api/posts/2/claims"
headers = {
    "Authorization": f"Bearer {token}"
}

claims_response = requests.get(claims_url, headers=headers)
print(f"获取认领请求状态码: {claims_response.status_code}")
print(f"认领请求列表: {json.dumps(claims_response.json(), indent=2, ensure_ascii=False)}")

# 批准认领请求（ID=3）
approve_url = "http://localhost:8000/api/claims/3/approve"
approve_data = {
    "owner_reply": "已验证身份，批准认领"
}

approve_response = requests.post(approve_url, headers=headers, json=approve_data)
print(f"批准认领请求状态码: {approve_response.status_code}")
print(f"批准认领请求结果: {json.dumps(approve_response.json(), indent=2, ensure_ascii=False)}")
