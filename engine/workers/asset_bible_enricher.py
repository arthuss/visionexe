import argparse
import glob
import json
import os
import re
import shlex
import shutil
import subprocess
import time
import urllib.request
from pathlib import Path

from visionexe_paths import ensure_dir, load_story_config, resolve_path

MODEL_NAME = "gpt-oss:20b"
OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"

SCENE_HEADER_RE = re.compile(r"\[SCENE\s+([0-9.]+)\]", re.IGNORECASE)
ACT_HEADER_RE = re.compile(r"\[ACT\s+([0-9A-Za-z.]+)\]", re.IGNORECASE)

DEFAULT_MAX_REGIE = 5
DEFAULT_MAX_ANALYSIS_SNIPPETS = 6
DEFAULT_MAX_OCCURRENCES = 12
DEFAULT_MAX_BRIEFING_CHARS = 4000

JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*([\[{].*?[\]}])\s*```", re.DOTALL | re.IGNORECASE)
SAFE_FOLDER_RE = re.compile(r"[^A-Za-z0-9_.-]+")
TIMELINE_TAG_RE = re.compile(r"[^0-9]")


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


def call_ollama(prompt, model_name, ollama_url):
    data = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.35,
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
            return resp_json.get("response", "")
    except Exception as exc:
        print(f"[asset_bible] Ollama request failed: {exc}")
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
    if lowered in {"gemini-3-pro", "gemini-3-pro-preview"}:
        return "gemini-3-pro-preview"
    return model


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


def call_gemini(prompt, model=None):
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
            print(f"[asset_bible] Gemini Fehler: {stderr}")
            return None
        return parse_gemini_response(stdout)
    except OSError as exc:
        print(f"[asset_bible] Gemini Start fehlgeschlagen: {exc}")
        return None


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
            if subject_id:
                regie_index.setdefault(subject_id, []).append(entry)
        environment = regie.get("environment")
        if environment:
            subject_id = match_subject_id(environment, alias_map, profiles_by_id, "environment")
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
                    ("environments", "environment"),
                    ("scenes", "scene"),
                ):
                    for item in block_item.get(category) or []:
                        name = item.get("name") if isinstance(item, dict) else item
                        subject_id = match_subject_id(name, alias_map, profiles_by_id, subject_type)
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
    tags = card.get("tags") or []
    tag_str = " ".join([f"#{tag}" for tag in tags])

    lines = []
    lines.append(f"## [{subject_type}] {name} (ID: {subject_id})")
    lines.append(f"**Description:** {card.get('description','').strip()}")
    if tag_str:
        lines.append(f"**Tags:** {tag_str}")
    lines.append("")
    lines.append("### 1. VISUAL ANATOMY / DESIGN")
    for item in card.get("visual_anatomy", []):
        lines.append(f"*   {item}")
    lines.append("")
    lines.append("### 2. EVOLUTION / VARIANTS")
    for item in card.get("evolution", []):
        lines.append(f"*   {item}")
    lines.append("")
    lines.append("### 3. PROPS & EQUIPMENT")
    for item in card.get("props", []):
        lines.append(f"*   {item}")
    lines.append("")
    keywords = card.get("prompt_keywords", [])
    if keywords:
        lines.append("### 4. AI PROMPT KEYWORDS")
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
        "tags": roles[:6],
        "visual_anatomy": visual or ["TBD"],
        "evolution": evolution or ["No known variants"],
        "props": ["TBD"],
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

def build_prompt(profile, context, regie_samples, occ_samples, analysis_snippets, briefing_text):
    name = profile.get("name") or "Unknown"
    subject_type = profile.get("type") or "subject"
    aliases = [a for a in (profile.get("aliases") or []) if a]
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
    if not briefing_text:
        briefing_text = "(none)"

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

    prompt = f"""
ROLE: Technical Asset Director for a high-end cinematic production.
TASK: Create ONE asset card for the subject below using the provided context.

VISUAL STYLE GUIDE:
- Genre: Ancient-tech, industrial mysticism, grounded realism.
- Tone: Serious, cinematic, photorealistic, tactile.
- Avoid: Generic sci-fi, cartoon, anime, toy/plastic look.
- Fusion: Ancient Ethiopian/Egyptian aesthetics with advanced, incomprehensible technology.

OUTPUT FORMAT (JSON ONLY):
{{
  "description": "...",
  "tags": ["tag1","tag2"],
  "visual_anatomy": ["**Body/Form:** ...", "**Face/Sensors:** ...", "**Clothing/Armor:** ...", "**Key Features:** ..."],
  "evolution": ["Phase 1 (...): ...", "Phase 2 (...): ..."],
  "props": ["Item: ...", "Item: ..."],
  "prompt_keywords": ["keyword1","keyword2"],
  "prompt_block": "single-paragraph T2I prompt, no markdown",
  "phase_prompts": [
    {{
      "state_id": "default",
      "label": "Phase name",
      "summary": "short phase-specific description",
      "prompt_keywords": ["keyword1","keyword2"],
      "prompt_block": "phase-specific T2I prompt, no markdown"
    }}
  ]
}}

RULES:
- Prioritize unique, visual identifiers. No filler.
- If screenplay/regie is available, use it as highest priority.
- If traits/roles/changes are sparse, infer plausible details consistent with style.
- Use Tech-Exegesis language (bio-luminescence, glyphs, crystalline hardware) when it fits the subject.
- Deliver dense, production-ready specificity (materials, wear, scale, light behavior).
- Provide phase_prompts for every state_id listed below. If a phase has no changes, still emit a prompt_block.

STORY BRIEFING:
{briefing_text}

SUBJECT
name: {name}
type: {subject_type}
aliases: {aliases}
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
    parser.add_argument("--max-regie", type=int, default=DEFAULT_MAX_REGIE, help="Max regie samples per subject.")
    parser.add_argument("--max-analysis", type=int, default=DEFAULT_MAX_ANALYSIS_SNIPPETS, help="Max analysis snippets per subject.")
    parser.add_argument("--max-occurrences", type=int, default=DEFAULT_MAX_OCCURRENCES, help="Max occurrence refs per subject.")
    parser.add_argument("--briefing-max-chars", type=int, default=DEFAULT_MAX_BRIEFING_CHARS, help="Max characters to include from story briefings.")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of subjects (0 = all).")
    parser.add_argument("--resume", action="store_true", help="Skip subjects already in output JSONL.")
    parser.add_argument("--use-gemini", action="store_true", help="Use Gemini CLI instead of Ollama.")
    parser.add_argument("--model", help="Override model name (Gemini model or Ollama model).")
    parser.add_argument("--ollama-url", help="Override Ollama URL.")
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

    profiles = load_jsonl(profiles_path)
    occurrences = load_jsonl(occurrences_path)
    analysis_records = load_jsonl(analysis_master_path)

    briefing_text = load_briefings(story_config, repo_root, args.briefing_max_chars)

    profiles_by_id = {p["id"]: p for p in profiles if p.get("id")}
    alias_map = build_alias_map(profiles)

    regie_entries = []
    if filmsets_root.exists():
        for drehbuch in filmsets_root.rglob("DREHBUCH_HOLLYWOOD.md"):
            regie_entries.extend(parse_regie_entries(drehbuch))
    for entry in regie_entries:
        entry["search_text"] = regie_entry_text(entry)

    regie_index = build_regie_index(regie_entries, alias_map, profiles_by_id)
    analysis_context = collect_analysis_context(analysis_records, alias_map, profiles_by_id)

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

    count = 0
    for profile in profiles:
        subject_id = profile.get("id")
        if not subject_id:
            continue
        if args.limit and count >= args.limit:
            break
        if args.resume and subject_id in existing:
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
        prompt = build_prompt(profile, context, regie_samples, occ_samples, analysis_snippets, briefing_text)
        if args.use_gemini:
            response = call_gemini(prompt, args.model)
            if response is None:
                print("[asset_bible] Gemini fehlgeschlagen, versuche Copilot Fallback.")
                response = call_copilot(prompt, args.model)
        else:
            model_name = args.model or MODEL_NAME
            response = call_ollama(prompt, model_name, args.ollama_url or OLLAMA_API_URL)

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
            "subject_dir": subject_dir_rel,
            "card_path": card_path_rel,
            "card_json": card_json_rel,
            "markdown": markdown,
            "card": card,
        }
        with output_jsonl.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        count += 1
        print(f"[asset_bible] {count}/{len(profiles)} {subject_id}")

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
