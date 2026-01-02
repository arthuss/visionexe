import argparse
import glob
import json
import os
import re
import time

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
FILMSETS_PATH = os.path.join(ROOT_PATH, "filmsets")
DEFAULT_CONFIG = os.path.join(ROOT_PATH, "scene_audit_config.json")


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


def extract_regie_json(text):
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("REGIE_JSON:"):
            payload = line.split(":", 1)[1].strip()
            try:
                return json.loads(payload)
            except json.JSONDecodeError:
                return {}
    return {}


def load_config(path):
    if not path or not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {}


def apply_patterns(patterns, values):
    matches = []
    for pattern in patterns:
        resolved = pattern.format(**values)
        matches.extend(glob.glob(resolved))
    return sorted(set(matches))


def resolve_requirements(regie, defaults):
    defaults = defaults or {}
    require_actor = defaults.get("require_actor", True)
    require_env = defaults.get("require_env", True)
    require_composite = defaults.get("require_composite", True)
    require_props_if_named = defaults.get("require_props_if_named", True)

    if isinstance(regie, dict):
        mode = (regie.get("start_image_mode") or "").strip().lower()
        subject = (regie.get("subject") or "").strip().lower()
        if mode in ("env_only", "ui_only") or subject in ("environment", "interface", "prop"):
            require_actor = False
        if mode == "ui_only":
            require_env = False

    props = []
    if isinstance(regie, dict):
        props = regie.get("props") or []
    require_props = bool(props) if require_props_if_named else False

    return {
        "actor_raw": require_actor,
        "actor_alpha": require_actor,
        "env_base": require_env,
        "prop_image": require_props,
        "prop_alpha": require_props,
        "composite": require_composite,
        "visual_audit": False
    }


def audit_scene(chapter, scene_id, block, config):
    scene_dot, scene_tag = normalize_scene(scene_id)
    media_root = config.get("media_root", "filmsets/{chapter}/Media").format(chapter=chapter)
    patterns = config.get("patterns", {})
    regie = extract_regie_json(block)
    defaults = config.get("defaults", {})
    required = resolve_requirements(regie, defaults)

    values = {
        "chapter": chapter,
        "scene": scene_tag,
        "scene_dot": scene_dot,
        "media": os.path.join(ROOT_PATH, media_root)
    }

    found = {}
    missing = []
    for key, needed in required.items():
        if not needed:
            found[key] = []
            continue
        hits = apply_patterns(patterns.get(key, []), values)
        found[key] = hits
        if not hits:
            missing.append(key)

    status = "complete" if not missing else "partial"

    return {
        "chapter": chapter,
        "scene": scene_dot,
        "scene_tag": scene_tag,
        "required": required,
        "found": found,
        "missing": missing,
        "status": status,
        "regie": regie
    }


def write_outputs(chapter_path, results):
    audit_path = os.path.join(chapter_path, "scene_audit.json")
    summary_path = os.path.join(chapter_path, "scene_audit_summary.md")

    with open(audit_path, "w", encoding="utf-8") as handle:
        json.dump({
            "generated_at": int(time.time()),
            "scenes": results
        }, handle, indent=2)

    lines = ["# Scene Audit Summary", ""]
    for item in results:
        missing = ", ".join(item["missing"]) if item["missing"] else "none"
        lines.append(f"- {item['scene_tag']}: {item['status']} (missing: {missing})")
    with open(summary_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description="Audit scene construction outputs.")
    parser.add_argument("--chapter", default="all", help="Chapter number(s), e.g. 1, 1-5, all")
    parser.add_argument("--config", default=DEFAULT_CONFIG, help="Config JSON path")
    parser.add_argument("--dry-run", action="store_true", help="Print summary only")
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
        results = [audit_scene(chapter, scene_id, block, config) for scene_id, block in scenes]

        if args.dry_run:
            print(f"{chapter}: {len(results)} scenes audited")
            continue
        write_outputs(chapter_path, results)
        print(f"{chapter}: wrote scene_audit.json")


if __name__ == "__main__":
    main()
