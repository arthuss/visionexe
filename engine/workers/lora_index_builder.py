import argparse
import json
import re
import time
import unicodedata
from pathlib import Path

from visionexe_paths import load_story_config, resolve_path


def load_json(path: Path):
    if not path or not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_jsonl(path: Path):
    items = []
    if not path or not path.exists():
        return items
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            items.append(json.loads(line))
    return items


def slugify(text: str) -> str:
    if text is None:
        return "unknown"
    normalized = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode("ascii")
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", normalized).strip("_").lower()
    return normalized or "unknown"


def normalize_key(text: str) -> str:
    if text is None:
        return ""
    normalized = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode("ascii")
    return "".join(ch.lower() if ch.isalnum() else " " for ch in normalized).strip()


def normalize_timeline_tag(value: str, padding: int) -> str:
    if not value:
        return f"{1:0{padding}d}"
    raw = str(value).strip().lower()
    if raw.startswith("r") and raw[1:].isdigit():
        return f"{int(raw[1:]):0{padding}d}"
    if raw.isdigit():
        return f"{int(raw):0{padding}d}"
    digits = re.sub(r"[^0-9]", "", raw)
    if digits:
        return f"{int(digits):0{padding}d}"
    return f"{1:0{padding}d}"


def load_profile_map(path: Path):
    profiles = load_jsonl(path)
    by_type = {}
    for profile in profiles:
        name = profile.get("name") or ""
        subject_type = profile.get("type") or ""
        key = normalize_key(name)
        by_type.setdefault(subject_type, {}).setdefault(key, []).append(profile.get("id"))
    return by_type


def resolve_subject_id(name, subject_type, profile_map):
    if not name:
        return ""
    key = normalize_key(name)
    if subject_type and subject_type in profile_map:
        ids = profile_map.get(subject_type, {}).get(key, [])
        if ids:
            return ids[0]
    for entries in profile_map.values():
        ids = entries.get(key)
        if ids:
            return ids[0]
    return ""


def build_lora_path(root: Path, category: str, actor_slug: str, phase_slug: str, filename: str):
    parts = [root, category]
    if actor_slug:
        parts.append(actor_slug)
    if phase_slug:
        parts.append(phase_slug)
    return str(Path(*parts) / filename)


def apply_lora_override(entry, overrides):
    if not overrides:
        return
    lora_overrides = overrides.get("loras", {})
    override = lora_overrides.get(entry.get("id"))
    if not override:
        return
    for key in ("lora_type", "strength", "prompt_mode", "notes"):
        if key in override:
            entry[key] = override[key]


def main():
    parser = argparse.ArgumentParser(description="Build LoRA index from existing training metadata.")
    parser.add_argument("--story-root", help="Story root path (defaults to engine_config default_story_root).")
    parser.add_argument("--story-config", help="Path to story_config.json (overrides story-root).")
    parser.add_argument("--profiles", help="Profiles.jsonl path for subject ID mapping.")
    parser.add_argument("--training-set", help="LORA_TRAINING_SET.json path.")
    parser.add_argument("--training-queue", help="LORA_TRAINING_QUEUE.json path.")
    parser.add_argument("--prop-queue", help="LORA_PROP_QUEUE.json path.")
    parser.add_argument("--triggers", help="LORA_TRIGGERS.json path.")
    parser.add_argument("--master-images", help="LORA_MASTER_IMAGES.json path.")
    parser.add_argument("--training-runs", help="lora_training_runs.jsonl path.")
    parser.add_argument("--overrides", help="Overrides JSON path.")
    parser.add_argument("--timeline", help="Timeline tag (e.g., 1 or r01).")
    parser.add_argument("--output", help="Output lora_index.json path.")
    args = parser.parse_args()

    story_config, _, repo_root = load_story_config(
        story_root=args.story_root,
        story_config_path=args.story_config,
    )

    subjects_root = resolve_path(story_config.get("subjects_root"), repo_root)
    profiles_path = resolve_path(args.profiles or f"{subjects_root}/profiles.jsonl", repo_root)
    profile_map = load_profile_map(profiles_path)

    training_set_path = resolve_path(args.training_set or story_config.get("lora_training_set_path", ""), repo_root)
    training_queue_path = resolve_path(args.training_queue or story_config.get("lora_training_queue_path", ""), repo_root)
    prop_queue_path = resolve_path(args.prop_queue or story_config.get("lora_prop_queue_path", ""), repo_root)
    triggers_path = resolve_path(args.triggers or story_config.get("lora_triggers_path", ""), repo_root)
    master_images_path = resolve_path(args.master_images or story_config.get("lora_master_images_path", ""), repo_root)
    training_runs_path = resolve_path(args.training_runs or story_config.get("lora_training_runs_path", ""), repo_root)
    overrides_path = resolve_path(args.overrides or story_config.get("lora_overrides_path", ""), repo_root)

    lora_root = resolve_path(story_config.get("lora_root"), repo_root)
    lora_training_root = resolve_path(story_config.get("lora_training_root"), repo_root)
    timeline_label = story_config.get("timeline_label", "timeline")
    timeline_padding = int(story_config.get("timeline_index_padding", 2))
    timeline_tag = normalize_timeline_tag(args.timeline, timeline_padding)
    timeline_folder = f"{timeline_label}_{timeline_tag}"
    lora_root = Path(lora_root) / timeline_folder
    lora_training_root = Path(lora_training_root) / timeline_folder if lora_training_root else None

    output_path = resolve_path(args.output or story_config.get("lora_index_path", ""), repo_root)
    if not output_path:
        raise SystemExit("No lora_index_path configured.")

    training_set = load_json(training_set_path) or {}
    training_queue = load_json(training_queue_path) or []
    prop_queue = load_json(prop_queue_path) or []
    triggers = load_json(triggers_path) or {}
    master_images = load_json(master_images_path) or {}
    training_runs = load_jsonl(training_runs_path)
    overrides = load_json(overrides_path) or {}

    actor_triggers = triggers.get("actors", {})
    master_actor_images = master_images.get("actors", {})

    actors = []
    loras = []
    for actor_name, info in (training_set.get("actors", {}) or {}).items():
        phases = info.get("phases", []) if isinstance(info, dict) else []
        props = info.get("props", []) if isinstance(info, dict) else []
        actor_slug = slugify(actor_name)
        subject_id = resolve_subject_id(actor_name, "character", profile_map)
        actor_entry = {
            "actor_name": actor_name,
            "actor_slug": actor_slug,
            "subject_id": subject_id,
            "trigger": actor_triggers.get(actor_name, ""),
            "props": props,
            "phases": [],
        }

        subject_override = overrides.get("subjects", {}).get(subject_id) or overrides.get("subjects", {}).get(actor_name) or {}
        phase_overrides = subject_override.get("phases", {}) if isinstance(subject_override, dict) else {}

        for phase in phases:
            phase_name = phase.get("name") if isinstance(phase, dict) else ""
            phase_slug = slugify(phase_name)
            phase_override = phase_overrides.get(phase_slug, {}) if isinstance(phase_overrides, dict) else {}
            phase_subject_id = subject_id
            base_id = f"{actor_slug}__{phase_slug}__base"
            style_id = f"{actor_slug}__{phase_slug}__style"
            base_filename = f"{base_id}.safetensors"
            style_filename = f"{style_id}.safetensors"
            base_path = build_lora_path(lora_root, "actors", actor_slug, phase_slug, base_filename)
            style_path = build_lora_path(lora_root, "actors", actor_slug, phase_slug, style_filename)
            master_entry = master_actor_images.get(actor_name, {}).get(phase_name, {}) if isinstance(master_actor_images, dict) else {}
            style_seed_dir = None
            multiangle_dir = None
            if lora_training_root:
                style_seed_dir = str(lora_training_root / "actors" / actor_slug / phase_slug / "style_seed")
                multiangle_dir = str(lora_training_root / "actors" / actor_slug / phase_slug / "multiangle")

            phase_entry = {
                "phase_name": phase_name,
                "phase_slug": phase_slug,
                "chapter_tags": phase.get("chapters") if isinstance(phase, dict) else "",
                "description": phase.get("description") if isinstance(phase, dict) else "",
                "keywords": phase.get("keywords") if isinstance(phase, dict) else [],
                "subject_id": phase_subject_id,
                "base_lora": {
                    "id": base_id,
                    "path": base_path,
                    "lora_type": "identity",
                },
                "style_lora": {
                    "id": style_id,
                    "path": style_path,
                    "lora_type": "style",
                },
                "master_image": master_entry.get("master_image", ""),
                "cutout_image": master_entry.get("cutout_image", ""),
                "notes": master_entry.get("notes", ""),
                "style_seed_dir": style_seed_dir,
                "multiangle_dir": multiangle_dir,
                "style_seed_count": phase_override.get("style_seed_count"),
                "multiangle_count": phase_override.get("multiangle_count"),
                "variants": phase_override.get("variants", []),
            }
            actor_entry["phases"].append(phase_entry)

            base_lora_entry = {
                "id": base_id,
                "lora_type": "identity",
                "subject_id": phase_subject_id,
                "subject_type": "character",
                "subject_name": actor_name,
                "phase_name": phase_name,
                "phase_slug": phase_slug,
                "path": base_path,
            }
            style_lora_entry = {
                "id": style_id,
                "lora_type": "style",
                "subject_id": phase_subject_id,
                "subject_type": "character",
                "subject_name": actor_name,
                "phase_name": phase_name,
                "phase_slug": phase_slug,
                "path": style_path,
            }
            apply_lora_override(base_lora_entry, overrides)
            apply_lora_override(style_lora_entry, overrides)
            loras.extend([base_lora_entry, style_lora_entry])

            for variant in phase_entry.get("variants", []) or []:
                variant_name = variant.get("name") or ""
                variant_slug = slugify(variant_name)
                if not variant_slug:
                    continue
                variant_id = f"{actor_slug}__{phase_slug}__{variant_slug}"
                variant_filename = f"{variant_id}.safetensors"
                variant_path = build_lora_path(lora_root, "actors", actor_slug, phase_slug, variant_filename)
                variant_entry = {
                    "id": variant_id,
                    "lora_type": variant.get("lora_type") or variant_name,
                    "subject_id": phase_subject_id,
                    "subject_type": "character",
                    "subject_name": actor_name,
                    "phase_name": phase_name,
                    "phase_slug": phase_slug,
                    "path": variant_path,
                    "strength": variant.get("strength"),
                    "prompt_mode": variant.get("prompt_mode"),
                }
                apply_lora_override(variant_entry, overrides)
                loras.append(variant_entry)

        actors.append(actor_entry)

    props = []
    for item in prop_queue:
        if not isinstance(item, dict):
            continue
        if item.get("entity_type") != "prop":
            continue
        actor_name = item.get("entity_name") or ""
        prop_name = item.get("prop_name") or item.get("entity_name") or ""
        actor_slug = slugify(item.get("actor_slug") or actor_name)
        prop_slug = slugify(item.get("prop_slug") or prop_name)
        subject_id = resolve_subject_id(prop_name, "prop", profile_map)
        prop_id = f"prop__{prop_slug}__{actor_slug}__base"
        prop_filename = f"{prop_id}.safetensors"
        prop_path = build_lora_path(lora_root, "props", actor_slug, prop_slug, prop_filename)
        prop_entry = {
            "prop_name": prop_name,
            "prop_slug": prop_slug,
            "actor_name": actor_name,
            "actor_slug": actor_slug,
            "subject_id": subject_id,
            "lora": {
                "id": prop_id,
                "path": prop_path,
                "lora_type": "prop",
            },
            "training_image_dir": item.get("output_dir") or "",
        }
        props.append(prop_entry)
        lora_entry = {
            "id": prop_id,
            "lora_type": "prop",
            "subject_id": subject_id,
            "subject_type": "prop",
            "subject_name": prop_name,
            "phase_name": "",
            "phase_slug": "",
            "path": prop_path,
        }
        apply_lora_override(lora_entry, overrides)
        loras.append(lora_entry)

    set_envs = []
    for run in training_runs:
        output_path = run.get("output") if isinstance(run, dict) else ""
        if not output_path or "env__" not in output_path.lower():
            continue
        filename = Path(output_path).name
        env_slug = filename.split("env__", 1)[-1].split(".safetensors", 1)[0]
        env_id = f"set__{env_slug}__base"
        subject_id = resolve_subject_id(env_slug.replace("_", " "), "set_environment", profile_map)
        env_path = build_lora_path(lora_root, "set_envs", env_slug, "", f"{env_id}.safetensors")
        env_entry = {
            "env_slug": env_slug,
            "subject_id": subject_id,
            "lora": {
                "id": env_id,
                "path": env_path,
                "lora_type": "set_environment",
            },
        }
        set_envs.append(env_entry)
        lora_entry = {
            "id": env_id,
            "lora_type": "set_environment",
            "subject_id": subject_id,
            "subject_type": "set_environment",
            "subject_name": env_slug.replace("_", " ").title(),
            "phase_name": "",
            "phase_slug": "",
            "path": env_path,
        }
        apply_lora_override(lora_entry, overrides)
        loras.append(lora_entry)

    payload = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "timeline": timeline_folder,
        "lora_root": str(lora_root),
        "actors": actors,
        "props": props,
        "set_environments": set_envs,
        "loras": sorted(loras, key=lambda item: item.get("id") or ""),
    }

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"Wrote LoRA index: {output_path}")


if __name__ == "__main__":
    main()
