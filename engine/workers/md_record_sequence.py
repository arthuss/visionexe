import argparse
import json
import sys
import time

import requests


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8123


def post(host, port, action, payload=None):
    url = f"http://{host}:{port}"
    body = {"action": action, "payload": payload or {}}
    resp = requests.post(url, json=body, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _sleep(seconds):
    try:
        time.sleep(float(seconds))
    except (TypeError, ValueError):
        return


def _run_step(host, port, step):
    step_type = (step.get("type") or step.get("action") or "").lower().strip()
    if step_type in ("sleep", "wait", "delay"):
        _sleep(step.get("seconds", step.get("delay_seconds", 0)))
        return {"ok": True, "type": step_type}
    if step_type in ("key", "keys", "hotkey"):
        payload = {
            "keys": step.get("keys") or ([step.get("key")] if step.get("key") else None),
            "key": step.get("key"),
            "delay_ms": step.get("delay_ms", 0),
            "start_md": step.get("start_md", False),
        }
        return post(host, port, "md_key", payload)
    if step_type in ("waypoints", "waypoint"):
        payload = {
            "camera_name": step.get("camera_name"),
            "points": step.get("points") or step.get("waypoints") or [],
            "delay_ms": step.get("delay_ms", 0),
            "start_md": step.get("start_md", False),
            "button": step.get("button", "left"),
            "modifiers": step.get("modifiers") or ["alt"],
            "viewport_hint": step.get("viewport_hint"),
        }
        return post(host, port, "md_waypoints", payload)
    if step_type in ("click_world", "click"):
        payload = {
            "camera_name": step.get("camera_name"),
            "world": step.get("world") or {},
            "button": step.get("button", "left"),
            "modifiers": step.get("modifiers") or ["alt"],
            "start_md": step.get("start_md", False),
            "viewport_hint": step.get("viewport_hint"),
        }
        return post(host, port, "md_click_world", payload)
    if step_type in ("action", "call"):
        action = step.get("call_action") or step.get("call") or ""
        payload = step.get("payload") or {}
        if not action:
            return {"ok": False, "error": "Missing call action"}
        return post(host, port, action, payload)
    return {"ok": False, "error": f"Unknown step type: {step_type}"}


def run_plan(host, port, plan, dry_run=False):
    avatar_name = plan.get("avatar_name")
    record = bool(plan.get("record", True))
    preserve_one_key = bool(plan.get("preserve_one_key", False))
    start_md = bool(plan.get("start_md", True))
    stop_md = bool(plan.get("stop_md", False))
    time_seconds = plan.get("time_seconds")

    if start_md:
        if dry_run:
            print("[md_record] start_md")
        else:
            post(host, port, "md_start", {})

    if record:
        payload = {
            "avatar_name": avatar_name,
            "record": True,
            "preserve_one_key": preserve_one_key,
        }
        if time_seconds is not None:
            payload["time_seconds"] = time_seconds
        if dry_run:
            print("[md_record] begin_command", payload)
        else:
            post(host, port, "md_begin_command", payload)

    steps = plan.get("steps") or []
    results = []
    for idx, step in enumerate(steps):
        if dry_run:
            print(f"[md_record] step {idx+1}/{len(steps)}: {step}")
            results.append({"ok": True, "dry_run": True})
            continue
        results.append(_run_step(host, port, step))

    if record:
        payload = {
            "avatar_name": avatar_name,
            "md_props": plan.get("md_props"),
        }
        if time_seconds is not None:
            payload["time_seconds"] = time_seconds
        if dry_run:
            print("[md_record] end_command", payload)
        else:
            post(host, port, "md_end_command", payload)

    if stop_md:
        if dry_run:
            print("[md_record] stop_md")
        else:
            post(host, port, "md_stop", {})

    return results


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Record a Motion Director sequence into the timeline.")
    parser.add_argument("--plan", required=True, help="Path to MD plan JSON.")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv or sys.argv[1:])
    plan_path = args.plan
    with open(plan_path, "r", encoding="utf-8") as f:
        plan = json.load(f)
    run_plan(args.host, args.port, plan, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
