import argparse
import glob
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

from vertex_gemini import call_vertex_gemini
from visionexe_paths import ensure_dir, load_engine_config, load_story_config, resolve_path

MODEL_NAME = "gpt-oss:20b"
OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"

SCENE_HEADER_RE = re.compile(r"\[SCENE\s+([0-9.]+)\]", re.IGNORECASE)
ACT_HEADER_RE = re.compile(r"\[ACT\s+([0-9A-Za-z.]+)\]", re.IGNORECASE)

DEFAULT_MAX_REGIE = 5
DEFAULT_MAX_ANALYSIS_SNIPPETS = 6
DEFAULT_MAX_OCCURRENCES = 12
DEFAULT_MAX_BRIEFING_CHARS = 4000
DEFAULT_GEMINI_CACHE_TTL = 21600
DEFAULT_LLM_TEMPERATURE = 0.35

JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*([\[{].*?[\]}])\s*```", re.DOTALL | re.IGNORECASE)
SAFE_FOLDER_RE = re.compile(r"[^A-Za-z0-9_.-]+")
TIMELINE_TAG_RE = re.compile(r"[^0-9]")
CACHE_VERSION = 1
PROP_ROLE_ACTOR_PREFIXES = ("actor_prop:", "character_prop:")
PROP_ROLE_SCENE_PREFIXES = ("scene_prop", "set_prop", "environment_prop")


def normalize_key(value: str) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip().lower()


def safe_folder_name(value: str) -> str:
    if not value:
        return "unknown"
    return SAFE_FOLDER_RE.sub("_", str(value)).strip("_")


def normalize_timeline_tag(value: str, padding: int) -> str:
    if not value:
        return f"{1:0{padding}d}"
    raw = str(value).strip().lower()
    if raw.startswith("r") and raw[1:].isdigit():
        return f"{int(raw[1:]):0{padding}d}"
    if raw.isdigit():
        return f"{int(raw):0{padding}d}"
    digits = TIMELINE_TAG_RE.sub("", raw)
    if digits:
        return f"{int(digits):0{padding}d}"
    return f"{1:0{padding}d}"


def resolve_llm_profiles(repo_root: Path) -> tuple[dict, str]:
    engine_config = load_engine_config()
    profiles_path = resolve_path(engine_config.get("llm_profiles_path"), repo_root)
    if not profiles_path or not Path(profiles_path).exists():
        return {}, engine_config.get("default_llm_profile") or ""
    try:
        profiles = json.loads(Path(profiles_path).read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        profiles = {}
    return profiles, engine_config.get("default_llm_profile") or ""


def load_jsonl(path: Path):
    items = []
    if not path.exists():
        return items
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            items.append(json.loads(line))
    return items


def load_briefings(story_config, repo_root, max_chars):
    briefings = story_config.get("briefings") or []
    if not briefings:
        return ""
    blocks = []
    remaining = max_chars
    for briefing in briefings:
        path = resolve_path(briefing, repo_root)
        if not path:
            continue
        try:
            text = Path(path).read_text(encoding="utf-8", errors="replace").strip()
        except OSError:
            continue
        if not text or remaining <= 0:
            continue
        if len(text) > remaining:
            text = text[:remaining]
        blocks.append(f"[{Path(path).name}]\n{text}")
        remaining -= len(text)
        if remaining <= 0:
            break
    return "\n\n".join(blocks)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace").strip()
    except OSError:
        return ""


def load_profile_value(value, repo_root: Path, story_root: Path) -> str:
    if not value:
        return ""
    if isinstance(value, list):
        chunks = [load_profile_value(item, repo_root, story_root) for item in value]
        return "\n\n".join([chunk for chunk in chunks if chunk]).strip()
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, indent=2)
    raw = str(value).strip()
    if not raw:
        return ""
    candidate = Path(raw)
    if not candidate.is_absolute():
        repo_candidate = repo_root / candidate
        story_candidate = story_root / candidate
        if repo_candidate.exists():
            candidate = repo_candidate
        elif story_candidate.exists():
            candidate = story_candidate
    if candidate.exists():
        return read_text(candidate)
    return raw


def load_timeline_profile(story_config, story_root: Path, repo_root: Path, timeline_id: str) -> str:
    if not timeline_id:
        return ""
    profile_map = story_config.get("timeline_profiles") or {}
    profile_path = profile_map.get(timeline_id)
    resolved = resolve_path(profile_path, repo_root) if profile_path else None
    if not resolved:
        resolved = story_root / "config" / "timelines" / f"{timeline_id}.json"
    if not resolved or not Path(resolved).exists():
        return ""
    return load_profile_value(str(resolved), repo_root, story_root)


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
        return blocks


def normalize_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    return [str(value).strip()] if str(value).strip() else []


def normalize_types(value):
    if not value:
        return []
    if isinstance(value, list):
        raw = value
    else:
        raw = str(value).replace(";", ",").replace("|", ",").split(",")
    cleaned = []
    for item in raw:
        token = str(item).strip().lower()
        if not token:
            continue
        if token in {"requisite", "requisites", "requisiten"}:
            token = "requisite"
        if token in {"scene_prop", "scene-prop", "set_prop", "set-prop"}:
            token = "requisite"
        cleaned.append(token)
    return cleaned


def infer_gemini_mode(model: str | None, force: bool) -> tuple[bool, str | None]:
    if force:
        return True, model
    if model and "gemini" in str(model).lower():
        return True, model
    return False, None


def resolve_gemini_api_key() -> str | None:
    for key in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "GENAI_API_KEY"):
        value = os.environ.get(key)
        if value:
            return value.strip()
    return None


def gemini_api_allowed(flag: bool) -> bool:
    if flag:
        return True
    env_flag = os.environ.get("ALLOW_GEMINI_API") or os.environ.get("GEMINI_ALLOW_API")
    return str(env_flag).strip() == "1"


def resolve_gemini_api_model(model: str | None, override: str | None = None) -> str | None:
    candidate = override or os.environ.get("GEMINI_API_MODEL") or os.environ.get("GENAI_API_MODEL")
    if candidate:
        normalized = normalize_gemini_model(candidate)
        if not normalized:
            return None
        lowered = normalized.lower()
        if lowered in {"pro", "flash", "flash-lite"}:
            return None
        if lowered.startswith("models/"):
            return normalized[len("models/") :]
        return normalized
    normalized = normalize_gemini_model(model)
    if not normalized:
        return None
    lowered = normalized.lower()
    if lowered in {"pro", "flash", "flash-lite"}:
        return None
    if lowered.startswith("models/"):
        return normalized[len("models/") :]
    return normalized


def hash_cache_key(model: str, static_prompt: str) -> str:
    payload = f"{CACHE_VERSION}:{model}\n{static_prompt}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def resolve_ollama_thinking(model_name: str) -> str | None:
    env_value = os.environ.get("OLLAMA_THINKING")
    if env_value:
        return env_value.strip()
    normalized = str(model_name or "").lower().replace("_", "-")
    if "gpt-oss:20b" in normalized or "gptoss" in normalized:
        return "high"
    return None


def call_ollama(prompt, model_name, ollama_url):
    thinking = resolve_ollama_thinking(model_name)
    data = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.35,
            "num_ctx": 16384,
        },
    }
    if thinking:
        data["options"]["thinking"] = thinking
    try:
        req = urllib.request.Request(
            ollama_url,
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as response:
            resp_json = json.loads(response.read().decode("utf-8"))
            return resp_json.get("response", "")
    except Exception as exc:
        print(f"[asset_bible] Ollama request failed: {exc}")
        return None


def call_openai_compat(prompt: str, profile: dict, temperature: float) -> str | None:
    base_url = (profile.get("base_url") or "").rstrip("/")
    if not base_url:
        print("[asset_bible] OpenAI-compat base_url fehlt im LLM-Profil.")
        return None
    if base_url.endswith("/v1"):
        endpoint = f"{base_url}/chat/completions"
    else:
        endpoint = f"{base_url}/v1/chat/completions"
    payload = {
        "model": profile.get("model") or "",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
    }
    extra_body = profile.get("extra_body") or profile.get("request") or {}
    if not isinstance(extra_body, dict):
        extra_body = {}
    thinking = profile.get("thinking")
    if thinking and "thinking" not in extra_body:
        extra_body["thinking"] = thinking
    reasoning = profile.get("reasoning")
    if reasoning and "reasoning" not in extra_body:
        extra_body["reasoning"] = reasoning
    if extra_body:
        payload.update(extra_body)
    headers = {"Content-Type": "application/json"}
    api_key = profile.get("api_key") or ""
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(endpoint, data=json.dumps(payload).encode("utf-8"), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read().decode("utf-8", errors="replace")
        except Exception:
            body = str(exc)
        print(f"[asset_bible] OpenAI-compat error: {body}")
        return None
    except Exception as exc:
        print(f"[asset_bible] OpenAI-compat request failed: {exc}")
        return None
    if isinstance(data, dict):
        choices = data.get("choices") or []
        if choices:
            message = choices[0].get("message") or {}
            content = message.get("content")
            if isinstance(content, str):
                return content.strip()
            text = choices[0].get("text")
            if isinstance(text, str):
                return text.strip()
    print("[asset_bible] OpenAI-compat Antwort ohne Inhalt.")
    return None


def resolve_gemini_command():
    gemini_path = shutil.which("gemini") or shutil.which("gemini.cmd")
    if gemini_path:
        return [gemini_path]

    npx_path = shutil.which("npx") or shutil.which("npx.cmd")
    if npx_path:
        return [npx_path, "-y", "@google/gemini-cli"]

    return None


def resolve_copilot_command():
    override = os.environ.get("COPILOT_CMD") or os.environ.get("LLM_CMD")
    if override:
        cmd = shlex.split(override)
        if is_copilot_cmd(cmd):
            return cmd
        print("[asset_bible] LLM_CMD/COPILOT_CMD ist kein Copilot-Aufruf, ignoriere Override.")

    copilot_path = shutil.which("copilot") or shutil.which("copilot.cmd")
    if copilot_path:
        return [copilot_path]

    home_dir = os.path.expanduser("~")
    npm_loader_glob = os.path.join(home_dir, ".copilot", "pkg", "universal", "*", "npm-loader.js")
    npm_loaders = glob.glob(npm_loader_glob)
    if npm_loaders:
        return ["node", npm_loaders[0], "copilot"]

    return None


def is_copilot_cmd(cmd):
    if not cmd:
        return False
    lowered = [os.path.basename(part).lower() for part in cmd]
    if "copilot" in lowered or "copilot.cmd" in lowered:
        return True
    return any(part.lower().endswith("npm-loader.js") for part in cmd)


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


def normalize_copilot_model(model: str | None):
    if not model:
        return None
    lowered = str(model).strip().replace("_", "-").lower()
    if not lowered:
        return None
    if lowered.startswith("gemini-2."):
        return None
    if lowered.startswith("gemini-3-") and lowered not in {"gemini-3-pro", "gemini-3-pro-preview"}:
        return None
    if lowered in {"gemini-3-pro", "gemini-3-pro-preview"}:
        return "gemini-3-pro-preview"
    return model


def resolve_gemini_cli_project(explicit: str | None = None, disable: bool = False) -> str | None:
    env_disable = os.environ.get("VISIONEXE_GEMINI_PROJECT_DISABLE") or os.environ.get("VISIONEXE_GCP_PROJECT_DISABLE")
    if disable or str(env_disable).strip() == "1":
        return None
    if explicit:
        return explicit.strip()
    for key in ("GOOGLE_CLOUD_PROJECT", "GOOGLE_CLOUD_PROJECT_ID"):
        value = os.environ.get(key)
        if value:
            return value.strip()
    try:
        result = subprocess.run(
            ["gcloud", "config", "get-value", "project"],
            capture_output=True,
            text=True,
            check=True,
        )
        project = result.stdout.strip()
        if project and project != "(unset)":
            return project
    except Exception:
        return None
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


def call_gemini(prompt, model=None, project: str | None = None, clear_project: bool = False):
    cmd = resolve_gemini_command()
    if not cmd:
        print("[asset_bible] Gemini CLI nicht gefunden (gemini/npx).")
        return None
    cmd = cmd + ["--output-format", "json"]
    normalized_model = normalize_gemini_model(model)
    if model and normalized_model is None:
        print("[asset_bible] Gemini Modell 'auto' -> CLI Default (kein --model).")
    elif model and normalized_model and normalized_model != model:
        print(f"[asset_bible] Gemini Modell '{model}' nicht kompatibel, nutze '{normalized_model}'.")
    if normalized_model:
        cmd += ["--model", normalized_model]
    env = None
    if project or clear_project:
        env = os.environ.copy()
        if project:
            env.setdefault("GOOGLE_CLOUD_PROJECT", project)
            env.setdefault("GOOGLE_CLOUD_PROJECT_ID", project)
        if clear_project:
            env.pop("GOOGLE_CLOUD_PROJECT", None)
            env.pop("GOOGLE_CLOUD_PROJECT_ID", None)
    try:
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            env=env,
        )
        stdout, stderr = process.communicate(input=prompt)
        if process.returncode != 0:
            print(f"[asset_bible] Gemini Fehler: {stderr}")
            return None
        return parse_gemini_response(stdout)
    except OSError as exc:
        print(f"[asset_bible] Gemini Start fehlgeschlagen: {exc}")
        return None


def gemini_api_request(url: str, payload: dict) -> dict | None:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read().decode("utf-8", errors="replace")
        except Exception:
            body = str(exc)
        print(f"[asset_bible] Gemini API error: {body}")
        return None
    except Exception as exc:
        print(f"[asset_bible] Gemini API request failed: {exc}")
        return None


def create_gemini_cache(static_prompt: str, model: str, api_key: str, ttl_seconds: int) -> str | None:
    url = f"https://generativelanguage.googleapis.com/v1beta/cachedContents?key={api_key}"
    payload = {
        "model": f"models/{model}",
        "displayName": "visionexe-asset-bible",
        "contents": [
            {
                "role": "user",
                "parts": [{"text": static_prompt}],
            }
        ],
        "ttl": f"{ttl_seconds}s",
    }
    response = gemini_api_request(url, payload)
    if not response:
        return None
    name = response.get("name")
    if not name:
        print("[asset_bible] Gemini cache did not return a name.")
        return None
    return name


def call_gemini_api(prompt: str, model: str, api_key: str, cached_content: str | None) -> str | None:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        ],
        "generationConfig": {
            "temperature": 0.35,
        },
    }
    if cached_content:
        payload["cachedContent"] = cached_content
    response = gemini_api_request(url, payload)
    if not response:
        return None
    candidates = response.get("candidates") or []
    if not candidates:
        return None
    content = candidates[0].get("content") or {}
    parts = content.get("parts") or []
    texts = [part.get("text") for part in parts if isinstance(part, dict) and part.get("text")]
    return "".join(texts).strip() if texts else None


def load_cache_state(path: Path) -> dict:
    if not path.exists():
        return {"version": CACHE_VERSION, "entries": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"version": CACHE_VERSION, "entries": {}}
    if data.get("version") != CACHE_VERSION:
        return {"version": CACHE_VERSION, "entries": {}}
    if "entries" not in data:
        data["entries"] = {}
    return data


def save_cache_state(path: Path, state: dict) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def get_cached_content(
    static_prompt: str,
    model: str,
    api_key: str,
    cache_path: Path,
    ttl_seconds: int,
    reset: bool,
) -> str | None:
    cache_state = load_cache_state(cache_path)
    cache_key = hash_cache_key(model, static_prompt)
    if not reset:
        entry = cache_state.get("entries", {}).get(cache_key)
        if entry:
            created_at = entry.get("created_at") or 0
            ttl = entry.get("ttl_seconds") or 0
            if ttl and (time.time() - created_at) < ttl:
                return entry.get("name")
    cached_name = create_gemini_cache(static_prompt, model, api_key, ttl_seconds)
    if not cached_name:
        return None
    cache_state["entries"][cache_key] = {
        "name": cached_name,
        "model": model,
        "created_at": time.time(),
        "ttl_seconds": ttl_seconds,
    }
    save_cache_state(cache_path, cache_state)
    return cached_name


def call_copilot(prompt: str, model: str | None):
    cmd = resolve_copilot_command()
    if not cmd:
        print("[asset_bible] Copilot CLI nicht gefunden. Setze COPILOT_CMD oder installiere copilot in PATH.")
        return None
    normalized_model = normalize_copilot_model(model)
    if normalized_model and "--model" not in cmd and "-m" not in cmd:
        cmd = cmd + ["--model", normalized_model]
    uses_copilot = is_copilot_cmd(cmd)
    if uses_copilot:
        if "--silent" not in cmd and "-s" not in cmd:
            cmd = cmd + ["--silent"]
        if "--no-color" not in cmd and "--color" not in cmd:
            cmd = cmd + ["--no-color"]
        if "--no-custom-instructions" not in cmd:
            cmd = cmd + ["--no-custom-instructions"]
        if "--prompt" not in cmd:
            cmd = cmd + ["--prompt", prompt]
    try:
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
        if uses_copilot:
            stdout, stderr = process.communicate()
        else:
            stdout, stderr = process.communicate(input=prompt)
        if process.returncode != 0:
            print(f"[asset_bible] Copilot Fehler: {stderr}")
            return None
        return parse_gemini_response(stdout)
    except OSError as exc:
        print(f"[asset_bible] Copilot Start fehlgeschlagen: {exc}")
        return None


def parse_llm_json(text):
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        blocks = extract_json_blocks(text)
        if blocks:
            return blocks[0]
    return None

def parse_regie_entries(drehbuch_path: Path):
    entries = []
    if not drehbuch_path.exists():
        return entries
    try:
        text = drehbuch_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return entries

    current_scene = None
    current_act = None
    last_entry = None
    expect_prompt = False

    for line in text.splitlines():
        line_stripped = line.strip()
        if not line_stripped:
            continue
        act_match = ACT_HEADER_RE.search(line_stripped)
        if act_match:
            current_act = act_match.group(1)
        scene_match = SCENE_HEADER_RE.search(line_stripped)
        if scene_match:
            current_scene = scene_match.group(1)
        if line_stripped.lower().startswith("### 1. start image prompt"):
            expect_prompt = True
            continue
        if expect_prompt and last_entry is not None:
            last_entry["start_image_prompt"] = line_stripped
            expect_prompt = False
            continue
        if "REGIE_JSON:" in line_stripped:
            raw = line_stripped.split("REGIE_JSON:", 1)[-1].strip()
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                continue
            entry = {
                "chapter": None,
                "act": current_act,
                "scene": current_scene,
                "regie": payload,
                "start_image_prompt": "",
            }
            entries.append(entry)
            last_entry = entry
    return entries


def regie_entry_text(entry):
    regie = entry.get("regie") or {}
    parts = []
    env = regie.get("environment")
    if env:
        parts.append(env)
    for actor in regie.get("actors") or []:
        if isinstance(actor, dict):
            parts.append(actor.get("name", ""))
        else:
            parts.append(str(actor))
    for prop in regie.get("props") or []:
        parts.append(str(prop))
    keywords = regie.get("start_image_keywords") or []
    if isinstance(keywords, list):
        parts.extend([str(k) for k in keywords])
    elif keywords:
        parts.append(str(keywords))
    prompt = entry.get("start_image_prompt")
    if prompt:
        parts.append(prompt)
    return normalize_key(" ".join(parts))


def build_alias_map(profiles):
    alias_map = {}
    for profile in profiles:
        for alias in [profile.get("name")] + (profile.get("aliases") or []):
            if not alias:
                continue
            key = normalize_key(alias)
            if not key:
                continue
            alias_map.setdefault(key, []).append(profile["id"])
    return alias_map


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


def match_subject_id(name, alias_map, profiles_by_id, preferred_type=None):
    key = normalize_key(name)
    if not key:
        return None
    candidates = alias_map.get(key) or []
    if not candidates:
        return None
    if preferred_type:
        for subject_id in candidates:
            profile = profiles_by_id.get(subject_id)
            if profile and profile.get("type") == preferred_type:
                return subject_id
    return candidates[0]


def build_regie_index(entries, alias_map, profiles_by_id):
    regie_index = {}
    for entry in entries:
        regie = entry.get("regie") or {}
        actor_names = []
        for actor in regie.get("actors") or []:
            if isinstance(actor, dict):
                actor_names.append(actor.get("name"))
            else:
                actor_names.append(actor)
        for actor_name in actor_names:
            subject_id = match_subject_id(actor_name, alias_map, profiles_by_id, "character")
            if subject_id:
                regie_index.setdefault(subject_id, []).append(entry)
        for prop in regie.get("props") or []:
            subject_id = match_subject_id(prop, alias_map, profiles_by_id, "prop")
            if not subject_id:
                subject_id = match_subject_id(prop, alias_map, profiles_by_id, "requisite")
            if subject_id:
                regie_index.setdefault(subject_id, []).append(entry)
        environment = regie.get("environment")
        if environment:
            subject_id = match_subject_id(environment, alias_map, profiles_by_id, "set_environment")
            if not subject_id:
                subject_id = match_subject_id(environment, alias_map, profiles_by_id, "geo_environment")
            if subject_id:
                regie_index.setdefault(subject_id, []).append(entry)
    return regie_index


def collect_analysis_context(analysis_records, alias_map, profiles_by_id):
    context = {}
    for record in analysis_records:
        chapter = record.get("chapter")
        segment_label = record.get("segment_label")
        blocks = record.get("analysis_blocks") or []
        for block in blocks:
            if isinstance(block, list):
                block_items = block
            else:
                block_items = [block]
            for block_item in block_items:
                if not isinstance(block_item, dict):
                    continue
                for category, subject_type in (
                    ("actors", "character"),
                    ("props", "prop"),
                    ("environments", "set_environment"),
                    ("scenes", "scene"),
                ):
                    for item in block_item.get(category) or []:
                        name = item.get("name") if isinstance(item, dict) else item
                        resolved_type = subject_type
                        if category == "props":
                            resolved_type = classify_prop_type(item)
                        subject_id = match_subject_id(name, alias_map, profiles_by_id, resolved_type)
                        if not subject_id and category == "props" and resolved_type != "prop":
                            subject_id = match_subject_id(name, alias_map, profiles_by_id, "prop")
                        if not subject_id:
                            continue
                        entry = context.setdefault(subject_id, {
                            "roles": set(),
                            "traits": set(),
                            "changes": set(),
                            "snippets": [],
                        })
                        for role in normalize_list(item.get("role") if isinstance(item, dict) else None):
                            entry["roles"].add(role)
                        for trait in normalize_list(item.get("visualTraits") if isinstance(item, dict) else None):
                            entry["traits"].add(trait)
                        for change in normalize_list(item.get("changes") if isinstance(item, dict) else None):
                            entry["changes"].add(change)
                        snippet = f"ch{chapter} {segment_label}: role={item.get('role') if isinstance(item, dict) else ''}; traits={item.get('visualTraits') if isinstance(item, dict) else ''}; changes={item.get('changes') if isinstance(item, dict) else ''}"
                        entry["snippets"].append(snippet)
    return context


def render_card(profile, card):
    name = profile.get("name") or "Unknown"
    subject_id = profile.get("id")
    subject_type = (profile.get("type") or "subject").upper()
    lines = []
    lines.append(f"## [{subject_type}] {name} (ID: {subject_id})")
    lines.append(f"**Description:** {card.get('description','').strip()}")
    lines.append("")
    lines.append("### 1. VISUAL ANATOMY / DESIGN")
    visual_anatomy = card.get("visual_anatomy", [])
    if isinstance(visual_anatomy, str):
        lines.append(visual_anatomy)
    else:
        for item in visual_anatomy:
            lines.append(f"{item}")
    lines.append("")
    lines.append("### 2. EVOLUTION / VARIANTS")
    evolution = card.get("evolution", [])
    if isinstance(evolution, str):
        lines.append(evolution)
    else:
        for item in evolution:
            lines.append(f"{item}")
    lines.append("")
    lines.append("### 3. PROPS & EQUIPMENT")
    props = card.get("props", [])
    if isinstance(props, str):
        lines.append(props)
    else:
        for item in props:
            lines.append(f"{item}")
    lines.append("")
    keywords = card.get("prompt_keywords", [])
    if keywords:
        lines.append("### 4. AI PROMPT KEYWORDS")
        if isinstance(keywords, str):
            lines.append(keywords)
        else:
            lines.append("`" + "`, `".join(keywords) + "`")
        lines.append("")
    prompt_block = card.get("prompt_block")
    if prompt_block:
        lines.append("### 5. PROMPT BLOCK (T2I)")
        lines.append(prompt_block.strip())
        lines.append("")
    phase_prompts = card.get("phase_prompts") or []
    if phase_prompts:
        lines.append("### 6. PHASE PROMPTS")
        for phase in phase_prompts:
            if not isinstance(phase, dict):
                continue
            label = phase.get("label") or phase.get("state_id") or "Phase"
            summary = phase.get("summary")
            prompt = phase.get("prompt_block")
            keywords = phase.get("prompt_keywords") or []
            if summary:
                lines.append(f"*   **{label}:** {summary}")
            else:
                lines.append(f"*   **{label}:**")
            if prompt:
                lines.append(f"    Prompt: {prompt.strip()}")
            if keywords:
                lines.append(f"    Keywords: {', '.join(keywords)}")
        lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def build_phase_prompt_map(card):
    phase_prompts = card.get("phase_prompts") or []
    mapping = {}
    if isinstance(phase_prompts, dict):
        for key, value in phase_prompts.items():
            if not key:
                continue
            if isinstance(value, dict):
                mapping[normalize_key(key)] = value
            else:
                mapping[normalize_key(key)] = {"prompt_block": str(value)}
        return mapping
    if isinstance(phase_prompts, list):
        for phase in phase_prompts:
            if not isinstance(phase, dict):
                continue
            key = normalize_key(phase.get("state_id") or phase.get("label") or "")
            if key:
                mapping[key] = phase
    return mapping


def render_state_card(profile, state, phase_prompt):
    name = profile.get("name") or "Unknown"
    state_id = state.get("state_id") or "state"
    label = state.get("label") or state_id
    lines = []
    lines.append(f"## [STATE] {name} :: {label}")
    lines.append(f"**State ID:** {state_id}")
    if state.get("chapter_start") is not None:
        lines.append(f"**Chapters:** {state.get('chapter_start')} - {state.get('chapter_end')}")
    if state.get("segment_labels"):
        lines.append(f"**Segments:** {', '.join(state.get('segment_labels'))}")
    if state.get("scene_labels"):
        lines.append(f"**Scenes:** {', '.join(state.get('scene_labels'))}")
    notes = state.get("notes") or []
    if notes:
        lines.append(f"**Notes:** {', '.join(notes)}")
    lines.append("")
    if phase_prompt:
        summary = phase_prompt.get("summary")
        if summary:
            lines.append(f"**Phase Summary:** {summary}")
        keywords = phase_prompt.get("prompt_keywords") or []
        if keywords:
            lines.append(f"**Phase Keywords:** {', '.join(keywords)}")
        prompt = phase_prompt.get("prompt_block")
        if prompt:
            lines.append("**Phase Prompt:**")
            lines.append(prompt.strip())
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def write_subject_bundle(subject_dir_root: Path, profile, card, markdown):
    subject_id = profile.get("id") or "unknown"
    safe_id = safe_folder_name(subject_id)
    subject_dir = subject_dir_root / safe_id
    ensure_dir(subject_dir)
    ensure_dir(subject_dir / "images")
    ensure_dir(subject_dir / "states")

    card_path = subject_dir / "card.md"
    card_json_path = subject_dir / "card.json"

    card_path.write_text(markdown, encoding="utf-8")
    card_payload = {
        "id": subject_id,
        "name": profile.get("name"),
        "type": profile.get("type"),
        "card": card,
        "profile": profile,
    }
    card_json_path.write_text(json.dumps(card_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    phase_map = build_phase_prompt_map(card)
    for idx, state in enumerate(profile.get("states") or []):
        state_id = state.get("state_id") or f"state_{idx+1:02d}"
        state_dir = subject_dir / "states" / safe_folder_name(state_id)
        ensure_dir(state_dir)
        ensure_dir(state_dir / "images")
        state_meta_path = state_dir / "state.json"
        phase_key = normalize_key(state_id) or normalize_key(state.get("label") or "")
        phase_prompt = phase_map.get(phase_key)
        if not phase_prompt:
            label_key = normalize_key(state.get("label") or "")
            if label_key:
                phase_prompt = phase_map.get(label_key)
        state_payload = dict(state)
        if phase_prompt:
            state_payload["phase_prompt"] = phase_prompt
        state_meta_path.write_text(json.dumps(state_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        if phase_prompt:
            prompt_block = phase_prompt.get("prompt_block")
            if prompt_block:
                (state_dir / "prompt.txt").write_text(prompt_block.strip(), encoding="utf-8")
            state_card = render_state_card(profile, state, phase_prompt)
            (state_dir / "card.md").write_text(state_card, encoding="utf-8")
            state_card_payload = {
                "subject_id": subject_id,
                "subject_name": profile.get("name"),
                "state": state,
                "phase_prompt": phase_prompt,
            }
            (state_dir / "card.json").write_text(
                json.dumps(state_card_payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

    return subject_dir, card_path, card_json_path


def build_fallback_card(profile, context):
    name = profile.get("name") or "Unknown"
    roles = sorted(set(profile.get("roles") or []) | context.get("roles", set()))
    traits = sorted(set(profile.get("visual_traits") or []) | context.get("traits", set()))
    changes = sorted(set(profile.get("changes") or []) | context.get("changes", set()))
    description = f"Auto-generated asset card for {name}."
    visual = []
    if traits:
        visual.append(f"Traits: {', '.join(traits)}")
    if roles:
        visual.append(f"Roles: {', '.join(roles)}")
    evolution = []
    phase_prompts = []
    if profile.get("states"):
        for state in profile.get("states"):
            label = state.get("label") or state.get("state_id")
            evolution.append(f"Phase ({label})")
            phase_label = label or "Phase"
            prompt = f"{name}, {', '.join(traits or roles)}"
            if phase_label and str(phase_label).lower() not in ("default", "none", "unknown"):
                prompt = f"{prompt}, {phase_label}"
            phase_prompts.append(
                {
                    "state_id": state.get("state_id") or "",
                    "label": phase_label,
                    "summary": "",
                    "prompt_keywords": traits[:12],
                    "prompt_block": prompt,
                }
            )
    if not evolution and changes:
        evolution.append(f"Changes: {', '.join(changes)}")
    return {
        "description": description,
        "visual_anatomy": visual or ["TBD."],
        "evolution": evolution or ["No known variants yet."],
        "props": ["TBD."],
        "prompt_keywords": traits[:12],
        "prompt_block": f"{name}, {', '.join(traits or roles)}",
        "phase_prompts": phase_prompts,
    }

def ensure_phase_prompts(card, profile):
    if card.get("phase_prompts"):
        return
    states = profile.get("states") or []
    if not states:
        return
    name = profile.get("name") or "Unknown"
    traits = normalize_list(card.get("prompt_keywords")) or normalize_list(profile.get("visual_traits"))
    roles = normalize_list(profile.get("roles"))
    base_prompt = card.get("prompt_block") or f"{name}, {', '.join(traits or roles)}"
    phase_prompts = []
    for state in states:
        label = state.get("label") or state.get("state_id") or "Phase"
        prompt = base_prompt
        if label and str(label).lower() not in ("default", "none", "unknown"):
            prompt = f"{base_prompt}, {label}"
        phase_prompts.append(
            {
                "state_id": state.get("state_id") or "",
                "label": label,
                "summary": "",
                "prompt_keywords": traits[:12],
                "prompt_block": prompt,
            }
        )
    card["phase_prompts"] = phase_prompts

def build_prompt(
    profile,
    context,
    regie_samples,
    occ_samples,
    analysis_snippets,
    briefing_text,
    injection_context,
    dup_candidates=None,
):
    static_prompt = build_prompt_static(briefing_text, injection_context)
    dynamic_prompt = build_prompt_dynamic(
        profile,
        context,
        regie_samples,
        occ_samples,
        analysis_snippets,
        dup_candidates,
    )
    return f"{static_prompt}\n\n{dynamic_prompt}".strip()


def build_prompt_static(briefing_text, injection_context):
    if not briefing_text:
        briefing_text = "(none)"
    prompt = f"""
ROLE: Narrative Asset Bible Author for a high-end cinematic production.
TASK: Create ONE asset card for the subject below using the provided context.

GOAL (HARD):
- Write dense, flowing prose. No short tags, no terse bullet fragments.
- Expand and enrich; do NOT summarize down. If in doubt, add clarifying texture.
- The card must read like a miniature art/production bible entry.

STYLE/GENRE/TIMELINE INJECTION (HARD):
Use the injected profiles to steer tone, worldview, era, and visual language.
Do NOT add new facts; only reframe with consistent style.

INJECTION CONTEXT:
{injection_context}

OUTPUT FORMAT (JSON ONLY):
{{
  "description": "multi-paragraph prose block",
  "visual_anatomy": ["paragraph 1", "paragraph 2", "paragraph 3"],
  "evolution": ["paragraph 1", "paragraph 2"],
  "props": ["paragraph 1", "paragraph 2"],
  "prompt_keywords": ["optional short phrases for prompts"],
  "prompt_block": "multi-sentence, rich prompt block (not markdown)",
  "phase_prompts": [
    {{
      "state_id": "default",
      "label": "Phase name",
      "summary": "2-4 sentences, literary but precise",
      "prompt_keywords": ["optional short phrases"],
      "prompt_block": "multi-sentence prompt block for this phase"
    }}
  ]
}}

RULES:
- Prioritize unique, visual identifiers (materials, wear, scale, light behavior, motion cues).
- Use screenplay/regie when available, but convert it into prose.
- Do NOT output tags or list fragments like "gold, robe, light". Always write full sentences.
- If traits/roles/changes are sparse, infer only within the injected style and the analysis context.
- Provide phase_prompts for every state_id listed below. If a phase has no changes, still emit a rich prompt_block.
- Type rules: prop = subject-bound item (mention owner if provided). requisite = scene dressing (no ownership).

STORY BRIEFING:
{briefing_text}
"""
    return prompt.strip()


def build_prompt_dynamic(profile, context, regie_samples, occ_samples, analysis_snippets, dup_candidates=None):
    name = profile.get("name") or "Unknown"
    subject_type = profile.get("type") or "subject"
    aliases = [a for a in (profile.get("aliases") or []) if a]
    owner_ids = profile.get("owner_subject_ids") or []
    owner_names = profile.get("owner_names") or []
    roles = sorted(set(profile.get("roles") or []) | context.get("roles", set()))
    traits = sorted(set(profile.get("visual_traits") or []) | context.get("traits", set()))
    changes = sorted(set(profile.get("changes") or []) | context.get("changes", set()))
    states = profile.get("states") or []

    regie_lines = []
    for entry in regie_samples:
        regie = entry.get("regie") or {}
        props = regie.get("props") or []
        actors = regie.get("actors") or []
        actor_names = [a.get("name") if isinstance(a, dict) else str(a) for a in actors]
        regie_lines.append(
            f"scene={entry.get('scene')}, env={regie.get('environment')}, props={props}, actors={actor_names}, prompt={entry.get('start_image_prompt')}"
        )

    occ_lines = [
        f"ch{occ.get('chapter')} {occ.get('segment_label')}/{occ.get('scene_label')}"
        for occ in occ_samples
    ]

    analysis_lines = [f"- {snippet}" for snippet in (analysis_snippets or [])]
    if not analysis_lines:
        analysis_lines = ["- (none)"]
    if not regie_lines:
        regie_lines = ["(none)"]
    if not occ_lines:
        occ_lines = ["(none)"]

    dup_lines = []
    for alias, candidates in dup_candidates or []:
        if not candidates:
            continue
        dup_lines.append(f"- {alias}: {', '.join(candidates)}")
    if not dup_lines:
        dup_lines = ["(none)"]

    state_lines = []
    for state in states:
        label = state.get("label") or state.get("state_id") or "Phase"
        chapter_start = state.get("chapter_start")
        chapter_end = state.get("chapter_end")
        notes = ", ".join(state.get("notes") or [])
        state_lines.append(f"- {state.get('state_id')} ({label}) ch{chapter_start}-{chapter_end} {notes}".strip())
    if not state_lines:
        state_lines = ["(none)"]

    analysis_text = "\n".join(analysis_lines)
    regie_text = "\n".join(regie_lines)
    occ_text = "\n".join(occ_lines)
    state_text = "\n".join(state_lines)
    dup_text = "\n".join(dup_lines)

    prompt = f"""
SUBJECT
name: {name}
type: {subject_type}
aliases: {aliases}
owner_subject_ids: {owner_ids}
owner_names: {owner_names}
roles: {roles}
visual_traits: {traits}
changes: {changes}
states: {states}

STATE TARGETS (must cover each):
{state_text}

ANALYSIS NOTES
{analysis_text}

REGIE / SCREENPLAY SNIPPETS
{regie_text}

OCCURRENCES
{occ_text}

DUPLICATE CANDIDATES (ALIAS COLLISIONS)
{dup_text}
"""
    return prompt.strip()


def main():
    parser = argparse.ArgumentParser(description="Enrich asset bible with dense cards for every subject.")
    parser.add_argument("--story-root", help="Story root path (defaults to engine_config default_story_root).")
    parser.add_argument("--story-config", help="Path to story_config.json (overrides story-root).")
    parser.add_argument("--analysis-master", help="analysis_master.jsonl path override.")
    parser.add_argument("--profiles", help="profiles.jsonl path override.")
    parser.add_argument("--occurrences", help="occurrences.jsonl path override.")
    parser.add_argument("--output-md", help="Output ASSET_BIBLE.md path.")
    parser.add_argument("--output-jsonl", help="Output JSONL cards path.")
    parser.add_argument("--subject-dir-root", help="Root folder for per-subject directories.")
    parser.add_argument("--timeline", help="Timeline tag (e.g., 1 or r01) for subject directory root.")
    parser.add_argument("--genre-profile", help="Override genre profile (path or label).")
    parser.add_argument(
        "--style-profile",
        action="append",
        help="Override style profile (path). Repeat to provide multiple.",
    )
    parser.add_argument("--tone-dials", help="Override tone dials (JSON, path, or label).")
    parser.add_argument(
        "--types",
        default="character,prop,requisite,set_environment,scene",
        help="Comma-separated subject types to include (default: character,prop,requisite,set_environment,scene).",
    )
    parser.add_argument("--max-regie", type=int, default=DEFAULT_MAX_REGIE, help="Max regie samples per subject.")
    parser.add_argument("--max-analysis", type=int, default=DEFAULT_MAX_ANALYSIS_SNIPPETS, help="Max analysis snippets per subject.")
    parser.add_argument("--max-occurrences", type=int, default=DEFAULT_MAX_OCCURRENCES, help="Max occurrence refs per subject.")
    parser.add_argument("--briefing-max-chars", type=int, default=DEFAULT_MAX_BRIEFING_CHARS, help="Max characters to include from story briefings.")
    parser.add_argument("--include-regie", action="store_true", help="Include DREHBUCH_HOLLYWOOD regie snippets (default: off).")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of subjects (0 = all).")
    parser.add_argument("--resume", action="store_true", help="Skip subjects already in output JSONL.")
    parser.add_argument("--use-vertex", action="store_true", help="Use Vertex AI Gemini via ADC.")
    parser.add_argument("--vertex-project", help="Override Vertex project ID.")
    parser.add_argument("--vertex-location", help="Override Vertex location (default: us-central1).")
    parser.add_argument("--vertex-model", help="Override Vertex model name (e.g. gemini-2.5-pro).")
    parser.add_argument("--use-lmstudio", action="store_true", help="Use LM Studio via OpenAI-compatible API.")
    parser.add_argument("--llm-profile", default="", help="LLM profile name (engine/config/llm_profiles.json).")
    parser.add_argument("--llm-temperature", type=float, default=DEFAULT_LLM_TEMPERATURE, help="Temperature for OpenAI-compatible calls.")
    parser.add_argument("--use-gemini", action="store_true", help="Use Gemini CLI instead of Ollama.")
    parser.add_argument("--model", help="Override model name (Gemini model or Ollama model).")
    parser.add_argument("--ollama-url", help="Override Ollama URL.")
    parser.add_argument("--gemini-cache", action="store_true", help="Use Gemini API cached content (requires API key).")
    parser.add_argument("--gemini-cache-ttl", type=int, default=DEFAULT_GEMINI_CACHE_TTL, help="Gemini cache TTL in seconds.")
    parser.add_argument("--gemini-cache-path", help="Path to Gemini cache metadata JSON.")
    parser.add_argument("--gemini-cache-reset", action="store_true", help="Ignore existing Gemini cache metadata.")
    parser.add_argument("--gemini-api-model", help="Explicit Gemini API model for cache (e.g. gemini-2.5-pro).")
    parser.add_argument("--allow-gemini-api", action="store_true", help="Allow paid Gemini API calls for cache.")
    parser.add_argument("--gemini-project", help="Gemini CLI project (sets GOOGLE_CLOUD_PROJECT).")
    parser.add_argument("--no-gemini-project", action="store_true", help="Do not pass GOOGLE_CLOUD_PROJECT to Gemini CLI.")
    args = parser.parse_args()

    story_config, story_root, repo_root = load_story_config(
        story_root=args.story_root,
        story_config_path=args.story_config,
    )

    subjects_root = resolve_path(story_config.get("subjects_root"), repo_root)
    filmsets_root = resolve_path(story_config.get("filmsets_root"), repo_root)
    analysis_master_path = resolve_path(
        args.analysis_master or story_config.get("analysis_master_path"), repo_root
    )
    profiles_path = resolve_path(args.profiles or f"{subjects_root}/profiles.jsonl", repo_root)
    occurrences_path = resolve_path(args.occurrences or f"{subjects_root}/occurrences.jsonl", repo_root)
    output_md = resolve_path(args.output_md or f"{subjects_root}/ASSET_BIBLE.md", repo_root)
    output_jsonl = resolve_path(args.output_jsonl or f"{subjects_root}/asset_bible_cards.jsonl", repo_root)
    timeline_label = story_config.get("timeline_label", "timeline")
    timeline_padding = int(story_config.get("timeline_index_padding", 2))
    timeline_tag = normalize_timeline_tag(
        args.timeline or story_config.get("timeline_default") or "1",
        timeline_padding,
    )
    timeline_folder = f"{timeline_label}_{timeline_tag}"
    subject_dir_root_config = args.subject_dir_root or story_config.get("subject_dir_root")
    if subject_dir_root_config:
        subject_dir_root_config = (
            str(subject_dir_root_config)
            .replace("{timeline_label}", timeline_label)
            .replace("{timeline_tag}", timeline_tag)
            .replace("{timeline_folder}", timeline_folder)
        )
        subject_dir_root = resolve_path(subject_dir_root_config, repo_root)
    else:
        subject_dir_root = Path(subjects_root) / "timelines" / timeline_folder

    timeline_id = f"{timeline_label}_{timeline_tag}"
    timeline_profile_text = load_timeline_profile(story_config, story_root, repo_root, timeline_id)

    genre_profile_value = args.genre_profile or story_config.get("genre_profile")
    genre_profile_text = load_profile_value(genre_profile_value, repo_root, story_root)

    style_profile_values = args.style_profile or story_config.get("style_profiles") or []
    style_profile_text = load_profile_value(style_profile_values, repo_root, story_root)

    tone_dials_value = args.tone_dials or story_config.get("tone_dials")
    tone_dials_text = load_profile_value(tone_dials_value, repo_root, story_root)

    injection_parts = []
    injection_parts.append("[TIMELINE_PROFILE]\n" + (timeline_profile_text or "(none)"))
    injection_parts.append("[GENRE_PROFILE]\n" + (genre_profile_text or "(none)"))
    injection_parts.append("[STYLE_PROFILES]\n" + (style_profile_text or "(none)"))
    injection_parts.append("[TONE_DIALS]\n" + (tone_dials_text or "(none)"))
    injection_context = "\n\n".join(injection_parts)

    include_types = set(normalize_types(args.types))

    use_vertex = bool(args.use_vertex)
    use_lmstudio = bool(args.use_lmstudio or args.llm_profile)
    use_gemini, gemini_model = infer_gemini_mode(args.model, args.use_gemini)
    if use_vertex and use_lmstudio:
        print("[asset_bible] Hinweis: --use-vertex deaktiviert LM Studio.")
        use_lmstudio = False
    if use_vertex and use_gemini:
        print("[asset_bible] Hinweis: --use-vertex deaktiviert Gemini CLI.")
        use_gemini = False
        gemini_model = None
    if use_lmstudio and use_gemini:
        print("[asset_bible] Hinweis: --use-lmstudio deaktiviert Gemini CLI.")
        use_gemini = False
        gemini_model = None

    llm_profiles = {}
    default_llm_profile = ""
    llm_profile = None
    if use_lmstudio:
        llm_profiles, default_llm_profile = resolve_llm_profiles(repo_root)
        llm_profile_name = args.llm_profile or (
            "lmstudio_local" if "lmstudio_local" in llm_profiles else default_llm_profile
        )
        if not llm_profile_name:
            raise SystemExit("LM Studio erfordert ein LLM-Profil (engine/config/llm_profiles.json).")
        llm_profile = llm_profiles.get(llm_profile_name)
        if not llm_profile:
            raise SystemExit(f"LLM profile not found: {llm_profile_name}")
        profile_type = str(llm_profile.get("type") or "").lower()
        if profile_type not in {"openai_compat", "openai-compatible", "openai"}:
            raise SystemExit(f"LLM profile '{llm_profile_name}' is not openai_compat.")
        if args.model:
            llm_profile = dict(llm_profile, model=args.model)

    ollama_model = args.model or MODEL_NAME
    gemini_cache_enabled = bool(args.gemini_cache or os.environ.get("GEMINI_CACHE") == "1")
    gemini_cache_path = resolve_path(
        args.gemini_cache_path or f"{subjects_root}/gemini_cache.json",
        repo_root,
    )
    allow_gemini_api = gemini_api_allowed(args.allow_gemini_api)
    gemini_api_key = resolve_gemini_api_key()
    gemini_api_model = resolve_gemini_api_model(gemini_model, args.gemini_api_model)
    gemini_project_disabled = bool(
        args.no_gemini_project
        or os.environ.get("VISIONEXE_GEMINI_PROJECT_DISABLE") == "1"
        or os.environ.get("VISIONEXE_GCP_PROJECT_DISABLE") == "1"
    )
    gemini_cli_project = resolve_gemini_cli_project(args.gemini_project, gemini_project_disabled)
    if use_gemini and not gemini_cli_project and not gemini_project_disabled:
        print("[asset_bible] Gemini CLI braucht GOOGLE_CLOUD_PROJECT (setze --gemini-project).")
    if gemini_cache_enabled and not allow_gemini_api:
        print("[asset_bible] Gemini API cache requested without --allow-gemini-api; disabling cache.")
        gemini_cache_enabled = False
    if use_vertex and gemini_cache_enabled:
        print("[asset_bible] Gemini API cache disabled for Vertex backend.")
        gemini_cache_enabled = False
    if gemini_cache_enabled and not gemini_api_key:
        print("[asset_bible] Gemini cache requested but no API key found; disabling cache.")
        gemini_cache_enabled = False
    if gemini_cache_enabled and not gemini_api_model:
        print("[asset_bible] Gemini cache requested but model is not API-compatible; disabling cache.")
        gemini_cache_enabled = False

    vertex_project = args.vertex_project
    vertex_location = args.vertex_location
    vertex_model = args.vertex_model

    if use_vertex:
        print("[asset_bible] Backend: Vertex AI (billing: Vertex/GenAI credits).")
    elif use_lmstudio:
        print("[asset_bible] Backend: LM Studio (OpenAI-compatible).")
    elif use_gemini:
        print("[asset_bible] Backend: Gemini CLI (billing: Cloud AI Companion credits).")

    profiles = load_jsonl(profiles_path)
    occurrences = load_jsonl(occurrences_path)
    analysis_records = load_jsonl(analysis_master_path)

    briefing_text = load_briefings(story_config, repo_root, args.briefing_max_chars)
    static_prompt = build_prompt_static(briefing_text, injection_context)

    profiles_by_id = {p["id"]: p for p in profiles if p.get("id")}
    alias_map = build_alias_map(profiles)

    regie_entries = []
    if args.include_regie and filmsets_root.exists():
        for drehbuch in filmsets_root.rglob("DREHBUCH_HOLLYWOOD.md"):
            regie_entries.extend(parse_regie_entries(drehbuch))
    for entry in regie_entries:
        entry["search_text"] = regie_entry_text(entry)

    regie_index = build_regie_index(regie_entries, alias_map, profiles_by_id)
    analysis_context = collect_analysis_context(analysis_records, alias_map, profiles_by_id)

    gemini_cached_name = None
    if use_gemini and gemini_cache_enabled and gemini_api_key and gemini_api_model:
        gemini_cached_name = get_cached_content(
            static_prompt,
            gemini_api_model,
            gemini_api_key,
            gemini_cache_path,
            args.gemini_cache_ttl,
            args.gemini_cache_reset,
        )
        if gemini_cached_name:
            print(f"[asset_bible] Gemini cache active: {gemini_cached_name}")

    occ_map = {}
    for occ in occurrences:
        subject_id = occ.get("subject_id")
        if subject_id:
            occ_map.setdefault(subject_id, []).append(occ)

    existing = set()
    card_map = {}
    if output_jsonl.exists():
        with output_jsonl.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError:
                    continue
                subject_id = payload.get("id")
                if subject_id and payload.get("markdown"):
                    card_map[subject_id] = payload["markdown"]
                if subject_id:
                    existing.add(subject_id)
    if output_jsonl.exists() and not args.resume:
        output_jsonl.unlink()
        existing.clear()
        card_map.clear()

    output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    ensure_dir(subject_dir_root)

    def has_existing_card(subject_id: str) -> bool:
        safe_id = safe_folder_name(subject_id)
        subject_dir = subject_dir_root / safe_id
        return (subject_dir / "card.json").exists() or (subject_dir / "card.md").exists()

    total_subjects = 0
    for profile in profiles:
        subject_type = str(profile.get("type") or "").strip().lower()
        if include_types and subject_type not in include_types:
            continue
        total_subjects += 1

    resume_from_dir = False
    if args.resume:
        print(f"[asset_bible] Resume aktiv: {len(existing)} Eintraege aus JSONL.")
        if not existing:
            resume_from_dir = True
            print("[asset_bible] Resume fallback: nutze vorhandene Subject-Cards auf Disk.")

    count = 0
    resume_hits = 0
    for profile in profiles:
        subject_id = profile.get("id")
        if not subject_id:
            continue
        subject_type = str(profile.get("type") or "").strip().lower()
        if include_types and subject_type not in include_types:
            continue
        if args.limit and count >= args.limit:
            break
        if args.resume:
            if subject_id in existing:
                resume_hits += 1
                continue
            if resume_from_dir and has_existing_card(subject_id):
                existing.add(subject_id)
                resume_hits += 1
                continue

        context = analysis_context.get(subject_id, {"roles": set(), "traits": set(), "changes": set(), "snippets": []})
        regie_samples = (regie_index.get(subject_id) or [])[: args.max_regie]
        if not regie_samples:
            alias_keys = [normalize_key(profile.get("name") or "")] + [
                normalize_key(a) for a in (profile.get("aliases") or [])
            ]
            alias_keys = [k for k in alias_keys if k]
            for entry in regie_entries:
                if any(alias in entry.get("search_text", "") for alias in alias_keys):
                    regie_samples.append(entry)
                    if len(regie_samples) >= args.max_regie:
                        break
        occ_samples = (occ_map.get(subject_id) or [])[: args.max_occurrences]

        analysis_snippets = (context.get("snippets") or [])[: args.max_analysis]
        dynamic_prompt = build_prompt_dynamic(
            profile,
            context,
            regie_samples,
            occ_samples,
            analysis_snippets,
        )
        prompt = f"{static_prompt}\n\n{dynamic_prompt}"
        response = None
        if use_vertex:
            response = call_vertex_gemini(
                prompt,
                model=vertex_model or None,
                project=vertex_project,
                location=vertex_location,
                temperature=0.25,
                log_fn=print,
            )
            if response is None:
                print("[asset_bible] Vertex fehlgeschlagen, nutze Fallback-Card.")
        elif use_lmstudio:
            response = call_openai_compat(prompt, llm_profile, args.llm_temperature)
            if response is None:
                print("[asset_bible] LM Studio fehlgeschlagen, nutze Fallback-Card.")
        elif use_gemini:
            if gemini_cached_name:
                response = call_gemini_api(dynamic_prompt, gemini_api_model, gemini_api_key, gemini_cached_name)
            if response is None:
                response = call_gemini(prompt, gemini_model, gemini_cli_project, gemini_project_disabled)
            if response is None:
                print("[asset_bible] Gemini fehlgeschlagen, versuche Copilot Fallback.")
                response = call_copilot(prompt, gemini_model or args.model)
        else:
            response = call_ollama(prompt, ollama_model, args.ollama_url or OLLAMA_API_URL)
            if response is None:
                if resolve_gemini_command():
                    print("[asset_bible] Ollama fehlgeschlagen, wechsle zu Gemini-Fallback.")
                    use_gemini = True
                    gemini_model = args.model if args.model and "gemini" in args.model.lower() else None
                    response = call_gemini(prompt, gemini_model, gemini_cli_project, gemini_project_disabled)
                    if response is None:
                        print("[asset_bible] Gemini fehlgeschlagen, versuche Copilot Fallback.")
                        response = call_copilot(prompt, gemini_model or args.model)

        card = parse_llm_json(response) if response else None
        if not isinstance(card, dict):
            card = build_fallback_card(profile, context)
        else:
            ensure_phase_prompts(card, profile)

        markdown = render_card(profile, card)
        card_map[subject_id] = markdown

        subject_dir, card_path, card_json_path = write_subject_bundle(subject_dir_root, profile, card, markdown)
        subject_dir_rel = os.path.relpath(subject_dir, subjects_root)
        card_path_rel = os.path.relpath(card_path, subjects_root)
        card_json_rel = os.path.relpath(card_json_path, subjects_root)

        record = {
            "id": subject_id,
            "name": profile.get("name"),
            "type": profile.get("type"),
            "owner_subject_ids": profile.get("owner_subject_ids") or [],
            "owner_names": profile.get("owner_names") or [],
            "subject_dir": subject_dir_rel,
            "card_path": card_path_rel,
            "card_json": card_json_rel,
            "markdown": markdown,
            "card": card,
        }
        with output_jsonl.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        count += 1
        progress = count + resume_hits
        print(f"[asset_bible] {progress}/{total_subjects or len(profiles)} {subject_id}")

    header = "# EXEGET:OS ASSET BIBLE (AUTO-GENERATED)\n\n"
    with output_md.open("w", encoding="utf-8") as f:
        f.write(header)
        for profile in profiles:
            subject_id = profile.get("id")
            if not subject_id:
                continue
            card = card_map.get(subject_id)
            if not card:
                fallback = build_fallback_card(profile, analysis_context.get(subject_id, {"roles": set(), "traits": set(), "changes": set(), "snippets": []}))
                card = render_card(profile, fallback)
            f.write(card)

    print(f"Wrote enriched asset bible: {output_md}")
    print(f"Wrote card JSONL: {output_jsonl}")


if __name__ == "__main__":
    main()
