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

# 获取所有帖子列表
posts_url = "http://localhost:8000/api/posts"
headers = {
    "Authorization": f"Bearer {token}"
}

posts_response = requests.get(posts_url, headers=headers)
print(f"帖子列表状态码: {posts_response.status_code}")
print(f"帖子列表: {json.dumps(posts_response.json(), indent=2, ensure_ascii=False)}")
