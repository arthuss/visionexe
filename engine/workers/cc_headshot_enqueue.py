import argparse
import json
import time
from pathlib import Path

WATCH_FILE = Path(r"C:\Users\sasch\visionexe\engine\character_creator\cc_command.json")
RESPONSE_FILE = Path(r"C:\Users\sasch\visionexe\engine\character_creator\cc_response.json")


def enqueue(photo_path, mode, body_type, save_name, folder, timeout):
    payload = {
        "action": "headshot_from_photo",
        "payload": {
            "photo_path": photo_path,
            "mode": mode,
            "body_type": body_type,
        },
    }

    if save_name:
        payload["payload"]["save_name"] = save_name
    if folder:
        payload["payload"]["folder"] = folder

    if RESPONSE_FILE.exists():
        RESPONSE_FILE.unlink()

    WATCH_FILE.write_text(json.dumps(payload), encoding="utf-8")
    print(f"[Client] Wrote command to {WATCH_FILE}")

    start = time.time()
    while time.time() - start < timeout:
        if RESPONSE_FILE.exists():
            text = RESPONSE_FILE.read_text(encoding="utf-8")
            result = json.loads(text)
            if result.get("ok"):
                print("[SUCCESS] Headshot created.")
                print(json.dumps(result, indent=2))
                return 0
            print("[ERROR] Headshot failed.")
            print(json.dumps(result, indent=2))
            return 1
        time.sleep(0.5)

    print("[ERROR] Timeout waiting for CC4 response.")
    return 1


def main():
    parser = argparse.ArgumentParser(description="Enqueue a Headshot photo for CC4 file watcher.")
    parser.add_argument("photo_path", help="Path to the input photo.")
    parser.add_argument("--mode", default="auto", choices=["auto", "pro"], help="Headshot mode.")
    parser.add_argument("--body-type", default="current", choices=["male", "female", "baby", "neutral", "current"], help="Body type.")
    parser.add_argument("--save-name", help="Save resulting avatar as .ccAvatar with this name.")
    parser.add_argument("--folder", default="Project/Avatar", help="Custom folder for saving.")
    parser.add_argument("--timeout", type=float, default=120.0, help="Seconds to wait for response.")

    args = parser.parse_args()
    raise SystemExit(
        enqueue(args.photo_path, args.mode, args.body_type, args.save_name, args.folder, args.timeout)
    )


if __name__ == "__main__":
    main()
