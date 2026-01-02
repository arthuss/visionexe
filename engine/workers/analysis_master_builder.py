import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

from visionexe_paths import ensure_dir, load_story_config, resolve_path


JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*([\[{].*?[\]}])\s*```", re.DOTALL | re.IGNORECASE)
CHAPTER_RE = re.compile(r"chapter_(\d+)", re.IGNORECASE)
VERSE_RE = re.compile(r"verse_(\d+)", re.IGNORECASE)
SEGMENT_RE = re.compile(r"segment_(\d+)", re.IGNORECASE)
SCENE_RE = re.compile(r"scene_(\d+)", re.IGNORECASE)
PART_RE = re.compile(r"part_(\d+)", re.IGNORECASE)


def parse_int(value):
    if value is None:
        return None
    try:
        return int(str(value).strip())
    except (ValueError, TypeError):
        return None


def extract_json_blocks(text):
    blocks = []
    if not text:
        return blocks
    for match in JSON_BLOCK_RE.finditer(text):
        raw = match.group(1)
        try:
            blocks.append(json.loads(raw))
        except json.JSONDecodeError:
            continue
    if blocks:
        return blocks
    stripped = text.strip()
    if not stripped:
        return blocks
    try:
        blocks.append(json.loads(stripped))
        return blocks
    except json.JSONDecodeError:
        pass
    decoder = json.JSONDecoder()
    for idx, ch in enumerate(stripped):
        if ch not in "{[":
            continue
        try:
            payload, _ = decoder.raw_decode(stripped[idx:])
            blocks.append(payload)
            return blocks
        except json.JSONDecodeError:
            continue
    return blocks


def extract_from_path(source_path):
    if not source_path:
        return None, None, None, None
    chapter = None
    segment_index = None
    segment_type = None
    scene_index = None
    match = CHAPTER_RE.search(source_path)
    if match:
        chapter = parse_int(match.group(1))
    match = VERSE_RE.search(source_path)
    if match:
        segment_index = parse_int(match.group(1))
        segment_type = "verse"
    match = SEGMENT_RE.search(source_path)
    if match and segment_index is None:
        segment_index = parse_int(match.group(1))
        segment_type = "segment"
    match = SCENE_RE.search(source_path)
    if match:
        scene_index = parse_int(match.group(1))
        if segment_index is None:
            segment_index = scene_index
            segment_type = "scene"
    match = PART_RE.search(source_path)
    if match and segment_index is None:
        segment_index = parse_int(match.group(1))
        segment_type = "part"
    return chapter, segment_index, segment_type, scene_index


def build_source_id(source_path, row_index, mode):
    if mode == "hash":
        base = source_path or f"row_{row_index}"
        return hashlib.sha1(base.encode("utf-8")).hexdigest()[:12]
    if source_path:
        return source_path.replace("\\", "/")
    return f"row_{row_index}"


def scan_analysis_files(root: Path):
    index = {}
    if not root or not root.exists():
        return index
    for path in root.rglob("analysis_llm.*"):
        chapter, segment_index, segment_type, _scene_index = extract_from_path(str(path))
        if chapter is None:
            continue
        key = (chapter, segment_index, segment_type)
        index.setdefault(key, []).append(str(path))
    return index


def find_field(row, names):
    for name in names:
        if name in row and row[name]:
            return row[name]
    return None


def main():
    parser = argparse.ArgumentParser(description="Build analysis_master.jsonl from CSV + analysis outputs.")
    parser.add_argument("--story-root", help="Story root path (defaults to engine_config default_story_root).")
    parser.add_argument("--story-config", help="Path to story_config.json (overrides story-root).")
    parser.add_argument("--csv", help="CSV input path (defaults to story_config analysis_progress_csv_path).")
    parser.add_argument("--analysis-dir", help="Optional analysis directory to scan for analysis_llm files.")
    parser.add_argument("--output", help="Output JSONL path (defaults to story_config analysis_master_path).")
    parser.add_argument("--include-raw", action="store_true", help="Include raw LLM content in output.")
    parser.add_argument("--max-raw-chars", type=int, default=0, help="Trim raw content to N chars (0 = no trim).")
    parser.add_argument("--id-mode", choices=("path", "hash"), default="path", help="Source ID strategy.")
    parser.add_argument("--no-extract-json", action="store_true", help="Disable JSON block extraction.")
    args = parser.parse_args()

    story_config, story_root, repo_root = load_story_config(
        story_root=args.story_root,
        story_config_path=args.story_config,
    )

    csv_path = args.csv or story_config.get("analysis_progress_csv_path")
    if not csv_path:
        csv_path = str(Path(story_config["data_root"]) / "raw" / "first_analysis_progress_python.csv")
    csv_path = resolve_path(csv_path, repo_root)
    if not csv_path.exists():
        raise SystemExit(f"CSV not found: {csv_path}")

    output_path = args.output or story_config.get("analysis_master_path")
    if not output_path:
        raise SystemExit("No output path configured (analysis_master_path).")
    output_path = resolve_path(output_path, repo_root)
    ensure_dir(output_path.parent)

    segment_label = story_config.get("segment_label", "segment")
    segment_type_default = story_config.get("segment_type", "segment")
    segment_padding = int(story_config.get("segment_index_padding", 3))
    scene_label = story_config.get("scene_label", "scene")
    scene_padding = int(story_config.get("scene_index_padding", 3))

    analysis_dir = args.analysis_dir
    analysis_index = {}
    if analysis_dir:
        analysis_dir_path = resolve_path(analysis_dir, repo_root)
        analysis_index = scan_analysis_files(analysis_dir_path)

    with csv_path.open("r", encoding="utf-8") as f, output_path.open("w", encoding="utf-8") as out:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=1):
            source_path = find_field(row, ["Path", "path", "Source", "source", "File", "file"])
            chapter = parse_int(find_field(row, ["ChapterID", "chapter", "Chapter", "chapter_id"]))
            segment_index = parse_int(find_field(row, ["Verse", "verse", "Segment", "segment", "Scene", "scene", "Part", "part"]))
            segment_type = find_field(row, ["segment_type", "SegmentType", "SegmentType"]) or None
            scene_index = parse_int(find_field(row, ["SceneIndex", "scene_index"]))

            if source_path:
                parsed_chapter, parsed_segment, parsed_type, parsed_scene = extract_from_path(source_path)
                chapter = chapter if chapter is not None else parsed_chapter
                segment_index = segment_index if segment_index is not None else parsed_segment
                segment_type = segment_type or parsed_type
                scene_index = scene_index if scene_index is not None else parsed_scene

            segment_type = segment_type or segment_type_default
            if segment_index is None:
                segment_index = 0
            segment_label_value = f"{segment_label}_{segment_index:0{segment_padding}d}"
            scene_label_value = ""
            if scene_index is not None:
                scene_label_value = f"{scene_label}_{scene_index:0{scene_padding}d}"

            summary = find_field(row, ["Summary", "summary", "ShortSummary", "short_summary"]) or ""
            raw_content = find_field(row, ["RawContent", "raw_content", "Content", "content", "Text", "text"]) or ""

            if args.max_raw_chars and raw_content:
                raw_content = raw_content[: args.max_raw_chars]

            record = {
                "source_id": build_source_id(source_path, idx, args.id_mode),
                "source_path": source_path or "",
                "chapter": chapter if chapter is not None else "",
                "segment_index": segment_index,
                "segment_label": segment_label_value,
                "segment_type": segment_type,
                "source_index": idx,
                "summary": summary,
                "scene_index": scene_index,
                "scene_label": scene_label_value,
            }

            if not args.no_extract_json and raw_content:
                record["analysis_blocks"] = extract_json_blocks(raw_content)

            if args.include_raw:
                record["raw_content"] = raw_content

            if analysis_index:
                key = (chapter, segment_index, segment_type)
                if key in analysis_index:
                    record["analysis_paths"] = analysis_index[key]

            out.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Wrote analysis master: {output_path}")


if __name__ == "__main__":
    main()
