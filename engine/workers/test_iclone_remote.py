import requests
import json
import sys
import time

URL = "http://127.0.0.1:8123"

def post(action, payload=None):
    try:
        response = requests.post(
            URL,
            json={"action": action, "payload": payload or {}},
            timeout=5
        )
        print(f"[{action}] Status: {response.status_code}")
        try:
            return response.json()
        except:
            print("Invalid JSON response:", response.text)
            return None
    except requests.exceptions.ConnectionError:
        print(f"[{action}] Failed to connect to {URL}. Is iClone Remote Server running?")
        return None

def main():
    print(f"Testing iClone Remote API at {URL}...")
    
    # 1. Ping
    res = post("ping")
    if not res:
        print("Aborting tests.")
        return
    print("Ping:", res)

    # 2. List Content
    print("\n--- Testing Content Indexing ---")
    payload = {
        "root_keys": ["MotionDirector", "Props"],
        "max_files": 5, 
        "recursive": False # Keep it fast
    }
    res = post("list_content", payload)
    if res:
        print(f"Found {res.get('total_files')}")
        if res.get('entries'):
            print("First entry:", res['entries'][0])
        else:
            print("No entries found (maybe paths invalid on this machine?)")

    # 3. Camera Info
    print("\n--- Testing Camera Info ---")
    res = post("get_camera_info") # Defaults to current camera
    if res:
        print("Camera Info:", json.dumps(res.get("info"), indent=2))

if __name__ == "__main__":
    main()
