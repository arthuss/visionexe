import os
import re
import json
import argparse
import subprocess
import shutil
import time
import urllib.request
import urllib.error
import sys

DEFAULT_BASE_PATH = r"C:\Users\sasch\henoch\filmsets"
DEFAULT_VOICE_PROFILES = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "audio_voice_profiles.json",
)
DEFAULT_ACTOR_KEY = "henoch"
DEFAULT_TTS_ENDPOINT = os.environ.get("TTS_ENDPOINT", "http://localhost:7865")
DEFAULT_TTS_TIMEOUT_SEC = 600
DEFAULT_TTS_POLL_INTERVAL = 1.5
DEFAULT_TTS_WSL_ROOT = os.environ.get("TTS_WSL_ROOT", r"\\wsl.localhost\Ubuntu22Old")
DEFAULT_TTS_PROJECT_ROOT = os.environ.get(
    "TTS_WSL_PROJECT_ROOT",
    r"\\wsl.localhost\Ubuntu22Old\home\sasch\chatterbox",
)
DEFAULT_TTS_SPEAKER_REGISTRY = os.environ.get(
    "TTS_SPEAKER_REGISTRY",
    r"\\wsl.localhost\Ubuntu22Old\home\sasch\chatterbox\data\speakers\registry.json",
)
DEFAULT_MAX_WORDS = 10
WORDS_PER_SEC = 2.0
MIN_WORDS = 4


def load_text(path):
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


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
        print("Gemini CLI nicht gefunden (gemini/npx).")
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
            print(f"Gemini Fehler: {stderr}")
            return None
        return parse_gemini_response(stdout)
    except OSError as exc:
        print(f"Gemini Start fehlgeschlagen: {exc}")
        return None


def load_voice_profiles(path):
    if not os.path.exists(path):
        return {}, {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        return payload.get("profiles", {}), payload.get("tts_defaults", {})
    except (json.JSONDecodeError, OSError) as exc:
        print(f"Warnung: Konnte Voice Profiles nicht lesen: {exc}")
        return {}, {}


def load_speaker_registry(path):
    if not path or not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"Warnung: Konnte Speaker Registry nicht lesen: {exc}")
        return {}

    entries = []
    if isinstance(payload, dict):
        if isinstance(payload.get("speakers"), list):
            entries = payload["speakers"]
        elif isinstance(payload.get("registry"), list):
            entries = payload["registry"]
        elif isinstance(payload.get("items"), list):
            entries = payload["items"]
        else:
            for key, value in payload.items():
                if isinstance(value, dict):
                    entry = dict(value)
                    entry.setdefault("name", key)
                    entries.append(entry)
                else:
                    entries.append({"name": key, "speaker_id": value})
    elif isinstance(payload, list):
        entries = payload

    mapping = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        speaker_id = (
            entry.get("speaker_id")
            or entry.get("id")
            or entry.get("uuid")
            or entry.get("key")
        )
        if not speaker_id:
            continue
        names = []
        for field in ("name", "label", "alias"):
            value = entry.get(field)
            if value:
                names.append(value)
        aliases = entry.get("aliases")
        if isinstance(aliases, list):
            names.extend(aliases)
        for name in names:
            norm = normalize_text(str(name))
            if norm:
                mapping[norm] = speaker_id
    return mapping


def extract_field(block, label):
    bold_pattern = re.compile(
        rf"^\*\*{re.escape(label)}:\*\*\s*(.+?)(?=^\*\*\w+:\*\*|^###\s+|^##\s+|\Z)",
        re.M | re.S,
    )
    match = bold_pattern.search(block)
    if match:
        return match.group(1).strip()
    plain_pattern = re.compile(
        rf"^{re.escape(label)}:\s*(.+?)(?=^\w+:\s+|^###\s+|^##\s+|\Z)",
        re.M | re.S,
    )
    match = plain_pattern.search(block)
    if not match:
        return ""
    return match.group(1).strip()


def normalize_text(text):
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def detect_actor(text, profiles, default_key):
    if not profiles:
        return default_key
    normalized = normalize_text(text)
    for key in sorted(profiles.keys(), key=len, reverse=True):
        candidate = normalize_text(key.replace("_", " "))
        if not candidate:
            continue
        if re.search(rf"\b{re.escape(candidate)}\b", normalized):
            return key
    return default_key


def resolve_speaker_id(actor_key, profile, registry_map):
    tts_profile = {}
    if isinstance(profile, dict):
        tts_profile = profile.get("tts") or {}
    if tts_profile.get("speaker_id") or tts_profile.get("audio_prompt_path"):
        return tts_profile.get("speaker_id")
    candidates = []
    if isinstance(profile, dict):
        if profile.get("speaker_match"):
            candidates.append(profile["speaker_match"])
        if profile.get("voice_id"):
            candidates.append(profile["voice_id"])
    candidates.append(actor_key)
    for candidate in candidates:
        norm = normalize_text(str(candidate))
        if norm and norm in registry_map:
            return registry_map[norm]
    return None

def merge_tts_settings(defaults, profile):
    settings = dict(defaults or {})
    tts_profile = {}
    if isinstance(profile, dict):
        tts_profile = profile.get("tts") or {}
    settings.update(tts_profile)
    return settings


def post_json(url, payload, timeout_sec):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout_sec) as response:
        return json.loads(response.read().decode("utf-8"))


def get_json(url, timeout_sec):
    with urllib.request.urlopen(url, timeout=timeout_sec) as response:
        return json.loads(response.read().decode("utf-8"))


def submit_tts_job(endpoint, payload, timeout_sec):
    response = post_json(f"{endpoint}/queue", payload, timeout_sec)
    if isinstance(response, dict):
        return response.get("job_id")
    return None


def fetch_tts_result(endpoint, job_id, timeout_sec):
    primary = f"{endpoint}/result/{job_id}"
    try:
        return get_json(primary, timeout_sec)
    except urllib.error.HTTPError:
        fallback = f"{endpoint}/result?job_id={job_id}"
        return get_json(fallback, timeout_sec)


def poll_tts_result(endpoint, job_id, timeout_sec, poll_interval):
    start = time.time()
    while time.time() - start < timeout_sec:
        result = fetch_tts_result(endpoint, job_id, timeout_sec)
        status = result.get("status")
        if status == "done":
            return result
        if status == "error":
            return result
        time.sleep(poll_interval)
    return {"status": "timeout", "job_id": job_id}


def resolve_wsl_path(path, wsl_root, project_root):
    if not path:
        return None
    if re.match(r"^[a-zA-Z]:\\", path) or path.startswith("\\\\"):
        return path
    if path.startswith("/"):
        return wsl_root + path.replace("/", "\\")
    if path.startswith("data/") or path.startswith("data\\"):
        return os.path.join(project_root, path.replace("/", "\\"))
    return path


def extract_audio_paths(result):
    if not isinstance(result, dict):
        return []
    if result.get("audio_paths"):
        return result["audio_paths"]
    if result.get("audio_path"):
        return [result["audio_path"]]
    return []


def copy_tts_outputs(audio_paths, output_dir, slug):
    os.makedirs(output_dir, exist_ok=True)
    outputs = []
    for idx, source in enumerate(audio_paths):
        suffix = f"_voice_v{idx + 1:02d}" if len(audio_paths) > 1 else "_voice"
        dest = os.path.join(output_dir, f"{slug}{suffix}.wav")
        shutil.copy(source, dest)
        outputs.append(dest)
    return outputs


def update_voice_meta(path, tts_meta):
    if not os.path.exists(path):
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except (json.JSONDecodeError, OSError):
        payload = {}
    payload["tts"] = tts_meta
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=True)


def build_monologue_prompt(
    scene,
    action_text,
    dialog_text,
    actor_key,
    regie,
    concept_excerpt,
    chapter_excerpt,
    max_words,
):
    regie_text = json.dumps(regie or {}, ensure_ascii=True)
    return (
        "You write internal monologue for Exeget:OS film scenes.\n"
        "Rules:\n"
        "- 1-2 sentences only.\n"
        f"- Max {max_words} words total.\n"
        "- First-person present tense.\n"
        "- German only.\n"
        "- No quotes, no markdown, no explanations.\n"
        "- No ellipses.\n"
        "- Emotional, concrete, sensory.\n"
        "- Avoid literal visual descriptions; focus on feeling, memory, cause/effect.\n"
        "- Avoid generic filler; anchor in one specific sensation or system detail.\n"
        "\n"
        f"Actor focus: {actor_key}\n"
        f"Scene: ACT {scene['act']} SCENE {scene['scene_id']} ({scene['title']})\n"
        f"Timecode: {scene['timecode']}\n"
        f"Regie JSON: {regie_text}\n"
        f"Mechanic concept (excerpt): {concept_excerpt}\n"
        f"Chapter text (excerpt): {chapter_excerpt}\n"
        f"Action: {action_text}\n"
        f"Dialog: {dialog_text}\n"
    )


def parse_timecode_value(value):
    if not value:
        return None
    parts = value.strip().split(":")
    try:
        if len(parts) == 2:
            minutes, seconds = parts
            return int(minutes) * 60 + float(seconds)
        if len(parts) == 3:
            hours, minutes, seconds = parts
            return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    except ValueError:
        return None
    return None


def parse_timecode_range(timecode):
    if not timecode or "-" not in timecode:
        return None
    start_raw, end_raw = [p.strip() for p in timecode.split("-", 1)]
    start = parse_timecode_value(start_raw)
    end = parse_timecode_value(end_raw)
    if start is None or end is None:
        return None
    duration = end - start
    return duration if duration > 0 else None


def compute_word_budget(scene, regie):
    if isinstance(regie, dict):
        regie_max = regie.get("voice_words_max")
        if isinstance(regie_max, int) and regie_max > 0:
            return regie_max
    duration = parse_timecode_range(scene.get("timecode", ""))
    if duration is None:
        return DEFAULT_MAX_WORDS
    budget = int(round(duration * WORDS_PER_SEC))
    budget = max(MIN_WORDS, budget)
    return min(DEFAULT_MAX_WORDS, budget)


def trim_to_word_limit(text, max_words):
    if not text:
        return text
    words = text.strip().split()
    if len(words) <= max_words:
        return text.strip()
    trimmed = " ".join(words[:max_words]).strip()
    if trimmed and trimmed[-1] not in ".!?":
        trimmed = trimmed + "."
    return trimmed


def extract_section(block, header):
    start = block.find(header)
    if start == -1:
        return ""
    start = block.find("\n", start)
    if start == -1:
        return ""
    start += 1
    next_marker = re.search(r"^###\s+", block[start:], re.M)
    end = start + next_marker.start() if next_marker else len(block)
    return block[start:end].strip()


def parse_scene_header(block):
    header_line = ""
    for line in block.splitlines():
        if line.strip().startswith("## [ACT"):
            header_line = line.strip()
            break
    if not header_line:
        return None
    match = re.search(
        r"\[ACT\s+(?P<act>\d+)\]\s+\[SCENE\s+(?P<scene>[\d\.]+)\]\s+\[Timecode:\s*(?P<time>[^\]]+)\]\s+\[(?P<title>[^\]]+)\]",
        header_line,
    )
    if not match:
        return None
    return {
        "act": int(match.group("act")),
        "scene_id": match.group("scene"),
        "timecode": match.group("time").strip(),
        "title": match.group("title").strip(),
    }


def normalize_scene_slug(act, scene_id):
    parts = scene_id.split(".")
    sub = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
    return f"scene_{act:02d}_{sub:02d}"


def parse_scene_ref(value):
    if not value:
        return None
    raw = str(value).strip()
    if raw.startswith("scene_"):
        return raw
    match = re.match(r"^(\d+)(?:\.(\d+))?$", raw)
    if match:
        act = int(match.group(1))
        sub = int(match.group(2) or 0)
        return f"scene_{act:02d}_{sub:02d}"
    return None


def parse_narrator_text(script_text):
    lines = script_text.splitlines()
    for idx, line in enumerate(lines):
        if line.strip().startswith("NARRATOR_TEXT:"):
            text = line.split(":", 1)[1].strip()
            if text:
                return text
            collected = []
            for follow in lines[idx + 1:]:
                if follow.strip().startswith("##"):
                    break
                if follow.strip() == "" and collected:
                    break
                if follow.strip():
                    collected.append(follow.strip())
            return " ".join(collected).strip()
    return ""


def parse_monologue_plan(script_text):
    for line in script_text.splitlines():
        line = line.strip()
        if line.startswith("MONOLOGUE_JSON:"):
            payload = line.split(":", 1)[1].strip()
            if not payload:
                return {}
            try:
                return json.loads(payload)
            except json.JSONDecodeError:
                return {}
    return {}


def build_monologue_lookup(plan):
    lookup = {}
    if not isinstance(plan, dict):
        return lookup
    actors = plan.get("actors")
    if not isinstance(actors, dict):
        return lookup
    for actor_name, entries in actors.items():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            slug = parse_scene_ref(entry.get("scene"))
            text = entry.get("text")
            if not slug or not text:
                continue
            lookup.setdefault(slug, []).append({
                "actor": actor_name,
                "text": str(text).strip(),
                "words_max": entry.get("words_max"),
            })
    return lookup


def resolve_actor_key_from_name(name, profiles, default_key):
    if not name:
        return default_key
    name_norm = normalize_text(str(name))
    if not name_norm:
        return default_key
    for key in profiles.keys():
        if normalize_text(key) == name_norm:
            return key
    return detect_actor(str(name), profiles, default_key)


def select_monologue_entry(entries, actor_key, profiles, default_key):
    if not entries:
        return None, actor_key
    actor_norm = normalize_text(actor_key)
    for entry in entries:
        entry_actor = entry.get("actor")
        if normalize_text(entry_actor) == actor_norm:
            resolved_actor = resolve_actor_key_from_name(entry_actor, profiles, default_key)
            return entry, resolved_actor
    entry = entries[0]
    resolved_actor = resolve_actor_key_from_name(entry.get("actor"), profiles, default_key)
    return entry, resolved_actor


def parse_json_value(line, key):
    if not line.startswith(key):
        return None
    value = line.split(":", 1)[1].strip()
    if not value:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return {"_raw": value, "_error": "json_decode_failed"}


def parse_regie_block(block_text):
    regie_json = None
    for line in block_text.splitlines():
        line = line.strip()
        if line.startswith("REGIE_JSON:"):
            regie_json = parse_json_value(line, "REGIE_JSON")
            break
    return regie_json or {}


def normalize_zeta_edits(edits):
    if isinstance(edits, list):
        return {"edits": edits}
    if isinstance(edits, dict):
        return edits
    return {"edits": []}


def parse_bgm_block(block_text):
    data = {"music_automation": None, "zeta_dynamic_edits": None}
    for line in block_text.splitlines():
        line = line.strip()
        if line.startswith("MUSIC_AUTOMATION_JSON:"):
            data["music_automation"] = parse_json_value(line, "MUSIC_AUTOMATION_JSON")
        elif line.startswith("ZETA_DYNAMIC_EDITS:"):
            data["zeta_dynamic_edits"] = parse_json_value(line, "ZETA_DYNAMIC_EDITS")
    return data


def parse_spot_fx_block(block_text):
    base_atmo = None
    object_injections = None
    for line in block_text.splitlines():
        line = line.strip()
        if line.startswith("BASE_ATMO:"):
            base_atmo = line.split(":", 1)[1].strip()
        elif line.startswith("OBJECT_INJECTIONS:"):
            object_injections = parse_json_value(line, "OBJECT_INJECTIONS")
    return {"base_atmo": base_atmo, "object_injections": object_injections}


def parse_scenes(script_text):
    scenes = []
    matches = list(re.finditer(r"^## \[ACT\s+", script_text, re.M))
    if not matches:
        return scenes
    for idx, match in enumerate(matches):
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(script_text)
        block = script_text[start:end].strip()
        header = parse_scene_header(block)
        if not header:
            continue
        action_text = extract_field(block, "Action")
        dialog_text = extract_field(block, "Dialog")
        regie_block = extract_section(block, "### 0. REGIE DATA")
        if not regie_block:
            regie_block = extract_section(block, "### 0. REGIE")
        bgm_block = extract_section(block, "### 7. BGM & HARMONICS")
        spot_block = extract_section(block, "### 8. SPOT FX INJECTION")
        regie_data = parse_regie_block(regie_block) if regie_block else {}
        bgm_data = parse_bgm_block(bgm_block) if bgm_block else {}
        spot_data = parse_spot_fx_block(spot_block) if spot_block else {}
        scenes.append({
            **header,
            "action": action_text,
            "dialog": dialog_text,
            "regie": regie_data,
            "bgm": bgm_data,
            "spot_fx": spot_data,
        })
    return scenes


def write_scene_meta(output_dir, scene):
    os.makedirs(output_dir, exist_ok=True)
    slug = normalize_scene_slug(scene["act"], scene["scene_id"])
    output_path = os.path.join(output_dir, f"{slug}_audio_meta.json")
    facesync = {
        "enabled": False,
        "method": "none",
        "source_audio": f"Media/{slug}_voice.wav",
        "target_media": f"Media/{slug}.mp4",
        "output": f"Media/{slug}_avatar.mp4",
    }
    gbuffer = {
        "enabled": False,
        "manifest": f"Media/{slug}_avatar_manifest.json",
        "pose_source": f"Media/{slug}_bodytrack.txt",
        "pose_source_type": "maxine_bodytrack_txt",
        "passes": {
            "normal": f"Media/{slug}_avatar_normal.exr",
            "depth": f"Media/{slug}_avatar_depth.exr",
            "motion": f"Media/{slug}_avatar_motion.exr",
            "mask": f"Media/{slug}_avatar_mask.exr",
        },
    }
    payload = {
        "scene": {
            "act": scene["act"],
            "scene_id": scene["scene_id"],
            "timecode": scene["timecode"],
            "title": scene["title"],
        },
        "actor": scene.get("actor"),
        "regie": scene.get("regie", {}),
        "music_automation": scene.get("bgm", {}).get("music_automation"),
        "zeta_dynamic_edits": normalize_zeta_edits(scene.get("bgm", {}).get("zeta_dynamic_edits")),
        "spot_fx": scene.get("spot_fx"),
        "facesync": facesync,
        "gbuffer": gbuffer,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=True)
    return output_path


def write_text_file(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text.strip() + "\n")


def write_monologue(output_dir, slug, text):
    path = os.path.join(output_dir, f"{slug}_monologue.txt")
    write_text_file(path, text)
    return path


def write_voice_meta(output_dir, slug, actor_key, profile, monologue_path, speaker_id=None):
    path = os.path.join(output_dir, f"{slug}_voice.json")
    payload = {
        "actor": actor_key,
        "voice_profile": profile or {},
        "monologue_file": monologue_path,
        "speaker_id": speaker_id,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=True)
    return path


def run(
    chapter_num,
    base_path,
    output_dir,
    voice_profiles_path,
    default_actor,
    monologue_source,
    monologue_output,
    gemini_model,
    tts_enabled,
    tts_endpoint,
    tts_timeout_sec,
    tts_poll_interval,
    tts_output_dir,
    tts_wsl_root,
    tts_project_root,
    speaker_registry_path,
    dry_run,
    skip_existing,
    no_monologue,
):
    chapter_folder = f"chapter_{chapter_num:03d}"
    chapter_path = os.path.join(base_path, chapter_folder)
    script_path = os.path.join(chapter_path, "DREHBUCH_HOLLYWOOD.md")
    if not os.path.exists(script_path):
        print(f"Fehler: Drehbuch nicht gefunden: {script_path}")
        return False

    script_text = load_text(script_path)
    narrator_text = parse_narrator_text(script_text)
    monologue_plan = parse_monologue_plan(script_text)
    monologue_lookup = build_monologue_lookup(monologue_plan)
    scenes = parse_scenes(script_text)
    if not scenes:
        print("Keine Szenen gefunden (keine passenden ACT/SCENE-Header).")
        return True

    concept_path = os.path.join(chapter_path, "concept_engine", "mechanic_concept.txt")
    concept_text = load_text(concept_path)
    concept_excerpt = " ".join(concept_text.split())
    if len(concept_excerpt) > 1200:
        concept_excerpt = concept_excerpt[:1200].rstrip() + "..."
    chapter_text = load_text(os.path.join(chapter_path, "chapter.txt"))
    chapter_excerpt = " ".join(chapter_text.split())
    if len(chapter_excerpt) > 1200:
        chapter_excerpt = chapter_excerpt[:1200].rstrip() + "..."

    profiles, tts_defaults = load_voice_profiles(voice_profiles_path)
    registry_map = load_speaker_registry(speaker_registry_path)
    if default_actor not in profiles:
        default_actor = DEFAULT_ACTOR_KEY

    output_dir = output_dir or os.path.join(chapter_path, "audio")
    tts_output_dir = tts_output_dir or os.path.join(chapter_path, "Media")
    tts_scene_enabled = bool(tts_enabled and monologue_output in ("scene", "both"))
    if tts_enabled and not tts_scene_enabled:
        print(f"Hinweis: TTS wird in monologue-output '{monologue_output}' uebersprungen.")
    monologue_bundle = []
    actor_bundles = {}

    if not dry_run and narrator_text:
        narration_path = os.path.join(output_dir, f"chapter_{chapter_num:03d}_narration.txt")
        write_text_file(narration_path, narrator_text)
        print(f"Wrote: {narration_path}")

    for scene in scenes:
        slug = normalize_scene_slug(scene["act"], scene["scene_id"])
        action_text = scene.get("action", "")
        dialog_text = scene.get("dialog", "")
        regie = scene.get("regie", {})
        max_words = compute_word_budget(scene, regie)
        actor_key = detect_actor(
            " ".join([scene.get("title", ""), action_text, dialog_text]),
            profiles,
            default_actor,
        )
        plan_entry = None
        if monologue_source in ("plan", "hybrid"):
            plan_entry, plan_actor = select_monologue_entry(
                monologue_lookup.get(slug),
                actor_key,
                profiles,
                default_actor,
            )
            if plan_actor:
                actor_key = plan_actor
        scene["actor"] = actor_key

        if dry_run:
            print(f"Scene {scene['scene_id']} parsed (dry run).")
            continue
        meta_path = write_scene_meta(output_dir, scene)
        print(f"Wrote: {meta_path}")

        if no_monologue:
            continue

        monologue_path = ""
        voice_path = ""
        if monologue_output in ("scene", "both"):
            monologue_path = os.path.join(output_dir, f"{slug}_monologue.txt")
            voice_path = os.path.join(output_dir, f"{slug}_voice.json")
            if skip_existing and os.path.exists(monologue_path) and os.path.exists(voice_path):
                print(f"Skip existing: {slug}")
                continue

        monologue = None
        if plan_entry:
            entry_words = plan_entry.get("words_max")
            if isinstance(entry_words, int) and entry_words > 0:
                max_words = entry_words
            monologue = plan_entry.get("text")

        if monologue_source in ("plan", "hybrid") and monologue:
            monologue = trim_to_word_limit(monologue, max_words)
        elif monologue_source == "plan":
            print(f"Skip monologue (no plan entry): {slug}")
            continue
        else:
            prompt = build_monologue_prompt(
                scene,
                action_text,
                dialog_text,
                actor_key,
                regie,
                concept_excerpt,
                chapter_excerpt,
                max_words,
            )
            monologue = call_gemini(prompt, model=gemini_model)
            if not monologue:
                print(f"Warnung: Keine Monolog-Antwort fuer Szene {scene['scene_id']}.")
                continue
            monologue = trim_to_word_limit(monologue, max_words)

        entry = {
            "scene": slug,
            "actor": actor_key,
            "timecode": scene.get("timecode", ""),
            "title": scene.get("title", ""),
            "words_max": max_words,
            "text": monologue,
        }
        monologue_bundle.append(entry)
        actor_bundles.setdefault(actor_key, []).append(entry)

        if monologue_output not in ("scene", "both"):
            continue

        monologue_path = write_monologue(output_dir, slug, monologue)
        profile = profiles.get(actor_key, {})
        speaker_id = resolve_speaker_id(actor_key, profile, registry_map)
        voice_path = write_voice_meta(
            output_dir,
            slug,
            actor_key,
            profile,
            monologue_path,
            speaker_id=speaker_id,
        )
        print(f"Wrote: {monologue_path}")
        print(f"Wrote: {voice_path}")

        if not tts_scene_enabled:
            continue

        if skip_existing:
            existing = [
                os.path.join(tts_output_dir, f"{slug}_voice.wav"),
                os.path.join(tts_output_dir, f"{slug}_voice_v01.wav"),
            ]
            if any(os.path.exists(path) for path in existing):
                print(f"Skip TTS existing: {slug}")
                continue

        tts_settings = merge_tts_settings(tts_defaults, profile)
        if speaker_id and not tts_settings.get("speaker_id"):
            tts_settings["speaker_id"] = speaker_id
        payload = {
            "model": tts_settings.get("model", "turbo"),
            "text": monologue,
            "language_id": tts_settings.get("language_id", "de"),
            "speaker_id": tts_settings.get("speaker_id"),
            "audio_prompt_path": tts_settings.get("audio_prompt_path"),
            "temperature": tts_settings.get("temperature", 0.8),
            "top_p": tts_settings.get("top_p", 0.95),
            "top_k": tts_settings.get("top_k", 1000),
            "repetition_penalty": tts_settings.get("repetition_penalty", 1.2),
            "min_p": tts_settings.get("min_p", 0.0),
            "exaggeration": tts_settings.get("exaggeration", 0.5),
            "cfg_weight": tts_settings.get("cfg_weight", 0.5),
            "norm_loudness": tts_settings.get("norm_loudness", True),
            "max_new_tokens": tts_settings.get("max_new_tokens", 400),
            "n_variations": tts_settings.get("n_variations", 1),
            "seed_base": tts_settings.get("seed_base"),
        }

        try:
            job_id = submit_tts_job(tts_endpoint, payload, tts_timeout_sec)
        except urllib.error.URLError as exc:
            print(f"TTS Queue Fehler: {exc}")
            continue

        if not job_id:
            print(f"TTS Queue Fehler: Keine job_id fuer {slug}")
            continue

        result = poll_tts_result(tts_endpoint, job_id, tts_timeout_sec, tts_poll_interval)
        if result.get("status") != "done":
            print(f"TTS Fehler fuer {slug}: {result}")
            continue

        audio_paths = []
        for path in extract_audio_paths(result):
            resolved = resolve_wsl_path(path, tts_wsl_root, tts_project_root)
            audio_paths.append(resolved)

        audio_paths = [path for path in audio_paths if path and os.path.exists(path)]
        if not audio_paths:
            print(f"TTS Fehler fuer {slug}: Keine Audio-Dateien gefunden.")
            continue

        outputs = copy_tts_outputs(audio_paths, tts_output_dir, slug)
        update_voice_meta(
            voice_path,
            {
                "endpoint": tts_endpoint,
                "job_id": job_id,
                "output_files": outputs,
                "speaker_id": tts_settings.get("speaker_id"),
            },
        )
        print(f"TTS outputs: {', '.join(outputs)}")

    if monologue_output in ("chapter", "both") and monologue_bundle:
        bundle_path = os.path.join(output_dir, f"chapter_{chapter_num:03d}_monologue.txt")
        if skip_existing and os.path.exists(bundle_path):
            print(f"Skip existing: {bundle_path}")
        else:
            lines = []
            for entry in monologue_bundle:
                tag = f"[{entry['scene']}][{entry['actor']}]"
                if entry.get("timecode"):
                    tag += f"[{entry['timecode']}]"
                lines.append(f"{tag} {entry['text']}")
            write_text_file(bundle_path, "\n".join(lines))
            print(f"Wrote: {bundle_path}")

    if monologue_output == "actor" and actor_bundles:
        for actor_key, entries in actor_bundles.items():
            bundle_path = os.path.join(
                output_dir,
                f"chapter_{chapter_num:03d}_monologue_{actor_key}.txt",
            )
            if skip_existing and os.path.exists(bundle_path):
                print(f"Skip existing: {bundle_path}")
                continue
            lines = []
            for entry in entries:
                tag = f"[{entry['scene']}]"
                if entry.get("timecode"):
                    tag += f"[{entry['timecode']}]"
                lines.append(f"{tag} {entry['text']}")
            write_text_file(bundle_path, "\n".join(lines))
            print(f"Wrote: {bundle_path}")

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse audio-related blocks from screenplay.")
    parser.add_argument("chapter", type=int, help="Chapter number (e.g. 74)")
    parser.add_argument("--base-path", default=DEFAULT_BASE_PATH)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--voice-profiles", default=DEFAULT_VOICE_PROFILES)
    parser.add_argument("--default-actor", default=DEFAULT_ACTOR_KEY)
    parser.add_argument(
        "--monologue-source",
        choices=["plan", "hybrid", "gemini"],
        default="plan",
        help="Monologue source: plan (MONOLOGUE_JSON only), hybrid (plan then gemini), or gemini",
    )
    parser.add_argument(
        "--monologue-output",
        choices=["scene", "chapter", "actor", "both"],
        default="chapter",
        help="Output mode for monologues (scene files, chapter bundle, actor bundle, or both).",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("GEMINI_MODEL", ""),
        help="Gemini model name (e.g. gemini-3-pro-preview).",
    )
    parser.add_argument("--tts", action="store_true")
    parser.add_argument("--tts-endpoint", default=DEFAULT_TTS_ENDPOINT)
    parser.add_argument("--tts-timeout-sec", type=int, default=DEFAULT_TTS_TIMEOUT_SEC)
    parser.add_argument("--tts-poll-interval", type=float, default=DEFAULT_TTS_POLL_INTERVAL)
    parser.add_argument("--tts-output-dir", default=None)
    parser.add_argument("--tts-wsl-root", default=DEFAULT_TTS_WSL_ROOT)
    parser.add_argument("--tts-wsl-project-root", default=DEFAULT_TTS_PROJECT_ROOT)
    parser.add_argument("--speaker-registry", default=DEFAULT_TTS_SPEAKER_REGISTRY)
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--no-monologue", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    ok = run(
        chapter_num=args.chapter,
        base_path=args.base_path,
        output_dir=args.output_dir,
        voice_profiles_path=args.voice_profiles,
        default_actor=args.default_actor,
        monologue_source=args.monologue_source,
        monologue_output=args.monologue_output,
        gemini_model=args.model,
        tts_enabled=args.tts,
        tts_endpoint=args.tts_endpoint,
        tts_timeout_sec=args.tts_timeout_sec,
        tts_poll_interval=args.tts_poll_interval,
        tts_output_dir=args.tts_output_dir,
        tts_wsl_root=args.tts_wsl_root,
        tts_project_root=args.tts_wsl_project_root,
        speaker_registry_path=args.speaker_registry,
        dry_run=args.dry_run,
        skip_existing=args.skip_existing,
        no_monologue=args.no_monologue,
    )
    if not ok:
        sys.exit(1)
