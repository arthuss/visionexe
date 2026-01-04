import argparse
import json
import urllib.error
import urllib.request


def post_json(url: str, payload: dict):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def send_action(url: str, action: str, payload: dict):
    return post_json(url, {"action": action, "payload": payload})


def main():
    parser = argparse.ArgumentParser(description="Run iClone lip sync flow via remote server.")
    parser.add_argument("--host", default="127.0.0.1", help="iClone remote host.")
    parser.add_argument("--port", type=int, default=8123, help="iClone remote port.")
    parser.add_argument("--avatar", help="Avatar name (optional).")
    parser.add_argument("--audio", required=True, help="Audio file for lip sync.")
    parser.add_argument("--output", required=True, help="Output iTalk file path.")
    parser.add_argument("--start-seconds", type=float, help="Clip start time in seconds.")
    parser.add_argument("--end-seconds", type=float, help="Clip end time in seconds.")
    parser.add_argument("--clip-name", help="Clip name for LoadVocal.")
    parser.add_argument("--a2f-json", help="Optional A2F JSON path to apply instead of LoadVocal.")
    parser.add_argument("--mapping-path", help="Optional A2F mapping JSON path.")
    parser.add_argument("--key-step", type=int, default=1, help="Frame step for A2F JSON sampling.")
    parser.add_argument("--strength-scale", type=float, default=1.0, help="Scale for A2F weights.")
    parser.add_argument("--use-mocap-order", action="store_true", help="Use mocap-ordered expression names.")
    args = parser.parse_args()

    url = f"http://{args.host}:{args.port}"

    if args.avatar:
        response = send_action(url, "select_avatar", {"name": args.avatar})
        if not response.get("ok"):
            raise SystemExit(f"Failed to select avatar: {response}")

    if args.a2f_json:
        response = send_action(
            url,
            "apply_a2f_json",
            {
                "avatar_name": args.avatar,
                "path": args.a2f_json,
                "mapping_path": args.mapping_path,
                "key_step": args.key_step,
                "strength_scale": args.strength_scale,
                "start_seconds": args.start_seconds,
                "clip_name": args.clip_name,
                "use_mocap_order": args.use_mocap_order,
            },
        )
    else:
        response = send_action(
            url,
            "load_vocal",
            {
                "avatar_name": args.avatar,
                "audio_path": args.audio,
                "start_seconds": args.start_seconds,
                "clip_name": args.clip_name,
            },
        )

    if not response.get("ok"):
        raise SystemExit(f"Lip sync failed: {response}")

    response = send_action(
        url,
        "save_italk",
        {
            "avatar_name": args.avatar,
            "output_path": args.output,
            "start_seconds": args.start_seconds,
            "end_seconds": args.end_seconds,
        },
    )
    if not response.get("ok"):
        raise SystemExit(f"iTalk export failed: {response}")

    print(json.dumps(response, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except urllib.error.URLError as exc:
        raise SystemExit(f"Failed to reach iClone remote server: {exc}") from exc
