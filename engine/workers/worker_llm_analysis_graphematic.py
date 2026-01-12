import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import time
import urllib.request
from pathlib import Path

from visionexe_paths import ensure_dir, load_story_config, resolve_path
from vertex_gemini import call_vertex_gemini


MODEL_NAME = "gpt-oss:20b"
OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"

TRIGGER_FILES = {"story.txt", "verse.txt", "segment.txt", "mechanic_concept.txt"}
STORY_FILENAME = "story.txt"

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
    parser.add_argument("--per-segment", action="store_false", help="Analyze per segment (verse/paragraph). Default: True.")
    parser.add_argument("--include-wave", action="store_true", help="Include Integration in WAVE sections.")
    parser.add_argument("--progress-csv", help="Override progress CSV path.")
    parser.add_argument("--model", help="Override model name.")
    parser.add_argument("--ollama-url", help="Override Ollama URL.")
    parser.add_argument("--use-gemini", action="store_true", help="Use Gemini CLI instead of Ollama.")
    parser.add_argument("--use-vertex", action="store_true", help="Use Vertex AI Gemini via ADC.")
    parser.add_argument("--vertex-project", help="Override Vertex project ID.")
    parser.add_argument("--vertex-location", help="Override Vertex location (default: us-central1).")
    parser.add_argument("--vertex-model", help="Override Vertex model name.")
    parser.add_argument("--force", action="store_true", help="Force re-run, ignoring progress CSV.")
    parser.add_argument("--chapter-batch", action="store_true", help="Process all segments per chapter in one request.")
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


def resolve_gemini_command():
    gemini_path = shutil.which("gemini") or shutil.which("gemini.cmd")
    if gemini_path:
        return [gemini_path]

    npx_path = shutil.which("npx") or shutil.which("npx.cmd")
    if npx_path:
        return [npx_path, "-y", "@google/gemini-cli"]

    return None


def parse_gemini_response(raw_output):
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


def parse_json_payload(text):
    if not text:
        return None
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None


def call_gemini(prompt, model=None):
    cmd = resolve_gemini_command()
    if not cmd:
        log("Gemini CLI nicht gefunden (gemini/npx).")
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
            log(f"Gemini Fehler: {stderr}")
            return None
        return parse_gemini_response(stdout)
    except OSError as exc:
        log(f"Gemini Start fehlgeschlagen: {exc}")
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
    target_path = os.path.join(target_dir, "analysis_llm_graphematic.txt")
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


def iter_chapters(base_dir, chapter_label="chapter"):
    entries = []
    prefix = f"{chapter_label}_"
    for name in os.listdir(base_dir):
        full = os.path.join(base_dir, name)
        if name.lower().startswith(prefix) and os.path.isdir(full):
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
    return f"""Instruction: Perform a scientific Graphematic Analysis (Level A) of the Ge'ez text.
Goal: Document the physical text state before any interpretation.

SCIENTIFIC RULES:
1. NO NORMALIZATION: do not fix spelling, do not remove repetition, do not reorder lines.
2. PUNCTUATION: preserve every marker exactly as seen; list them separately.
3. ARTIFACTS: identify non-Ge'ez elements (dashes, Latin text, numbering) as artifacts.
4. UNCERTAINTY: mark damaged/illegible spans with offsets into graphematic_string.

Input Text:
{text_content}

Output strictly valid JSON:
{{
  "source": {{
    "witness_id": "chapter_XXX/segment_YYY",
    "graphematic_string": "...",
    "normalization_policy": "none",
    "punctuation_markers": ["..."],
    "removed_artifacts": ["dash"],
    "uncertainties": [
      {{"span": {{"start": 0, "end": 0}}, "type": "damaged", "note": ""}}
    ]
  }}
}}"""


def build_batch_prompt(story_text, segments):
    payload = {
        "story_text": story_text,
        "segments": [
            {
                "segment_label": segment["segment_label"],
                "witness_id": segment["witness_id"],
                "text": segment["text"],
            }
            for segment in segments
        ],
    }
    return (
        "Instruction: Perform a scientific Graphematic Analysis (Level A) per segment.\n"
        "Goal: Document the physical text state for each segment without normalization.\n\n"
        "Rules:\n"
        "1. Preserve segment text exactly as provided.\n"
        "2. Mark punctuation markers and artifacts explicitly.\n"
        "3. Return one source object per segment_label.\n\n"
        f"Input JSON:\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n\n"
        "Output strictly valid JSON:\n"
        "{\n"
        '  "segments": [\n'
        "    {\n"
        '      "segment_label": "segment_001",\n'
        '      "source": {\n'
        '        "witness_id": "story_001/segment_001",\n'
        '        "graphematic_string": "...",\n'
        '        "normalization_policy": "none",\n'
        '        "punctuation_markers": ["..."],\n'
        '        "removed_artifacts": ["dash"],\n'
        '        "uncertainties": []\n'
        "      }\n"
        "    }\n"
        "  ]\n"
        "}"
    )


def collect_segment_inputs(chapter_id, chapter_name, chapter_dir, segment_label, completed, target_chapters, include_wave):
    segments = []
    for segment_name, segment_dir in iter_segments(chapter_dir, segment_label):
        key = f"{chapter_id}:{segment_name}"
        if key in completed and not target_chapters:
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
        if not include_wave:
            text_content = strip_wave_sections(text_content)
        segments.append({
            "segment_label": segment_name,
            "segment_dir": segment_dir,
            "text": text_content,
            "text_file": text_file,
            "witness_id": f"{chapter_name}/{segment_name}",
        })
    return segments


def main():
    args = parse_args()
    use_vertex = bool(args.use_vertex)
    use_gemini = bool(args.use_gemini) and not use_vertex
    model_name = args.model or MODEL_NAME
    gemini_model = args.model or os.environ.get("GEMINI_MODEL", "")
    vertex_model = args.vertex_model or args.model or os.environ.get("VERTEX_MODEL", "")
    vertex_project = args.vertex_project
    vertex_location = args.vertex_location
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
    progress_csv = args.progress_csv
    if not progress_csv:
        progress_csv = str(Path(data_root) / "analysis" / "analysis_progress_python_graphematic_v2.csv")
    else:
        progress_csv = str(resolve_path(progress_csv, repo_root))

    segment_label = story_config.get("segment_label", "segment")
    segment_type = story_config.get("segment_type", "segment")
    chapter_label = story_config.get("chapter_label", "chapter")
    phase_limit = int(story_config.get("dynamic_phase_max", 3))

    target_chapters = [int(ch) for ch in args.chapters] if args.chapters else []

    if args.force:
        log("Force enabled: Ignoring previous progress.")
        completed = set()
    else:
        completed = load_completed(progress_csv, args.per_segment)

    if use_vertex:
        log(
            "LLM: Vertex (model=%s, project=%s, location=%s)"
            % (vertex_model or "default", vertex_project or "auto", vertex_location or "auto")
        )
    elif use_gemini:
        log(f"LLM: Gemini ({gemini_model or 'default'})")
    else:
        log(f"LLM: Ollama ({model_name})")
    log(f"Filmsets: {filmsets_root}")
    log(f"Progress CSV: {progress_csv}")
    log(f"Chapter Label: {chapter_label}")

    chapter_entries = iter_chapters(filmsets_root, chapter_label)
    log(f"Found {len(chapter_entries)} chapters.")
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

        if args.chapter_batch:
            segment_inputs = collect_segment_inputs(
                chapter_id,
                chapter_name,
                chapter_dir,
                segment_label,
                completed,
                target_chapters,
                args.include_wave,
            )
            if not segment_inputs:
                log(f"No segments found in {chapter_name}.")
                continue

            story_path = os.path.join(chapter_dir, STORY_FILENAME)
            story_text = ""
            if os.path.exists(story_path):
                try:
                    story_text = Path(story_path).read_text(encoding="utf-8")
                except Exception as e:
                    log(f"Failed to read {story_path}: {e}")
            else:
                log(f"Story text not found: {story_path}")

            if story_text and not args.include_wave:
                story_text = strip_wave_sections(story_text)

            prompt = build_batch_prompt(story_text, segment_inputs)
            start_time = time.time()
            if use_vertex:
                result = call_vertex_gemini(
                    prompt,
                    model=vertex_model or None,
                    project=vertex_project,
                    location=vertex_location,
                    log_fn=log,
                )
            elif use_gemini:
                result = call_gemini(prompt, gemini_model)
            else:
                result = call_ollama(prompt, model_name, ollama_url)
            duration = time.time() - start_time

            if not result:
                log(f"No response for {chapter_name}.")
                continue

            payload = parse_json_payload(result)
            if not payload or "segments" not in payload:
                log(f"Batch output missing segments for {chapter_name}.")
                continue

            segment_map = {item["segment_label"]: item for item in segment_inputs}
            returned_labels = set()
            for item in payload.get("segments", []):
                segment_label_value = item.get("segment_label")
                source = item.get("source")
                if not segment_label_value or not source:
                    continue
                segment_info = segment_map.get(segment_label_value)
                if not segment_info:
                    continue
                if not source.get("witness_id"):
                    source["witness_id"] = segment_info["witness_id"]
                content = json.dumps({"source": source}, ensure_ascii=False, indent=2)
                write_analysis(segment_info["segment_dir"], content)
                append_progress(progress_csv, {
                    "ChapterID": chapter_id,
                    "SegmentLabel": segment_label_value,
                    "SegmentType": segment_type,
                    "Status": "DONE",
                    "SourcePath": segment_info["text_file"],
                    "RawContent": content,
                })
                returned_labels.add(segment_label_value)

            missing = sorted(set(segment_map.keys()) - returned_labels)
            if missing:
                log(f"Batch missing segments in {chapter_name}: {', '.join(missing)}")
            log(f"Analyzed {chapter_name} batch ({duration:.1f}s).")
            continue

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
                if use_vertex:
                    result = call_vertex_gemini(
                        prompt,
                        model=vertex_model or None,
                        project=vertex_project,
                        location=vertex_location,
                        log_fn=log,
                    )
                elif use_gemini:
                    result = call_gemini(prompt, gemini_model)
                else:
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
            if use_vertex:
                result = call_vertex_gemini(
                    prompt,
                    model=vertex_model or None,
                    project=vertex_project,
                    location=vertex_location,
                    log_fn=log,
                )
            elif use_gemini:
                result = call_gemini(prompt, gemini_model)
            else:
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
