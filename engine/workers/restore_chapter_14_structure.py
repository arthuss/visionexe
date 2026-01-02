import argparse
import os
import re
import shutil
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Restore chapter_014 structure from the source 14.txt file."
    )
    root = Path(__file__).resolve().parent
    parser.add_argument(
        "--source",
        default=str(root / "HENOCH-Exeget" / "14.txt"),
        help="Source 14.txt path.",
    )
    parser.add_argument(
        "--chapter-dir",
        default=str(root / "filmsets" / "chapter_014"),
        help="Target chapter_014 directory.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files (creates .bak copies).",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip creating .bak backups when overwriting.",
    )
    return parser.parse_args()


def read_lines(path):
    return Path(path).read_text(encoding="utf-8", errors="replace").splitlines()


def extract_verses(lines):
    verses = []
    for line in lines:
        match = re.match(r"^14:(\d+)\s*(.*)$", line)
        if match:
            verses.append((int(match.group(1)), line))
    return verses


def slice_section(lines, start_prefix, end_prefixes):
    section = []
    capture = False
    for line in lines:
        if line.startswith(start_prefix):
            capture = True
        elif capture and any(line.startswith(prefix) for prefix in end_prefixes):
            break
        if capture:
            section.append(line)
    return section


def extract_weg(visual_lines, label):
    prefix = f"#### **Weg {label.upper()}:"
    section = []
    capture = False
    for line in visual_lines:
        if line.startswith(prefix):
            capture = True
        elif capture and line.startswith("#### **Weg "):
            break
        if capture:
            section.append(line)
    return section


def ensure_dirs(chapter_dir):
    subfolders = [
        "analysis_linguistik",
        "tech_hypothesen",
        "visual_abc",
        "einleitung",
        "integration_wave",
        "concept_engine",
        "produced_assets",
    ]
    for name in subfolders:
        (chapter_dir / name).mkdir(parents=True, exist_ok=True)
    for name in ["weg_a", "weg_b", "weg_c"]:
        (chapter_dir / "visual_abc" / name).mkdir(parents=True, exist_ok=True)


def write_text(path, content, overwrite, backup):
    path = Path(path)
    if path.exists() and not overwrite:
        return False
    if path.exists() and backup:
        backup_path = path.with_suffix(path.suffix + ".bak")
        if not backup_path.exists():
            shutil.copy2(path, backup_path)
    path.write_text(content, encoding="utf-8")
    return True


def main():
    args = parse_args()
    source_path = Path(args.source)
    chapter_dir = Path(args.chapter_dir)

    if not source_path.exists():
        raise SystemExit(f"Source file not found: {source_path}")

    ensure_dirs(chapter_dir)
    lines = read_lines(source_path)
    verses = extract_verses(lines)

    section_1 = slice_section(lines, "### 1.", ["### 2.", "### 3.", "### 4."])
    section_2 = slice_section(lines, "### 2.", ["### 3.", "### 4."])
    section_3 = slice_section(lines, "### 3.", ["### 4."])
    section_4 = slice_section(lines, "### 4.", [])

    weg_a = extract_weg(section_3, "A")
    weg_b = extract_weg(section_3, "B")
    weg_c = extract_weg(section_3, "C")

    backup = not args.no_backup
    writes = []

    verse_lines = [line for _, line in verses]
    if verse_lines:
        analysis_story = "\n".join(verse_lines + [""] + section_1).strip() + "\n"
        writes.append(
            ("analysis_linguistik/story.txt", analysis_story)
        )

    source_body = [line for line in section_1 if not line.startswith("### 1.")]
    if source_body:
        tech_story = "\n".join(source_body).strip() + "\n"
        writes.append(("tech_hypothesen/story.txt", tech_story))

    if section_2:
        einleitung_story = "\n".join(section_2).strip() + "\n"
        writes.append(("einleitung/story.txt", einleitung_story))

    if section_3:
        visual_story = "\n".join(section_3).strip() + "\n"
        writes.append(("visual_abc/story.txt", visual_story))

    if section_4:
        integration_story = "\n".join(section_4).strip() + "\n"
        writes.append(("integration_wave/story.txt", integration_story))

    if weg_a:
        writes.append(("visual_abc/weg_a/story.txt", "\n".join(weg_a).strip() + "\n"))
    if weg_b:
        writes.append(("visual_abc/weg_b/story.txt", "\n".join(weg_b).strip() + "\n"))
    if weg_c:
        writes.append(("visual_abc/weg_c/story.txt", "\n".join(weg_c).strip() + "\n"))

    story_written = 0
    for rel_path, content in writes:
        target = chapter_dir / rel_path
        if write_text(target, content, args.overwrite, backup):
            story_written += 1

    verse_written = 0
    for num, line in verses:
        verse_dir = chapter_dir / f"verse_{num:03d}"
        verse_dir.mkdir(parents=True, exist_ok=True)
        verse_path = verse_dir / "verse.txt"
        if write_text(verse_path, line.strip() + "\n", args.overwrite, backup):
            verse_written += 1

    print(f"Story files written: {story_written}")
    print(f"Verse files written: {verse_written}")
    print(f"Chapter dir: {chapter_dir}")


if __name__ == "__main__":
    main()
