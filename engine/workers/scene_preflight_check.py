import argparse
import json
import re
from pathlib import Path

from visionexe_paths import load_story_config, resolve_path


SCENE_HEADER_RE = re.compile(
    r"^##\s+\[ACT\s+(?P<act>\d+)\]\s+\[SCENE\s+(?P<scene>[0-9.]+)\]\s+\[(?:Timecode:\s*)?(?P<timecode>[0-9:\s.-]+)\]\s+\[(?P<title>[^\]]+)\]",
    re.MULTILINE,
)


def build_chapter_regex(label: str):
    safe_label = re.escape(label or "chapter")
    return re.compile(rf"{safe_label}_(\d+)", re.IGNORECASE)


def extract_chapter_number(path: Path, primary_regex, fallback_regex=None):
    for regex in (primary_regex, fallback_regex):
        if not regex:
            continue
        match = regex.search(str(path))
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return None
    return None


def scan_screenplay(path: Path) -> dict:
    issues = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return {"has_scenes": False, "issues": [f"read_error:{exc}"]}

    if not SCENE_HEADER_RE.search(text):
        issues.append("no_scene_headers")
    if "Permission denied" in text or "permission denied" in text:
        issues.append("permission_denied_log")
    if "Check existing filmsets" in text or "check existing filmsets" in text:
        issues.append("command_log")
    return {"has_scenes": not issues or "no_scene_headers" not in issues, "issues": issues}


def main():
    parser = argparse.ArgumentParser(description="Preflight DREHBUCH_HOLLYWOOD.md for missing/invalid scene headers.")
    parser.add_argument("--story-root", help="Story root path (defaults to engine_config default_story_root).")
    parser.add_argument("--story-config", help="Path to story_config.json (overrides story-root).")
    parser.add_argument("--start", type=int, default=1, help="Start chapter number.")
    parser.add_argument("--end", type=int, default=108, help="End chapter number.")
    parser.add_argument("--output", help="Optional JSON output path.")
    args = parser.parse_args()

    story_config, story_root, repo_root = load_story_config(
        story_root=args.story_root,
        story_config_path=args.story_config,
    )

    filmsets_root = resolve_path(story_config.get("filmsets_root"), repo_root)
    if not filmsets_root:
        raise SystemExit("filmsets_root missing in story_config.json")

    chapter_label = story_config.get("chapter_label", "chapter")
    chapter_padding = int(story_config.get("chapter_index_padding", 3))
    primary_regex = build_chapter_regex(chapter_label)
    fallback_regex = None
    if chapter_label.lower() != "chapter":
        fallback_regex = build_chapter_regex("chapter")

    missing = []
    invalid = []
    ok = []

    for chapter in range(args.start, args.end + 1):
        folder = filmsets_root / f"{chapter_label}_{chapter:0{chapter_padding}d}"
        if not folder.exists() and chapter_label != "chapter":
            fallback = filmsets_root / f"chapter_{chapter:03d}"
            if fallback.exists():
                folder = fallback

        screenplay_path = folder / "DREHBUCH_HOLLYWOOD.md"
        if not screenplay_path.exists():
            missing.append({"chapter": chapter, "path": str(screenplay_path)})
            continue

        chapter_in_path = extract_chapter_number(screenplay_path, primary_regex, fallback_regex)
        if chapter_in_path and chapter_in_path != chapter:
            invalid.append({"chapter": chapter, "path": str(screenplay_path), "issues": ["chapter_mismatch"]})
            continue

        scan = scan_screenplay(screenplay_path)
        if scan["issues"]:
            invalid.append({"chapter": chapter, "path": str(screenplay_path), "issues": scan["issues"]})
            continue

        ok.append({"chapter": chapter, "path": str(screenplay_path)})

    summary = {
        "story_root": str(story_root),
        "filmsets_root": str(filmsets_root),
        "chapter_label": chapter_label,
        "chapter_padding": chapter_padding,
        "range": {"start": args.start, "end": args.end},
        "missing": missing,
        "invalid": invalid,
        "ok": ok,
    }

    if args.output:
        output_path = resolve_path(args.output, repo_root)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote preflight report: {output_path}")
    else:
        print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
