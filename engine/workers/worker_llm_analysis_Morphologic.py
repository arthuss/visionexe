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

from geez_morphology_filter import apply_morphology_filters, load_json as load_filter_json, parse_json_payload
from visionexe_paths import ensure_dir, load_story_config, resolve_path
from vertex_gemini import call_vertex_gemini


MODEL_NAME = "gpt-oss:20b"
OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"

TRIGGER_FILES = {"story.txt", "verse.txt", "segment.txt", "mechanic_concept.txt"}
STORY_FILENAME = "story.txt"
GRAPHEMATIC_ANALYSIS_FILENAME = "analysis_llm_graphematic.txt"

WAVE_SECTION_RE = re.compile(
    r"^###\s+.*Integration in WAVE.*?(?=^###\s|\Z)",
    re.IGNORECASE | re.MULTILINE | re.DOTALL,
)
TOKEN_RE = re.compile(r"\S+")

ENGINE_ROOT = Path(__file__).resolve().parents[1]
TAGSET_PATH = ENGINE_ROOT / "analysis" / "tagsets" / "gez_pos_1.json"
CONFIG_TAGSET_PATH = ENGINE_ROOT / "config" / "gez_pos_tagset.json"


def strip_wave_sections(text):
    if not text:
        return text
    cleaned = WAVE_SECTION_RE.sub("", text)
    return cleaned.strip()


def wait_for_dependency(path, label, poll_seconds=2.0):
    if os.path.exists(path):
        return
    log(f"Waiting for {label} output: {path}")
    while not os.path.exists(path):
        time.sleep(poll_seconds)


def tokenize_text(text):
    tokens = []
    for match in TOKEN_RE.finditer(text):
        token_id = f"t{len(tokens) + 1}"
        tokens.append({
            "token_id": token_id,
            "surface": match.group(0),
            "span": {"start": match.start(), "end": match.end()},
        })
    return tokens


def load_tagset_data():
    for path in (TAGSET_PATH, CONFIG_TAGSET_PATH):
        try:
            if path.exists():
                return json.loads(path.read_text(encoding="utf-8"))
        except OSError:
            continue
    return {}


def build_timestamp():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def build_batch_prompt(story_text, segments, pos_tags, function_words):
    payload = {
        "story_text": story_text,
        "pos_tags": pos_tags,
        "function_words": function_words,
        "tokenization_policy": "whitespace",
        "segments": [
            {
                "segment_label": segment["segment_label"],
                "witness_id": segment["witness_id"],
                "tokens": segment["tokens"],
            }
            for segment in segments
        ],
    }
    return (
        "Instruction: Perform a rigorous Morphological Analysis (Level B) per segment.\n"
        "Goal: Enumerate morphologically valid options per token without choosing.\n\n"
        "Rules:\n"
        "1. Use only provided tokens and token_ids.\n"
        "2. POS tags must come from pos_tags.\n"
        "3. Function words must use allowed POS from function_words.\n"
        "4. root != surface; use null for function words.\n"
        "5. Provide evidence.lexicon_status + evidence.attestation for each option.\n\n"
        f"Input JSON:\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n\n"
        "Output strictly valid JSON:\n"
        "{\n"
        '  "segments": [\n'
        "    {\n"
        '      "segment_label": "segment_001",\n'
        '      "tokens": [\n'
        "        {\n"
        '          "token_id": "t1",\n'
        '          "options": [\n'
        "            {\n"
        '              "option_id": "A",\n'
        '              "pos": "N",\n'
        '              "analysis": {"kind": "lexical", "root": "root", "lemma": "lemma", "pattern": "pattern"},\n'
        '              "confidence": {"type": "undecided", "score": null},\n'
        '              "evidence": {"lexicon_status": "attested_in_lexicon", "attestation": []}\n'
        "            }\n"
        "          ]\n"
        "        }\n"
        "      ]\n"
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
        wait_for_dependency(
            os.path.join(segment_dir, GRAPHEMATIC_ANALYSIS_FILENAME),
            "graphematic",
        )
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
        tokens = tokenize_text(text_content)
        segments.append({
            "segment_label": segment_name,
            "segment_dir": segment_dir,
            "text": text_content,
            "text_file": text_file,
            "tokens": tokens,
            "witness_id": f"{chapter_name}/{segment_name}",
        })
    return segments


def merge_tokens(base_tokens, llm_tokens):
    token_map = {token.get("token_id"): token for token in (llm_tokens or []) if token.get("token_id")}
    merged = []
    for token in base_tokens:
        token_id = token["token_id"]
        entry = token_map.get(token_id, {})
        options = entry.get("options") or []
        segmentation = entry.get("segmentation")
        if not options:
            options = [
                {
                    "option_id": "MISSING",
                    "pos": "N",
                    "analysis": {
                        "kind": "lexical",
                        "root": None,
                        "lemma": None,
                        "pattern": None,
                        "affixes": {"prefixes": [], "suffixes": [], "clitics": []},
                        "features": {},
                        "gloss": None,
                    },
                    "confidence": {"type": "ruled_out", "score": 0.0},
                    "evidence": {
                        "lexicon_status": "unattested",
                        "attestation": [],
                        "constraints_checked": [],
                        "notes": "LLM missing token options",
                    },
                }
            ]
        merged_token = dict(token)
        if segmentation:
            merged_token["segmentation"] = segmentation
        merged_token["options"] = options
        merged.append(merged_token)
    return merged


def resolve_filter_overrides(args, repo_root):
    tagset_data = None
    function_words_data = None
    if args.filter_tagset:
        tagset_path = resolve_path(args.filter_tagset, repo_root)
        tagset_data = load_filter_json(tagset_path)
    if args.filter_function_words:
        function_words_path = resolve_path(args.filter_function_words, repo_root)
        function_words_data = load_filter_json(function_words_path)
    return tagset_data, function_words_data


def apply_filtering_payload(payload, args, repo_root):
    if not payload or args.no_filter:
        return payload, None
    tagset_data, function_words_data = resolve_filter_overrides(args, repo_root)
    return apply_morphology_filters(
        payload,
        tagset_data=tagset_data,
        function_words_data=function_words_data,
        drop_ruled_out=args.filter_drop_ruled_out,
        allow_unattested=args.filter_allow_unattested,
    )


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
    parser.add_argument("--no-filter", action="store_true", help="Write raw LLM output without filtering.")
    parser.add_argument("--filter-drop-ruled-out", action="store_true", help="Drop ruled-out options after filtering.")
    parser.add_argument("--filter-report", action="store_true", help="Write filter report JSON next to analysis.")
    parser.add_argument("--filter-tagset", help="Override POS tagset JSON path.")
    parser.add_argument("--filter-function-words", help="Override function word list JSON path.")
    parser.add_argument("--filter-allow-unattested", action="store_true", help="Keep unattested options (downgrade only).")
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
    target_path = os.path.join(target_dir, "analysis_llm_morphologic.txt")
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


def build_prompt(text_content, phase_limit, tokens, pos_tags, function_words, witness_id):
    payload = {
        "tokens": tokens,
        "pos_tags": pos_tags,
        "function_words": function_words,
        "tokenization_policy": "whitespace",
    }
    return f"""Instruction: Perform a rigorous, scientific Morphological Analysis (Level B) of the Ge'ez text.
Goal: Produce a matrix of options for each token, separating Graphematic, Morphemic, and Lexical layers.

SCIENTIFIC RULES:
1. Graphematic fidelity: keep token surfaces exactly as provided (no normalization, no hidden joins).
2. POS tags must come from GEZ-POS-1:
   [N, PN, ADJ, V, ADV, NUM, PRO.PERS, PRO.DEM, PRO.REL, PRO.INT, PRO.INDEF,
    PREP, CONJ.COORD, CONJ.SUB, PART.NEG, PART.MOD, PART.FOC, PART.REL, DET, AUX,
    CLIT.PRON, CLIT.CONJ, CLIT.PREP].
3. Use the provided tokens as-is; do not create or merge tokens.
4. Do not merge POS tags (no "Noun|Verb"). Emit separate options instead.
5. ROOT vs SURFACE: root is consonantal root only; function words must use null.
6. SEGMENTATION: mark prefixes/suffixes/clitics as morphemes, but do not split tokens into new tokens.
7. EVIDENCE: each option needs lexicon_status + attestation array (empty only if explicitly unattested).
8. CONFIDENCE: set type (undecided/weak/moderate/strong/ruled_out) and optional score.

Input Text:
{text_content}

Tokenization + constraints JSON:
{json.dumps(payload, ensure_ascii=False, indent=2)}

Output strictly valid JSON matching data/schemas/gez_morphology.schema.json:
{{
  "meta": {{
    "schema_version": "1.0.0",
    "created_at": "YYYY-MM-DDThh:mm:ssZ",
    "created_by": "llm",
    "language": "gez",
    "tagset_id": "GEZ-POS-1",
    "tokenization_policy": "whitespace"
  }},
  "source": {{
    "witness_id": "{witness_id}",
    "graphematic_string": "...",
    "normalization_policy": "none",
    "uncertainties": []
  }},
  "tokens": [
    {{
      "token_id": "t1",
      "surface": "token_surface",
      "span": {{"start": 0, "end": 0}},
      "segmentation": {{
        "morphemes": [{{"morph_id": "m1", "surface": "prefix", "type": "prefix"}}]
      }},
      "options": [
        {{
          "option_id": "A",
          "pos": "N",
          "analysis": {{
            "kind": "lexical",
            "root": "root",
            "lemma": "lemma",
            "pattern": "pattern_code",
            "affixes": {{"prefixes": [], "suffixes": [], "clitics": []}},
            "features": {{"state": "construct"}},
            "gloss": "gloss"
          }},
          "confidence": {{"type": "undecided", "score": null}},
          "evidence": {{
            "lexicon_status": "attested_in_lexicon",
            "attestation": [{{"type": "lexicon", "ref": "REF"}}],
            "constraints_checked": [],
            "notes": ""
          }}
        }}
      ]
    }}
  ]
}}"""


def apply_filtering(result, args, repo_root):
    if not result or args.no_filter:
        return result, None

    payload = parse_json_payload(result)
    if payload is None:
        log("Filter skipped: LLM output is not valid JSON.")
        return result, None

    tagset_data = None
    function_words_data = None
    if args.filter_tagset:
        tagset_path = resolve_path(args.filter_tagset, repo_root)
        tagset_data = load_filter_json(tagset_path)
    if args.filter_function_words:
        function_words_path = resolve_path(args.filter_function_words, repo_root)
        function_words_data = load_filter_json(function_words_path)

    filtered_payload, report = apply_morphology_filters(
        payload,
        tagset_data=tagset_data,
        function_words_data=function_words_data,
        drop_ruled_out=args.filter_drop_ruled_out,
        allow_unattested=args.filter_allow_unattested,
    )
    filtered_text = json.dumps(filtered_payload, ensure_ascii=False, indent=2)
    return filtered_text, report


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
        progress_csv = str(Path(data_root) / "analysis" / "analysis_progress_python_morphologic_v2.csv")
    else:
        progress_csv = str(resolve_path(progress_csv, repo_root))

    segment_label = story_config.get("segment_label", "segment")
    segment_type = story_config.get("segment_type", "segment")
    chapter_label = story_config.get("chapter_label", "chapter")
    phase_limit = int(story_config.get("dynamic_phase_max", 3))

    tagset_data = load_tagset_data()
    pos_tags = [entry.get("tag") for entry in tagset_data.get("tags", []) if entry.get("tag")]
    function_words = tagset_data.get("function_words", [])

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

            prompt = build_batch_prompt(story_text, segment_inputs, pos_tags, function_words)
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
                llm_tokens = item.get("tokens")
                if not segment_label_value:
                    continue
                segment_info = segment_map.get(segment_label_value)
                if not segment_info:
                    continue
                merged_tokens = merge_tokens(segment_info["tokens"], llm_tokens)
                segment_payload = {
                    "meta": {
                        "schema_version": "1.0.0",
                        "created_at": build_timestamp(),
                        "created_by": "worker_llm_analysis_Morphologic",
                        "language": "gez",
                        "tagset_id": tagset_data.get("tagset_id", "GEZ-POS-1"),
                        "tokenization_policy": "whitespace",
                    },
                    "source": {
                        "witness_id": segment_info["witness_id"],
                        "graphematic_string": segment_info["text"],
                        "normalization_policy": "none",
                        "uncertainties": [],
                    },
                    "tokens": merged_tokens,
                }
                filtered_payload, report = apply_filtering_payload(segment_payload, args, repo_root)
                output_payload = filtered_payload or segment_payload
                output_text = json.dumps(output_payload, ensure_ascii=False, indent=2)
                write_analysis(segment_info["segment_dir"], output_text)
                if args.filter_report and report:
                    report_path = os.path.join(
                        segment_info["segment_dir"],
                        "analysis_llm_morphologic_filter_report.json",
                    )
                    with open(report_path, "w", encoding="utf-8") as f:
                        json.dump(report, f, ensure_ascii=False, indent=2)
                append_progress(progress_csv, {
                    "ChapterID": chapter_id,
                    "SegmentLabel": segment_label_value,
                    "SegmentType": segment_type,
                    "Status": "DONE",
                    "SourcePath": segment_info["text_file"],
                    "RawContent": output_text,
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

                wait_for_dependency(
                    os.path.join(segment_dir, GRAPHEMATIC_ANALYSIS_FILENAME),
                    "graphematic",
                )
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

                tokens = tokenize_text(text_content)
                witness_id = f"{chapter_name}/{segment_name}"
                prompt = build_prompt(text_content, phase_limit, tokens, pos_tags, function_words, witness_id)
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
                    filtered_result, report = apply_filtering(result, args, repo_root)
                    log(f"Analyzed {chapter_name}/{segment_name} ({duration:.1f}s).")
                    write_analysis(segment_dir, filtered_result)
                    if args.filter_report and report:
                        report_path = os.path.join(segment_dir, "analysis_llm_morphologic_filter_report.json")
                        with open(report_path, "w", encoding="utf-8") as f:
                            json.dump(report, f, ensure_ascii=False, indent=2)
                    append_progress(progress_csv, {
                        "ChapterID": chapter_id,
                        "SegmentLabel": segment_name,
                        "SegmentType": segment_type,
                        "Status": "DONE",
                        "SourcePath": text_file,
                        "RawContent": filtered_result,
                    })
                else:
                    log(f"No response for {chapter_name}/{segment_name}.")
        else:
            if chapter_id in completed and not target_chapters:
                log(f"Skipping {chapter_name} (done).")
                continue

            wait_for_dependency(
                os.path.join(chapter_dir, GRAPHEMATIC_ANALYSIS_FILENAME),
                "graphematic",
            )
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

            tokens = tokenize_text(text_content)
            witness_id = chapter_name
            prompt = build_prompt(text_content, phase_limit, tokens, pos_tags, function_words, witness_id)
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
                filtered_result, report = apply_filtering(result, args, repo_root)
                log(f"Analyzed {chapter_name} ({duration:.1f}s).")
                files_written = distribute_analysis(chapter_dir, filtered_result)
                log(f"Wrote analysis to {files_written} folders.")
                if args.filter_report and report:
                    report_path = os.path.join(chapter_dir, "analysis_llm_morphologic_filter_report.json")
                    with open(report_path, "w", encoding="utf-8") as f:
                        json.dump(report, f, ensure_ascii=False, indent=2)
                append_progress(progress_csv, {
                    "ChapterID": chapter_id,
                    "SegmentLabel": "",
                    "SegmentType": "",
                    "Status": "DONE",
                    "SourcePath": text_file,
                    "RawContent": filtered_result,
                })
            else:
                log(f"No response for {chapter_name}.")

    log("All tasks completed.")


if __name__ == "__main__":
    main()
