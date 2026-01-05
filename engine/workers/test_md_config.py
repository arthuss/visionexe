import requests
import json

URL = "http://127.0.0.1:8123"

def main():
    payload = {
        "action": "md_set_config",
        "payload": {
            "avatar_name": "CC3_Base_Plus",
            "config": {
                "speed_ratio": 1.2,
                "behavior": "Walk"
            }
        }
    }
    
    print(f"Testing MD configuration on {URL}...")
    try:
        res = requests.post(URL, json=payload, timeout=5)
        print("Status:", res.status_code)
        print("Response:", json.dumps(res.json(), indent=2))
    except Exception as e:
        print("Connection failed. Make sure VisionExe Remote Server is started in iClone.")
        print("Error details:", e)

if __name__ == "__main__":
    main()
