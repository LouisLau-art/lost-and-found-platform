import os
import sys
import time
import json
import subprocess
import tempfile
from datetime import datetime
from urllib import request, error, parse
from sqlmodel import create_engine

TEST_HOST = "127.0.0.1"
TEST_PORT = 8000
BASE_URL = f"http://{TEST_HOST}:{TEST_PORT}"
API = f"{BASE_URL}/api"


def http_post_json(url, data, token=None):
    data_bytes = json.dumps(data).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = request.Request(url, data=data_bytes, headers=headers, method="POST")
    with request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def http_get_json(url, token=None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = request.Request(url, headers=headers, method="GET")
    with request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def wait_for_server(timeout=30, proc=None):
    start = time.time()
    last_err = None
    while time.time() - start < timeout:
        try:
            _ = http_get_json(f"{API}/posts")
            return True
        except Exception as e:
            last_err = e
            # If the server process has already exited, abort early
            try:
                if proc is not None and proc.poll() is not None:
                    break
            except Exception:
                pass
            time.sleep(0.5)
    if last_err:
        raise last_err
    return False


def start_server(env, backend_dir):
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        TEST_HOST,
        "--port",
        str(TEST_PORT),
        "--log-level",
        "debug",
    ]
    # Inherit stdout/stderr so uvicorn logs show up in the test output
    return subprocess.Popen(cmd, cwd=backend_dir, env=env)


def stop_server(proc):
    if proc and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()


def assert_post_in_db(engine, post_id):
    from sqlmodel import Session
    from app.models.post import Post
    with Session(engine) as session:
        post = session.get(Post, post_id)
        assert post is not None, f"Post {post_id} not found in DB"


def run():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    backend_dir = os.path.abspath(os.path.dirname(__file__))

    tmp_db_fd, tmp_db_path = tempfile.mkstemp(prefix="lostfound_test_", suffix=".db")
    os.close(tmp_db_fd)
    if os.path.exists(tmp_db_path):
        os.remove(tmp_db_path)

    env = os.environ.copy()
    env["DATABASE_URL"] = f"sqlite:///{tmp_db_path}"
    # Also set in current process to ensure any local imports use the same DB
    os.environ["DATABASE_URL"] = env["DATABASE_URL"]

    # Create a direct engine to the same SQLite DB for validation
    local_engine = create_engine(env["DATABASE_URL"], connect_args={"check_same_thread": False})

    proc = None
    try:
        proc = start_server(env, backend_dir)
        wait_for_server(timeout=40, proc=proc)

        user_a = {
            "name": "User A",
            "email": "user_a_test@example.com",
            "password": "passA123!"
        }
        user_b = {
            "name": "User B",
            "email": "user_b_test@example.com",
            "password": "passB123!"
        }

        http_post_json(f"{API}/auth/register", user_a)
        http_post_json(f"{API}/auth/register", user_b)

        tok_a = http_post_json(f"{API}/auth/login", {"email": user_a["email"], "password": user_a["password"]})["access_token"]
        tok_b = http_post_json(f"{API}/auth/login", {"email": user_b["email"], "password": user_b["password"]})["access_token"]

        now_iso = datetime.utcnow().isoformat()
        post_a_payload = {
            "title": "Lost Wallet",
            "content": "Black leather wallet lost near campus gate.",
            "item_type": "lost",
            "location": "Campus Gate",
            "item_time": now_iso,
            "contact_info": "user_a_contact",
            "category_id": None,
            "images": []
        }
        created_a = http_post_json(f"{API}/posts/", post_a_payload, token=tok_a)
        assert "id" in created_a, "Create post A failed: no id"
        post_a_id = created_a["id"]

        assert_post_in_db(local_engine, post_a_id)

        posts_list = http_get_json(f"{API}/posts")
        if isinstance(posts_list, dict) and "data" in posts_list:
            ids = [p.get("id") for p in posts_list.get("data", [])]
        elif isinstance(posts_list, list):
            ids = [p.get("id") for p in posts_list]
        else:
            raise AssertionError("Unexpected posts list response format")
        assert post_a_id in ids, "Post A not returned by /api/posts"

        post_b_payload = {
            "title": "Found Keys",
            "content": "Set of keys found near library.",
            "item_type": "found",
            "location": "Library",
            "item_time": now_iso,
            "contact_info": "user_b_contact",
            "category_id": None,
            "images": []
        }
        created_b = http_post_json(f"{API}/posts/", post_b_payload, token=tok_b)
        assert "id" in created_b, "Create post B failed: no id"
        post_b_id = created_b["id"]

        assert_post_in_db(local_engine, post_b_id)
        posts_list2 = http_get_json(f"{API}/posts")
        if isinstance(posts_list2, dict) and "data" in posts_list2:
            ids2 = [p.get("id") for p in posts_list2.get("data", [])]
        elif isinstance(posts_list2, list):
            ids2 = [p.get("id") for p in posts_list2]
        else:
            raise AssertionError("Unexpected posts list response format (2)")
        assert post_b_id in ids2, "Post B not returned by /api/posts"

        print("OK: DB and API consistency validated for posts A and B")
        return 0
    except error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore") if hasattr(e, "read") else ""
        print(f"HTTPError: {e.code} {e.reason} at {e.geturl() if hasattr(e, 'geturl') else ''}\n{body}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        stop_server(proc)
        if os.path.exists(tmp_db_path):
            os.remove(tmp_db_path)


if __name__ == "__main__":
    code = run()
    sys.exit(code)
