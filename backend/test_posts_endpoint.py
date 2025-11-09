import requests

try:
    response = requests.get('http://localhost:8000/api/posts/')
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response keys: {list(data.keys())}")
        print(f"Data type: {type(data)}")
        if 'data' in data:
            print(f"Number of posts: {len(data['data'])}")
            print(f"Total: {data.get('total')}")
    else:
        print(f"Error response: {response.text}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
