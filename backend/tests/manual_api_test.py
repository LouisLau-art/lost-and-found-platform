import json
import textwrap
from dataclasses import dataclass
from typing import Callable, Dict, Any, Optional

import requests

BASE_URL = "http://localhost:8000/api"

@dataclass
class TestResult:
    name: str
    success: bool
    status_code: Optional[int]
    details: str
    severity: str = "low"

class APITester:
    def __init__(self):
        self.results = []
        self.tokens: Dict[str, str] = {}

    def record(self, name: str, response: Optional[requests.Response], success: bool, details: str, severity: str = "low"):
        status = response.status_code if response is not None else None
        self.results.append(TestResult(name, success, status, details, severity))
        print(f"[{name}] => {'PASS' if success else 'FAIL'} ({status})\n{details}\n")

    def login(self, alias: str, email: str, password: str):
        name = f"auth.login ({alias})"
        try:
            resp = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
            if resp.status_code == 200:
                token = resp.json().get("access_token")
                if token:
                    self.tokens[alias] = token
                    self.record(name, resp, True, "Login successful")
                else:
                    self.record(name, resp, False, "No access_token in response", severity="high")
            else:
                self.record(name, resp, False, resp.text, severity="high")
        except Exception as exc:
            self.record(name, None, False, f"Exception: {exc}", severity="high")

    def auth_headers(self, alias: str) -> Dict[str, str]:
        token = self.tokens.get(alias)
        if not token:
            raise RuntimeError(f"No token for alias {alias}")
        return {"Authorization": f"Bearer {token}"}

    def get(self, name: str, url: str, *, alias: Optional[str] = None, expected_status: int = 200, severity: str = "medium"):
        headers = {}
        if alias:
            headers.update(self.auth_headers(alias))
        try:
            resp = requests.get(url, headers=headers)
            success = resp.status_code == expected_status
            details = resp.text if not success else "OK"
            self.record(name, resp, success, details if not success else "OK", severity=severity)
            return resp
        except Exception as exc:
            self.record(name, None, False, f"Exception: {exc}", severity="high")

    def post(self, name: str, url: str, *, alias: Optional[str] = None, json_body: Optional[Dict[str, Any]] = None, expected_status: int = 200, severity: str = "medium"):
        headers = {"Content-Type": "application/json"}
        if alias:
            headers.update(self.auth_headers(alias))
        try:
            resp = requests.post(url, headers=headers, json=json_body)
            success = resp.status_code == expected_status
            details = resp.text if not success else "OK"
            self.record(name, resp, success, details if not success else "OK", severity=severity)
            return resp
        except Exception as exc:
            self.record(name, None, False, f"Exception: {exc}", severity="high")

    def put(self, name: str, url: str, *, alias: Optional[str] = None, json_body: Optional[Dict[str, Any]] = None, expected_status: int = 200, severity: str = "medium"):
        headers = {"Content-Type": "application/json"}
        if alias:
            headers.update(self.auth_headers(alias))
        try:
            resp = requests.put(url, headers=headers, json=json_body)
            success = resp.status_code == expected_status
            details = resp.text if not success else "OK"
            self.record(name, resp, success, details if not success else "OK", severity=severity)
            return resp
        except Exception as exc:
            self.record(name, None, False, f"Exception: {exc}", severity="high")

    def delete(self, name: str, url: str, *, alias: Optional[str] = None, expected_status: int = 200, severity: str = "medium"):
        headers = {}
        if alias:
            headers.update(self.auth_headers(alias))
        try:
            resp = requests.delete(url, headers=headers)
            success = resp.status_code == expected_status
            details = resp.text if not success else "OK"
            self.record(name, resp, success, details if not success else "OK", severity=severity)
            return resp
        except Exception as exc:
            self.record(name, None, False, f"Exception: {exc}", severity="high")

    def summary(self):
        total = len(self.results)
        fails = [r for r in self.results if not r.success]
        print("=" * 80)
        print(f"Total tests: {total}, Failures: {len(fails)}")
        for res in fails:
            print(f"- {res.name} (status={res.status_code}, severity={res.severity})\n  Details: {textwrap.shorten(res.details.replace('\n', ' '), width=200, placeholder='…')}")
        print("=" * 80)
        return fails

if __name__ == "__main__":
    tester = APITester()

    # 1. Public endpoints
    tester.get("categories.list", f"{BASE_URL}/categories/", expected_status=200, severity="medium")

    # 2. Login as admin and a regular user (if available)
    tester.login("admin", "admin@example.com", "admin123")

    # Attempt to login as a known regular user (from test data)
    tester.login("user1", "user17@example.com", "admin123")  # generated data uses admin123 as default

    # 3. Protected endpoints
    tester.get("users.profile", f"{BASE_URL}/users/profile", alias="admin", expected_status=200, severity="high")
    tester.get("users.profile.noauth", f"{BASE_URL}/users/profile", alias=None, expected_status=401, severity="medium")

    # Posts listing with filters
    tester.get("posts.list", f"{BASE_URL}/posts/?limit=5", alias=None, expected_status=200, severity="high")

    # Create post (admin should be able since any authenticated user)
    post_payload = {
        "title": "测试帖子 - 自动化",
        "content": "自动化测试创建帖子内容",
        "item_type": "found",
        "location": "图书馆",
        "category_id": 1,
        "contact_info": "电话 123456789"
    }
    resp = tester.post("posts.create", f"{BASE_URL}/posts/", alias="admin", json_body=post_payload, expected_status=200, severity="high")
    new_post_id = None
    if resp and resp.status_code == 200:
        new_post_id = resp.json().get("id")

    # Attempt to create post without auth
    tester.post("posts.create.noauth", f"{BASE_URL}/posts/", json_body=post_payload, expected_status=401, severity="medium")

    if new_post_id:
        # Fetch post detail
        tester.get("posts.detail", f"{BASE_URL}/posts/{new_post_id}", alias="admin", expected_status=200, severity="medium")

        # Comment on post
        comment_payload = {"content": "测试评论"}
        tester.post("comments.create", f"{BASE_URL}/posts/{new_post_id}/comments", alias="admin", json_body=comment_payload, expected_status=200, severity="medium")

        # List comments
        tester.get("comments.list", f"{BASE_URL}/posts/{new_post_id}/comments", alias="admin", expected_status=200, severity="medium")

    # Claims - requires second user
    if new_post_id and "user1" in tester.tokens:
        claim_payload = {"post_id": new_post_id, "message": "我认领这个物品"}
        tester.post("claims.create", f"{BASE_URL}/claims/", alias="user1", json_body=claim_payload, expected_status=200, severity="high")
        tester.get("claims.my", f"{BASE_URL}/claims/my-claims", alias="user1", expected_status=200, severity="medium")

    # Ratings - likely requires claim, skipping for now but test unauthorized access
    tester.get("ratings.require_auth", f"{BASE_URL}/ratings/user/1/received", alias=None, expected_status=401, severity="medium")

    fails = tester.summary()
    if fails:
        exit(1)
