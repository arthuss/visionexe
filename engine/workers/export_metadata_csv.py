#!/usr/bin/env python
"""
Sammelt alle verse-level metadata.json unterhalb von filmsets und schreibt zwei CSVs:
 - verses.csv  : eine Zeile pro Vers mit Actors-/Scene-Infos aggregiert
 - actors.csv  : eine Zeile pro Actor (mit Verse-Referenzen)

Aufruf:
    python export_metadata_csv.py [basispfad]

Standard-Basispfad ist ./filmsets
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


def main() -> None:
    base = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("filmsets")
    if not base.exists():
        sys.exit(f"Basisordner nicht gefunden: {base}")

    verse_rows: List[Dict[str, Any]] = []
    actor_rows: List[Dict[str, Any]] = []

    for meta_file in base.rglob("metadata.json"):
        data = load_json(meta_file)
        if not data:
            continue

        chapter = data.get("chapter")
        verse_id = data.get("verseId") or data.get("verse_id")
        verse_range = data.get("verseRange") or data.get("range") or ""
        source_file = data.get("sourceFile") or ""
        text_preview = clean_text(data.get("textPreview") or "")

        actors = data.get("actors") or []
        scenes = data.get("scenes") or []

        actor_names = uniq([a.get("name", "") for a in actors])
        actor_traits = uniq(
            part for a in actors for part in (a.get("traits") or [])
        )
        actor_changes = uniq(
            part for a in actors for part in (a.get("changes") or [])
        )

        scene_beats = uniq(
            (s.get("beat") or s.get("description") or "") for s in scenes
        )
        scene_locations = uniq(s.get("location", "") for s in scenes)
        scene_props = uniq(
            part for s in scenes for part in (s.get("props") or [])
        )
        scene_looks = uniq(s.get("look", "") for s in scenes)

        verse_rows.append(
            {
                "chapter": chapter,
                "verse_id": verse_id,
                "verse_range": verse_range,
                "source_file": source_file,
                "text_preview": text_preview,
                "actors": join(actor_names),
                "actor_traits": join(actor_traits),
                "actor_changes": join(actor_changes),
                "scene_beats": join(scene_beats),
                "scene_locations": join(scene_locations),
                "scene_props": join(scene_props),
                "scene_looks": join(scene_looks),
                "actor_count": len(actor_names),
                "scene_count": len(scenes),
                "meta_path": str(meta_file),
            }
        )

        for actor in actors:
            actor_rows.append(
                {
                    "chapter": chapter,
                    "verse_range_ref": join(uniq(actor.get("verses") or [])),
                    "name": actor.get("name", ""),
                    "traits": join(uniq(actor.get("traits") or [])),
                    "changes": join(uniq(actor.get("changes") or [])),
                    "visual": clean_text(actor.get("visual") or ""),
                    "source_file": source_file,
                    "meta_path": str(meta_file),
                }
            )

    out_dir = Path.cwd()
    write_csv(out_dir / "verses.csv", verse_rows, [
        "chapter",
        "verse_id",
        "verse_range",
        "source_file",
        "text_preview",
        "actors",
        "actor_traits",
        "actor_changes",
        "scene_beats",
        "scene_locations",
        "scene_props",
        "scene_looks",
        "actor_count",
        "scene_count",
        "meta_path",
    ])

    write_csv(out_dir / "actors.csv", actor_rows, [
        "chapter",
        "verse_range_ref",
        "name",
        "traits",
        "changes",
        "visual",
        "source_file",
        "meta_path",
    ])

    print(f"Geschrieben: {out_dir / 'verses.csv'} ({len(verse_rows)} Zeilen)")
    print(f"Geschrieben: {out_dir / 'actors.csv'} ({len(actor_rows)} Zeilen)")


def load_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        print(f"Überspringe {path}: {exc}")
        return {}


def clean_text(text: str) -> str:
    return " ".join(text.split())


def uniq(items) -> List[str]:
    seen = set()
    result: List[str] = []
    for item in items:
        if item is None:
            continue
        s = str(item).strip()
        if not s or s in seen:
            continue
        seen.add(s)
        result.append(s)
    return result


def join(items: List[str]) -> str:
    return " | ".join(items)


def write_csv(path: Path, rows: List[Dict[str, Any]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


if __name__ == "__main__":
    main()
