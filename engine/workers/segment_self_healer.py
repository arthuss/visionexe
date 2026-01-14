import argparse
import json
import re
from pathlib import Path

from visionexe_paths import ensure_dir, load_story_config, resolve_path


HEADER_RE = re.compile(r"^(?P<prefix>[A-Za-z]+)\s+\d+\s+Segment\s+\d+\s*$", re.IGNORECASE)
VERSE_LINE_RE = re.compile(r"^\s*(?P<chapter>\d+)\s*:\s*(?P<verse>\d+)\s+(?P<text>.+)$")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Detect and repair missing segment folders using verse-per-line chapter files."
    )
    parser.add_argument("--story-root", help="Story root path.")
    parser.add_argument("--story-config", help="Path to story_config.json.")
    parser.add_argument(
        "--verse-root",
        help="Folder with chapter_XX.txt verse files (default: docs/ethiopic_1enoch_p).",
    )
    parser.add_argument("--chapters", nargs="*", type=int, help="Limit to specific chapters.")
    parser.add_argument("--report", help="Write a JSON report to this path.")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without writing.")
    parser.add_argument(
        "--refresh-existing",
        action="store_true",
        help="Overwrite existing segment.txt with verse file content when available.",
    )
    return parser.parse_args()


def parse_segment_index(name: str, prefix: str):
    match = re.match(rf"^{re.escape(prefix)}_(\d+)$", name, re.IGNORECASE)
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None


def find_header_prefix(segments: list[tuple[int, Path]]) -> str | None:
    for _index, seg_dir in segments:
        seg_path = seg_dir / "segment.txt"
        if not seg_path.exists():
            continue
        first_line = seg_path.read_text(encoding="utf-8", errors="replace").splitlines()[:1]
        if not first_line:
            continue
        match = HEADER_RE.match(first_line[0].strip())
        if match:
            return match.group("prefix")
    return None


def build_segment_text(prefix: str, chapter: int, segment: int, verse_text: str) -> str:
    header = f"{prefix} {chapter} Segment {segment}"
    body = verse_text.strip()
    if body:
        return f"{header}\n\n{body}\n"
    return f"{header}\n"


def resolve_verse_file(verse_root: Path, chapter_num: int) -> Path | None:
    for fmt in (f"chapter_{chapter_num:02d}.txt", f"chapter_{chapter_num:03d}.txt"):
        candidate = verse_root / fmt
        if candidate.exists():
            return candidate
    return None


def load_verse_overrides(verse_root: Path) -> dict[int, int]:
    overrides_path = verse_root / "verse_overrides.json"
    if not overrides_path.exists():
        return {}
    try:
        data = json.loads(overrides_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    raw = data.get("max_verse_by_chapter", {})
    overrides: dict[int, int] = {}
    for chapter_key, max_verse in raw.items():
        try:
            chapter_num = int(chapter_key)
            overrides[chapter_num] = int(max_verse)
        except (TypeError, ValueError):
            continue
    return overrides


def load_verse_lines(path: Path) -> dict[int, str]:
    verses: dict[int, str] = {}
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = VERSE_LINE_RE.match(raw_line.strip())
        if not match:
            continue
        verse_num = int(match.group("verse"))
        text = match.group("text").strip()
        verses[verse_num] = text
    return verses


def main():
    args = parse_args()
    story_config, _story_root, repo_root = load_story_config(
        story_root=args.story_root,
        story_config_path=args.story_config,
    )

    filmsets_root = story_config.get("filmsets_root")
    if not filmsets_root:
        raise SystemExit("filmsets_root is not configured.")
    filmsets_root = resolve_path(filmsets_root, repo_root)

    verse_root_value = args.verse_root or "docs/ethiopic_1enoch_p"
    verse_root = resolve_path(verse_root_value, repo_root)
    verse_overrides = load_verse_overrides(verse_root)

    chapter_label = story_config.get("chapter_label", "chapter")
    segment_label = story_config.get("segment_label", "segment")
    segment_padding = int(story_config.get("segment_index_padding", 3))
    scene_label = story_config.get("scene_label", "scene")
    scene_padding = int(story_config.get("scene_index_padding", 3))
    timeline_label = story_config.get("timeline_label", "timeline")
    timeline_padding = int(story_config.get("timeline_index_padding", 2))
    timeline_tag = "1".zfill(timeline_padding)

    chapter_filter = set(args.chapters or [])
    report = {
        "created": [],
        "refreshed": [],
        "refresh_skipped": [],
        "skipped": [],
        "missing_segments": [],
        "extra_segments": [],
    }

    chapter_dirs = sorted([d for d in filmsets_root.iterdir() if d.is_dir() and d.name.startswith(f"{chapter_label}_")])
    for chapter_dir in chapter_dirs:
        chapter_num = parse_segment_index(chapter_dir.name, chapter_label)
        if chapter_num is None:
            continue
        if chapter_filter and chapter_num not in chapter_filter:
            continue

        verse_path = resolve_verse_file(verse_root, chapter_num)
        if not verse_path:
            report["skipped"].append({"chapter": chapter_num, "reason": "verse file missing"})
            continue

        verses = load_verse_lines(verse_path)
        if not verses:
            report["skipped"].append({"chapter": chapter_num, "reason": "verse file empty"})
            continue
        target_max = max(verses)
        if chapter_num in verse_overrides:
            target_max = verse_overrides[chapter_num]

        segment_dirs = []
        for seg in chapter_dir.iterdir():
            if not seg.is_dir():
                continue
            seg_index = parse_segment_index(seg.name, segment_label)
            if seg_index is None:
                continue
            segment_dirs.append((seg_index, seg))

        if not segment_dirs:
            report["skipped"].append({"chapter": chapter_num, "reason": "no segment dirs"})
            continue

        segment_dirs.sort(key=lambda item: item[0])
        segment_indices = [idx for idx, _ in segment_dirs]
        missing = [idx for idx in range(1, target_max + 1) if idx not in segment_indices]
        for extra_index in [idx for idx in segment_indices if idx > target_max]:
            report["extra_segments"].append({"chapter": chapter_num, "segment": extra_index})
        if not missing:
            if not args.refresh_existing:
                continue

        header_prefix = find_header_prefix(segment_dirs) or chapter_label.capitalize()

        if args.refresh_existing:
            for seg_index, seg_dir in segment_dirs:
                if seg_index > target_max:
                    continue
                verse_text = verses.get(seg_index)
                if not verse_text:
                    report["refresh_skipped"].append(
                        {"chapter": chapter_num, "segment": seg_index, "reason": "verse missing"}
                    )
                    continue
                if args.dry_run:
                    print(f"[dry-run] refresh {seg_dir / 'segment.txt'}")
                else:
                    segment_text = build_segment_text(header_prefix, chapter_num, seg_index, verse_text)
                    (seg_dir / "segment.txt").write_text(segment_text, encoding="utf-8")
                report["refreshed"].append(
                    {
                        "chapter": chapter_num,
                        "segment": seg_index,
                        "segment_label": seg_dir.name,
                        "verse_source": str(verse_path),
                        "method": "verse_file",
                    }
                )

        for seg_index in missing:
            if seg_index not in verses:
                report["missing_segments"].append(
                    {"chapter": chapter_num, "segment": seg_index, "reason": "verse missing"}
                )
                continue
            verse_text = verses[seg_index]

            seg_label = f"{segment_label}_{seg_index:0{segment_padding}d}"
            seg_dir = chapter_dir / seg_label
            scene_dir = seg_dir / f"{scene_label}_{1:0{scene_padding}d}"
            timeline_dir = scene_dir / f"{timeline_label}_{timeline_tag}"

            if args.dry_run:
                print(f"[dry-run] write {seg_dir / 'segment.txt'}")
            else:
                ensure_dir(timeline_dir)
                segment_text = build_segment_text(header_prefix, chapter_num, seg_index, verse_text)
                (seg_dir / "segment.txt").write_text(segment_text, encoding="utf-8")

            report["created"].append(
                {
                    "chapter": chapter_num,
                    "segment": seg_index,
                    "segment_label": seg_label,
                    "verse_source": str(verse_path),
                    "method": "verse_file",
                }
            )

    if args.report:
        report_path = resolve_path(args.report, repo_root)
    else:
        data_root = story_config.get("data_root") or "stories/template/data"
        report_path = resolve_path(str(Path(data_root) / "analysis" / "segment_self_heal_report.json"), repo_root)

    if report_path and not args.dry_run:
        ensure_dir(report_path.parent)
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Done. Created {len(report['created'])} segment(s).")


if __name__ == "__main__":
    main()
