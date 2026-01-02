"""
Aggregates Henoch/Enoch Kapitel from local sources and splits them into
per-chapter UTF-8 text files.

Sources:
- Exploring Egyptian Antiquities and Research (JSON with chunkedPrompt/chunks[*].text)
- 1.md, 2.md, 3.md (plain markdown)

Heuristics for Kapitel-Start (beginning of a block):
- Lines starting with "<number> 1" (chapter + verse 1 in Ge'ez)
- Lines starting with "Kapitel <number>"
- Lines starting with "Henoch <number>"
- Lines starting with "1. Henoch <number>"

Output: local_enoch_chapters_full/chapter_XX.txt (or chapter_XX_N.txt for duplicates)
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

JSON_SOURCE = Path("Exploring Egyptian Antiquities and Research")
PLAIN_SOURCES = [Path("1.md"), Path("2.md"), Path("3.md")]
OUTPUT_DIR = Path("local_enoch_chapters_full")


def load_json_text(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    chunks = data.get("chunkedPrompt", {}).get("chunks", [])
    texts = [c.get("text", "") for c in chunks if c.get("text")]
    return "\n".join(texts)


def load_plain_text(paths: Iterable[Path]) -> str:
    texts: List[str] = []
    for p in paths:
        if p.exists():
            texts.append(p.read_text(encoding="utf-8"))
    return "\n".join(texts)


@dataclass
class Marker:
    chapter: int
    pos: int


def find_markers(text: str) -> List[Marker]:
    patterns = [
        r"(?m)(?<!\d)(?P<num>\d{1,3})\s+1\b",          # numeric with verse 1 (anywhere)
        r"(?m)Kapitel\s+(?P<num>\d{1,3})\b",           # Kapitel 40
        r"(?m)Henoch\s+(?P<num>\d{1,3})\b",            # Henoch 40
        r"(?m)1\.\s*Henoch\s+(?P<num>\d{1,3})\b",      # 1. Henoch 40
    ]

    markers: List[Marker] = []
    for pat in patterns:
        for m in re.finditer(pat, text):
            num = int(m.group("num"))
            markers.append(Marker(num, m.start()))

    # Deduplicate by position (keep earliest for same position)
    markers.sort(key=lambda m: m.pos)
    unique: List[Marker] = []
    seen_pos = set()
    for m in markers:
        if m.pos in seen_pos:
            continue
        seen_pos.add(m.pos)
        unique.append(m)
    return unique


def split_blocks(text: str, markers: List[Marker]) -> dict[int, List[str]]:
    chapters: dict[int, List[str]] = defaultdict(list)
    for i, m in enumerate(markers):
        start = m.pos
        end = markers[i + 1].pos if i + 1 < len(markers) else len(text)
        block = text[start:end].strip()
        chapters[m.chapter].append(block)
    return chapters


def write_blocks(chapters: dict[int, List[str]]) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    for chap, blocks in sorted(chapters.items()):
        for idx, block in enumerate(blocks, start=1):
            suffix = f"_{idx}" if len(blocks) > 1 else ""
            out_path = OUTPUT_DIR / f"chapter_{chap:03d}{suffix}.txt"
            out_path.write_text(block, encoding="utf-8")


def main() -> None:
    combined = "\n\n".join(
        [
            load_json_text(JSON_SOURCE),
            load_plain_text(PLAIN_SOURCES),
        ]
    )
    markers = find_markers(combined)
    if not markers:
        print("No markers found.")
        return
    chapters = split_blocks(combined, markers)
    write_blocks(chapters)
    print(f"Found {len(markers)} markers, {len(chapters)} unique chapters.")
    print(f"Output dir: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
