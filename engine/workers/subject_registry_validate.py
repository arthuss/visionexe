import argparse
import json
import os
import re
import shutil
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

from visionexe_paths import load_story_config, resolve_path


CHAPTER_RE = re.compile(r"chapter_(\d+)", re.IGNORECASE)
JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*([\[{].*?[\]}])\s*```", re.DOTALL | re.IGNORECASE)
PROP_ROLE_ACTOR_PREFIXES = ("actor_prop:", "character_prop:")
PROP_ROLE_SCENE_PREFIXES = ("scene_prop", "set_prop", "environment_prop")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def normalize_gemini_model(model: str | None):
    if not model:
        return None
    raw = str(model).strip()
    if not raw:
        return None
    normalized = raw.replace("_", "-")
    lowered = normalized.lower()
    if lowered in {"auto"}:
        return None
    if lowered in {"pro", "flash", "flash-lite"}:
        return lowered
    if lowered in {"gemini-3-pro"}:
        return "gemini-3-pro-preview"
    if lowered.startswith(("gemini-3", "gemini-2.5")):
        return normalized
    if lowered.startswith(("gemini-2.0", "gemini-1")):
        if "flash" in lowered:
            return "flash-lite" if "lite" in lowered else "flash"
        return "pro"
    return normalized


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
        json_text = json_text[: json_end + 1]
    try:
        payload = json.loads(json_text)
        response = payload.get("response")
        if isinstance(response, str):
            return response.strip()
    except json.JSONDecodeError:
        return raw_output.strip()
    return None


def classify_prop_type(item):
    if not isinstance(item, dict):
        return "requisite"
    role_value = str(item.get("role") or "").strip()
    lowered = role_value.lower()
    for prefix in PROP_ROLE_ACTOR_PREFIXES:
        if lowered.startswith(prefix):
            return "prop"
    for prefix in PROP_ROLE_SCENE_PREFIXES:
        if lowered.startswith(prefix):
            return "requisite"
    return "requisite"


def extract_json_blocks(text: str):
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


def call_gemini(prompt, model=None):
    cmd = resolve_gemini_command()
    if not cmd:
        raise RuntimeError("Gemini CLI nicht gefunden (gemini/npx).")
    cmd = cmd + ["--output-format", "json"]
    normalized_model = normalize_gemini_model(model)
    if model and normalized_model is None:
        print("[subject_registry_validate] Gemini Modell 'auto' -> CLI Default.")
    elif model and normalized_model and normalized_model != model:
        print(f"[subject_registry_validate] Gemini Modell '{model}' nicht kompatibel, nutze '{normalized_model}'.")
    if normalized_model:
        cmd += ["--model", normalized_model]
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
        raise RuntimeError(f"Gemini Fehler: {stderr}")
    response = parse_gemini_response(stdout)
    if not response:
        raise RuntimeError("Gemini: leere Antwort.")
    return response


def load_registry(path: Path):
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def build_chapter_regex(chapter_label: str) -> re.Pattern:
    safe_label = re.escape(chapter_label or "chapter")
    return re.compile(rf"{safe_label}_(\d+)", re.IGNORECASE)


def load_story_texts(filmsets_root: Path, chapter_label: str, chapter_padding: int) -> str:
    if not filmsets_root or not filmsets_root.exists():
        return ""
    chapters = []
    chapter_regex = build_chapter_regex(chapter_label)
    for path in filmsets_root.iterdir():
        if not path.is_dir():
            continue
        match = chapter_regex.search(path.name) or CHAPTER_RE.search(path.name)
        if not match:
            continue
        try:
            chapter_num = int(match.group(1))
        except ValueError:
            continue
        chapters.append((chapter_num, path))
    if not chapters:
        for path in filmsets_root.iterdir():
            if not path.is_dir():
                continue
            story_path = path / "story.txt"
            if story_path.exists():
                chapters.append((0, path))

    chapters.sort(key=lambda item: item[0])

    parts = []
    for chapter_num, chapter_dir in chapters:
        story_path = chapter_dir / "story.txt"
        text = read_text(story_path).strip()
        if not text:
            continue
        parts.append(f"[CHAPTER {chapter_num:0{chapter_padding}d}]\n{text}")
    return "\n\n".join(parts)


def extract_entities(analysis_master_path: Path):
    if not analysis_master_path.exists():
        return {}
    counts = defaultdict(Counter)
    with analysis_master_path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            blocks = record.get("analysis_blocks") or []
            if not isinstance(blocks, list):
                blocks = [blocks]
            for block in blocks:
                if not isinstance(block, dict):
                    continue
                for field, subject_type in (
                    ("actors", "character"),
                    ("props", "prop"),
                    ("environments", "set_environment"),
                    ("scenes", "scene"),
                ):
                    for item in block.get(field) or []:
                        name = item.get("name") if isinstance(item, dict) else item
                        if not name:
                            continue
                        resolved_type = subject_type
                        if field == "props":
                            resolved_type = classify_prop_type(item)
                        counts[resolved_type][str(name).strip()] += 1
    summary = {}
    for subject_type, counter in counts.items():
        summary[subject_type] = [
            {"name": name, "count": count}
            for name, count in counter.most_common()
        ]
    return summary


def build_prompt(registry, story_text, entity_summary):
    registry_json = json.dumps(registry, ensure_ascii=False, indent=2)
    entity_json = json.dumps(entity_summary, ensure_ascii=False, indent=2)
    return f"""
ROLE: Subject Registry Auditor / Canonicalizer.
TASK: Validate and normalize the subject registry based on the full story.

HARD RULES:
- Use ONLY the story text and evidence in the entity summary.
- Do NOT invent new entities.
- Consolidate duplicates and spelling variants (e.g., Henoch/Henou/Heno).
- If unsure, leave the entity and add a note in "notes".
- Provide a merge log that can be applied programmatically.
TYPE RULES:
- prop = subject-bound item (role actor_prop:<name>). Otherwise treat as requisite.
- requisite = scene dressing / set prop (role scene_prop or unknown ownership).

OUTPUT FORMAT (JSON ONLY):
{{
  "merges": [{{"canonical_id":"ID","merge_ids":["ID1","ID2"],"reason":"..."}}],
  "renames": [{{"old_id":"ID","new_id":"ID","reason":"..."}}],
  "aliases": [{{"canonical_id":"ID","aliases":["name1","name2"],"reason":"..."}}],
  "invalid": [{{"id":"ID","reason":"..."}}],
  "notes": ["free-form notes about anomalies or risks"]
}}

STORY TEXT (FULL):
{story_text}

ENTITY SUMMARY (FROM ANALYSIS):
{entity_json}

CURRENT REGISTRY:
{registry_json}
""".strip()


def main():
    parser = argparse.ArgumentParser(description="Validate subject registry and emit merge log via Gemini.")
    parser.add_argument("--story-root", help="Story root path (defaults to engine_config default_story_root).")
    parser.add_argument("--story-config", help="Path to story_config.json (overrides story-root).")
    parser.add_argument("--registry", help="Registry JSON path override.")
    parser.add_argument("--analysis-master", help="analysis_master.jsonl path override.")
    parser.add_argument("--output", help="Merge log output path.")
    parser.add_argument("--dump-prompt", help="Write the full prompt to a file and exit.")
    parser.add_argument("--model", help="Gemini model name.")
    args = parser.parse_args()

    story_config, story_root, repo_root = load_story_config(
        story_root=args.story_root,
        story_config_path=args.story_config,
    )

    filmsets_root = resolve_path(story_config.get("filmsets_root"), repo_root)
    subjects_root = resolve_path(story_config.get("subjects_root"), repo_root)
    registry_path = resolve_path(args.registry or (subjects_root / "registry.json"), repo_root)
    analysis_master_path = resolve_path(
        args.analysis_master or story_config.get("analysis_master_path"), repo_root
    )
    output_path = resolve_path(
        args.output or (subjects_root / "registry_merge_log.json"), repo_root
    )

    chapter_label = story_config.get("chapter_label", "chapter")
    chapter_padding = int(story_config.get("chapter_index_padding", 3))

    registry = load_registry(registry_path)
    if not registry:
        raise SystemExit(f"Registry not found or empty: {registry_path}")

    story_text = load_story_texts(filmsets_root, chapter_label, chapter_padding)
    if not story_text:
        raise SystemExit("Story text not found under filmsets.")

    entity_summary = extract_entities(analysis_master_path)

    prompt = build_prompt(registry, story_text, entity_summary)
    if args.dump_prompt:
        dump_path = resolve_path(args.dump_prompt, repo_root)
        dump_path.parent.mkdir(parents=True, exist_ok=True)
        dump_path.write_text(prompt, encoding="utf-8")
        print(f"Wrote prompt: {dump_path}")
        return
    response = call_gemini(prompt, args.model)
    payload = None
    try:
        payload = json.loads(response)
    except json.JSONDecodeError:
        blocks = extract_json_blocks(response)
        if blocks:
            payload = blocks[0]
    if payload is None:
        raw_path = output_path.with_suffix(".raw.txt")
        raw_path.write_text(response or "", encoding="utf-8")
        raise SystemExit(
            f"Gemini output is not valid JSON. Raw output saved to: {raw_path}"
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote merge log: {output_path}")


if __name__ == "__main__":
    main()
