import argparse
import json
import re
import time
from pathlib import Path

from visionexe_paths import ensure_dir, load_story_config, resolve_path


NARRATOR_RE = re.compile(r"^NARRATOR_TEXT:\s*(.+)$", re.MULTILINE)
MONOLOGUE_RE = re.compile(r"^MONOLOGUE_JSON:\s*(\{.*\})\s*$", re.MULTILINE)
DIALOG_HEADER_RE = re.compile(r"^\*\*Dialog:\*\*\s*(.*)$")
SPEAKER_LINE_RE = re.compile(r"^\s*([^:]{1,64})\s*:\s*(.+)$")


def normalize_speaker_id(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", name.strip())
    cleaned = cleaned.strip("_").lower()
    return cleaned or "unknown"


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def parse_narrator(text: str):
    match = NARRATOR_RE.search(text)
    if not match:
        return None
    line = match.group(1).strip()
    return line or None


def parse_monologues(text: str):
    match = MONOLOGUE_RE.search(text)
    if not match:
        return {}
    payload = match.group(1).strip()
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return {}
    actors = data.get("actors")
    if not isinstance(actors, dict):
        return {}
    results = {}
    for actor, entries in actors.items():
        if not actor:
            continue
        if not isinstance(entries, list):
            continue
        lines = []
        for entry in entries:
            if isinstance(entry, dict):
                text_line = str(entry.get("text", "")).strip()
                if text_line:
                    lines.append(text_line)
        if lines:
            results[actor] = lines
    return results


def parse_dialog(text: str):
    speakers = {}
    lines = text.splitlines()
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        header = DIALOG_HEADER_RE.match(line)
        if not header:
            idx += 1
            continue
        inline = header.group(1).strip()
        dialog_lines = []
        if inline and inline not in {"-", "—"}:
            dialog_lines.append(inline)
        idx += 1
        while idx < len(lines):
            candidate = lines[idx]
            if candidate.startswith("### ") or candidate.startswith("## ["):
                break
            if candidate.strip() == "":
                break
            dialog_lines.append(candidate.strip())
            idx += 1
        for dialog_line in dialog_lines:
            match = SPEAKER_LINE_RE.match(dialog_line)
            if not match:
                continue
            name = match.group(1).strip()
            spoken = match.group(2).strip()
            if not name:
                continue
            speakers.setdefault(name, []).append(spoken)
        continue
    return speakers


def merge_speaker(speakers, name, speaker_type, chapter_id, samples):
    speaker_id = normalize_speaker_id(name)
    entry = speakers.setdefault(
        speaker_id,
        {
            "id": speaker_id,
            "display_name": name.strip(),
            "aliases": [],
            "types": set(),
            "chapters": set(),
            "count": 0,
            "samples": [],
        },
    )
    if name.strip() not in entry["aliases"]:
        entry["aliases"].append(name.strip())
    entry["types"].add(speaker_type)
    entry["chapters"].add(chapter_id)
    entry["count"] += len(samples)
    for sample in samples:
        if sample and sample not in entry["samples"]:
            entry["samples"].append(sample)


def list_chapters(filmsets_root: Path, label: str):
    pattern = f"{label}_*"
    chapters = []
    for path in filmsets_root.glob(pattern):
        if path.is_dir():
            chapters.append(path)
    return sorted(chapters)


def build_voice_cast(story_config: dict, story_root: Path, repo_root: Path):
    filmsets_root = resolve_path(story_config.get("filmsets_root"), repo_root)
    if not filmsets_root:
        filmsets_root = story_root / "filmsets"
    label = story_config.get("chapter_label", "story")
    chapters = list_chapters(filmsets_root, label)

    speakers = {}
    for chapter_dir in chapters:
        chapter_id = chapter_dir.name
        script_path = chapter_dir / "DREHBUCH_HOLLYWOOD.md"
        text = read_text(script_path)
        if not text:
            continue

        narrator = parse_narrator(text)
        if narrator:
            merge_speaker(
                speakers,
                "Narrator",
                "narrator",
                chapter_id,
                [narrator[:240]],
            )

        for actor, lines in parse_monologues(text).items():
            merge_speaker(speakers, actor, "monologue", chapter_id, lines[:3])

        dialog_map = parse_dialog(text)
        for actor, lines in dialog_map.items():
            merge_speaker(speakers, actor, "dialog", chapter_id, lines[:3])

    output = []
    for entry in speakers.values():
        entry["types"] = sorted(entry["types"])
        entry["chapters"] = sorted(entry["chapters"])
        output.append(entry)
    output.sort(key=lambda item: item["id"])
    return output


def main():
    parser = argparse.ArgumentParser(description="Build voice cast from screenplays.")
    parser.add_argument("--story-root", default="", help="Path to story root.")
    parser.add_argument("--story-config", default="", help="Path to story_config.json.")
    parser.add_argument("--output", default="", help="Output path (defaults to subjects/voice_cast.json).")
    args = parser.parse_args()

    story_config, story_root, repo_root = load_story_config(
        story_root=args.story_root or None,
        story_config_path=args.story_config or None,
    )
    subjects_root = resolve_path(story_config.get("subjects_root"), repo_root)
    if not subjects_root:
        subjects_root = story_root / "subjects"
    output_path = resolve_path(args.output, repo_root) if args.output else subjects_root / "voice_cast.json"
    ensure_dir(output_path.parent)

    cast = build_voice_cast(story_config, story_root, repo_root)
    payload = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "story_id": story_config.get("story_id", ""),
        "speaker_count": len(cast),
        "speakers": cast,
    }
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote voice cast: {output_path}")


if __name__ == "__main__":
    main()
