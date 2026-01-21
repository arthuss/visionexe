import argparse
import json
import os
import sys
import urllib.error
import urllib.request


DEFAULT_BASE_URL = os.environ.get("ANIMGRAPH_BASE_URL", "http://127.0.0.1:8020")


def request_json(base_url, method, path, body=None):
    url = f"{base_url}{path}"
    data = None
    headers = {}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode("utf-8")
            if not raw:
                return ""
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return raw
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {err.code} {err.reason}: {detail}") from err


def print_result(result):
    if isinstance(result, (dict, list)):
        print(json.dumps(result, indent=2))
    else:
        print(result)


def build_parser():
    parser = argparse.ArgumentParser(
        description="HTTP client for ia-animation-graph-microservice (port 8020)."
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"Base URL for the HTTP API (default: {DEFAULT_BASE_URL})",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("readiness", help="GET /readiness")
    subparsers.add_parser("liveness", help="GET /liveness")
    subparsers.add_parser("graphs", help="GET /animation_graphs")
    subparsers.add_parser("list-vars", help="GET /animation_graphs/avatar/variables")
    subparsers.add_parser("streams", help="GET /streams")

    add_stream = subparsers.add_parser("add-stream", help="POST /streams/{stream_id}")
    add_stream.add_argument("--stream-id", required=True)

    remove_stream = subparsers.add_parser("remove-stream", help="DELETE /streams/{stream_id}")
    remove_stream.add_argument("--stream-id", required=True)

    set_var = subparsers.add_parser(
        "set-var",
        help="PUT /streams/{stream_id}/animation_graphs/avatar/variables/{route}/{value}",
    )
    set_var.add_argument("--stream-id", required=True)
    set_var.add_argument("--route", required=True)
    set_var.add_argument("--value", required=True)

    sdr_add = subparsers.add_parser(
        "sdr-add-stream", help="POST /sdr/add_stream with event.camera_id"
    )
    sdr_add.add_argument("--camera-id", required=True)

    sdr_remove = subparsers.add_parser(
        "sdr-remove-stream", help="POST /sdr/remove_stream with event.camera_id"
    )
    sdr_remove.add_argument("--camera-id", required=True)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/")

    if args.command == "readiness":
        print_result(request_json(base_url, "GET", "/readiness"))
        return
    if args.command == "liveness":
        print_result(request_json(base_url, "GET", "/liveness"))
        return
    if args.command == "graphs":
        print_result(request_json(base_url, "GET", "/animation_graphs"))
        return
    if args.command == "list-vars":
        print_result(request_json(base_url, "GET", "/animation_graphs/avatar/variables"))
        return
    if args.command == "streams":
        print_result(request_json(base_url, "GET", "/streams"))
        return
    if args.command == "add-stream":
        print_result(request_json(base_url, "POST", f"/streams/{args.stream_id}"))
        return
    if args.command == "remove-stream":
        print_result(request_json(base_url, "DELETE", f"/streams/{args.stream_id}"))
        return
    if args.command == "set-var":
        path = f"/streams/{args.stream_id}/animation_graphs/avatar/variables/{args.route}/{args.value}"
        print_result(request_json(base_url, "PUT", path))
        return
    if args.command == "sdr-add-stream":
        body = {"event": {"camera_id": args.camera_id}}
        print_result(request_json(base_url, "POST", "/sdr/add_stream", body=body))
        return
    if args.command == "sdr-remove-stream":
        body = {"event": {"camera_id": args.camera_id}}
        print_result(request_json(base_url, "POST", "/sdr/remove_stream", body=body))
        return

    parser.print_help()


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
