import argparse
import json
import re
from pathlib import Path

from visionexe_paths import load_story_config, resolve_path


MARKER_PATTERNS = [
    re.compile(r"^#\s+DREHBUCH\b", re.IGNORECASE),
    re.compile(r"^##\s+\[ACT\b", re.IGNORECASE),
]

JUNK_HINTS = [
    "permission denied",
    "check existing filmsets",
    "write the generated screenplay",
    "test-path",
    "get-childitem",
    "ps ",
    "cmd ",
    "warning:",
]


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


def should_trim(prefix: str) -> bool:
    prefix_lower = prefix.lower()
    return any(hint in prefix_lower for hint in JUNK_HINTS)


def find_marker_line(lines: list[str]) -> int | None:
    for idx, line in enumerate(lines):
        line_strip = line.strip()
        if not line_strip:
            continue
        for pattern in MARKER_PATTERNS:
            if pattern.match(line_strip):
                return idx
    return None


def sanitize_text(text: str) -> tuple[str, str]:
    lines = text.splitlines()
    marker_idx = find_marker_line(lines)
    if marker_idx is None:
        return text, "no_marker"

    prefix = "\n".join(lines[:marker_idx])
    if marker_idx == 0:
        return text, "ok"
    if not should_trim(prefix):
        return text, "ok"

    cleaned = "\n".join(lines[marker_idx:]).lstrip()
    return cleaned, "trimmed"


def main():
    parser = argparse.ArgumentParser(description="Trim command/log junk before screenplay headers.")
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

        try:
            text = screenplay_path.read_text(encoding="utf-8")
        except OSError as exc:
            results.append({"chapter": chapter, "path": str(screenplay_path), "status": f"read_error:{exc}"})
            continue

        cleaned, status = sanitize_text(text)
        if status == "trimmed" and not args.dry_run:
            screenplay_path.write_text(cleaned, encoding="utf-8")
        results.append({"chapter": chapter, "path": str(screenplay_path), "status": status})

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
        print(f"Wrote sanitize report: {output_path}")
    else:
        print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
