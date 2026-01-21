import json
import time
from pathlib import Path

WATCH_FILE = Path(r"C:\Users\sasch\visionexe\engine\character_creator\cc_command.json")
RESPONSE_FILE = Path(r"C:\Users\sasch\visionexe\engine\character_creator\cc_response.json")

def inspect():
    payload = {"action": "inspect_ui"}
    if RESPONSE_FILE.exists(): RESPONSE_FILE.unlink()
    WATCH_FILE.write_text(json.dumps(payload), encoding="utf-8")
    
    print("Waiting for UI dump...")
    time.sleep(2)
    
    if RESPONSE_FILE.exists():
        print(RESPONSE_FILE.read_text(encoding="utf-8"))
    else:
        print("Timeout.")

if __name__ == "__main__":
    inspect()
