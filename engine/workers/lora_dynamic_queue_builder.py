import argparse
import json
import re
import time
from pathlib import Path

from visionexe_paths import ensure_dir, load_story_config, resolve_path


QUEUE_TYPE_MAP = {
    "character": "actor",
    "prop": "prop",
    "set_environment": "asset",
}

PLACEHOLDER_IDS = {
    "CHAR_",
    "PROP_",
    "SETENV_",
    "ENV_",
    "GEOENV_",
    "SCENE_",
    "LOC_",
}

SAFE_FOLDER_RE = re.compile(r"[^A-Za-z0-9_.-]+")
TIMELINE_TAG_RE = re.compile(r"[^0-9]")


def load_jsonl(path: Path):
    items = []
    if not path or not path.exists():
        return items
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            items.append(json.loads(line))
    return items


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


def safe_folder_name(value: str) -> str:
    if not value:
        return "default"
    return SAFE_FOLDER_RE.sub("_", str(value)).strip("_") or "default"


def build_workflow_prefix(workflow_name: str) -> str:
    if not workflow_name:
        return ""
    return safe_folder_name(workflow_name)


def is_placeholder_subject(subject_id: str, name: str) -> bool:
    if not subject_id:
        return True
    if subject_id in PLACEHOLDER_IDS:
        return True
    if subject_id.endswith("_"):
        return True
    if name and "?" in name:
        return True
    return False


def resolve_subject_dir(subjects_root_rel: Path, subjects_root_abs: Path, card):
    subject_dir = card.get("subject_dir") if isinstance(card, dict) else None
    if subject_dir:
        rel = Path(str(subject_dir).replace("\\", "/"))
        return rel, subjects_root_abs / rel
    safe_id = safe_folder_name(card.get("id") if isinstance(card, dict) else "") or "unknown"
    rel = subjects_root_rel / safe_id
    return rel, subjects_root_abs / rel


def choose_phase_prompt(card_data, state_id, state_label):
    phase_prompts = card_data.get("phase_prompts") or []
    if not phase_prompts:
        return None
    for prompt in phase_prompts:
        if prompt.get("state_id") == state_id:
            return prompt
    for prompt in phase_prompts:
        if prompt.get("label") == state_label:
            return prompt
    if len(phase_prompts) == 1:
        return phase_prompts[0]
    return None


def collect_phase_prompts(card_data, state_id, state_label):
    phase_prompts = card_data.get("phase_prompts") or []
    if isinstance(phase_prompts, dict):
        prompts = [value for value in phase_prompts.values() if isinstance(value, dict)]
        return prompts
    if not isinstance(phase_prompts, list):
        return []
    matches = []
    for prompt in phase_prompts:
        if not isinstance(prompt, dict):
            continue
        if state_id and prompt.get("state_id") == state_id:
            matches.append(prompt)
            continue
        if state_label and prompt.get("label") == state_label:
            matches.append(prompt)
    if matches:
        return matches
    return [prompt for prompt in phase_prompts if isinstance(prompt, dict)]


def build_chapter_tag(state):
    start = state.get("chapter_start")
    end = state.get("chapter_end")
    if start in ("", None) and end in ("", None):
        return ""
    try:
        start_val = int(start)
        end_val = int(end) if end is not None else start_val
    except (TypeError, ValueError):
        return ""
    if start_val == end_val:
        return f"ch{start_val:03d}"
    return f"ch{start_val:03d}-ch{end_val:03d}"


def build_prompt(card_data, phase_prompt, fallback_name):
    prompt_block = card_data.get("prompt_block") or ""
    if phase_prompt:
        return phase_prompt.get("prompt_block") or prompt_block or fallback_name
    return prompt_block or fallback_name


def main():
    parser = argparse.ArgumentParser(description="Build dynamic-only LoRA queues from subject cards.")
    parser.add_argument("--story-root", help="Story root path (defaults to engine_config default_story_root).")
    parser.add_argument("--story-config", help="Path to story_config.json (overrides story-root).")
    parser.add_argument("--profiles", help="profiles.jsonl path.")
    parser.add_argument("--cards", help="asset_bible_cards.jsonl path.")
    parser.add_argument("--output-set", help="Output lora_training_set.json path.")
    parser.add_argument("--output-queue", help="Output lora_training_queue.json path.")
    parser.add_argument("--output-prop-queue", help="Output lora_prop_queue.json path.")
    parser.add_argument("--timeline", help="Timeline tag (e.g., 1 or r01).")
    parser.add_argument("--include-static", action="store_true", help="Include non-dynamic subjects.")
    parser.add_argument("--types", default="character,prop,set_environment", help="Comma list of subject types to include.")
    parser.add_argument("--style-seed-workflow", help="Workflow override for style seed generation.")
    parser.add_argument("--style-seed-count", type=int, help="Repeat count for style seed generation.")
    args = parser.parse_args()

    story_config, _, repo_root = load_story_config(
        story_root=args.story_root,
        story_config_path=args.story_config,
    )

    subjects_root_rel = Path(story_config.get("subjects_root") or "stories/template/subjects")
    subjects_root_abs = resolve_path(subjects_root_rel, repo_root)

    profiles_path = resolve_path(args.profiles or f"{subjects_root_rel}/profiles.jsonl", repo_root)
    cards_path = resolve_path(args.cards or f"{subjects_root_rel}/asset_bible_cards.jsonl", repo_root)

    output_set = resolve_path(args.output_set or story_config.get("lora_training_set_path"), repo_root)
    output_queue = resolve_path(args.output_queue or story_config.get("lora_training_queue_path"), repo_root)
    output_prop_queue = resolve_path(args.output_prop_queue or story_config.get("lora_prop_queue_path"), repo_root)

    timeline_label = story_config.get("timeline_label", "timeline")
    timeline_padding = int(story_config.get("timeline_index_padding", 2))
    timeline_tag = normalize_timeline_tag(args.timeline, timeline_padding)
    timeline_folder = f"{timeline_label}_{timeline_tag}"

    allowed_types = {item.strip() for item in args.types.split(",") if item.strip()}
    style_seed_workflow = args.style_seed_workflow or story_config.get("lora_style_seed_workflow", "")
    style_seed_count = int(args.style_seed_count or story_config.get("lora_style_seed_count", 20))

    profiles = load_jsonl(profiles_path)
    cards = load_jsonl(cards_path)

    cards_by_id = {card.get("id"): card for card in cards if isinstance(card, dict)}

    training_set = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "timeline": timeline_folder,
        "actors": {},
    }
    training_queue = []
    prop_queue = []

    for profile in profiles:
        subject_id = profile.get("id") or ""
        name = profile.get("name") or ""
        subject_type = profile.get("type") or ""

        if subject_type not in allowed_types:
            continue
        if not args.include_static and not profile.get("is_dynamic", False):
            continue
        if is_placeholder_subject(subject_id, name):
            continue

        card = cards_by_id.get(subject_id, {})
        card_data = card.get("card") if isinstance(card.get("card"), dict) else {}
        states = profile.get("states") or []
        if not states:
            states = [{
                "state_id": "default",
                "label": "Default",
                "chapter_start": profile.get("first_chapter"),
                "chapter_end": profile.get("last_chapter"),
            }]

        subject_dir_rel, subject_dir_abs = resolve_subject_dir(subjects_root_rel, subjects_root_abs, card or {"id": subject_id})

        if args.timeline and timeline_folder not in str(subject_dir_rel).replace("\\", "/"):
            continue

        for state in states:
            state_id = state.get("state_id") or "default"
            state_label = state.get("label") or state_id
            safe_state = safe_folder_name(state_id)
            phase_prompt = choose_phase_prompt(card_data, state_id, state_label)
            queue_phase_prompts = collect_phase_prompts(card_data, state_id, state_label)
            if not queue_phase_prompts:
                queue_phase_prompts = [None]

            prompt = build_prompt(card_data, phase_prompt, name)
            keywords = phase_prompt.get("prompt_keywords") if phase_prompt else card_data.get("prompt_keywords") or []
            summary = phase_prompt.get("summary") if phase_prompt else ""
            chapters = build_chapter_tag(state)

            state_dir_rel = subject_dir_rel / "states" / safe_state
            state_dir_abs = subject_dir_abs / "states" / safe_state
            style_seed_rel = state_dir_rel / "images" / "style_seed"
            multiangle_rel = state_dir_rel / "images" / "multiangle"
            style_seed_abs = state_dir_abs / "images" / "style_seed"
            multiangle_abs = state_dir_abs / "images" / "multiangle"
            ensure_dir(style_seed_abs)
            ensure_dir(multiangle_abs)

            queue_type = QUEUE_TYPE_MAP.get(subject_type, "asset")

            for phase_idx, phase_entry in enumerate(queue_phase_prompts, start=1):
                phase_id = state_id
                phase_name = state_label
                phase_label = ""
                if phase_entry:
                    phase_id = phase_entry.get("state_id") or phase_id
                    phase_name = phase_entry.get("label") or phase_name
                    phase_label = phase_entry.get("label") or ""
                phase_suffix = safe_folder_name(phase_id or phase_name or "")
                if len(queue_phase_prompts) > 1:
                    if not phase_suffix or phase_suffix == safe_folder_name(state_id):
                        phase_suffix = f"{phase_suffix or 'phase'}_{phase_idx:02d}"
                prompt = build_prompt(card_data, phase_entry, name)
                job_id = f"{subject_id}__{state_id}__{phase_suffix}__seed"
                workflow_prefix = build_workflow_prefix(style_seed_workflow)
                output_basename = job_id
                if workflow_prefix:
                    output_basename = f"{workflow_prefix}__{job_id}"

                training_queue.append({
                    "id": job_id,
                    "type": queue_type,
                    "entity_type": queue_type,
                    "entity_name": name,
                    "subject_id": subject_id,
                    "subject_type": subject_type,
                    "phase_name": phase_name,
                    "phase_id": phase_id,
                    "phase_prompt_label": phase_label,
                    "prompt": prompt,
                    "workflow": style_seed_workflow,
                    "output_dir": str(style_seed_rel).replace("\\", "/"),
                    "output_basename": output_basename,
                    "expected_outputs": 1,
                    "repeat_count": style_seed_count,
                })

                if subject_type == "prop":
                    prop_queue.append({
                        "entity_type": "prop",
                        "entity_name": name,
                        "actor_slug": "global",
                        "prop_name": name,
                        "prop_slug": safe_folder_name(name),
                        "prompt": prompt,
                        "output_dir": str(style_seed_rel).replace("\\", "/"),
                        "output_basename": output_basename,
                        "workflow": style_seed_workflow,
                        "expected_outputs": 1,
                        "repeat_count": style_seed_count,
                    })

            if subject_type != "character":
                continue

            actor_entry = training_set["actors"].setdefault(name, {
                "subject_id": subject_id,
                "subject_type": subject_type,
                "props": card_data.get("props") or [],
                "phases": [],
            })

            actor_entry["phases"].append({
                "name": state_label,
                "state_id": state_id,
                "chapters": chapters,
                "description": summary or card_data.get("description") or "",
                "keywords": keywords,
                "prompt": prompt,
                "prompt_block": prompt,
                "subject_id": subject_id,
                "subject_dir": str(subject_dir_rel).replace("\\", "/"),
                "style_seed_dir": str(style_seed_rel).replace("\\", "/"),
                "multiangle_dir": str(multiangle_rel).replace("\\", "/"),
            })

    if output_set:
        output_set.parent.mkdir(parents=True, exist_ok=True)
        with output_set.open("w", encoding="utf-8") as handle:
            json.dump(training_set, handle, indent=2, ensure_ascii=False)
        print(f"Wrote training set: {output_set}")

    if output_queue:
        output_queue.parent.mkdir(parents=True, exist_ok=True)
        with output_queue.open("w", encoding="utf-8") as handle:
            json.dump(training_queue, handle, indent=2, ensure_ascii=False)
        print(f"Wrote training queue: {output_queue}")

    if output_prop_queue:
        output_prop_queue.parent.mkdir(parents=True, exist_ok=True)
        with output_prop_queue.open("w", encoding="utf-8") as handle:
            json.dump(prop_queue, handle, indent=2, ensure_ascii=False)
        print(f"Wrote prop queue: {output_prop_queue}")


if __name__ == "__main__":
    main()
