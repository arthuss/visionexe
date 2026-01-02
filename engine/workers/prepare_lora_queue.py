import json
import os
import re
import unicodedata

import csv

ROOT_PATH = os.path.abspath(r"C:\Users\sasch\henoch")
INPUT_JSON = os.path.join(ROOT_PATH, "LORA_TRAINING_SET.json")
MASTER_IMAGES_JSON = os.path.join(ROOT_PATH, "LORA_MASTER_IMAGES.json")
TRIGGER_JSON = os.path.join(ROOT_PATH, "LORA_TRIGGERS.json")
OUTPUT_QUEUE = os.path.join(ROOT_PATH, "LORA_TRAINING_QUEUE.json")
OUTPUT_SUMMARY = os.path.join(ROOT_PATH, "LORA_TRAINING_QUEUE.md")
ENV_MAPPING_FILE = os.path.join(ROOT_PATH, "Environments", "mapping.csv")

WORKFLOW_ACTOR = os.path.join(ROOT_PATH, "workflows", "Qwen_edit_multiple_view_api.json")
WORKFLOW_MULTIVIEW = "Qwen_edit_multiple_view_api.json"
WORKFLOW_ENV_IMG2IMG = os.path.join(ROOT_PATH, "workflows", "Flux_img2img.json")
OUTPUT_ROOT = os.path.join(ROOT_PATH, "produced_assets", "lora_training")
TRAINING_ROOT = os.path.join(ROOT_PATH, "training_data", "lora_training")

DEFAULT_TRIGGER_PREFIX = "sks"
DEFAULT_SCENE_TAG = "S000"
INHERIT_PREVIOUS_PHASE = True

VIEW_ANGLES = [0, 45, 90, 135, 180, 225, 270, 315]
VIEW_LABELS = {
    0: "front",
    45: "three_quarter_right",
    90: "right_profile",
    135: "rear_three_quarter_right",
    180: "back",
    225: "rear_three_quarter_left",
    270: "left_profile",
    315: "three_quarter_left",
}

PROMPTS_PER_VIEW = 3
SHOT_VARIANTS = [
    "close-up portrait",
    "medium shot",
    "full body",
]
STYLE_VARIANTS = [
    "cinematic lighting",
    "high detail",
    "photorealistic",
]

ABC_LAYER_HINT = "layer A (organic texture), layer B (structural grid), layer C (interface overlay)"

EXCLUDE_ACTORS = {
    "Wave App",
}


def slugify(text):
    if text is None:
        return "unknown"
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_").lower()
    return text or "unknown"


def parse_chapter_start(chapter_str):
    if not chapter_str:
        return 9999
    match = re.search(r"(\d+)", str(chapter_str))
    if not match:
        return 9999
    return int(match.group(1))


def format_chapter_tag(chapter_str):
    if not chapter_str:
        return "ch000"
    parts = re.findall(r"\d+", str(chapter_str))
    if not parts:
        return "ch000"
    if len(parts) == 1:
        return f"ch{int(parts[0]):03d}"
    return f"ch{int(parts[0]):03d}-{int(parts[1]):03d}"


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, payload):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def build_trigger_map(actors):
    triggers = load_json(TRIGGER_JSON)
    if triggers:
        return triggers

    triggers = {"actors": {}}
    for name in actors:
        slug = slugify(name)
        triggers["actors"][name] = f"{DEFAULT_TRIGGER_PREFIX}_{slug}"
    save_json(TRIGGER_JSON, triggers)
    return triggers

def process_environments(queue):
    if not os.path.exists(ENV_MAPPING_FILE):
        print(f"No environment mapping found at {ENV_MAPPING_FILE}")
        return

    print(f"Processing environments from {ENV_MAPPING_FILE}...")
    env_workflow = WORKFLOW_ENV_IMG2IMG if os.path.exists(WORKFLOW_ENV_IMG2IMG) else WORKFLOW_MULTIVIEW

    def resolve_env_image_path(filename, target_folder):
        if not filename:
            return None
        if os.path.isabs(filename) and os.path.exists(filename):
            return filename

        # If mapping already contains a relative path under Environments
        candidate = os.path.join(ROOT_PATH, "Environments", filename)
        if os.path.exists(candidate):
            return candidate

        if target_folder:
            candidate = os.path.join(ROOT_PATH, "Environments", target_folder, filename)
            if os.path.exists(candidate):
                return candidate

        # Fallback: search by basename
        env_root = os.path.join(ROOT_PATH, "Environments")
        for root, _, files in os.walk(env_root):
            if filename in files:
                return os.path.join(root, filename)

        return None

    with open(ENV_MAPPING_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            filename = row.get("Image_Filename")
            target_folder = row.get("Target_Folder_Name")
            
            if not filename or not target_folder:
                continue
                
            # Construct full path to the image
            image_path = resolve_env_image_path(filename, target_folder)
            
            if not os.path.exists(image_path):
                print(f"  [WARN] Image not found: {image_path}")
                continue
                
            job_id = f"Env_{target_folder}_{os.path.splitext(filename)[0]}"
            
            queue.append({
                "id": job_id,
                "type": "environment",
                "input_image_path": image_path,
                "workflow_step2": env_workflow,
                "output_folder": target_folder
            })
            print(f"  + Added environment job: {job_id}")


def build_master_images_map(actors):
    master_images = load_json(MASTER_IMAGES_JSON)
    if master_images:
        return master_images

    master_images = {"actors": {}}
    for name, phases in actors.items():
        master_images["actors"][name] = {}
        for phase in phases:
            master_images["actors"][name][phase["name"]] = {
                "master_image": "",
                "cutout_image": "",
                "notes": ""
            }
    save_json(MASTER_IMAGES_JSON, master_images)
    return master_images


def get_phase_keywords(phase):
    keywords = phase.get("keywords", []) or []
    if isinstance(keywords, str):
        keywords = [keywords]
    return [str(k) for k in keywords if k]


def get_props(props):
    items = []
    for prop in props or []:
        name = prop.get("name")
        if name:
            items.append(name)
    return items


def make_prompt(trigger_word, actor_name, phase, keywords, props, view_angle, view_label, variant):
    parts = []
    if trigger_word:
        parts.append(trigger_word)
    parts.append(actor_name)
    parts.append(phase["name"])
    if phase.get("description"):
        parts.append(phase["description"])
    if keywords:
        parts.append(", ".join(keywords))
    if props:
        parts.append("props: " + ", ".join(props))
    parts.append(ABC_LAYER_HINT)
    parts.append(f"{variant}, {view_label} view, {view_angle} degree rotation")
    parts.extend(STYLE_VARIANTS)
    return ", ".join([p for p in parts if p])


def main():
    data = load_json(INPUT_JSON)
    if not data:
        print(f"Missing input: {INPUT_JSON}")
        return

    actors = data.get("actors", {})

    actor_phases = {}
    for name, payload in actors.items():
        if name in EXCLUDE_ACTORS:
            continue
        phases = payload.get("phases", []) or []
        if not phases:
            phases = [{"name": "Default", "chapters": "", "description": "", "keywords": []}]
        phases = sorted(phases, key=lambda p: parse_chapter_start(p.get("chapters")))
        actor_phases[name] = phases

    trigger_map = build_trigger_map(actor_phases.keys())
    master_images = build_master_images_map(actor_phases)

    ensure_dir(OUTPUT_ROOT)
    ensure_dir(TRAINING_ROOT)

    queue = []
    total_prompts = 0

    for actor_name, phases in actor_phases.items():
        actor_slug = slugify(actor_name)
        trigger_word = trigger_map.get("actors", {}).get(actor_name, f"{DEFAULT_TRIGGER_PREFIX}_{actor_slug}")
        previous_keywords = []

        for phase_index, phase in enumerate(phases, start=1):
            phase_slug = slugify(phase["name"])
            chapter_tag = format_chapter_tag(phase.get("chapters"))
            output_dir = os.path.join(OUTPUT_ROOT, "actors", actor_slug, phase_slug)
            training_dir = os.path.join(TRAINING_ROOT, "actors", actor_slug, phase_slug)
            ensure_dir(output_dir)
            ensure_dir(training_dir)

            phase_keywords = get_phase_keywords(phase)
            props = get_props(actors[actor_name].get("props", []))

            keywords = phase_keywords[:]
            if INHERIT_PREVIOUS_PHASE and previous_keywords:
                keywords = previous_keywords + phase_keywords

            view_variants = SHOT_VARIANTS[:PROMPTS_PER_VIEW]
            for view_angle in VIEW_ANGLES:
                view_label = VIEW_LABELS.get(view_angle, f"view_{view_angle}")
                for variant_index, variant in enumerate(view_variants, start=1):
                    prompt = make_prompt(
                        trigger_word,
                        actor_name,
                        phase,
                        keywords,
                        props,
                        view_angle,
                        view_label,
                        variant,
                    )

                    base_name = f"{actor_slug}__{phase_slug}__{chapter_tag}__{DEFAULT_SCENE_TAG}__v{view_angle:03d}__p{variant_index:02d}"
                    queue.append({
                        "entity_type": "actor",
                        "entity_name": actor_name,
                        "phase_name": phase["name"],
                        "chapter_tag": chapter_tag,
                        "scene_tag": DEFAULT_SCENE_TAG,
                        "view_angle": view_angle,
                        "view_label": view_label,
                        "prompt": prompt,
                        "output_dir": output_dir,
                        "output_basename": base_name,
                        "output_filename": base_name + ".png",
                        "training_target_dir": training_dir,
                        "workflow": WORKFLOW_ACTOR if os.path.exists(WORKFLOW_ACTOR) else "",
                        "master_image": master_images.get("actors", {}).get(actor_name, {}).get(phase["name"], {}).get("master_image", ""),
                        "cutout_image": master_images.get("actors", {}).get(actor_name, {}).get(phase["name"], {}).get("cutout_image", ""),
                        "inherits_from": phases[phase_index - 2]["name"] if phase_index > 1 else "",
                    })
                    total_prompts += 1

            previous_keywords = phase_keywords[:]

    process_environments(queue)
    save_json(OUTPUT_QUEUE, queue)

    with open(OUTPUT_SUMMARY, "w", encoding="utf-8") as f:
        f.write("# LoRA Training Queue Summary\n\n")
        f.write(f"- Total actors: {len(actor_phases)}\n")
        f.write(f"- Total prompts: {total_prompts}\n")
        f.write(f"- View angles: {', '.join(str(a) for a in VIEW_ANGLES)}\n")
        f.write(f"- Prompts per view: {PROMPTS_PER_VIEW}\n\n")

        for actor_name, phases in actor_phases.items():
            f.write(f"## {actor_name}\n")
            for phase in phases:
                chapter_tag = format_chapter_tag(phase.get("chapters"))
                f.write(f"- {phase['name']} ({chapter_tag})\n")
            f.write("\n")

    print(f"Wrote queue: {OUTPUT_QUEUE}")
    print(f"Wrote summary: {OUTPUT_SUMMARY}")
    print(f"Trigger map: {TRIGGER_JSON}")
    print(f"Master images: {MASTER_IMAGES_JSON}")


if __name__ == "__main__":
    main()
