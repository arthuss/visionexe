import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

from pypdf import PdfReader

from visionexe_paths import ensure_dir, resolve_repo_root, resolve_path


CHAPTER_RE = re.compile(r"^\s*Chapter\s+(?P<num>\d{1,3})\b", re.IGNORECASE)
VERSE_MARKER_RE = re.compile(
    r"\b(?:[A-Z]{1,3}\s*)?(?P<chapter>\d{1,3})\s*:\s*(?P<verse>\d{1,3})\b"
)
ETHIOPIC_RE = re.compile(r"[\u1200-\u137f]")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract Ge'ez verse lines from a Henoch text source."
    )
    parser.add_argument(
        "--pdf",
        default="docs/ethiopic_1enoch_p/Henoch_from_Geez_text.pdf",
        help="Path to the PDF source.",
    )
    parser.add_argument(
        "--text-file",
        default="docs/ethiopic_1enoch_p/full_henoch_108.txt",
        help="Path to a plaintext source (preferred).",
    )
    parser.add_argument(
        "--output-dir",
        default="docs/ethiopic_1enoch_p",
        help="Directory for chapter_XX.txt outputs.",
    )
    parser.add_argument(
        "--verse-overrides",
        default="docs/ethiopic_1enoch_p/verse_overrides.json",
        help="Optional JSON overrides for verse fixes.",
    )
    parser.add_argument(
        "--chapters",
        nargs="*",
        type=int,
        help="Chapter numbers to extract (default: 72-108).",
    )
    parser.add_argument("--use-gemini", action="store_true", help="Use Gemini CLI.")
    parser.add_argument("--model", help="Gemini model name.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing chapter files.")
    parser.add_argument("--report", help="Write a JSON report to this path.")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without writing.")
    return parser.parse_args()


def resolve_gemini_command():
    gemini_path = shutil.which("gemini") or shutil.which("gemini.cmd")
    if gemini_path:
        return [gemini_path]

    npx_path = shutil.which("npx") or shutil.which("npx.cmd")
    if npx_path:
        return [npx_path, "-y", "@google/gemini-cli"]

    return None


def parse_gemini_response(raw_output: str | None) -> str | None:
    if not raw_output:
        return None
    json_start = raw_output.find("{")
    if json_start == -1:
        return raw_output.strip()
    json_text = raw_output[json_start:]
    json_end = json_text.rfind("}")
    if json_end != -1:
        json_text = json_text[:json_end + 1]
    try:
        payload = json.loads(json_text)
        response = payload.get("response")
        if isinstance(response, str):
            return response.strip()
    except json.JSONDecodeError:
        return raw_output.strip()
    return None


def call_gemini(prompt: str, model: str | None) -> str | None:
    cmd = resolve_gemini_command()
    if not cmd:
        print("Gemini CLI nicht gefunden (gemini/npx).")
        return None
    cmd = cmd + ["--output-format", "json"]
    if model:
        cmd += ["--model", model]
    try:
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
        stdout, stderr = process.communicate(input=prompt)
        if process.returncode != 0:
            print(f"Gemini Fehler: {stderr}")
            return None
        return parse_gemini_response(stdout)
    except OSError as exc:
        print(f"Gemini Start fehlgeschlagen: {exc}")
        return None


def log(msg: str) -> None:
    print(msg)


def is_toc_page(text: str) -> bool:
    if not text:
        return False
    lines = [line for line in text.splitlines() if line.strip()]
    chapter_hits = sum(1 for line in lines if CHAPTER_RE.search(line))
    underscore_hits = sum(1 for line in lines if "____" in line)
    return chapter_hits >= 4 and underscore_hits >= 2


def collect_chapter_blocks(reader: PdfReader) -> dict[int, list[str]]:
    blocks: dict[int, list[str]] = {}
    current = None
    for page in reader.pages:
        text = page.extract_text() or ""
        if is_toc_page(text):
            continue
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            match = CHAPTER_RE.match(line)
            if match:
                current = int(match.group("num"))
                blocks.setdefault(current, [])
                continue
            if current is not None:
                blocks[current].append(raw_line.rstrip())
    return blocks


def collect_chapter_blocks_from_text(text: str) -> dict[int, list[str]]:
    blocks: dict[int, list[str]] = {}
    current = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = CHAPTER_RE.match(line)
        if match:
            current = int(match.group("num"))
            blocks.setdefault(current, [])
            continue
        if current is not None:
            blocks[current].append(raw_line.rstrip())
    return blocks


def summarize_lines(lines: list[str]) -> tuple[int, int]:
    marker_count = 0
    ethiopic_count = 0
    for line in lines:
        if VERSE_MARKER_RE.search(line):
            marker_count += 1
        if ETHIOPIC_RE.search(line):
            ethiopic_count += 1
    return marker_count, ethiopic_count


def clean_ethiopic_line(line: str) -> str | None:
    match = ETHIOPIC_RE.search(line)
    if not match:
        return None
    return line[match.start():].strip()


def extract_verses(lines: list[str], chapter: int) -> tuple[list[dict], list[int]]:
    verses: list[dict] = []
    missing: list[int] = []
    pending: list[str] = []
    seen: set[tuple[int, int]] = set()
    for raw_line in lines:
        marker = VERSE_MARKER_RE.search(raw_line)
        if marker:
            verse_chapter = int(marker.group("chapter"))
            verse_number = int(marker.group("verse"))
            if verse_chapter != chapter:
                continue
            key = (verse_chapter, verse_number)
            if pending:
                text = " ".join(pending).strip()
                if key in seen:
                    for item in verses:
                        if item["verse"] == verse_number:
                            item["text"] = f"{item['text']} {text}".strip()
                            break
                else:
                    verses.append({"verse": verse_number, "text": text, "uncertain": False})
                pending = []
            else:
                if key not in seen:
                    missing.append(verse_number)
            seen.add(key)
            continue
        cleaned = clean_ethiopic_line(raw_line)
        if cleaned:
            pending.append(cleaned)
    return verses, missing


def extract_verses_from_text(text: str) -> tuple[dict[int, list[dict]], dict[int, list[int]], int]:
    verses_by_chapter: dict[int, list[dict]] = {}
    missing_by_chapter: dict[int, list[int]] = {}
    pending: list[str] = []
    seen: set[tuple[int, int]] = set()
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        marker = VERSE_MARKER_RE.search(line)
        if marker:
            chapter = int(marker.group("chapter"))
            verse = int(marker.group("verse"))
            key = (chapter, verse)
            if pending:
                text_line = " ".join(pending).strip()
                if key in seen:
                    for item in verses_by_chapter.get(chapter, []):
                        if item["verse"] == verse:
                            item["text"] = f"{item['text']} {text_line}".strip()
                            break
                else:
                    verses_by_chapter.setdefault(chapter, []).append(
                        {"verse": verse, "text": text_line, "uncertain": False}
                    )
                pending = []
            else:
                if key not in seen:
                    missing_by_chapter.setdefault(chapter, []).append(verse)
            seen.add(key)
            continue
        cleaned = clean_ethiopic_line(line)
        if cleaned:
            pending.append(cleaned)
    return verses_by_chapter, missing_by_chapter, len(pending)


def build_prompt(chapter: int, lines: list[str]) -> str:
    markers = []
    ethiopic_lines = []
    for line in lines:
        marker = VERSE_MARKER_RE.search(line)
        if marker:
            markers.append(line.strip())
        if ETHIOPIC_RE.search(line):
            ethiopic_lines.append(line.strip())

    marker_block = "\n".join(markers) if markers else "(none)"
    ethiopic_block = "\n".join(ethiopic_lines)

    return (
        f"You are extracting Ge'ez verses for 1 Enoch Chapter {chapter}.\n"
        "Return JSON only with this schema:\n"
        "{\n"
        '  "chapter": <int>,\n'
        '  "verses": [\n'
        '    {"verse": <int>, "text": "<Ge\'ez text>", "uncertain": <bool>}\n'
        "  ]\n"
        "}\n\n"
        "Rules:\n"
        "- Use only Ethiopic text present in the input.\n"
        "- Preserve order.\n"
        "- Merge Ethiopic lines that belong to the same verse with a single space.\n"
        "- Use verse markers when available; if inferred, set uncertain=true.\n"
        "- Do not output English or translations.\n\n"
        f"Verse markers (English lines):\n{marker_block}\n\n"
        f"Ethiopic lines (order preserved):\n{ethiopic_block}\n"
    )


def parse_json_payload(raw_text: str | None) -> dict | None:
    if not raw_text:
        return None
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        json_start = raw_text.find("{")
        json_end = raw_text.rfind("}")
        if json_start == -1 or json_end == -1 or json_end <= json_start:
            return None
        try:
            return json.loads(raw_text[json_start : json_end + 1])
        except json.JSONDecodeError:
            return None


def write_chapter_file(output_dir: Path, chapter: int, verses: list[dict], force: bool, dry_run: bool) -> Path | None:
    filename = f"chapter_{chapter:02d}.txt"
    path = output_dir / filename
    if path.exists() and not force:
        return None
    lines = []
    for verse in verses:
        number = verse.get("verse")
        text = (verse.get("text") or "").strip()
        if not number or not text:
            continue
        lines.append(f"{chapter}:{int(number)} {text}")
    content = "\n".join(lines).strip() + "\n"
    if dry_run:
        print(f"[dry-run] write {path}")
        return path
    ensure_dir(output_dir)
    path.write_text(content, encoding="utf-8")
    return path


def load_overrides(path: Path | None) -> dict:
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def apply_overrides(verses: list[dict], chapter: int, overrides: dict) -> tuple[list[dict], list[str]]:
    notes: list[str] = []
    if not overrides:
        return verses, notes

    chapter_key = str(chapter)
    remap = (overrides.get("remap_verses_by_chapter") or {}).get(chapter_key, {})
    drop = set((overrides.get("drop_verses_by_chapter") or {}).get(chapter_key, []))
    max_verse = (overrides.get("max_verse_by_chapter") or {}).get(chapter_key)

    merged: dict[int, dict] = {}
    for entry in verses:
        verse_num = int(entry["verse"])
        if remap and str(verse_num) in remap:
            new_verse = int(remap[str(verse_num)])
            notes.append(f"remap:{verse_num}->{new_verse}")
            verse_num = new_verse
        text = entry.get("text", "").strip()
        if verse_num in merged:
            merged[verse_num]["text"] = f"{merged[verse_num]['text']} {text}".strip()
        else:
            merged[verse_num] = {
                "verse": verse_num,
                "text": text,
                "uncertain": entry.get("uncertain", False),
            }

    filtered = []
    for verse_num in sorted(merged.keys()):
        if max_verse is not None and verse_num > int(max_verse):
            notes.append(f"drop:{verse_num}:max")
            continue
        if verse_num in drop:
            notes.append(f"drop:{verse_num}:list")
            continue
        filtered.append(merged[verse_num])

    return filtered, notes


def main():
    args = parse_args()
    repo_root = resolve_repo_root()
    pdf_path = resolve_path(args.pdf, repo_root)
    text_path = resolve_path(args.text_file, repo_root)
    output_dir = resolve_path(args.output_dir, repo_root)
    overrides_path = resolve_path(args.verse_overrides, repo_root)

    chapters = args.chapters or list(range(72, 109))

    blocks = {}
    used_source = None
    verses_by_chapter = {}
    missing_by_chapter = {}
    trailing_unassigned = 0
    if text_path and text_path.exists():
        text = text_path.read_text(encoding="utf-8", errors="replace")
        verses_by_chapter, missing_by_chapter, trailing_unassigned = extract_verses_from_text(text)
        used_source = f"text:{text_path}"
    elif pdf_path and pdf_path.exists():
        if args.use_gemini and not resolve_gemini_command():
            raise SystemExit("Gemini CLI not found (gemini/npx).")
        reader = PdfReader(str(pdf_path))
        log(f"Loaded PDF: {pdf_path} ({len(reader.pages)} pages)")
        blocks = collect_chapter_blocks(reader)
        used_source = f"pdf:{pdf_path}"
    else:
        raise SystemExit("No source found: provide --text-file or --pdf.")

    detected_count = len(verses_by_chapter) if verses_by_chapter else len(blocks)
    log(f"Detected chapters in source: {detected_count} ({used_source})")
    if trailing_unassigned:
        log(f"Trailing Ethiopic lines without verse marker: {trailing_unassigned}")

    overrides = load_overrides(overrides_path)
    report = {"written": [], "skipped": [], "missing": [], "errors": [], "overrides": []}

    for chapter in chapters:
        lines = blocks.get(chapter)
        if verses_by_chapter:
            verses = verses_by_chapter.get(chapter, [])
            missing_verses = missing_by_chapter.get(chapter, [])
            if not verses:
                report["missing"].append({"chapter": chapter, "reason": "no verses parsed"})
                log(f"Chapter {chapter}: no verses parsed from text.")
                continue
        else:
            verses = []
            missing_verses = []
        if not verses_by_chapter and not lines:
            report["missing"].append({"chapter": chapter, "reason": "no chapter block"})
            log(f"Chapter {chapter}: missing in source blocks.")
            continue

        if not verses_by_chapter:
            marker_count, ethiopic_count = summarize_lines(lines)
            log(
                f"Chapter {chapter}: {len(lines)} lines, "
                f"{marker_count} markers, {ethiopic_count} Ethiopic lines"
            )
            prompt = build_prompt(chapter, lines)
            if not args.use_gemini:
                report["errors"].append({"chapter": chapter, "reason": "gemini disabled"})
                log(f"Chapter {chapter}: skipped (gemini disabled).")
                continue

            response = call_gemini(prompt, args.model)
            payload = parse_json_payload(response)
            if not payload:
                report["errors"].append({"chapter": chapter, "reason": "invalid json"})
                log(f"Chapter {chapter}: Gemini returned invalid JSON.")
                continue

            verses = payload.get("verses") or []
            if not verses:
                report["errors"].append({"chapter": chapter, "reason": "no verses"})
                log(f"Chapter {chapter}: Gemini returned no verses.")
                continue
            missing_verses = [v["verse"] for v in verses if v.get("uncertain")]
        else:
            log(
                f"Chapter {chapter}: parsed {len(verses)} verses "
                f"({len(missing_verses)} missing markers)"
            )

        verses, override_notes = apply_overrides(verses, chapter, overrides)
        if override_notes:
            report["overrides"].append({"chapter": chapter, "notes": override_notes})
            log(f"Chapter {chapter}: overrides applied ({', '.join(override_notes)})")

        written = write_chapter_file(output_dir, chapter, verses, args.force, args.dry_run)
        if written:
            report["written"].append(
                {
                    "chapter": chapter,
                    "path": str(written),
                    "verse_count": len(verses),
                    "uncertain_count": len(missing_verses),
                    "override_notes": override_notes,
                }
            )
            log(
                f"Chapter {chapter}: wrote {written} "
                f"({len(verses)} verses, {len(missing_verses)} missing)"
            )
        else:
            report["skipped"].append({"chapter": chapter, "reason": "exists"})
            log(f"Chapter {chapter}: skipped (file exists).")

        for verse_num in missing_verses:
            report["missing"].append(
                {"chapter": chapter, "reason": "missing verse text", "verse": verse_num}
            )

    if args.report:
        report_path = resolve_path(args.report, repo_root)
    else:
        report_path = output_dir / "verse_extraction_report.json"

    if report_path and not args.dry_run:
        ensure_dir(report_path.parent)
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    log(
        "Done. "
        f"Written: {len(report['written'])}, "
        f"Skipped: {len(report['skipped'])}, "
        f"Missing: {len(report['missing'])}, "
        f"Errors: {len(report['errors'])}."
    )


if __name__ == "__main__":
    main()
