import argparse
import csv
import json
import re
from pathlib import Path

from visionexe_paths import ensure_dir, resolve_repo_root, resolve_path


VERSE_MARKER_RE = re.compile(
    r"\b(?:[A-Z]{1,3}\s*)?(?P<chapter>\d{1,3})\s*:\s*(?P<verse>\d{1,3})\b"
)
VERSE_LINE_RE = re.compile(r"^\s*(?P<chapter>\d{1,3})\s*:\s*(?P<verse>\d{1,3})\b")
ETHIOPIC_RE = re.compile(r"[\u1200-\u137f]")
CHAPTER_FILE_RE = re.compile(r"^chapter_(\d{2,3})\.txt$", re.IGNORECASE)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Audit verse counts and Ethiopic line coverage per chapter."
    )
    parser.add_argument(
        "--text-file",
        default="docs/ethiopic_1enoch_p/full_henoch_108.txt",
        help="Full text source with verse markers.",
    )
    parser.add_argument(
        "--verse-dir",
        default="docs/ethiopic_1enoch_p",
        help="Directory with chapter_XX.txt files.",
    )
    parser.add_argument(
        "--verse-overrides",
        default="docs/ethiopic_1enoch_p/verse_overrides.json",
        help="Optional JSON overrides for verse fixes.",
    )
    parser.add_argument("--chapters", nargs="*", type=int, help="Limit to chapters.")
    parser.add_argument(
        "--report",
        default="docs/ethiopic_1enoch_p/verse_count_audit.json",
        help="Write JSON report to this path.",
    )
    parser.add_argument(
        "--csv",
        default="docs/ethiopic_1enoch_p/verse_count_audit.csv",
        help="Write CSV report to this path.",
    )
    return parser.parse_args()


def parse_full_text(text: str):
    order_by_chapter: dict[int, list[int]] = {}
    ethiopic_lines_by_verse: dict[tuple[int, int], int] = {}
    current_key: tuple[int, int] | None = None
    unassigned_ethiopic = 0

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        marker = VERSE_MARKER_RE.search(line)
        if marker:
            chapter = int(marker.group("chapter"))
            verse = int(marker.group("verse"))
            order_by_chapter.setdefault(chapter, []).append(verse)
            current_key = (chapter, verse)
            continue
        if ETHIOPIC_RE.search(line):
            if current_key:
                ethiopic_lines_by_verse[current_key] = (
                    ethiopic_lines_by_verse.get(current_key, 0) + 1
                )
            else:
                unassigned_ethiopic += 1

    return order_by_chapter, ethiopic_lines_by_verse, unassigned_ethiopic


def parse_chapter_file(path: Path) -> list[int]:
    verses: list[int] = []
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = VERSE_LINE_RE.match(raw_line.strip())
        if not match:
            continue
        verses.append(int(match.group("verse")))
    return verses


def load_overrides(path: Path | None) -> dict:
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def apply_overrides_to_list(values: list[int], chapter: int, overrides: dict) -> tuple[list[int], list[str]]:
    notes: list[str] = []
    if not overrides:
        return values, notes
    chapter_key = str(chapter)
    remap = (overrides.get("remap_verses_by_chapter") or {}).get(chapter_key, {})
    drop = set((overrides.get("drop_verses_by_chapter") or {}).get(chapter_key, []))
    max_verse = (overrides.get("max_verse_by_chapter") or {}).get(chapter_key)

    adjusted = []
    for verse in values:
        if remap and str(verse) in remap:
            new_verse = int(remap[str(verse)])
            notes.append(f"remap:{verse}->{new_verse}")
            verse = new_verse
        adjusted.append(verse)

    filtered = []
    for verse in adjusted:
        if max_verse is not None and verse > int(max_verse):
            notes.append(f"drop:{verse}:max")
            continue
        if verse in drop:
            notes.append(f"drop:{verse}:list")
            continue
        filtered.append(verse)

    return filtered, notes


def build_chapter_stats(
    chapter: int,
    order: list[int],
    ethiopic_lines_by_verse: dict[tuple[int, int], int],
    reference: list[int] | None,
):
    unique = sorted(set(order))
    duplicates = sorted({v for v in order if order.count(v) > 1})
    missing = []
    if unique:
        min_v, max_v = unique[0], unique[-1]
        missing = [v for v in range(min_v, max_v + 1) if v not in unique]
    non_monotonic = 0
    for prev, curr in zip(order, order[1:]):
        if curr < prev:
            non_monotonic += 1
    ethiopic_total = 0
    verses_no_ethiopic = 0
    for verse in unique:
        count = ethiopic_lines_by_verse.get((chapter, verse), 0)
        ethiopic_total += count
        if count == 0:
            verses_no_ethiopic += 1

    reference_count = len(reference) if reference is not None else None
    reference_missing = None
    if reference:
        ref_unique = sorted(set(reference))
        if ref_unique:
            min_ref, max_ref = ref_unique[0], ref_unique[-1]
            reference_missing = [v for v in range(min_ref, max_ref + 1) if v not in ref_unique]

    return {
        "chapter": chapter,
        "marker_count": len(order),
        "unique_verses": len(unique),
        "duplicates": duplicates,
        "missing_numbers": missing,
        "non_monotonic": non_monotonic,
        "ethiopic_lines_total": ethiopic_total,
        "verses_with_no_ethiopic": verses_no_ethiopic,
        "reference_count": reference_count,
        "reference_missing": reference_missing,
        "count_diff": None if reference_count is None else len(unique) - reference_count,
    }


def main():
    args = parse_args()
    repo_root = resolve_repo_root()
    text_path = resolve_path(args.text_file, repo_root)
    verse_dir = resolve_path(args.verse_dir, repo_root)
    overrides_path = resolve_path(args.verse_overrides, repo_root)
    report_path = resolve_path(args.report, repo_root)
    csv_path = resolve_path(args.csv, repo_root)

    if not text_path or not text_path.exists():
        raise SystemExit(f"Text source not found: {text_path}")

    text = text_path.read_text(encoding="utf-8", errors="replace")
    order_by_chapter, ethiopic_lines_by_verse, unassigned = parse_full_text(text)
    overrides = load_overrides(overrides_path)

    reference_by_chapter: dict[int, list[int]] = {}
    if verse_dir and verse_dir.exists():
        for path in verse_dir.iterdir():
            if not path.is_file():
                continue
            match = CHAPTER_FILE_RE.match(path.name)
            if not match:
                continue
            chapter = int(match.group(1))
            reference_by_chapter[chapter] = parse_chapter_file(path)

    chapters = sorted(set(order_by_chapter) | set(reference_by_chapter))
    if args.chapters:
        chapters = [c for c in chapters if c in set(args.chapters)]

    stats = []
    mismatches = []
    for chapter in chapters:
        order = order_by_chapter.get(chapter, [])
        reference = reference_by_chapter.get(chapter)
        order, order_notes = apply_overrides_to_list(order, chapter, overrides)
        if reference:
            reference, _ref_notes = apply_overrides_to_list(reference, chapter, overrides)
        entry = build_chapter_stats(chapter, order, ethiopic_lines_by_verse, reference)
        if order_notes:
            entry["override_notes"] = order_notes
        stats.append(entry)
        if entry["count_diff"]:
            mismatches.append(chapter)

    report = {
        "source_text": str(text_path),
        "reference_dir": str(verse_dir) if verse_dir else None,
        "unassigned_ethiopic_lines": unassigned,
        "mismatched_chapters": mismatches,
        "chapters": stats,
    }

    if report_path:
        ensure_dir(report_path.parent)
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if csv_path:
        ensure_dir(csv_path.parent)
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(
                [
                    "chapter",
                    "marker_count",
                    "unique_verses",
                    "duplicates",
                    "missing_numbers",
                    "non_monotonic",
                    "ethiopic_lines_total",
                    "verses_with_no_ethiopic",
                    "reference_count",
                    "reference_missing",
                    "count_diff",
                ]
            )
            for entry in stats:
                writer.writerow(
                    [
                        entry["chapter"],
                        entry["marker_count"],
                        entry["unique_verses"],
                        ",".join(map(str, entry["duplicates"])),
                        ",".join(map(str, entry["missing_numbers"])),
                        entry["non_monotonic"],
                        entry["ethiopic_lines_total"],
                        entry["verses_with_no_ethiopic"],
                        entry["reference_count"] if entry["reference_count"] is not None else "",
                        ",".join(map(str, entry["reference_missing"] or [])),
                        entry["count_diff"] if entry["count_diff"] is not None else "",
                    ]
                )

    print(f"Done. Chapters audited: {len(stats)}.")


if __name__ == "__main__":
    main()
