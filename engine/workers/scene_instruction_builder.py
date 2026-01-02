import argparse
import json
import re
from pathlib import Path

from visionexe_paths import load_story_config, resolve_path


SCENE_HEADER_RE = re.compile(
    r"^##\s+\[ACT\s+(?P<act>\d+)\]\s+\[SCENE\s+(?P<scene>[0-9.]+)\]\s+\[Timecode:\s*(?P<timecode>[^\]]+)\]\s+\[(?P<title>[^\]]+)\]",
    re.MULTILINE,
)
CHAPTER_RE = re.compile(r"chapter_(\d+)", re.IGNORECASE)


def parse_timecode(value: str):
    if not value:
        return "", ""
    parts = [p.strip() for p in value.split("-") if p.strip()]
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[1]


def parse_scene_number(scene_value: str):
    if not scene_value:
        return None, None
    parts = [p for p in scene_value.split(".") if p]
    segment_index = int(parts[0]) if parts and parts[0].isdigit() else None
    scene_index = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None
    return segment_index, scene_index


def extract_json_after_marker(text: str, marker: str):
    idx = text.find(marker)
    if idx == -1:
        return None
    start = text.find("{", idx)
    if start == -1:
        return None
    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == "\"":
                in_string = False
            continue
        if ch == "\"":
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                raw = text[start:i + 1]
                try:
                    return json.loads(raw)
                except json.JSONDecodeError:
                    return None
    return None


def extract_first_line(text: str, marker: str):
    for line in text.splitlines():
        if marker in line:
            return line.split(marker, 1)[-1].strip()
    return ""


def extract_regie_blocks(text: str):
    scenes = []
    matches = list(SCENE_HEADER_RE.finditer(text))
    for idx, match in enumerate(matches):
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        block = text[start:end]

        regie = extract_json_after_marker(block, "REGIE_JSON")
        scene_number = match.group("scene")
        segment_index, scene_index = parse_scene_number(scene_number)
        timecode_raw = match.group("timecode").strip()
        timecode_start, timecode_end = parse_timecode(timecode_raw)

        scenes.append({
            "act": int(match.group("act")),
            "scene_number": scene_number,
            "segment_index": segment_index,
            "scene_index": scene_index,
            "title": match.group("title").strip(),
            "timecode": timecode_raw,
            "timecode_start": timecode_start,
            "timecode_end": timecode_end,
            "regie": regie,
        })
    return scenes


def build_scene_id(chapter, scene_number):
    if not chapter:
        return f"SCENE_{scene_number}"
    return f"SCENE_{int(chapter):03d}_{scene_number}"


def extract_chapter_number(path: Path):
    match = CHAPTER_RE.search(str(path))
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None


def main():
    parser = argparse.ArgumentParser(description="Build scene_instructions.jsonl from screenplay REGIE_JSON blocks.")
    parser.add_argument("--story-root", help="Story root path (defaults to engine_config default_story_root).")
    parser.add_argument("--story-config", help="Path to story_config.json (overrides story-root).")
    parser.add_argument("--filmsets-root", help="Optional filmsets root path override.")
    parser.add_argument("--chapter", help="Limit to a chapter number (e.g. 18).")
    parser.add_argument("--output", help="Output JSONL path.")
    args = parser.parse_args()

    story_config, _, repo_root = load_story_config(
        story_root=args.story_root,
        story_config_path=args.story_config,
    )

    filmsets_root = resolve_path(args.filmsets_root or story_config.get("filmsets_root"), repo_root)
    output_path = resolve_path(args.output or story_config.get("scene_instructions_path", ""), repo_root)
    if not output_path:
        raise SystemExit("scene_instructions_path is missing.")

    chapter_filter = None
    if args.chapter:
        digits = re.sub(r"[^0-9]", "", str(args.chapter))
        if digits:
            chapter_filter = int(digits)

    records = []
    for path in filmsets_root.rglob("DREHBUCH_HOLLYWOOD.md"):
        chapter = extract_chapter_number(path)
        if chapter_filter and chapter != chapter_filter:
            continue
        text = path.read_text(encoding="utf-8")
        narrator_text = extract_first_line(text, "NARRATOR_TEXT:")
        monologue_json = extract_json_after_marker(text, "MONOLOGUE_JSON")

        chapter_record = {
            "record_type": "chapter",
            "chapter": chapter,
            "source_path": str(path),
            "narrator_text": narrator_text,
            "monologue_json": monologue_json,
        }
        records.append(chapter_record)

        scenes = extract_regie_blocks(text)
        for scene in scenes:
            segment_label = ""
            scene_label = ""
            segment_index = scene.get("segment_index")
            scene_index = scene.get("scene_index")
            segment_padding = int(story_config.get("segment_index_padding", 3))
            scene_padding = int(story_config.get("scene_index_padding", 3))
            segment_label_name = story_config.get("segment_label", "segment")
            scene_label_name = story_config.get("scene_label", "scene")
            if segment_index is not None:
                segment_label = f"{segment_label_name}_{segment_index:0{segment_padding}d}"
            if scene_index is not None:
                scene_label = f"{scene_label_name}_{scene_index:0{scene_padding}d}"

            regie = scene.get("regie") or {}
            actors = regie.get("actors") if isinstance(regie, dict) else []
            props = regie.get("props") if isinstance(regie, dict) else []
            env_name = regie.get("environment") if isinstance(regie, dict) else ""
            director_intent = regie.get("director_intent") if isinstance(regie, dict) else ""
            start_image_keywords = regie.get("start_image_keywords") if isinstance(regie, dict) else None
            video_plan = regie.get("video_plan") if isinstance(regie, dict) else None

            records.append({
                "record_type": "scene",
                "scene_id": build_scene_id(chapter or 0, scene.get("scene_number")),
                "chapter": chapter,
                "act": scene.get("act"),
                "scene_number": scene.get("scene_number"),
                "segment_index": segment_index,
                "scene_index": scene_index,
                "segment_label": segment_label,
                "scene_label": scene_label,
                "title": scene.get("title"),
                "timecode": scene.get("timecode"),
                "timecode_start": scene.get("timecode_start"),
                "timecode_end": scene.get("timecode_end"),
                "environment": env_name,
                "actors": actors,
                "props": props,
                "director_intent": director_intent,
                "start_image_keywords": start_image_keywords,
                "video_plan": video_plan,
                "regie": regie,
                "source_path": str(path),
            })

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Wrote scene instructions: {output_path} ({len(records)} records)")


if __name__ == "__main__":
    main()
