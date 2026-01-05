import argparse
import json
import sys
import time
from pathlib import Path

WATCH_FILE = Path(r"C:\Users\sasch\visionexe\engine\character_creator\cc_command.json")
RESPONSE_FILE = Path(r"C:\Users\sasch\visionexe\engine\character_creator\cc_response.json")

def save_actor(name, folder="Project/Avatar"):
    payload = {
        "action": "save_character",
        "payload": {
            "name": name,
            "folder": folder
        }
    }
    
    # Clear old response
    if RESPONSE_FILE.exists():
        RESPONSE_FILE.unlink()
        
    # Write command
    try:
        WATCH_FILE.write_text(json.dumps(payload), encoding="utf-8")
        print(f"[Client] Wrote command to {WATCH_FILE}")
    except Exception as e:
        print(f"[ERROR] Could not write command file: {e}")
        return False
        
    # Wait for response (30s)
    print("[Client] Waiting for CC4 response...")
    start = time.time()
    while time.time() - start < 30:
        if RESPONSE_FILE.exists():
            try:
                res_text = RESPONSE_FILE.read_text(encoding="utf-8")
                result = json.loads(res_text)
                if result.get("ok"):
                    print(f"[SUCCESS] Saved '{name}' to {result.get('path')}")
                    return True
                else:
                    print(f"[ERROR] CC4 Error: {result.get('error')}")
                    return False
            except Exception:
                pass # Read error (writing?)
        time.sleep(0.5)
        
    print("[ERROR] Timeout waiting for CC4 response.")
    return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Save current CC4 avatar via File Watcher.")
    parser.add_argument("name", help="Name of the asset (e.g. vx_henoch_p01)")
    parser.add_argument("--folder", default="Project/Avatar", help="Subfolder in Custom Content")
    
    args = parser.parse_args()
    
    success = save_actor(args.name, args.folder)
    sys.exit(0 if success else 1)