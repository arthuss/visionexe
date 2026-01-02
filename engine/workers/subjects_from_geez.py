import argparse
import json
import time
from pathlib import Path

from visionexe_paths import ensure_dir, load_story_config, resolve_path

ETHIOPIC_RANGES = (
    (0x1200, 0x137F),  # Ethiopic
    (0x1380, 0x139F),  # Ethiopic Supplement
    (0x2D80, 0x2DDF),  # Ethiopic Extended
    (0xAB00, 0xAB2F),  # Ethiopic Extended-A
)

ETHIOPIC_PUNCT = set(range(0x1361, 0x1369))
ETHIOPIC_NUMERALS = set(range(0x1369, 0x137D))


def is_ethiopic_letter(ch: str) -> bool:
    code = ord(ch)
    if not any(start <= code <= end for start, end in ETHIOPIC_RANGES):
        return False
    if code in ETHIOPIC_PUNCT or code in ETHIOPIC_NUMERALS:
        return False
    return True


def iter_tokens(text: str, min_len: int):
    buffer = []
    for ch in text:
        if is_ethiopic_letter(ch):
            buffer.append(ch)
            continue
        if len(buffer) >= min_len:
            yield "".join(buffer)
        buffer = []
    if len(buffer) >= min_len:
        yield "".join(buffer)


def load_stoplist(path: Path | None) -> set[str]:
    if not path or not path.exists():
        return set()
    tokens = set()
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            cleaned = line.strip()
            if not cleaned or cleaned.startswith("#"):
                continue
            tokens.add(cleaned)
    return tokens


def parse_chapter_from_name(path: Path) -> int | None:
    stem = path.stem
    parts = stem.split("_")
    if len(parts) < 2:
        return None
    try:
        return int(parts[1])
    except ValueError:
        return None


def main():
    parser = argparse.ArgumentParser(description="Extract Ge'ez subject candidates from verse JSONL.")
    parser.add_argument("--story-root", help="Story root path (defaults to engine_config default_story_root).")
    parser.add_argument("--story-config", help="Path to story_config.json (overrides story-root).")
    parser.add_argument("--geez-root", help="Root folder containing chapter_###_verses.jsonl.")
    parser.add_argument("--stoplist", help="Optional stoplist file (one token per line).")
    parser.add_argument("--min-len", type=int, default=2, help="Minimum token length to keep.")
    parser.add_argument("--max-samples", type=int, default=4, help="Max samples per candidate.")
    parser.add_argument("--max-sample-chars", type=int, default=240, help="Max chars stored in sample text.")
    parser.add_argument("--max-occurrences", type=int, default=0, help="Stop after N occurrences (0 = no limit).")
    parser.add_argument("--candidates-out", help="Output candidates JSON path.")
    parser.add_argument("--occurrences-out", help="Output occurrences JSONL path.")
    args = parser.parse_args()

    story_config, _, repo_root = load_story_config(
        story_root=args.story_root,
        story_config_path=args.story_config,
    )

    data_root = story_config.get("data_root") or "stories/template/data"
    data_root = resolve_path(data_root, repo_root)
    default_geez_root = data_root / "raw" / "henoch_geez"
    geez_root = resolve_path(args.geez_root or str(default_geez_root), repo_root)

    if not geez_root.exists():
        raise SystemExit(f"Ge'ez root not found: {geez_root}")

    subjects_root = resolve_path(story_config.get("subjects_root"), repo_root)
    ensure_dir(subjects_root)

    candidates_out = resolve_path(
        args.candidates_out or f"{subjects_root}/subject_candidates_geez.json",
        repo_root,
    )
    occurrences_out = resolve_path(
        args.occurrences_out or f"{subjects_root}/subject_occurrences_geez.jsonl",
        repo_root,
    )

    stoplist_path = resolve_path(args.stoplist, repo_root) if args.stoplist else None
    stoplist = load_stoplist(stoplist_path)

    verse_files = sorted(geez_root.glob("chapter_*_verses.jsonl"))
    if not verse_files:
        raise SystemExit(f"No verse files found under: {geez_root}")

    candidate_map = {}
    occurrence_total = 0
    verse_total = 0

    with occurrences_out.open("w", encoding="utf-8") as occ_handle:
        for verse_path in verse_files:
            chapter = parse_chapter_from_name(verse_path)
            with verse_path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    record = json.loads(line)
                    verse_total += 1
                    verse_chapter = record.get("chapter") or chapter
                    verse_number = record.get("verse")
                    verse_text = record.get("text", "")

                    tokens = list(iter_tokens(verse_text, args.min_len))
                    for token_index, token in enumerate(tokens):
                        if token in stoplist:
                            continue
                        occurrence_total += 1
                        if args.max_occurrences and occurrence_total > args.max_occurrences:
                            break

                        source_id = f"geez_{int(verse_chapter):03d}_{int(verse_number):03d}" if verse_chapter and verse_number else ""
                        occ = {
                            "token": token,
                            "chapter": int(verse_chapter) if verse_chapter else None,
                            "verse": int(verse_number) if verse_number else None,
                            "token_index": token_index,
                            "token_count": len(tokens),
                            "source_id": source_id,
                            "source_path": str(verse_path),
                            "verse_text": verse_text,
                            "language": "geez",
                        }
                        occ_handle.write(json.dumps(occ, ensure_ascii=False) + "\n")

                        data = candidate_map.setdefault(token, {
                            "count": 0,
                            "chapters": set(),
                            "verses": set(),
                            "samples": [],
                        })
                        data["count"] += 1
                        if verse_chapter:
                            data["chapters"].add(int(verse_chapter))
                        if verse_chapter and verse_number:
                            data["verses"].add(f"{int(verse_chapter)}:{int(verse_number)}")

                        if len(data["samples"]) < args.max_samples:
                            sample_text = verse_text
                            if args.max_sample_chars and len(sample_text) > args.max_sample_chars:
                                sample_text = sample_text[: args.max_sample_chars].rstrip() + "..."
                            data["samples"].append({
                                "chapter": int(verse_chapter) if verse_chapter else None,
                                "verse": int(verse_number) if verse_number else None,
                                "text": sample_text,
                                "source_id": source_id,
                            })

                    if args.max_occurrences and occurrence_total >= args.max_occurrences:
                        break
            if args.max_occurrences and occurrence_total >= args.max_occurrences:
                break

    candidates = []
    for token, data in candidate_map.items():
        candidates.append({
            "token": token,
            "count": data["count"],
            "chapter_count": len(data["chapters"]),
            "verse_count": len(data["verses"]),
            "chapters": sorted(data["chapters"]),
            "samples": data["samples"],
        })

    candidates.sort(key=lambda item: (-item["count"], item["token"]))

    payload = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "story_id": story_config.get("story_id"),
        "geez_root": str(geez_root),
        "min_len": args.min_len,
        "max_samples": args.max_samples,
        "max_sample_chars": args.max_sample_chars,
        "stoplist": str(stoplist_path) if stoplist_path else "",
        "candidate_count": len(candidates),
        "occurrence_count": occurrence_total,
        "verse_count": verse_total,
        "candidates": candidates,
    }

    candidates_out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote candidates: {candidates_out}")
    print(f"Wrote occurrences: {occurrences_out}")


if __name__ == "__main__":
    main()
