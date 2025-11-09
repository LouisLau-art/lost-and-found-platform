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

# 创建新帖子
posts_url = "http://localhost:8000/api/posts"
headers = {
    "Authorization": f"Bearer {token}"
}

post_data = {
    "title": "测试认领的新手机",
    "content": "在图书馆捡到的新手机，黑色，有保护壳。",
    "item_type": "found",
    "location": "图书馆",
    "category_id": 1,
    "contact_info": "请联系失主认领"
}

post_response = requests.post(posts_url, headers=headers, json=post_data)
print(f"创建帖子状态码: {post_response.status_code}")
print(f"创建帖子结果: {json.dumps(post_response.json(), indent=2, ensure_ascii=False)}")

# 如果创建成功，尝试用Test User B认领这个帖子
if post_response.status_code == 200:
    new_post_id = post_response.json()["id"]
    print(f"新创建的帖子ID: {new_post_id}")
    
    # 登录Test User B
    login_data_b = {
        "email": "testuserB@example.com",
        "password": "password123"
    }
    
    login_response_b = requests.post(login_url, json=login_data_b)
    if login_response_b.status_code != 200:
        print(f"Test User B登录失败: {login_response_b.text}")
        exit(1)
    
    token_b = login_response_b.json()["access_token"]
    print(f"Test User B令牌: {token_b}")
    
    # 创建认领请求
    claims_url = "http://localhost:8000/api/claims"
    headers_b = {
        "Authorization": f"Bearer {token_b}"
    }
    
    claim_data = {
        "post_id": new_post_id,
        "claim_description": "这是我丢失的手机，有锁屏密码和个人照片。"
    }
    
    claim_response = requests.post(claims_url, headers=headers_b, json=claim_data)
    print(f"创建认领请求状态码: {claim_response.status_code}")
    print(f"创建认领请求结果: {json.dumps(claim_response.json(), indent=2, ensure_ascii=False)}")
