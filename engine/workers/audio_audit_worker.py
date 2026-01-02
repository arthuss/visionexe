import argparse
import json
import os
import re
import time

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
FILMSETS_PATH = os.path.join(ROOT_PATH, "filmsets")
DEFAULT_CONFIG = os.path.join(ROOT_PATH, "audio_audit_config.json")


def load_json(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None


def load_config(path):
    defaults = {
        "audio_dir": "audio",
        "media_dir": "Media",
        "require_voice_if_words_max": True,
        "require_monologue_if_words_max": True,
        "require_voice_json": False,
        "check_facesync_outputs": True,
        "check_gbuffer_outputs": True,
        "require_narration_if_present": True
    }
    config = load_json(path) or {}
    defaults.update({k: v for k, v in config.items() if v is not None})
    return defaults


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


def detect_scene_from_filename(filename):
    match = re.search(r"(scene_\d{2}_\d{2})", filename)
    if match:
        return match.group(1)
    return ""


def normalize_scene_tag(scene_tag):
    match = re.search(r"scene_(\d{2})_(\d{2})", scene_tag or "")
    if not match:
        return "", ""
    scene_dot = f"{int(match.group(1))}.{int(match.group(2))}"
    return scene_dot, scene_tag


def resolve_path(chapter_path, media_dir, value):
    if not value:
        return ""
    if os.path.isabs(value) or value.startswith("\\\\"):
        return value
    normalized = value.replace("/", "\\")
    if normalized.lower().startswith("media\\"):
        return os.path.join(chapter_path, normalized)
    if normalized.lower().startswith("audio\\"):
        return os.path.join(chapter_path, normalized)
    if "\\" in normalized:
        return os.path.join(chapter_path, normalized)
    return os.path.join(media_dir, normalized)


def read_text(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            return handle.read()
    except OSError:
        return ""


def parse_narrator_present(script_path):
    if not os.path.exists(script_path):
        return False
    content = read_text(script_path)
    return "NARRATOR_TEXT:" in content


def check_file(label, path_value, required, chapter_path, media_dir):
    resolved = resolve_path(chapter_path, media_dir, path_value)
    exists = bool(resolved and os.path.exists(resolved))
    return {
        "label": label,
        "path": resolved,
        "exists": exists,
        "required": bool(required)
    }


def build_scene_checks(meta_path, meta, config, chapter_path, audio_dir, media_dir):
    scene_tag = detect_scene_from_filename(meta_path)
    scene_dot, scene_tag = normalize_scene_tag(scene_tag)
    regie = meta.get("regie", {}) if isinstance(meta, dict) else {}
    facesync = meta.get("facesync", {}) if isinstance(meta, dict) else {}
    gbuffer = meta.get("gbuffer", {}) if isinstance(meta, dict) else {}

    voice_words = regie.get("voice_words_max") if isinstance(regie, dict) else None
    needs_voice = bool(config.get("require_voice_if_words_max") and isinstance(voice_words, int) and voice_words > 0)
    needs_monologue = bool(config.get("require_monologue_if_words_max") and isinstance(voice_words, int) and voice_words > 0)

    checks = []
    missing = []

    voice_json_path = os.path.join(audio_dir, f"{scene_tag}_voice.json") if scene_tag else ""
    monologue_path = os.path.join(audio_dir, f"{scene_tag}_monologue.txt") if scene_tag else ""
    if voice_json_path and os.path.exists(voice_json_path):
        payload = load_json(voice_json_path) or {}
        monologue_path = payload.get("monologue_file") or monologue_path

    if config.get("require_voice_json"):
        item = {
            "label": "voice_json",
            "path": voice_json_path,
            "exists": bool(voice_json_path and os.path.exists(voice_json_path)),
            "required": True
        }
        checks.append(item)
        if not item["exists"]:
            missing.append(item["label"])

    if needs_monologue:
        item = {
            "label": "monologue",
            "path": monologue_path,
            "exists": bool(monologue_path and os.path.exists(monologue_path)),
            "required": True
        }
        checks.append(item)
        if not item["exists"]:
            missing.append(item["label"])

    if needs_voice:
        checks.append(check_file(
            "source_audio",
            facesync.get("source_audio"),
            True,
            chapter_path,
            media_dir,
        ))

    if config.get("check_facesync_outputs") and facesync.get("enabled"):
        checks.append(check_file(
            "target_media",
            facesync.get("target_media"),
            True,
            chapter_path,
            media_dir,
        ))
        checks.append(check_file(
            "facesync_output",
            facesync.get("output"),
            True,
            chapter_path,
            media_dir,
        ))

    if config.get("check_gbuffer_outputs") and gbuffer.get("enabled"):
        checks.append(check_file(
            "gbuffer_manifest",
            gbuffer.get("manifest"),
            True,
            chapter_path,
            media_dir,
        ))
        checks.append(check_file(
            "pose_source",
            gbuffer.get("pose_source"),
            True,
            chapter_path,
            media_dir,
        ))
        passes = gbuffer.get("passes") if isinstance(gbuffer.get("passes"), dict) else {}
        for key in ("normal", "depth", "motion", "mask"):
            checks.append(check_file(
                f"gbuffer_{key}",
                passes.get(key),
                True,
                chapter_path,
                media_dir,
            ))

    for item in checks:
        if item["required"] and not item["exists"] and item["label"] not in missing:
            missing.append(item["label"])

    status = "ok" if not missing else "missing"

    return {
        "scene": scene_dot,
        "scene_tag": scene_tag,
        "voice_words_max": voice_words,
        "facesync_enabled": bool(facesync.get("enabled")),
        "gbuffer_enabled": bool(gbuffer.get("enabled")),
        "checks": checks,
        "missing": missing,
        "status": status
    }


def audit_chapter(chapter, config):
    chapter_path = os.path.join(FILMSETS_PATH, chapter)
    audio_dir = os.path.join(chapter_path, config["audio_dir"])
    media_dir = os.path.join(chapter_path, config["media_dir"])
    results = []
    narration = {
        "required": False,
        "path": "",
        "exists": False
    }

    script_path = os.path.join(chapter_path, "DREHBUCH_HOLLYWOOD.md")
    narrator_present = parse_narrator_present(script_path)
    if narrator_present and config.get("require_narration_if_present"):
        narration_path = os.path.join(audio_dir, f"{chapter}_narration.txt")
        narration = {
            "required": True,
            "path": narration_path,
            "exists": os.path.exists(narration_path)
        }

    if not os.path.isdir(audio_dir):
        return results, narration

    for name in sorted(os.listdir(audio_dir)):
        if not name.endswith("_audio_meta.json"):
            continue
        meta_path = os.path.join(audio_dir, name)
        meta = load_json(meta_path) or {}
        results.append(build_scene_checks(meta_path, meta, config, chapter_path, audio_dir, media_dir))

    return results, narration


def write_outputs(chapter_path, results, narration):
    audit_path = os.path.join(chapter_path, "audio_audit.json")
    summary_path = os.path.join(chapter_path, "audio_audit_summary.md")

    with open(audit_path, "w", encoding="utf-8") as handle:
        json.dump({
            "generated_at": int(time.time()),
            "narration": narration,
            "scenes": results
        }, handle, indent=2)

    lines = ["# Audio Audit Summary", ""]
    if narration["required"]:
        status = "ok" if narration["exists"] else "missing"
        lines.append(f"- narration: {status} ({narration['path']})")
        lines.append("")
    for item in results:
        missing = ", ".join(item["missing"]) if item["missing"] else "none"
        lines.append(f"- {item['scene_tag']}: {item['status']} (missing: {missing})")
    with open(summary_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description="Audit audio meta outputs and referenced media.")
    parser.add_argument("--chapter", default="all", help="Chapter number(s), e.g. 1, 1-5, all")
    parser.add_argument("--config", default=DEFAULT_CONFIG, help="Config JSON path")
    parser.add_argument("--dry-run", action="store_true", help="Print summary only")
    args = parser.parse_args()

    config = load_config(args.config)
    chapters = get_chapters(args.chapter)

    for chapter in chapters:
        chapter_path = os.path.join(FILMSETS_PATH, chapter)
        results, narration = audit_chapter(chapter, config)
        if args.dry_run:
            print(f"{chapter}: {len(results)} scenes audited")
            continue
        write_outputs(chapter_path, results, narration)
        print(f"{chapter}: wrote audio_audit.json")


if __name__ == "__main__":
    main()
