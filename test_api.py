import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    # 1. Login
    print("Logging in...")
    login_data = {
        "email": "john@bazeuniversity.edu.ng",
        "password": "password123"
    }
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code != 200:
            print(f"Login failed: {response.status_code} {response.text}")
            return
        
        data = response.json()
        token = data.get("token")
        print(f"Login successful. Token: {token[:20]}...")
        
        # 2. Get Conversations
        print("\nFetching conversations...")
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/conversations", headers=headers)
        
        if response.status_code != 200:
            print(f"Get conversations failed: {response.status_code} {response.text}")
        else:
            conversations = response.json()
            print(f"Conversations found: {len(conversations)}")
            print(json.dumps(conversations, indent=2))
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
