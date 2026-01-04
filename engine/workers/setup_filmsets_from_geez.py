import argparse
import json
import re
from pathlib import Path

from visionexe_paths import ensure_dir, load_story_config, resolve_path


VERSE_FILENAME_RE = re.compile(r"chapter_(\d+)_verses\.jsonl", re.IGNORECASE)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Scaffold filmsets from Ge'ez verse JSONL files."
    )
    parser.add_argument("--story-root", help="Story root path.")
    parser.add_argument("--story-config", help="Path to story_config.json.")
    parser.add_argument("--geez-root", help="Root folder with chapter_###_verses.jsonl.")
    parser.add_argument("--filmsets-root", help="Override filmsets root.")
    parser.add_argument("--chapters", nargs="*", type=int, help="Limit to specific chapters.")
    parser.add_argument("--segment-label", help="Override segment label.")
    parser.add_argument("--scene-label", help="Override scene label.")
    parser.add_argument("--timeline-label", help="Override timeline label.")
    parser.add_argument("--timeline", default="1", help="Timeline tag (default: 1).")
    parser.add_argument("--segment-padding", type=int, help="Segment index padding.")
    parser.add_argument("--scene-padding", type=int, help="Scene index padding.")
    parser.add_argument("--timeline-padding", type=int, help="Timeline index padding.")
    parser.add_argument("--include-chapter-text", action="store_true", help="Write story.txt per chapter.")
    parser.add_argument("--include-intro", action="store_true", help="Write intro.txt if available.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing text files.")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without writing.")
    return parser.parse_args()


def format_index(value, padding):
    try:
        return f"{int(value):0{padding}d}"
    except (TypeError, ValueError):
        return str(value)


def parse_chapter_num(path: Path):
    match = VERSE_FILENAME_RE.search(path.name)
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None


def iter_chapter_files(geez_root: Path):
    for path in sorted(geez_root.glob("chapter_*_verses.jsonl")):
        chapter = parse_chapter_num(path)
        if chapter is None:
            continue
        yield chapter, path


def load_verses(path: Path):
    verses = []
    with path.open("r", encoding="utf-8") as handle:
        for idx, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            verse = record.get("verse") or idx
            text = record.get("text", "").strip()
            verses.append((verse, text))
    return verses


def write_text(path: Path, content: str, force: bool, dry_run: bool):
    if path.exists() and not force:
        return False
    if dry_run:
        print(f"[dry-run] write {path}")
        return True
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")
    return True


def build_segment_text(chapter: int, verse: int, text: str):
    header = f"Chapter {chapter} Segment {verse}\n"
    return f"{header}\n{text}".strip() + "\n"


def main():
    args = parse_args()

    story_config, _, repo_root = load_story_config(
        story_root=args.story_root,
        story_config_path=args.story_config,
    )

    data_root = story_config.get("data_root") or "stories/template/data"
    default_geez_root = Path(data_root) / "raw" / "henoch_geez"
    geez_root = resolve_path(args.geez_root or str(default_geez_root), repo_root)
    if not geez_root.exists():
        raise SystemExit(f"Ge'ez root not found: {geez_root}")

    filmsets_root = args.filmsets_root or story_config.get("filmsets_root")
    if not filmsets_root:
        raise SystemExit("filmsets_root is not configured.")
    filmsets_root = resolve_path(filmsets_root, repo_root)
    ensure_dir(filmsets_root)

    segment_label = args.segment_label or story_config.get("segment_label", "segment")
    scene_label = args.scene_label or story_config.get("scene_label", "scene")
    timeline_label = args.timeline_label or story_config.get("timeline_label", "timeline")
    segment_padding = args.segment_padding or int(story_config.get("segment_index_padding", 3))
    scene_padding = args.scene_padding or int(story_config.get("scene_index_padding", 3))
    timeline_padding = args.timeline_padding or int(story_config.get("timeline_index_padding", 2))
    timeline_tag = format_index(args.timeline, timeline_padding)

    chapter_filter = set(args.chapters or [])

    created_segments = 0
    created_chapters = 0
    for chapter, verse_path in iter_chapter_files(geez_root):
        if chapter_filter and chapter not in chapter_filter:
            continue
        chapter_label = format_index(chapter, 3)
        chapter_dir = filmsets_root / f"chapter_{chapter_label}"
        if not args.dry_run:
            ensure_dir(chapter_dir)

        if args.include_chapter_text:
            chapter_text_path = geez_root / f"chapter_{chapter_label}.txt"
            if chapter_text_path.exists():
                content = chapter_text_path.read_text(encoding="utf-8")
            else:
                verses = load_verses(verse_path)
                content = "\n".join([f"{chapter}:{v} {t}" for v, t in verses]).strip()
            if content:
                wrote = write_text(chapter_dir / "story.txt", content + "\n", args.force, args.dry_run)
                if wrote:
                    created_chapters += 1

        if args.include_intro:
            intro_path = geez_root / f"chapter_{chapter_label}_intro.txt"
            if intro_path.exists():
                content = intro_path.read_text(encoding="utf-8")
                write_text(chapter_dir / "intro.txt", content + "\n", args.force, args.dry_run)

        verses = load_verses(verse_path)
        for verse, text in verses:
            segment_index = format_index(verse, segment_padding)
            segment_dir = chapter_dir / f"{segment_label}_{segment_index}"
            scene_dir = segment_dir / f"{scene_label}_{format_index(1, scene_padding)}"
            timeline_dir = scene_dir / f"{timeline_label}_{timeline_tag}"

            if args.dry_run:
                print(f"[dry-run] mkdir {segment_dir}")
                print(f"[dry-run] mkdir {scene_dir}")
                print(f"[dry-run] mkdir {timeline_dir}")
            else:
                ensure_dir(timeline_dir)

            segment_text = build_segment_text(chapter, verse, text)
            wrote = write_text(segment_dir / "segment.txt", segment_text, args.force, args.dry_run)
            if wrote:
                created_segments += 1

    print(f"Done. Chapters written: {created_chapters}, segments written: {created_segments}")


if __name__ == "__main__":
    main()
