import requests
import json

# 登录Test User A（帖子所有者）创建新帖子
login_url = "http://localhost:8000/api/auth/login"
login_data_a = {
    "email": "testuserA@example.com",
    "password": "testpassword"
}

login_response_a = requests.post(login_url, json=login_data_a)
if login_response_a.status_code != 200:
    print(f"Test User A登录失败: {login_response_a.text}")
    exit(1)

token_a = login_response_a.json()["access_token"]
print(f"Test User A令牌: {token_a}")

# 创建新帖子用于取消认领测试
posts_url = "http://localhost:8000/api/posts"
headers_a = {
    "Authorization": f"Bearer {token_a}"
}

post_data = {
    "title": "测试取消认领的物品",
    "content": "这是一个用于测试取消认领功能的测试物品。",
    "item_type": "found",
    "location": "测试地点",
    "category_id": 1,
    "contact_info": "测试联系信息"
}

post_response = requests.post(posts_url, headers=headers_a, json=post_data)
print(f"创建帖子状态码: {post_response.status_code}")
print(f"创建帖子结果: {json.dumps(post_response.json(), indent=2, ensure_ascii=False)}")

if post_response.status_code == 200:
    new_post_id = post_response.json()["id"]
    print(f"新创建的帖子ID: {new_post_id}")
    
    # 登录Test User B创建认领请求
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
        "claim_description": "这是我要测试取消认领的认领请求。"
    }
    
    claim_response = requests.post(claims_url, headers=headers_b, json=claim_data)
    print(f"创建认领请求状态码: {claim_response.status_code}")
    print(f"创建认领请求结果: {json.dumps(claim_response.json(), indent=2, ensure_ascii=False)}")
    
    if claim_response.status_code == 200:
        claim_id = claim_response.json()["id"]
        print(f"新创建的认领请求ID: {claim_id}")
        
        # 取消认领请求（使用DELETE方法）
        cancel_url = f"http://localhost:8000/api/claims/{claim_id}"
        cancel_response = requests.delete(cancel_url, headers=headers_b)
        print(f"取消认领请求状态码: {cancel_response.status_code}")
        print(f"取消认领请求结果: {json.dumps(cancel_response.json(), indent=2, ensure_ascii=False)}")
