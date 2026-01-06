import argparse
import json
import re
from pathlib import Path

from visionexe_paths import load_story_config, resolve_path


CANON_RE = re.compile(
    r"^##\s+\[ACT\s+(?P<act>\d+)\]\s+\[SCENE\s+(?P<scene>[0-9.]+)\]\s+\[(?:Timecode:\s*)?(?P<timecode>[0-9:\s.-]+)\]\s+\[(?P<title>[^\]]+)\]$",
    re.IGNORECASE,
)
ACT_RE = re.compile(r"\bACT\s*(\d+)\b", re.IGNORECASE)
SCENE_RE = re.compile(r"\bSCENE\s*([0-9]+(?:\.[0-9]+)*)\b", re.IGNORECASE)
TIMECODE_RE = re.compile(r"(\d{2}:\d{2}(?::\d{2})?)\s*-\s*(\d{2}:\d{2}(?::\d{2})?)")


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


def extract_title(line: str) -> str:
    segments = re.findall(r"\[([^\]]+)\]", line)
    for candidate in reversed(segments):
        if "act" in candidate.lower() and "scene" in candidate.lower():
            continue
        if "timecode" in candidate.lower():
            continue
        if TIMECODE_RE.search(candidate):
            continue
        title = candidate.strip()
        if title:
            return title
    tail = re.sub(r"\[[^\]]+\]", "", line).strip()
    if tail.startswith("##"):
        tail = tail[2:].strip()
    return tail or "UNTITLED"


def fix_header_line(line: str) -> str | None:
    raw = line.strip()
    if CANON_RE.match(raw):
        return None
    if not raw.startswith("##"):
        return None
    if "ACT" not in raw.upper() or "SCENE" not in raw.upper():
        return None

    act_match = ACT_RE.search(raw)
    scene_match = SCENE_RE.search(raw)
    if not act_match or not scene_match:
        return None
    act = int(act_match.group(1))
    scene_id = scene_match.group(1)

    time_match = TIMECODE_RE.search(raw)
    if time_match:
        timecode = f"{time_match.group(1)}-{time_match.group(2)}"
    else:
        timecode = "00:00-00:00"

    title = extract_title(raw)
    return f"## [ACT {act}] [SCENE {scene_id}] [Timecode: {timecode}] [{title}]"


def fix_script(path: Path, dry_run: bool) -> dict:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return {"path": str(path), "status": f"read_error:{exc}", "changed": 0}

    changed = 0
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        fixed = fix_header_line(line)
        if fixed:
            lines[idx] = fixed
            changed += 1

    if changed and not dry_run:
        path.write_text("\n".join(lines) + ("\n" if text.endswith("\n") else ""), encoding="utf-8")
        return {"path": str(path), "status": "fixed", "changed": changed}
    if changed:
        return {"path": str(path), "status": "would_fix", "changed": changed}
    return {"path": str(path), "status": "ok", "changed": 0}


def main():
    parser = argparse.ArgumentParser(description="Fix malformed ACT/SCENE headers in DREHBUCH files.")
    parser.add_argument("--story-root", help="Story root path (defaults to engine_config default_story_root).")
    parser.add_argument("--story-config", help="Path to story_config.json (overrides story-root).")
    parser.add_argument("--start", type=int, default=1, help="Start chapter number.")
    parser.add_argument("--end", type=int, default=108, help="End chapter number.")
    parser.add_argument("--dry-run", action="store_true", help="Only report; do not write files.")
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

    results = []
    for chapter in range(args.start, args.end + 1):
        folder = filmsets_root / f"{chapter_label}_{chapter:0{chapter_padding}d}"
        if not folder.exists() and chapter_label != "chapter":
            fallback = filmsets_root / f"chapter_{chapter:03d}"
            if fallback.exists():
                folder = fallback

        screenplay_path = folder / "DREHBUCH_HOLLYWOOD.md"
        if not screenplay_path.exists():
            results.append({"chapter": chapter, "path": str(screenplay_path), "status": "missing"})
            continue

        chapter_in_path = extract_chapter_number(screenplay_path, primary_regex, fallback_regex)
        if chapter_in_path and chapter_in_path != chapter:
            results.append({"chapter": chapter, "path": str(screenplay_path), "status": "chapter_mismatch"})
            continue

        report = fix_script(screenplay_path, args.dry_run)
        report["chapter"] = chapter
        results.append(report)

    summary = {
        "story_root": str(story_root),
        "filmsets_root": str(filmsets_root),
        "chapter_label": chapter_label,
        "chapter_padding": chapter_padding,
        "range": {"start": args.start, "end": args.end},
        "results": results,
    }

    if args.output:
        output_path = resolve_path(args.output, repo_root)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote header-fix report: {output_path}")
    else:
        print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
