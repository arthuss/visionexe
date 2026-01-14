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
from progress_lock import progress_lock


MODEL_NAME = "gpt-oss:20b"
OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"

TRIGGER_FILES = {"story.txt", "verse.txt", "segment.txt", "mechanic_concept.txt"}

WAVE_SECTION_RE = re.compile(
    r"^###\s+.*Integration in WAVE.*?(?=^###\s|\Z)",
    re.IGNORECASE | re.MULTILINE | re.DOTALL,
)

ANALYSIS_LAYER_FILES = {
    "graphematic": "analysis_llm_graphematic.txt",
    "morphologic": "analysis_llm_morphologic.txt",
    "synthactic": "analysis_llm_synthactic.txt",
    "semantic_historical": "analysis_llm_semantic_historical.txt",
}

DEFAULT_GEO_ENV_FILES = ("geo_env_catalog.json", "geo_environments.json")


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
    parser.add_argument("--use-gemini", action="store_true", help="Use Gemini CLI instead of Ollama.")
    parser.add_argument("--use-vertex", action="store_true", help="Use Vertex AI Gemini via ADC.")
    parser.add_argument("--vertex-project", help="Override Vertex project ID.")
    parser.add_argument("--vertex-location", help="Override Vertex location (default: us-central1).")
    parser.add_argument("--vertex-model", help="Override Vertex model name.")
    parser.add_argument("--force", action="store_true", help="Ignore progress CSV and re-run all targets.")
    parser.add_argument("--wait-analysis-layers", action="store_true", help="Wait for all analysis layer files before analyzing a segment.")
    parser.add_argument("--wait-analysis-interval", type=float, default=2.0, help="Seconds between analysis layer checks.")
    parser.add_argument("--carry-location", action="store_true", help="Carry forward the last known scene location when current location is unknown.")
    parser.add_argument("--include-prev-segment", action="store_true", help="Include previous segment context for continuity checks.")
    parser.add_argument("--prev-context-chars", type=int, default=2000, help="Max chars to include from previous segment text.")
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
    ensure_dir(os.path.dirname(progress_csv))
    try:
        with progress_lock(progress_csv):
            file_exists = os.path.exists(progress_csv)
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


def load_json_text(text):
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def extract_json_payload(raw_text):
    if not raw_text:
        return None
    stripped = raw_text.strip()
    if not stripped:
        return None
    payload = load_json_text(stripped)
    if payload is not None:
        return payload
    match = re.search(r"```(?:json)?\s*([\[{].*?[\]}])\s*```", stripped, re.DOTALL | re.IGNORECASE)
    if match:
        payload = load_json_text(match.group(1))
        if payload is not None:
            return payload
    decoder = json.JSONDecoder()
    for idx, ch in enumerate(stripped):
        if ch not in "{[":
            continue
        try:
            payload, _ = decoder.raw_decode(stripped[idx:])
            return payload
        except json.JSONDecodeError:
            continue
    return None


def normalize_location(value):
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if text.lower() in {"unknown", "unk", "n/a", "none"}:
        return None
    return text


def apply_location_carry(payload, last_location):
    if not isinstance(payload, dict):
        return payload, last_location, False
    scenes = payload.get("scenes")
    if not isinstance(scenes, list):
        return payload, last_location, False
    updated = False
    for scene in scenes:
        if not isinstance(scene, dict):
            continue
        loc = normalize_location(scene.get("location"))
        if loc is None and last_location:
            scene["location"] = last_location
            updated = True
        elif loc:
            last_location = loc
    return payload, last_location, updated


def summarize_analysis_payload(payload):
    if not isinstance(payload, dict):
        return None
    keys = ["scenes", "geo_environments", "places", "locations", "environments"]
    summary = {key: payload.get(key) for key in keys if key in payload}
    return summary if summary else None


def load_prev_segment_context(segment_dir, include_wave, max_chars):
    context = {"segment": os.path.basename(segment_dir)}
    text_file = find_text_file(segment_dir)
    if text_file:
        try:
            text_content = Path(text_file).read_text(encoding="utf-8")
        except OSError:
            text_content = ""
        if text_content and not include_wave:
            text_content = strip_wave_sections(text_content)
        if text_content:
            context["text"] = text_content[:max_chars]

    analysis_path = Path(segment_dir) / "analysis_llm.txt"
    if analysis_path.exists():
        try:
            raw = analysis_path.read_text(encoding="utf-8")
        except OSError:
            raw = ""
        payload = extract_json_payload(raw)
        summary = summarize_analysis_payload(payload)
        if summary:
            context["analysis"] = summary

    return context if len(context) > 1 else None


def read_analysis_layers(segment_dir):
    layers = {}
    for key, filename in ANALYSIS_LAYER_FILES.items():
        path = os.path.join(segment_dir, filename)
        if not os.path.exists(path):
            continue
        try:
            raw = Path(path).read_text(encoding="utf-8").strip()
        except OSError:
            continue
        payload = load_json_text(raw)
        if payload is None:
            layers[key] = {"raw": raw}
        else:
            layers[key] = payload
    return layers


def wait_for_analysis_layers(segment_dir, poll_seconds=2.0):
    missing = []
    for filename in ANALYSIS_LAYER_FILES.values():
        path = os.path.join(segment_dir, filename)
        if not os.path.exists(path):
            missing.append(filename)
            continue
        try:
            if os.path.getsize(path) == 0:
                missing.append(filename)
        except OSError:
            missing.append(filename)
    if not missing:
        return
    log(f"Waiting for analysis layers in {segment_dir}: {', '.join(missing)}")
    while missing:
        time.sleep(poll_seconds)
        missing = []
        for filename in ANALYSIS_LAYER_FILES.values():
            path = os.path.join(segment_dir, filename)
            if not os.path.exists(path):
                missing.append(filename)
                continue
            try:
                if os.path.getsize(path) == 0:
                    missing.append(filename)
            except OSError:
                missing.append(filename)
        if missing:
            log(f"Still waiting for: {', '.join(missing)}")


def load_geo_env_catalog(story_config, repo_root):
    env_root = story_config.get("environments_root")
    if env_root:
        env_root = resolve_path(env_root, repo_root)
        for name in DEFAULT_GEO_ENV_FILES:
            candidate = env_root / name
            if candidate.exists():
                try:
                    data = json.loads(candidate.read_text(encoding="utf-8"))
                except OSError:
                    continue
                except json.JSONDecodeError:
                    continue
                if isinstance(data, list):
                    return [str(item).strip() for item in data if str(item).strip()]
                if isinstance(data, dict):
                    if "aliases" in data:
                        return data
                    items = data.get("geo_environments") or data.get("items") or []
                    return [str(item).strip() for item in items if str(item).strip()]
    return []


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


def iter_chapters(base_dir, chapter_label):
    entries = []
    prefix = f"{chapter_label}_".lower()
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


def build_prompt(text_content, phase_limit, analysis_layers, geo_env_catalog, prev_segment_context):
    analysis_blob = json.dumps(analysis_layers, ensure_ascii=False, indent=2) if analysis_layers else "{}"
    geo_env_blob = json.dumps(geo_env_catalog, ensure_ascii=False, indent=2) if geo_env_catalog else "[]"
    prev_blob = json.dumps(prev_segment_context, ensure_ascii=False, indent=2) if prev_segment_context else "null"
    return (
        "Extract all actors, props, environments, and scenes.\n"
        "Goal: production consistency so characters, props, and places are recognizable.\n"
        "Dynamic vs static is based on CHANGE OVER TIME (not just presence).\n"
        "Also extract blocking (anchors + movement paths) when the text implies staging.\n\n"
        "Rules:\n"
        "- Use only information from the text.\n"
        "- Use analysis_context for canonical names and disambiguation.\n"
        "- Use previous_segment_context only to judge continuity of location and flow.\n"
        "- Do not introduce entities or locations from previous_segment_context unless current text implies continuity.\n"
        "- Do not invent new actors/props/places/scenes.\n"
        "- Do not duplicate the same entity across actors/characters.\n"
        "- actors: named persons/beings; characters: unnamed roles or groups.\n"
        "- props: tangible items; role must be actor_prop:<name> | scene_prop | unknown.\n"
        "- places: named locations; locations: relative/local areas; environments: setting descriptors.\n"
        "- geo_environments: use canonical names from geo_env_catalog (map via aliases when provided).\n"
        "- 'changes' must be structural or long-term (body mods, tech upgrades, identity shifts).\n"
        "- Ignore clothing-only changes unless the text says it's a permanent transformation.\n"
        f"- Limit changes to at most {phase_limit} sequential phases; merge minor shifts into the closest phase.\n"
        "- Use stable phase labels across segments (e.g., 'Phase 1: pre-tech', 'Phase 2: mid', 'Phase 3: full').\n"
        "- If details are missing, omit or mark unknown.\n"
        "- Preserve verse/beat order.\n"
        "- Blocking anchors: use only locations implied by the text (altar, gate, ridge, center).\n"
        "- Blocking paths: only include explicit movement; use motion = walk/run/hover/stand/unknown.\n"
        "- If duration is not implied, set duration_sec to null.\n\n"
        "Output JSON keys:\n"
        "- actors: [{name, visualTraits, changes, role}]\n"
        "- characters: [{name, visualTraits, changes, role}]\n"
        "- props: [{name, visualTraits, changes, role}]\n"
        "- places: [{name, visualTraits, changes, role}]\n"
        "- locations: [{name, visualTraits, changes, role}]\n"
        "- environments: [{name, visualTraits, changes, role}]\n"
        "- geo_environments: [{name, visualTraits, changes, role}]\n"
        "- scenes: [{title, location, action, actorsInvolved}]\n\n"
        "- blocking: {anchors: [{id, description}], paths: [{actor, start_anchor, end_anchor, motion, duration_sec, notes}]}\n\n"
        f"analysis_context:\n{analysis_blob}\n\n"
        f"previous_segment_context:\n{prev_blob}\n\n"
        f"geo_env_catalog:\n{geo_env_blob}\n\n"
        f"Text:\n{text_content[:12000]}\n\n"
        "Return JSON only."
    )


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
    geo_env_catalog = load_geo_env_catalog(story_config, repo_root)

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
    chapter_label = story_config.get("chapter_label", "chapter")
    phase_limit = int(story_config.get("dynamic_phase_max", 3))

    target_chapters = [int(ch) for ch in args.chapters] if args.chapters else []
    completed = set() if args.force else load_completed(progress_csv, args.per_segment)

    if args.force:
        log("Force enabled: Ignoring previous progress.")
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

    chapter_entries = iter_chapters(filmsets_root, chapter_label)
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
        last_location = None
        prev_segment_dir = None

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
                if args.wait_analysis_layers:
                    wait_for_analysis_layers(segment_dir, args.wait_analysis_interval)

                try:
                    with open(text_file, "r", encoding="utf-8") as f:
                        text_content = f.read()
                except Exception as e:
                    log(f"Failed to read {text_file}: {e}")
                    continue

                if not args.include_wave:
                    text_content = strip_wave_sections(text_content)

                analysis_layers = read_analysis_layers(segment_dir)
                prev_context = None
                if args.include_prev_segment and prev_segment_dir:
                    prev_context = load_prev_segment_context(
                        prev_segment_dir,
                        args.include_wave,
                        args.prev_context_chars,
                    )

                prompt = build_prompt(text_content, phase_limit, analysis_layers, geo_env_catalog, prev_context)
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
                    payload = extract_json_payload(result)
                    if payload is not None:
                        _payload, last_location, updated = apply_location_carry(payload, last_location) if args.carry_location else (payload, last_location, False)
                        if args.carry_location and updated:
                            result = json.dumps(_payload, ensure_ascii=False, indent=2)
                        elif args.carry_location and last_location is None:
                            last_location = normalize_location(next(
                                (scene.get("location") for scene in (_payload.get("scenes") or []) if isinstance(scene, dict)),
                                None,
                            ))
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
                prev_segment_dir = segment_dir
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

            analysis_layers = read_analysis_layers(chapter_dir)
            prompt = build_prompt(text_content, phase_limit, analysis_layers, geo_env_catalog, None)
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
