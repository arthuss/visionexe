import argparse
import csv
import json
import re
from fnmatch import fnmatch
from pathlib import Path

from visionexe_paths import ensure_dir, load_story_config, resolve_path


FALLBACK_CHAPTER_RE = re.compile(r"(?:chapter|story)_(\d+)", re.IGNORECASE)


def normalize_extensions(raw: str) -> set[str]:
    items = [ext.strip().lower().lstrip(".") for ext in raw.split(",") if ext.strip()]
    return {f".{ext}" for ext in items} if items else {".txt"}


def parse_chapter_from_path(path: Path, chapter_label: str) -> int | None:
    chapter_re = re.compile(rf"{re.escape(chapter_label)}_(\d+)", re.IGNORECASE)
    for part in path.parts:
        match = chapter_re.search(part)
        if match:
            return int(match.group(1))
    match = FALLBACK_CHAPTER_RE.search(str(path))
    if match:
        return int(match.group(1))
    return None


def classify_source(path: Path) -> str:
    name = path.name.lower()
    if name == "story.txt":
        return "story"
    if name.startswith("analysis_llm"):
        return "analysis_llm"
    if name.startswith("analysis_"):
        return "analysis"
    return "other"


def should_exclude(rel_path: str, patterns: list[str]) -> bool:
    for pattern in patterns:
        if fnmatch(rel_path, pattern):
            return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a raw subject corpus from filmset .txt files.")
    parser.add_argument("--story-root", help="Story root path (defaults to engine_config default_story_root).")
    parser.add_argument("--story-config", help="Path to story_config.json (overrides story-root).")
    parser.add_argument("--filmsets-root", help="Filmsets root override (defaults to story_config).")
    parser.add_argument("--output", help="Output corpus path (JSON or JSONL).")
    parser.add_argument("--format", choices=("json", "jsonl", "csv"), default="json", help="Output format.")
    parser.add_argument("--extensions", default="txt", help="Comma-separated extensions to include.")
    parser.add_argument("--exclude", action="append", default=[], help="Glob pattern to exclude (repeatable).")
    args = parser.parse_args()

    story_config, _story_root, repo_root = load_story_config(
        story_root=args.story_root,
        story_config_path=args.story_config,
    )

    filmsets_root = resolve_path(
        args.filmsets_root or story_config.get("filmsets_root"),
        repo_root,
    )
    if not filmsets_root.exists():
        raise SystemExit(f"Filmsets root not found: {filmsets_root}")

    output_path = resolve_path(
        args.output or "stories/template/subjects/subject_corpus.json",
        repo_root,
    )

    chapter_label = story_config.get("chapter_label", "chapter")
    extensions = normalize_extensions(args.extensions)

    records = []
    for path in filmsets_root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in extensions:
            continue
        rel_path = str(path.relative_to(filmsets_root))
        if should_exclude(rel_path, args.exclude or []):
            continue
        content = path.read_text(encoding="utf-8", errors="replace").strip()
        if not content:
            continue
        chapter = parse_chapter_from_path(path, chapter_label)
        records.append(
            {
                "chapter": chapter,
                "source_path": rel_path,
                "file_name": path.name,
                "source_type": classify_source(path),
                "content": content,
            }
        )

    ensure_dir(output_path.parent)
    if args.format == "jsonl":
        with output_path.open("w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    elif args.format == "csv":
        with output_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["chapter", "source_path", "file_name", "source_type", "content"],
            )
            writer.writeheader()
            for record in records:
                writer.writerow(record)
    else:
        output_path.write_text(
            json.dumps(records, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    print(f"Wrote subject corpus: {output_path} ({len(records)} files)")


if __name__ == "__main__":
    main()
