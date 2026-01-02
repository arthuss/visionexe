import os
import re
import json
import argparse
import subprocess
import time
import unicodedata

# Configuration
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
FILMSETS_PATH = os.path.join(ROOT_PATH, "filmsets")
GENERATE_SCRIPT = os.path.join(ROOT_PATH, "generate.py")

# Workflows
WORKFLOW_IMAGE = "flux_schnell"
WORKFLOW_VIDEO = "wan22_image"
# WORKFLOW_AUDIO = "hunyuan_foley" # Not yet available
LORA_TRIGGER_FILE = os.path.join(ROOT_PATH, "LORA_TRIGGERS.json")
LORA_TRAINING_SET_FILE = os.path.join(ROOT_PATH, "LORA_TRAINING_SET.json")
LORA_PHASE_ALIAS_FILE = os.path.join(ROOT_PATH, "LORA_PHASE_ALIASES.json")
LORA_DEFAULT_ROOTS = [
    os.path.join(ROOT_PATH, "produced_assets", "lora_training", "loras"),
    os.path.join(ROOT_PATH, "produced_assets", "lora_training", "actors"),
]
MAX_LORA_SLOTS = 2

def get_chapters(chapter_arg):
    all_chapters = sorted([d for d in os.listdir(FILMSETS_PATH) if d.startswith("chapter_")])
    
    if chapter_arg == "all":
        return all_chapters
    
    # Handle ranges like "1-5" or single numbers "3"
    selected = []
    parts = chapter_arg.split(',')
    for part in parts:
        if '-' in part:
            start, end = map(int, part.split('-'))
            for i in range(start, end + 1):
                ch_name = f"chapter_{i:03d}"
                if ch_name in all_chapters:
                    selected.append(ch_name)
        else:
            ch_num = int(part)
            ch_name = f"chapter_{ch_num:03d}"
            if ch_name in all_chapters:
                selected.append(ch_name)
                
    return sorted(list(set(selected)))


def normalize_key(value):
    text = unicodedata.normalize("NFKD", str(value or "")).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def slugify(value):
    text = unicodedata.normalize("NFKD", str(value or "")).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_") or "unknown"


def normalize_timeline_tag(value):
    if value is None:
        return None
    raw = str(value).strip().lower()
    if not raw:
        return None
    if raw.startswith("r") and raw[1:].isdigit():
        number = int(raw[1:])
        return f"r{number:02d}"
    if raw.isdigit():
        number = int(raw)
        return f"r{number:02d}"
    cleaned = re.sub(r"[^a-z0-9]+", "", raw)
    return cleaned or None


def load_trigger_map(path=LORA_TRIGGER_FILE):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        mapping = payload.get("actors", {})
        for name, trigger in list(mapping.items()):
            norm = normalize_key(name)
            if norm and norm not in mapping:
                mapping[norm] = trigger
        return mapping
    except (json.JSONDecodeError, OSError):
        return {}


def load_phase_aliases(path=LORA_PHASE_ALIAS_FILE):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}
    if not isinstance(raw, dict):
        return {}
    mapped = {}
    for actor, data in raw.items():
        if not isinstance(data, dict):
            continue
        alias_block = data.get("aliases") if "aliases" in data else data
        if not isinstance(alias_block, dict):
            continue
        actor_norm = normalize_key(actor)
        if not actor_norm:
            continue
        for alias, phase in alias_block.items():
            alias_norm = normalize_key(alias)
            if not alias_norm or not phase:
                continue
            mapped.setdefault(actor_norm, {})[alias_norm] = str(phase)
    return mapped


def parse_chapter_ranges(value):
    ranges = []
    if not value:
        return ranges
    for chunk in re.split(r"[,\s]+", str(value)):
        part = chunk.strip()
        if not part:
            continue
        if "-" in part:
            start_text, end_text = part.split("-", 1)
            if start_text.isdigit() and end_text.isdigit():
                start = int(start_text)
                end = int(end_text)
                if start > end:
                    start, end = end, start
                ranges.append((start, end))
        elif part.isdigit():
            num = int(part)
            ranges.append((num, num))
    return ranges


def load_phase_index(path=LORA_TRAINING_SET_FILE):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}
    actors = payload.get("actors") if isinstance(payload, dict) else None
    if not isinstance(actors, dict):
        return {}
    phase_index = {}
    for actor_name, data in actors.items():
        phases = data.get("phases") if isinstance(data, dict) else None
        if not isinstance(phases, list):
            continue
        actor_norm = normalize_key(actor_name)
        if not actor_norm:
            continue
        for phase in phases:
            if not isinstance(phase, dict):
                continue
            name = phase.get("name")
            ranges = parse_chapter_ranges(phase.get("chapters"))
            if name and ranges:
                phase_index.setdefault(actor_norm, []).append({"name": name, "ranges": ranges})
    return phase_index


def phase_for_chapter(phase_index, actor_name, chapter_num):
    if not phase_index or not actor_name or chapter_num is None:
        return None
    actor_norm = normalize_key(actor_name)
    if not actor_norm:
        return None
    for phase in phase_index.get(actor_norm, []):
        for start, end in phase.get("ranges", []):
            if start <= chapter_num <= end:
                return phase.get("name")
    return None


def build_lora_index(roots):
    index = []
    for root in roots:
        if not root or not os.path.exists(root):
            continue
        for dirpath, _, filenames in os.walk(root):
            for name in filenames:
                if not name.lower().endswith(".safetensors"):
                    continue
                full_path = os.path.join(dirpath, name)
                rel = os.path.relpath(full_path, root).replace(os.sep, "/")
                index.append({
                    "root": root,
                    "path": full_path,
                    "rel": rel,
                    "norm": normalize_key(rel),
                })
    return index


def resolve_actor_lora(lora_index, actor_name, phase_name, chapter_num, phase_aliases, phase_index):
    actor_norm = normalize_key(actor_name)
    phase_norm = normalize_key(phase_name)
    if not actor_norm:
        return None
    if phase_aliases:
        alias = phase_aliases.get(actor_norm, {}).get(phase_norm)
        if alias:
            phase_norm = normalize_key(alias)
    candidates = [entry for entry in lora_index if actor_norm in entry["norm"]]
    if not candidates:
        return None
    if phase_norm:
        for entry in candidates:
            if phase_norm in entry["norm"]:
                return entry["rel"]
    chapter_phase = phase_for_chapter(phase_index, actor_name, chapter_num)
    chapter_norm = normalize_key(chapter_phase)
    if chapter_norm:
        for entry in candidates:
            if chapter_norm in entry["norm"]:
                return entry["rel"]
    tokens = set((phase_norm or chapter_norm).split())
    if tokens:
        best_entry = None
        best_score = 0
        for entry in candidates:
            entry_tokens = set(entry["norm"].split())
            score = len(tokens & entry_tokens)
            if score > best_score:
                best_score = score
                best_entry = entry
        if best_entry and best_score > 0:
            return best_entry["rel"]
    return candidates[0]["rel"]
    return None


def resolve_prop_lora(lora_index, actor_name, prop_name):
    actor_slug = slugify(actor_name)
    prop_slug = slugify(prop_name)
    needle = normalize_key(f"prop__{prop_slug}__{actor_slug}")
    for entry in lora_index:
        if needle and needle in entry["norm"]:
            return entry["rel"]
    return None


def extract_regie_json(text):
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("REGIE_JSON:"):
            payload = line.split(":", 1)[1].strip()
            try:
                return json.loads(payload)
            except json.JSONDecodeError:
                return {}
    return {}


def should_include_actor(regie):
    if not isinstance(regie, dict):
        return True
    subject = normalize_key(regie.get("subject", ""))
    mode = normalize_key(regie.get("start_image_mode", ""))
    if mode in ("env_only", "prop_only", "ui_only"):
        return False
    if subject in ("environment", "prop", "interface"):
        return False
    return True


def should_include_loras(regie):
    if not isinstance(regie, dict):
        return True
    mode = normalize_key(regie.get("start_image_mode", ""))
    if mode in ("env_only", "ui_only"):
        return False
    return True


def collect_lora_args(regie, lora_index, chapter_num, phase_aliases, phase_index):
    loras = []
    if not isinstance(regie, dict):
        return loras
    actors = regie.get("actors") or []
    for actor in actors:
        if not isinstance(actor, dict):
            continue
        actor_name = actor.get("name")
        phase_name = actor.get("phase") or ""
        lora_name = resolve_actor_lora(
            lora_index,
            actor_name,
            phase_name,
            chapter_num,
            phase_aliases,
            phase_index,
        )
        if lora_name:
            loras.append(f"{lora_name}:1.0")
    props = regie.get("props") or []
    for prop in props:
        prop_name = prop if isinstance(prop, str) else prop.get("name")
        if not prop_name:
            continue
        actor_name = actors[0].get("name") if actors else ""
        lora_name = resolve_prop_lora(lora_index, actor_name, prop_name)
        if lora_name:
            loras.append(f"{lora_name}:0.8")
    return loras[:MAX_LORA_SLOTS]


def apply_actor_trigger(prompt, regie, trigger_map):
    if not isinstance(regie, dict):
        return prompt
    actors = regie.get("actors") or []
    if not actors:
        return prompt
    actor_name = actors[0].get("name")
    trigger = trigger_map.get(actor_name)
    if not trigger:
        trigger = trigger_map.get(normalize_key(actor_name))
    if not trigger:
        return prompt
    if trigger in prompt:
        return prompt
    return f"{trigger}, {prompt}"


def collect_start_image_keywords(regie):
    if not isinstance(regie, dict):
        return []
    raw = regie.get("start_image_keywords")
    if not raw:
        return []
    items = []
    if isinstance(raw, str):
        parts = [part.strip() for part in raw.split(",") if part.strip()]
        items.extend(parts)
    elif isinstance(raw, list):
        for entry in raw:
            if not isinstance(entry, str):
                continue
            value = entry.strip()
            if value:
                items.append(value)
    seen = set()
    unique = []
    for item in items:
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def apply_start_image_keywords(prompt, regie):
    keywords = collect_start_image_keywords(regie)
    if not keywords:
        return prompt
    prompt_lower = prompt.lower()
    to_add = []
    seen = set()
    for keyword in keywords:
        key = keyword.lower()
        if key in seen:
            continue
        seen.add(key)
        if key in prompt_lower:
            continue
        to_add.append(keyword)
    if not to_add:
        return prompt
    return f"{', '.join(to_add)}, {prompt}"


def format_lora_tag(lora_entry):
    if not lora_entry:
        return None
    raw = str(lora_entry).strip()
    if not raw:
        return None
    if raw.startswith("<lora:") and raw.endswith(">"):
        return raw
    if ":" in raw:
        path_part, weight_part = raw.rsplit(":", 1)
        path_part = path_part.strip().replace("\\", "/")
        weight_part = weight_part.strip() or "1.0"
    else:
        path_part = raw.replace("\\", "/")
        weight_part = "1.0"
    if not path_part:
        return None
    return f"<lora:{path_part}:{weight_part}>"


def apply_lora_tags(prompt, lora_args):
    if not lora_args:
        return prompt
    prompt_lower = prompt.lower()
    tags = []
    seen = set()
    for entry in lora_args:
        tag = format_lora_tag(entry)
        if not tag:
            continue
        key = tag.lower()
        if key in seen:
            continue
        seen.add(key)
        if key in prompt_lower:
            continue
        tags.append(tag)
    if not tags:
        return prompt
    return f"{', '.join(tags)}, {prompt}"

def parse_script(file_path, chapter_name, workflow_image, workflow_video):
    if not os.path.exists(file_path):
        return []

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    prompts = []
    
    # Split by Scene headers
    scene_splits = re.split(r'(^##\s+\[ACT\s+\d+\]\s+\[SCENE\s+[\d\.]+\])', content, flags=re.MULTILINE)
    
    current_scene_header = ""
    
    for part in scene_splits:
        if part.strip().startswith("## [ACT"):
            current_scene_header = part.strip()
            continue
        
        if not current_scene_header:
            continue
            
        # Extract Scene Number
        scene_match = re.search(r'\[SCENE\s+([\d\.]+)\]', current_scene_header)
        scene_num = scene_match.group(1) if scene_match else "0.0"
        
        regie = extract_regie_json(part)

        # 1. IMAGE PROMPTS
        # Regex to find the block and capture content flexibly
        # Matches: ### 1. START IMAGE PROMPT (Midjourney/Flux) [newline] [optional markdown] CONTENT [optional markdown]
        img_matches = re.finditer(r'### 1\. START IMAGE PROMPT \(Midjourney/Flux\)\s*\n(.*?)(?=\n###|\n---|$)', part, re.DOTALL)
        for m in img_matches:
            raw_content = m.group(1).strip()
            # Clean up markdown wrappers like ** or `
            clean_content = raw_content.strip('`*').strip()
            
            if clean_content:
                prompts.append({
                    "type": "image",
                    "chapter": chapter_name,
                    "scene": scene_num,
                    "content": clean_content,
                    "regie": regie,
                    "workflow": workflow_image
                })

        # 2. VIDEO PROMPTS
        vid_matches = re.finditer(r'### 2\. VIDEO PROMPT.*?\n(.*?)(?=\n###|\n---|$)', part, re.DOTALL)
        for m in vid_matches:
            raw_content = m.group(1).strip()
            if raw_content:
                prompts.append({
                    "type": "video",
                    "chapter": chapter_name,
                    "scene": scene_num,
                    "content": raw_content,
                    "regie": regie,
                    "workflow": workflow_video
                })

        # 3. AUDIO PROMPTS (Placeholder for future)
        # aud_matches = re.finditer(r'### 3\. AUDIO PROMPT.*?\n\*\*(.*?)\*\*', part, re.DOTALL)
        # ...

    return prompts

def main():
    parser = argparse.ArgumentParser(description="Generate assets for Henoch chapters")
    parser.add_argument("--chapter", default="all", help="Chapter number(s) to process (e.g. '1', '1-5', 'all')")
    parser.add_argument("--type", default="image", choices=["image", "video", "audio", "all"], help="Asset type to generate")
    parser.add_argument("--dry-run", action="store_true", help="Only list what would be generated")
    parser.add_argument("--lora-root", action="append", help="Additional LoRA search root (repeatable)")
    parser.add_argument("--no-lora", action="store_true", help="Disable LoRA injection")
    parser.add_argument("--image-workflow", default=WORKFLOW_IMAGE, help="Workflow for image prompts")
    parser.add_argument("--video-workflow", default=WORKFLOW_VIDEO, help="Workflow for video prompts")
    parser.add_argument("--timeline", help="Timeline tag (e.g. 1 or r01) appended to output filename")
    
    args = parser.parse_args()
    
    trigger_map = load_trigger_map()
    phase_aliases = load_phase_aliases()
    phase_index = load_phase_index()
    lora_roots = args.lora_root or LORA_DEFAULT_ROOTS
    lora_index = [] if args.no_lora else build_lora_index(lora_roots)

    chapters = get_chapters(args.chapter)
    print(f"Scanning {len(chapters)} chapters...")
    
    all_tasks = []
    
    for ch in chapters:
        script_path = os.path.join(FILMSETS_PATH, ch, "DREHBUCH_HOLLYWOOD.md")
        if os.path.exists(script_path):
            tasks = parse_script(script_path, ch, args.image_workflow, args.video_workflow)
            all_tasks.extend(tasks)
        else:
            # print(f"Skipping {ch} (No script found)")
            pass
            
    print(f"Found {len(all_tasks)} tasks total.")
    
    # Filter by type
    if args.type != "all":
        all_tasks = [t for t in all_tasks if t["type"] == args.type]
        
    print(f"Processing {len(all_tasks)} {args.type} tasks...")
    
    timeline_tag = normalize_timeline_tag(args.timeline)

    for i, task in enumerate(all_tasks):
        # Construct ID: CH003_SC1.1_IMG
        ch_num = task['chapter'].replace("chapter_", "")
        chapter_num = int(ch_num) if ch_num.isdigit() else None
        task_id = f"CH{ch_num}_SC{task['scene']}_{task['type'].upper()}"
        if timeline_tag:
            task_id = f"{task_id}__{timeline_tag}"
        regie = task.get("regie", {})
        prompt = task["content"]
        if should_include_actor(regie):
            prompt = apply_actor_trigger(prompt, regie, trigger_map)
        prompt = apply_start_image_keywords(prompt, regie)
        lora_args = (
            collect_lora_args(regie, lora_index, chapter_num, phase_aliases, phase_index)
            if should_include_loras(regie)
            else []
        )
        prompt = apply_lora_tags(prompt, lora_args)
        
        print(f"[{i+1}/{len(all_tasks)}] {task_id} -> {task['workflow']}")
        
        if not args.dry_run:
            cmd = [
                "python", 
                GENERATE_SCRIPT, 
                "--workflow", task['workflow'],
                "--prompt", prompt,
                "--filename", task_id
            ]
            
            try:
                subprocess.run(cmd, check=True)
                time.sleep(0.5)
            except subprocess.CalledProcessError as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    main()
