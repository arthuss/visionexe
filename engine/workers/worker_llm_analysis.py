import argparse
import csv
import json
import os
import re
import time
import urllib.request
from pathlib import Path

from visionexe_paths import ensure_dir, load_story_config, resolve_path


MODEL_NAME = "gpt-oss:20b"
OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"

TRIGGER_FILES = {"story.txt", "verse.txt", "segment.txt", "mechanic_concept.txt"}

WAVE_SECTION_RE = re.compile(
    r"^###\s+.*Integration in WAVE.*?(?=^###\s|\Z)",
    re.IGNORECASE | re.MULTILINE | re.DOTALL,
)


def strip_wave_sections(text):
    if not text:
        return text
    cleaned = WAVE_SECTION_RE.sub("", text)
    return cleaned.strip()


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")


def parse_args():
    parser = argparse.ArgumentParser(description="LLM worker for story analysis.")
    parser.add_argument("chapters", nargs="*", type=int, help="Chapter numbers to process (e.g. 96).")
    parser.add_argument("--story-root", help="Story root path.")
    parser.add_argument("--story-config", help="Path to story_config.json.")
    parser.add_argument("--per-segment", action="store_true", help="Analyze per segment (verse/paragraph).")
    parser.add_argument("--include-wave", action="store_true", help="Include Integration in WAVE sections.")
    parser.add_argument("--progress-csv", help="Override progress CSV path.")
    parser.add_argument("--model", help="Override model name.")
    parser.add_argument("--ollama-url", help="Override Ollama URL.")
    return parser.parse_args()


def parse_chapter_number(chapter_name):
    match = re.search(r"\d+", chapter_name)
    if not match:
        return None
    try:
        return int(match.group(0))
    except ValueError:
        return None


def load_completed(progress_csv, per_segment):
    completed = set()
    if not os.path.exists(progress_csv):
        return completed
    try:
        with open(progress_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row:
                    continue
                status = row.get("Status", "")
                if status != "DONE":
                    continue
                chapter_id = row.get("ChapterID", "").strip()
                if not per_segment:
                    completed.add(chapter_id)
                else:
                    segment_label = row.get("SegmentLabel", "").strip()
                    completed.add(f"{chapter_id}:{segment_label}")
    except Exception as e:
        log(f"Failed to read progress CSV: {e}")
    return completed


def append_progress(progress_csv, row):
    file_exists = os.path.exists(progress_csv)
    ensure_dir(os.path.dirname(progress_csv))
    try:
        with open(progress_csv, "a", newline="", encoding="utf-8") as f:
            fieldnames = [
                "ChapterID",
                "SegmentLabel",
                "SegmentType",
                "Status",
                "SourcePath",
                "RawContent",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)
    except Exception as e:
        log(f"Failed to write progress CSV: {e}")


def call_ollama(prompt, model_name, ollama_url):
    data = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_ctx": 16384,
        },
    }
    try:
        req = urllib.request.Request(
            ollama_url,
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as response:
            resp_json = json.loads(response.read().decode("utf-8"))
            main_response = resp_json.get("response", "")
            return main_response
    except Exception as e:
        log(f"Ollama request failed: {e}")
        return None


def find_text_file(target_dir):
    for name in TRIGGER_FILES:
        path = os.path.join(target_dir, name)
        if os.path.exists(path):
            return path
    for filename in os.listdir(target_dir):
        if filename.endswith(".txt") and "analysis" not in filename:
            return os.path.join(target_dir, filename)
    return None


def write_analysis(target_dir, content):
    target_path = os.path.join(target_dir, "analysis_llm.txt")
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(content)
    return target_path


def distribute_analysis(start_dir, content):
    count = 0
    for root, _, files in os.walk(start_dir):
        if TRIGGER_FILES.intersection(files):
            try:
                write_analysis(root, content)
                count += 1
            except Exception as e:
                log(f"Failed to write analysis in {root}: {e}")
    return count


def iter_chapters(base_dir):
    entries = []
    for name in os.listdir(base_dir):
        full = os.path.join(base_dir, name)
        if name.startswith("chapter_") and os.path.isdir(full):
            entries.append((name, parse_chapter_number(name)))
    entries.sort(key=lambda item: (item[1] is None, item[1] if item[1] is not None else item[0]))
    return entries


def iter_segments(chapter_dir, segment_label):
    prefix = f"{segment_label}_"
    for name in os.listdir(chapter_dir):
        full = os.path.join(chapter_dir, name)
        if name.startswith(prefix) and os.path.isdir(full):
            yield name, full


def build_prompt(text_content, phase_limit):
    return (
        "Extract all actors, props, environments, and scenes.\n"
        "Goal: production consistency so characters, props, and places are recognizable.\n"
        "Dynamic vs static is based on CHANGE OVER TIME (not just presence).\n\n"
        "Rules:\n"
        "- Use only information from the text.\n"
        "- Do not invent new actors/props/places/scenes.\n"
        "- 'changes' must be structural or long-term (body mods, tech upgrades, identity shifts).\n"
        "- Ignore clothing-only changes unless the text says it's a permanent transformation.\n"
        f"- Limit changes to at most {phase_limit} sequential phases; merge minor shifts into the closest phase.\n"
        "- Use stable phase labels across segments (e.g., 'Phase 1: pre-tech', 'Phase 2: mid', 'Phase 3: full').\n"
        "- If details are missing, omit or mark unknown.\n"
        "- Preserve verse/beat order.\n\n"
        "Output JSON keys:\n"
        "- actors: [{name, visualTraits, changes, role}]\n"
        "- props: [{name, visualTraits, changes, role}]\n"
        "- environments: [{name, visualTraits, changes, role}]\n"
        "- scenes: [{title, location, action, actorsInvolved}]\n\n"
        f"Text:\n{text_content[:12000]}\n\n"
        "Return JSON only."
    )


def main():
    args = parse_args()
    model_name = args.model or MODEL_NAME
    ollama_url = args.ollama_url or OLLAMA_API_URL

    story_config, _, repo_root = load_story_config(
        story_root=args.story_root,
        story_config_path=args.story_config,
    )

    filmsets_root = resolve_path(story_config.get("filmsets_root"), repo_root)
    if not filmsets_root or not os.path.exists(filmsets_root):
        log(f"Filmsets root not found: {filmsets_root}")
        return

    data_root = resolve_path(story_config.get("data_root"), repo_root)
    progress_csv = args.progress_csv or story_config.get("analysis_progress_csv_path")
    if not progress_csv:
        progress_csv = str(Path(data_root) / "analysis" / "analysis_progress_python.csv")
    else:
        progress_csv = str(resolve_path(progress_csv, repo_root))

    segment_label = story_config.get("segment_label", "segment")
    segment_type = story_config.get("segment_type", "segment")
    phase_limit = int(story_config.get("dynamic_phase_max", 3))

    target_chapters = [int(ch) for ch in args.chapters] if args.chapters else []
    completed = load_completed(progress_csv, args.per_segment)

    log(f"Model: {model_name}")
    log(f"Filmsets: {filmsets_root}")
    log(f"Progress CSV: {progress_csv}")

    chapter_entries = iter_chapters(filmsets_root)
    if target_chapters:
        target_set = set(target_chapters)
        chapter_entries = [(name, num) for name, num in chapter_entries if num in target_set]
        missing = sorted(target_set - {num for _, num in chapter_entries if num is not None})
        for missing_id in missing:
            log(f"Chapter {missing_id} not found.")
        if not chapter_entries:
            log("No target chapters found.")
            return

    for chapter_name, chapter_num in chapter_entries:
        chapter_id = str(chapter_num) if chapter_num is not None else chapter_name
        chapter_dir = os.path.join(filmsets_root, chapter_name)

        if args.per_segment:
            segment_entries = list(iter_segments(chapter_dir, segment_label))
            if not segment_entries:
                log(f"No segments found in {chapter_name}.")
                continue

            for segment_name, segment_dir in segment_entries:
                key = f"{chapter_id}:{segment_name}"
                if key in completed and not target_chapters:
                    log(f"Skipping {chapter_name}/{segment_name} (done).")
                    continue

                text_file = find_text_file(segment_dir)
                if not text_file:
                    log(f"No text file in {segment_name}.")
                    continue

                try:
                    with open(text_file, "r", encoding="utf-8") as f:
                        text_content = f.read()
                except Exception as e:
                    log(f"Failed to read {text_file}: {e}")
                    continue

                if not args.include_wave:
                    text_content = strip_wave_sections(text_content)

                prompt = build_prompt(text_content, phase_limit)
                start_time = time.time()
                result = call_ollama(prompt, model_name, ollama_url)
                duration = time.time() - start_time

                if result:
                    log(f"Analyzed {chapter_name}/{segment_name} ({duration:.1f}s).")
                    write_analysis(segment_dir, result)
                    append_progress(progress_csv, {
                        "ChapterID": chapter_id,
                        "SegmentLabel": segment_name,
                        "SegmentType": segment_type,
                        "Status": "DONE",
                        "SourcePath": text_file,
                        "RawContent": result,
                    })
                else:
                    log(f"No response for {chapter_name}/{segment_name}.")
        else:
            if chapter_id in completed and not target_chapters:
                log(f"Skipping {chapter_name} (done).")
                continue

            text_file = find_text_file(chapter_dir)
            if not text_file:
                log(f"No chapter text in {chapter_name}.")
                continue

            try:
                with open(text_file, "r", encoding="utf-8") as f:
                    text_content = f.read()
            except Exception as e:
                log(f"Failed to read {text_file}: {e}")
                continue

            if not args.include_wave:
                text_content = strip_wave_sections(text_content)

            prompt = build_prompt(text_content, phase_limit)
            start_time = time.time()
            result = call_ollama(prompt, model_name, ollama_url)
            duration = time.time() - start_time

            if result:
                log(f"Analyzed {chapter_name} ({duration:.1f}s).")
                files_written = distribute_analysis(chapter_dir, result)
                log(f"Wrote analysis to {files_written} folders.")
                append_progress(progress_csv, {
                    "ChapterID": chapter_id,
                    "SegmentLabel": "",
                    "SegmentType": "",
                    "Status": "DONE",
                    "SourcePath": text_file,
                    "RawContent": result,
                })
            else:
                log(f"No response for {chapter_name}.")

    log("All tasks completed.")


if __name__ == "__main__":
    main()
