import argparse
import json
import time
from pathlib import Path

from visionexe_paths import load_story_config, resolve_path


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


def main():
    parser = argparse.ArgumentParser(description="Build asset_bible.json from subjects registry files.")
    parser.add_argument("--story-root", help="Story root path (defaults to engine_config default_story_root).")
    parser.add_argument("--story-config", help="Path to story_config.json (overrides story-root).")
    parser.add_argument("--profiles", help="Path to profiles.jsonl.")
    parser.add_argument("--occurrences", help="Path to occurrences.jsonl.")
    parser.add_argument("--output", help="Output asset_bible.json path.")
    parser.add_argument("--max-occurrences", type=int, default=200, help="Max occurrences to include per subject.")
    args = parser.parse_args()

    story_config, _, repo_root = load_story_config(
        story_root=args.story_root,
        story_config_path=args.story_config,
    )

    subjects_root = resolve_path(story_config.get("subjects_root"), repo_root)
    profiles_path = resolve_path(args.profiles or f"{subjects_root}/profiles.jsonl", repo_root)
    occurrences_path = resolve_path(args.occurrences or f"{subjects_root}/occurrences.jsonl", repo_root)
    output_path = resolve_path(args.output or f"{subjects_root}/asset_bible.json", repo_root)

    profiles = load_jsonl(profiles_path)
    occurrences = load_jsonl(occurrences_path)

    occurrence_map = {}
    for occ in occurrences:
        subject_id = occ.get("subject_id")
        if not subject_id:
            continue
        occurrence_map.setdefault(subject_id, []).append({
            "chapter": occ.get("chapter"),
            "segment_label": occ.get("segment_label"),
            "scene_label": occ.get("scene_label"),
            "source_id": occ.get("source_id"),
            "source_path": occ.get("source_path"),
        })

    payload = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "story_id": story_config.get("story_id"),
        "subjects": [],
    }

    for profile in profiles:
        subject_id = profile.get("id")
        occs = occurrence_map.get(subject_id, [])
        payload["subjects"].append({
            "id": subject_id,
            "name": profile.get("name"),
            "type": profile.get("type"),
            "aliases": profile.get("aliases") or [],
            "roles": profile.get("roles") or [],
            "visual_traits": profile.get("visual_traits") or [],
            "changes": profile.get("changes") or [],
            "notes": profile.get("notes") or [],
            "sources": profile.get("sources") or [],
            "occurrence_count": profile.get("occurrence_count", len(occs)),
            "is_dynamic": profile.get("is_dynamic", False),
            "state_policy": profile.get("state_policy"),
            "states": profile.get("states") or [],
            "occurrences_sample": occs[: args.max_occurrences],
        })

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"Wrote asset bible: {output_path}")


if __name__ == "__main__":
    main()
