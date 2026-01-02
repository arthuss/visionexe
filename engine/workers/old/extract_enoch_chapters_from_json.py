"""
Extracts Henoch/Enoch chapters from the local conversation log
`Exploring Egyptian Antiquities and Research` and saves each chapter
as a separate UTF-8 text file.

Heuristics:
- The source file is JSON with a `chunkedPrompt.chunks` list.
- Each chapter starts with a number followed by verse 1, e.g. "34 1 ".
- We split on every occurrence of "(chapter_number) 1" that is not
  preceded by another digit.

Output: ./local_enoch_chapters/chapter_XX.txt (or chapter_XX_Y.txt for
duplicates).
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

SOURCE_FILE = Path("Exploring Egyptian Antiquities and Research")
OUTPUT_DIR = Path("local_enoch_chapters")


def load_text() -> str:
    """Load and concatenate all `text` fields from the JSON source."""
    data = json.loads(SOURCE_FILE.read_text(encoding="utf-8"))
    chunks = data.get("chunkedPrompt", {}).get("chunks", [])
    texts = [c.get("text", "") for c in chunks if c.get("text")]
    return "\n".join(texts)


def split_chapters(all_text: str) -> dict[int, list[str]]:
    """
    Find chapter blocks by the pattern "<number> 1" (not preceded by a digit)
    and return a mapping of chapter number -> list of blocks.
    """
    starts = list(re.finditer(r"(?<!\d)(\d{1,3})\s+1\b", all_text))
    chapters: dict[int, list[str]] = defaultdict(list)

    for i, match in enumerate(starts):
        chapter_num = int(match.group(1))
        start = match.start()
        end = starts[i + 1].start() if i + 1 < len(starts) else len(all_text)
        block = all_text[start:end].strip()
        chapters[chapter_num].append(block)

    return chapters


def clean_block(block: str) -> str:
    """
    Normalize a chapter block to verse-per-line.
    Drops trailing/non-verse commentary by only keeping segments that start
    with a verse number.
    """
    parts = block.strip().split(maxsplit=1)
    if len(parts) < 2:
        return block.strip()

    # Remove leading chapter number to isolate verse sequence.
    _, remainder = parts[0], parts[1]

    verses = []
    for match in re.finditer(r"(\d{1,3})\s+([^\d]+?)(?=(?:\s+\d{1,3}\s)|$)", remainder, flags=re.S):
        verse_num, verse_text = match.groups()
        verses.append(f"{verse_num} {verse_text.strip()}")

    return "\n".join(verses) if verses else block.strip()


def write_chapters(chapters: dict[int, list[str]]) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    for chapter_num, blocks in sorted(chapters.items()):
        for idx, block in enumerate(blocks, start=1):
            suffix = f"_{idx}" if len(blocks) > 1 else ""
            filename = OUTPUT_DIR / f"chapter_{chapter_num:02d}{suffix}.txt"
            filename.write_text(clean_block(block), encoding="utf-8")


def main() -> None:
    all_text = load_text()
    chapters = split_chapters(all_text)
    write_chapters(chapters)
    print(f"Extracted {sum(len(v) for v in chapters.values())} chapter blocks.")
    print(f"Unique chapters: {sorted(chapters)}")
    print(f"Output dir: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
