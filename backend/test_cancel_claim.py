import requests
import json

# 登录Test User B（认领者，认领ID=3为pending状态）
login_url = "http://localhost:8000/api/auth/login"
login_data = {
    "email": "testuserB@example.com",
    "password": "testpassword"
}

login_response = requests.post(login_url, json=login_data)
if login_response.status_code != 200:
    print(f"Test User B登录失败: {login_response.text}")
    exit(1)

token = login_response.json()["access_token"]
print(f"Test User B令牌: {token}")

# 取消认领请求（有效pending状态claim_id=3）
claim_id = 3
cancel_url = f"http://localhost:8000/api/claims/{claim_id}"
headers = {
    "Authorization": f"Bearer {token}"
}

cancel_response = requests.delete(cancel_url, headers=headers)
print(f"取消请求状态码: {cancel_response.status_code}")
print(f"取消请求结果: {json.dumps(cancel_response.json(), indent=2, ensure_ascii=False)}")
