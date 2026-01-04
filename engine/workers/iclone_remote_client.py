import argparse
import json
import urllib.error
import urllib.request


def post_json(url: str, payload: dict):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description="Send commands to the iClone remote server.")
    parser.add_argument("--host", default="127.0.0.1", help="iClone remote host.")
    parser.add_argument("--port", type=int, default=8123, help="iClone remote port.")
    parser.add_argument("--action", required=True, help="Action to send.")
    parser.add_argument("--payload", help="JSON payload string.")
    parser.add_argument("--payload-file", help="Path to JSON payload file.")
    args = parser.parse_args()

    payload = {}
    if args.payload_file:
        with open(args.payload_file, "r", encoding="utf-8") as f:
            payload = json.load(f)
    elif args.payload:
        payload = json.loads(args.payload)

    url = f"http://{args.host}:{args.port}"
    body = {"action": args.action, "payload": payload}
    try:
        response = post_json(url, body)
    except urllib.error.URLError as exc:
        raise SystemExit(f"Failed to reach iClone remote server: {exc}") from exc

    print(json.dumps(response, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
