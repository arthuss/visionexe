import argparse
import base64
import json
import os
import re
import time

from rag_utils import request_json

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
FILMSETS_PATH = os.path.join(ROOT_PATH, "filmsets")
DEFAULT_CONFIG = os.path.join(ROOT_PATH, "vision_audit_config.json")
SCENE_AUDIT_CONFIG = os.path.join(ROOT_PATH, "scene_audit_config.json")

IMAGE_MIME = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp"
}
COMPONENT_KEYS = ("actor_raw", "env_base", "prop_image")


def load_json(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None


def load_config(path):
    config = load_json(path) or {}
    return {
        "enabled": bool(config.get("enabled", False)),
        "endpoint": config.get("endpoint", ""),
        "api_key": config.get("api_key", ""),
        "model": config.get("model", ""),
        "timeout_sec": int(config.get("timeout_sec", 120)),
        "max_tokens": int(config.get("max_tokens", 400)),
        "output_dir": config.get("output_dir", "filmsets/{chapter}/vision"),
        "queue_filename": config.get("queue_filename", "vision_audit_queue.json"),
        "results_filename": config.get("results_filename", "vision_audit.json"),
        "summary_filename": config.get("summary_filename", "vision_audit_summary.md"),
        "image_max_mb": float(config.get("image_max_mb", 6)),
        "include_components": bool(config.get("include_components", False)),
        "system_prompt": config.get("system_prompt", "")
    }


def get_chapters(chapter_arg):
    all_chapters = sorted([d for d in os.listdir(FILMSETS_PATH) if d.startswith("chapter_")])
    if chapter_arg == "all":
        return all_chapters
    selected = []
    parts = chapter_arg.split(",")
    for part in parts:
        if "-" in part:
            start, end = map(int, part.split("-"))
            for i in range(start, end + 1):
                name = f"chapter_{i:03d}"
                if name in all_chapters:
                    selected.append(name)
        else:
            number = int(part)
            name = f"chapter_{number:03d}"
            if name in all_chapters:
                selected.append(name)
    return sorted(set(selected))


def normalize_scene(scene_id):
    if not scene_id:
        return "", ""
    raw = str(scene_id)
    if "_" in raw:
        parts = raw.split("_")
    elif "." in raw:
        parts = raw.split(".")
    else:
        return raw, raw
    if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
        scene_dot = f"{int(parts[0])}.{int(parts[1])}"
        scene_tag = f"{int(parts[0]):02d}_{int(parts[1]):02d}"
        return scene_dot, scene_tag
    return raw, raw


def read_text(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            return handle.read()
    except OSError:
        return ""


def split_scenes(content):
    pattern = r"(^##\s+\[ACT\s+\d+\]\s+\[SCENE\s+[\d\.]+\])"
    parts = re.split(pattern, content, flags=re.MULTILINE)
    scenes = []
    current_header = ""
    for part in parts:
        if part.strip().startswith("## [ACT"):
            current_header = part.strip()
            continue
        if not current_header:
            continue
        scene_match = re.search(r"\[SCENE\s+([\d\.]+)\]", current_header)
        scene_id = scene_match.group(1) if scene_match else ""
        scenes.append((scene_id, part))
    return scenes


def extract_start_image_prompt(block):
    match = re.search(r"### 1\. START IMAGE PROMPT.*?\n(.*?)(?=\n###|\n---|$)", block, re.DOTALL)
    if not match:
        return ""
    raw = match.group(1).strip()
    return raw.strip("`* ").strip()


def extract_action(block):
    for line in block.splitlines():
        if line.strip().startswith("**Action:**"):
            return line.split("**Action:**", 1)[1].strip()
    return ""


def load_scene_audit(chapter_path):
    audit_path = os.path.join(chapter_path, "scene_audit.json")
    data = load_json(audit_path)
    if not data:
        return {}
    index = {}
    for item in data.get("scenes", []):
        scene = item.get("scene")
        if scene:
            index[str(scene)] = item
    return index


def load_scene_audit_config():
    config = load_json(SCENE_AUDIT_CONFIG) or {}
    return config.get("patterns", {})


def resolve_composite(found):
    if not isinstance(found, dict):
        return ""
    composite = found.get("composite") or []
    if composite:
        return composite[0]
    return ""


def build_queue(chapter, scene_entries, scene_audit_index, config, scene_filter=None):
    output_dir = config["output_dir"].format(chapter=chapter)
    os.makedirs(os.path.join(ROOT_PATH, output_dir), exist_ok=True)
    jobs = []
    for scene_id, block in scene_entries:
        scene_dot, scene_tag = normalize_scene(scene_id)
        if scene_filter and scene_dot != scene_filter and scene_tag != scene_filter:
            continue
        prompt = extract_start_image_prompt(block)
        action = extract_action(block)
        audit = scene_audit_index.get(scene_dot) or {}
        if audit.get("missing"):
            continue
        composite_path = resolve_composite(audit.get("found"))
        if not composite_path or not os.path.exists(composite_path):
            continue
        jobs.append({
            "chapter": chapter,
            "scene": scene_dot,
            "scene_tag": scene_tag,
            "prompt": prompt,
            "action": action,
            "composite_path": composite_path,
            "inputs": audit.get("found", {}),
        })
    queue_path = os.path.join(ROOT_PATH, output_dir, config["queue_filename"])
    with open(queue_path, "w", encoding="utf-8") as handle:
        json.dump({"jobs": jobs}, handle, indent=2)
    return queue_path, jobs


def encode_image(path, max_mb):
    size_mb = os.path.getsize(path) / (1024 * 1024)
    if size_mb > max_mb:
        raise RuntimeError(f"Image too large ({size_mb:.2f} MB) for audit: {path}")
    ext = os.path.splitext(path)[1].lower()
    mime = IMAGE_MIME.get(ext, "image/png")
    with open(path, "rb") as handle:
        encoded = base64.b64encode(handle.read()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def parse_json_response(text):
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
    return None


def send_job(job, config):
    headers = {"Content-Type": "application/json"}
    if config["api_key"]:
        headers["Authorization"] = f"Bearer {config['api_key']}"

    content = [
        {"type": "text", "text": f"Action: {job['action']}\nPrompt: {job['prompt']}"},
        {"type": "image_url", "image_url": {"url": encode_image(job["composite_path"], config["image_max_mb"])}}
    ]
    if config.get("include_components"):
        for key in COMPONENT_KEYS:
            paths = job.get("inputs", {}).get(key) or []
            if not paths:
                continue
            try:
                content.append({"type": "text", "text": f"{key}:"})
                content.append({
                    "type": "image_url",
                    "image_url": {"url": encode_image(paths[0], config["image_max_mb"])}
                })
            except RuntimeError as exc:
                content.append({"type": "text", "text": f"{key}: skipped ({exc})"})

    payload = {
        "model": config["model"],
        "messages": [
            {"role": "system", "content": config["system_prompt"]},
            {"role": "user", "content": content}
        ],
        "max_tokens": config["max_tokens"]
    }
    status, data = request_json("POST", config["endpoint"], payload=payload, headers=headers, timeout=config["timeout_sec"])
    if status < 200 or status >= 300:
        raise RuntimeError(f"Vision API error {status}: {data}")
    return data


def write_results(chapter, jobs, responses, config):
    output_dir = os.path.join(ROOT_PATH, config["output_dir"].format(chapter=chapter))
    results_path = os.path.join(output_dir, config["results_filename"])
    summary_path = os.path.join(output_dir, config["summary_filename"])

    payload = {
        "generated_at": int(time.time()),
        "items": responses
    }
    with open(results_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)

    lines = ["# Vision Audit Summary", ""]
    for item in responses:
        scene_tag = item.get("scene_tag")
        status = item.get("status")
        notes = item.get("notes", "")
        lines.append(f"- {scene_tag}: {status} {notes}".strip())
    with open(summary_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description="Audit composite start images with a vision model.")
    parser.add_argument("--chapter", default="all", help="Chapter number(s), e.g. 1, 1-5, all")
    parser.add_argument("--scene", help="Scene filter (e.g. 1.1 or 01_01)")
    parser.add_argument("--config", default=DEFAULT_CONFIG, help="Config JSON path")
    parser.add_argument("--send", action="store_true", help="Send to vision endpoint if configured")
    parser.add_argument("--dry-run", action="store_true", help="Only build queue")
    args = parser.parse_args()

    config = load_config(args.config)
    chapters = get_chapters(args.chapter)

    for chapter in chapters:
        chapter_path = os.path.join(FILMSETS_PATH, chapter)
        script_path = os.path.join(chapter_path, "DREHBUCH_HOLLYWOOD.md")
        if not os.path.exists(script_path):
            continue
        content = read_text(script_path)
        scenes = split_scenes(content)
        scene_audit_index = load_scene_audit(chapter_path)
        queue_path, jobs = build_queue(chapter, scenes, scene_audit_index, config, args.scene)
        print(f"{chapter}: queued {len(jobs)} jobs -> {queue_path}")

        if args.dry_run or not args.send:
            continue
        if not config["endpoint"] or not config["model"] or not config["enabled"]:
            print("Vision endpoint not configured/enabled; skipping send.")
            continue

        responses = []
        for job in jobs:
            try:
                response = send_job(job, config)
                content = ""
                if isinstance(response, dict):
                    choices = response.get("choices")
                    if choices:
                        content = choices[0].get("message", {}).get("content", "")
                parsed = parse_json_response(content)
                responses.append({
                    "chapter": job["chapter"],
                    "scene": job["scene"],
                    "scene_tag": job["scene_tag"],
                    "status": parsed.get("pass") if isinstance(parsed, dict) else "review",
                    "score": parsed.get("score") if isinstance(parsed, dict) else None,
                    "issues": parsed.get("issues") if isinstance(parsed, dict) else [],
                    "notes": parsed.get("notes") if isinstance(parsed, dict) else content,
                    "raw": response
                })
            except Exception as exc:
                responses.append({
                    "chapter": job["chapter"],
                    "scene": job["scene"],
                    "scene_tag": job["scene_tag"],
                    "status": "error",
                    "notes": str(exc),
                    "raw": None
                })
        write_results(chapter, jobs, responses, config)


if __name__ == "__main__":
    main()
