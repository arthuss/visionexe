import argparse
import json
import time
from pathlib import Path

from visionexe_paths import load_story_config, resolve_path


def load_json(path: Path):
    if not path or not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def normalize_timeline_tag(value: str, padding: int) -> str:
    if not value:
        return f"{1:0{padding}d}"
    raw = str(value).strip().lower()
    if raw.startswith("r") and raw[1:].isdigit():
        return f"{int(raw[1:]):0{padding}d}"
    if raw.isdigit():
        return f"{int(raw):0{padding}d}"
    digits = "".join(ch for ch in raw if ch.isdigit())
    if digits:
        return f"{int(digits):0{padding}d}"
    return f"{1:0{padding}d}"


def build_task_id(stage, subject_slug, phase_slug):
    return f"{stage}__{subject_slug}__{phase_slug}"


def main():
    parser = argparse.ArgumentParser(description="Build LoRA pipeline tasks from lora_index.json.")
    parser.add_argument("--story-root", help="Story root path (defaults to engine_config default_story_root).")
    parser.add_argument("--story-config", help="Path to story_config.json (overrides story-root).")
    parser.add_argument("--lora-index", help="Path to lora_index.json.")
    parser.add_argument("--timeline", help="Timeline tag (e.g., 1 or r01).")
    parser.add_argument("--output", help="Output JSONL path.")
    args = parser.parse_args()

    story_config, _, repo_root = load_story_config(
        story_root=args.story_root,
        story_config_path=args.story_config,
    )

    lora_index_path = resolve_path(args.lora_index or story_config.get("lora_index_path", ""), repo_root)
    if not lora_index_path:
        raise SystemExit("No lora_index_path configured.")
    lora_index = load_json(lora_index_path) or {}

    timeline_label = story_config.get("timeline_label", "timeline")
    timeline_padding = int(story_config.get("timeline_index_padding", 2))
    timeline_tag = normalize_timeline_tag(args.timeline, timeline_padding)
    timeline_folder = f"{timeline_label}_{timeline_tag}"

    lora_training_root = resolve_path(story_config.get("lora_training_root"), repo_root)
    lora_training_root = Path(lora_training_root) / timeline_folder

    output_path = resolve_path(args.output or story_config.get("lora_pipeline_path", ""), repo_root)
    if not output_path:
        raise SystemExit("No lora_pipeline_path configured.")

    style_seed_count_default = int(story_config.get("lora_style_seed_count", 20))
    multiangle_count_default = int(story_config.get("lora_multiangle_count", 40))
    style_seed_workflow = story_config.get("lora_style_seed_workflow", "")
    multiangle_workflow = story_config.get("lora_multiangle_workflow", "")
    base_train_workflow = story_config.get("lora_base_train_workflow", "")

    tasks = []
    actors = lora_index.get("actors", [])
    for actor in actors:
        actor_name = actor.get("actor_name") or ""
        actor_slug = actor.get("actor_slug") or ""
        trigger = actor.get("trigger") or ""
        for phase in actor.get("phases", []):
            phase_name = phase.get("phase_name") or ""
            phase_slug = phase.get("phase_slug") or ""
            subject_id = phase.get("subject_id") or actor.get("subject_id") or ""
            base_lora = phase.get("base_lora") or {}
            style_lora = phase.get("style_lora") or {}
            style_seed_count = phase.get("style_seed_count") or style_seed_count_default
            multiangle_count = phase.get("multiangle_count") or multiangle_count_default

            style_seed_dir = lora_training_root / "actors" / actor_slug / phase_slug / "style_seed"
            multiangle_dir = lora_training_root / "actors" / actor_slug / phase_slug / "multiangle"

            prompt_seed = {
                "trigger": trigger,
                "actor": actor_name,
                "phase": phase_name,
                "description": phase.get("description") or "",
                "keywords": phase.get("keywords") or [],
                "props": phase.get("props") or actor.get("props") or [],
            }

            style_seed_id = build_task_id("style_seed", actor_slug, phase_slug)
            tasks.append({
                "task_id": style_seed_id,
                "stage": "style_seed",
                "timeline": timeline_folder,
                "subject_id": subject_id,
                "subject_name": actor_name,
                "subject_type": "character",
                "phase_name": phase_name,
                "phase_slug": phase_slug,
                "image_count": style_seed_count,
                "output_dir": str(style_seed_dir),
                "workflow": style_seed_workflow,
                "prompt_seed": prompt_seed,
            })

            style_train_id = build_task_id("style_train", actor_slug, phase_slug)
            tasks.append({
                "task_id": style_train_id,
                "stage": "style_train",
                "timeline": timeline_folder,
                "subject_id": subject_id,
                "subject_name": actor_name,
                "subject_type": "character",
                "phase_name": phase_name,
                "phase_slug": phase_slug,
                "input_dir": str(style_seed_dir),
                "lora_output": style_lora.get("path") or "",
                "workflow": style_seed_workflow,
                "depends_on": [style_seed_id],
            })

            multiangle_id = build_task_id("multiangle_gen", actor_slug, phase_slug)
            tasks.append({
                "task_id": multiangle_id,
                "stage": "multiangle_gen",
                "timeline": timeline_folder,
                "subject_id": subject_id,
                "subject_name": actor_name,
                "subject_type": "character",
                "phase_name": phase_name,
                "phase_slug": phase_slug,
                "image_count": multiangle_count,
                "output_dir": str(multiangle_dir),
                "workflow": multiangle_workflow,
                "lora_input": style_lora.get("path") or "",
                "prompt_seed": prompt_seed,
                "depends_on": [style_train_id],
            })

            base_train_id = build_task_id("base_train", actor_slug, phase_slug)
            tasks.append({
                "task_id": base_train_id,
                "stage": "base_train",
                "timeline": timeline_folder,
                "subject_id": subject_id,
                "subject_name": actor_name,
                "subject_type": "character",
                "phase_name": phase_name,
                "phase_slug": phase_slug,
                "input_dir": str(multiangle_dir),
                "lora_output": base_lora.get("path") or "",
                "workflow": base_train_workflow,
                "depends_on": [multiangle_id],
            })

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for task in tasks:
            f.write(json.dumps(task, ensure_ascii=False) + "\n")

    print(f"Wrote LoRA pipeline tasks: {output_path} ({len(tasks)} tasks)")


if __name__ == "__main__":
    main()
