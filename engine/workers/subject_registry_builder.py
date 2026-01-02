import argparse
import json
import re
from pathlib import Path

from visionexe_paths import ensure_dir, load_story_config, resolve_path


JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*([\[{].*?[\]}])\s*```", re.DOTALL | re.IGNORECASE)

TYPE_PREFIX = {
    "character": "CHAR",
    "prop": "PROP",
    "environment": "ENV",
    "set_environment": "SETENV",
    "geo_environment": "GEOENV",
    "scene": "SCENE",
    "location": "LOC",
}

DYNAMIC_POLICIES = {"per_segment", "per_scene", "per_occurrence"}


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


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


def extract_json_blocks(text):
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


def slugify(value: str) -> str:
    value = value.strip().upper()
    value = re.sub(r"[^A-Z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value)
    return value.strip("_")


def normalize_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    return [str(value).strip()] if str(value).strip() else []


def extract_name(item, fields):
    if isinstance(item, str):
        return item.strip()
    if not isinstance(item, dict):
        return None
    for field in fields:
        if field in item and item[field]:
            return str(item[field]).strip()
    return None


def add_subject(subjects, subject_id, name, subject_type):
    subject = subjects.get(subject_id)
    if not subject:
        subject = {
            "id": subject_id,
            "name": name,
            "type": subject_type,
            "aliases": set(),
            "roles": set(),
            "visual_traits": set(),
            "changes": set(),
            "notes": set(),
            "sources": set(),
            "first_chapter": None,
            "last_chapter": None,
            "occurrence_count": 0,
            "state_policy": None,
            "seed_states": None,
            "dynamic_override": None,
        }
        subjects[subject_id] = subject
    if name:
        subject["aliases"].add(name)
    return subject


def update_chapter_range(subject, chapter_value):
    if chapter_value in ("", None):
        return
    try:
        chapter_int = int(chapter_value)
    except (ValueError, TypeError):
        return
    if subject["first_chapter"] is None or chapter_int < subject["first_chapter"]:
        subject["first_chapter"] = chapter_int
    if subject["last_chapter"] is None or chapter_int > subject["last_chapter"]:
        subject["last_chapter"] = chapter_int


def build_subject_id(subject_type, name):
    prefix = TYPE_PREFIX.get(subject_type, "SUB")
    return f"{prefix}_{slugify(name)}"


def main():
    parser = argparse.ArgumentParser(description="Build subject registry + profiles from analysis_master.jsonl.")
    parser.add_argument("--story-root", help="Story root path (defaults to engine_config default_story_root).")
    parser.add_argument("--story-config", help="Path to story_config.json (overrides story-root).")
    parser.add_argument("--analysis-master", help="Path to analysis_master.jsonl.")
    parser.add_argument("--keymap", help="Subjects keymap JSON path.")
    parser.add_argument("--seed", help="Optional seed profiles JSON.")
    parser.add_argument("--registry-out", help="Output registry.json path.")
    parser.add_argument("--profiles-out", help="Output profiles.jsonl path.")
    parser.add_argument("--occurrences-out", help="Output occurrences.jsonl path.")
    parser.add_argument("--scenes-out", help="Output scenes.jsonl path.")
    parser.add_argument("--dynamic-out", help="Output dynamic_subjects.json path.")
    parser.add_argument("--env-route-out", help="Output environment_route.jsonl path.")
    args = parser.parse_args()

    story_config, story_root, repo_root = load_story_config(
        story_root=args.story_root,
        story_config_path=args.story_config,
    )

    analysis_master_path = args.analysis_master or story_config.get("analysis_master_path")
    if not analysis_master_path:
        raise SystemExit("analysis_master_path is missing.")
    analysis_master_path = resolve_path(analysis_master_path, repo_root)

    default_dynamic_policy = story_config.get("dynamic_state_policy_default", "per_segment")

    keymap_path = args.keymap or "engine/config/subjects_keymap.json"
    keymap_path = resolve_path(keymap_path, repo_root)
    keymap = load_json(keymap_path)

    subjects_root = resolve_path(story_config.get("subjects_root"), repo_root)
    ensure_dir(subjects_root)

    registry_out = resolve_path(args.registry_out or f"{subjects_root}/registry.json", repo_root)
    profiles_out = resolve_path(args.profiles_out or f"{subjects_root}/profiles.jsonl", repo_root)
    occurrences_out = resolve_path(args.occurrences_out or f"{subjects_root}/occurrences.jsonl", repo_root)
    scenes_out = resolve_path(args.scenes_out or f"{subjects_root}/scenes.jsonl", repo_root)
    dynamic_out = resolve_path(args.dynamic_out or f"{subjects_root}/dynamic_subjects.json", repo_root)
    env_route_out = resolve_path(args.env_route_out or f"{subjects_root}/environment_route.jsonl", repo_root)

    seed_path = args.seed or f"{subjects_root}/profiles_seed.json"
    seed_path = resolve_path(seed_path, repo_root)

    subjects = {}
    occurrences = []
    occurrence_map = {}
    change_by_segment = {}
    change_by_scene = {}
    scenes = []
    env_route = []

    if seed_path.exists():
        seed_profiles = load_json(seed_path)
        for profile in seed_profiles:
            name = profile.get("name") or profile.get("label") or profile.get("id")
            subject_type = profile.get("type", "subject")
            if not name:
                continue
            subject_id = profile.get("id") or build_subject_id(subject_type, name)
            subject = add_subject(subjects, subject_id, name, subject_type)
            if "is_dynamic" in profile:
                subject["dynamic_override"] = bool(profile.get("is_dynamic"))
            elif "dynamic" in profile:
                subject["dynamic_override"] = bool(profile.get("dynamic"))
            if profile.get("state_policy"):
                subject["state_policy"] = str(profile.get("state_policy"))
            if profile.get("states"):
                subject["seed_states"] = profile.get("states")
            for field in ["roles", "visual_traits", "changes", "notes"]:
                values = normalize_list(profile.get(field))
                subject[field].update(values)

    records = load_jsonl(analysis_master_path)
    for record in records:
        blocks = record.get("analysis_blocks") or []
        if not blocks and record.get("raw_content"):
            blocks = extract_json_blocks(record.get("raw_content", ""))

        for block in blocks:
            if not isinstance(block, dict):
                continue
            if "scenes" in block:
                scene_items = block.get("scenes")
                if isinstance(scene_items, dict):
                    scene_items = [scene_items]
                if isinstance(scene_items, list):
                    for idx, scene in enumerate(scene_items, start=1):
                        if not isinstance(scene, dict):
                            continue
                        scene_id = f"SCENE_{record.get('chapter')}_{record.get('segment_label')}_{idx:02d}"
                        scene_record = {
                            "scene_id": scene_id,
                            "title": scene.get("title", ""),
                            "location": scene.get("location", ""),
                            "action": scene.get("action", []),
                            "actors_involved": scene.get("actorsInvolved", []),
                            "chapter": record.get("chapter"),
                            "segment_label": record.get("segment_label"),
                            "segment_type": record.get("segment_type"),
                            "source_id": record.get("source_id"),
                            "source_path": record.get("source_path", ""),
                        }
                        scenes.append(scene_record)
                        location = scene_record.get("location")
                        if location:
                            env_route.append({
                                "sequence": len(env_route) + 1,
                                "chapter": record.get("chapter"),
                                "segment_label": record.get("segment_label"),
                                "scene_id": scene_id,
                                "location": location,
                            })
            for key, items in block.items():
                mapping = keymap.get(str(key).lower())
                if not mapping:
                    continue
                subject_type = mapping.get("type", "subject")
                name_fields = mapping.get("name_fields", [])
                role_fields = mapping.get("role_fields", [])
                visual_fields = mapping.get("visual_fields", [])
                change_fields = mapping.get("change_fields", [])
                location_fields = mapping.get("location_fields", [])
                create_location_subjects = bool(mapping.get("create_location_subjects"))
                location_subject_type = mapping.get("location_subject_type") or subject_type

                if isinstance(items, dict):
                    items = [items]
                if not isinstance(items, list):
                    continue

                for item in items:
                    name = extract_name(item, name_fields)
                    if name:
                        subject_id = build_subject_id(subject_type, name)
                        subject = add_subject(subjects, subject_id, name, subject_type)
                        for field_name in role_fields:
                            if isinstance(item, dict) and item.get(field_name):
                                subject["roles"].update(normalize_list(item.get(field_name)))
                        for field_name in visual_fields:
                            if isinstance(item, dict) and item.get(field_name):
                                subject["visual_traits"].update(normalize_list(item.get(field_name)))
                        for field_name in change_fields:
                            if isinstance(item, dict) and item.get(field_name):
                                change_values = normalize_list(item.get(field_name))
                                if change_values:
                                    subject["changes"].update(change_values)
                                    segment_label = record.get("segment_label")
                                    scene_label = record.get("scene_label") or ""
                                    if segment_label:
                                        change_by_segment.setdefault(subject_id, {}).setdefault(segment_label, set()).update(change_values)
                                    if scene_label:
                                        change_by_scene.setdefault(subject_id, {}).setdefault(scene_label, set()).update(change_values)

                        subject["sources"].add(record.get("source_id"))
                        update_chapter_range(subject, record.get("chapter"))
                        subject["occurrence_count"] += 1

                        occurrence = {
                            "subject_id": subject_id,
                            "source_id": record.get("source_id"),
                            "chapter": record.get("chapter"),
                            "segment_label": record.get("segment_label"),
                            "segment_type": record.get("segment_type"),
                            "scene_label": record.get("scene_label", ""),
                            "source_path": record.get("source_path", ""),
                        }
                        occurrences.append(occurrence)
                        occurrence_map.setdefault(subject_id, []).append(occurrence)

                    if create_location_subjects and location_fields:
                        location_name = extract_name(item, location_fields)
                        if location_name:
                            env_id = build_subject_id(location_subject_type, location_name)
                            env_subject = add_subject(subjects, env_id, location_name, location_subject_type)
                            env_subject["sources"].add(record.get("source_id"))
                            update_chapter_range(env_subject, record.get("chapter"))
                            env_subject["occurrence_count"] += 1
                            occurrence = {
                                "subject_id": env_id,
                                "source_id": record.get("source_id"),
                                "chapter": record.get("chapter"),
                                "segment_label": record.get("segment_label"),
                                "segment_type": record.get("segment_type"),
                                "scene_label": record.get("scene_label", ""),
                                "source_path": record.get("source_path", ""),
                            }
                            occurrences.append(occurrence)
                            occurrence_map.setdefault(env_id, []).append(occurrence)

    registry = []
    profiles = []
    dynamic_registry = []
    for subject_id, subject in sorted(subjects.items(), key=lambda x: x[0]):
        state_policy = subject.get("state_policy")
        dynamic_override = subject.get("dynamic_override")
        is_dynamic = bool(subject["changes"])
        if dynamic_override is True:
            is_dynamic = True
        if dynamic_override is False:
            is_dynamic = False

        if state_policy is None:
            state_policy = default_dynamic_policy if is_dynamic else "static"
        if state_policy in DYNAMIC_POLICIES:
            is_dynamic = True

        registry.append({
            "id": subject_id,
            "name": subject["name"],
            "type": subject["type"],
            "occurrence_count": subject["occurrence_count"],
            "first_chapter": subject["first_chapter"],
            "last_chapter": subject["last_chapter"],
            "is_dynamic": is_dynamic,
        })

        chapter_start = subject["first_chapter"]
        chapter_end = subject["last_chapter"]
        states = []
        if subject.get("seed_states"):
            states = subject.get("seed_states")
        elif state_policy in DYNAMIC_POLICIES:
            subject_occurrences = occurrence_map.get(subject_id, [])
            grouped = {}
            if state_policy == "per_occurrence":
                for occ in subject_occurrences:
                    key = (occ.get("source_id") or "",)
                    grouped[key] = {
                        "chapters": {occ.get("chapter")},
                        "segment_labels": {occ.get("segment_label")},
                        "scene_labels": {occ.get("scene_label")},
                        "source_ids": {occ.get("source_id")},
                    }
            elif state_policy == "per_scene":
                for occ in subject_occurrences:
                    chapter = occ.get("chapter")
                    segment_label = occ.get("segment_label") or ""
                    scene_label = occ.get("scene_label") or "scene_000"
                    key = (chapter, segment_label, scene_label)
                    group = grouped.setdefault(key, {
                        "chapters": set(),
                        "segment_labels": set(),
                        "scene_labels": set(),
                        "source_ids": set(),
                    })
                    group["chapters"].add(chapter)
                    group["segment_labels"].add(segment_label)
                    group["scene_labels"].add(scene_label)
                    group["source_ids"].add(occ.get("source_id"))
            else:
                for occ in subject_occurrences:
                    chapter = occ.get("chapter")
                    segment_label = occ.get("segment_label") or ""
                    key = (chapter, segment_label)
                    group = grouped.setdefault(key, {
                        "chapters": set(),
                        "segment_labels": set(),
                        "scene_labels": set(),
                        "source_ids": set(),
                    })
                    group["chapters"].add(chapter)
                    group["segment_labels"].add(segment_label)
                    group["scene_labels"].add(occ.get("scene_label"))
                    group["source_ids"].add(occ.get("source_id"))

            for key, data in sorted(grouped.items(), key=lambda x: str(x[0])):
                if state_policy == "per_occurrence":
                    source_id = key[0] or "source"
                    state_id = f"occ_{slugify(source_id)}"
                    label = f"Occurrence {source_id}"
                elif state_policy == "per_scene":
                    chapter, segment_label, scene_label = key
                    chapter_label = f"{int(chapter):03d}" if str(chapter).isdigit() else slugify(str(chapter or "NA"))
                    state_id = f"scene_ch{chapter_label}_{segment_label}_{scene_label}"
                    label = f"Chapter {chapter_label} {segment_label} {scene_label}"
                else:
                    chapter, segment_label = key
                    chapter_label = f"{int(chapter):03d}" if str(chapter).isdigit() else slugify(str(chapter or "NA"))
                    state_id = f"seg_ch{chapter_label}_{segment_label}"
                    label = f"Chapter {chapter_label} {segment_label}"

                segment_labels = sorted({seg for seg in data.get("segment_labels") if seg})
                scene_labels = sorted({scene for scene in data.get("scene_labels") if scene})
                notes = set()
                for seg in segment_labels:
                    notes.update(change_by_segment.get(subject_id, {}).get(seg, set()))
                for scene in scene_labels:
                    notes.update(change_by_scene.get(subject_id, {}).get(scene, set()))

                states.append({
                    "state_id": state_id,
                    "label": label.strip(),
                    "chapter_start": chapter_start,
                    "chapter_end": chapter_end,
                    "segment_labels": segment_labels,
                    "scene_labels": scene_labels,
                    "source_ids": sorted({sid for sid in data.get("source_ids") if sid}),
                    "notes": sorted(notes),
                })
        else:
            states = [
                {
                    "state_id": "default",
                    "label": "Default",
                    "chapter_start": chapter_start,
                    "chapter_end": chapter_end,
                    "segment_labels": [],
                    "scene_labels": [],
                    "source_ids": [],
                    "notes": [],
                }
            ]
            for idx, change in enumerate(sorted(subject["changes"]), start=1):
                states.append({
                    "state_id": f"change_{idx:02d}",
                    "label": change,
                    "chapter_start": chapter_start,
                    "chapter_end": chapter_end,
                    "segment_labels": [],
                    "scene_labels": [],
                    "source_ids": [],
                    "notes": [],
                })

        if not states:
            states = [
                {
                    "state_id": "default",
                    "label": "Default",
                    "chapter_start": chapter_start,
                    "chapter_end": chapter_end,
                    "segment_labels": [],
                    "scene_labels": [],
                    "source_ids": [],
                    "notes": [],
                }
            ]
        profile = {
            "id": subject_id,
            "name": subject["name"],
            "type": subject["type"],
            "aliases": sorted(subject["aliases"]),
            "roles": sorted(subject["roles"]),
            "visual_traits": sorted(subject["visual_traits"]),
            "changes": sorted(subject["changes"]),
            "notes": sorted(subject["notes"]),
            "sources": sorted(subject["sources"]),
            "occurrence_count": subject["occurrence_count"],
            "is_dynamic": is_dynamic,
            "state_policy": state_policy,
            "states": states,
        }
        profiles.append(profile)
        if is_dynamic:
            dynamic_registry.append(registry[-1])

    ensure_dir(registry_out.parent)
    with registry_out.open("w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)

    with profiles_out.open("w", encoding="utf-8") as f:
        for profile in profiles:
            f.write(json.dumps(profile, ensure_ascii=False) + "\n")

    with occurrences_out.open("w", encoding="utf-8") as f:
        for item in occurrences:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    with scenes_out.open("w", encoding="utf-8") as f:
        for scene in scenes:
            f.write(json.dumps(scene, ensure_ascii=False) + "\n")

    with env_route_out.open("w", encoding="utf-8") as f:
        for entry in env_route:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    with dynamic_out.open("w", encoding="utf-8") as f:
        json.dump({"subjects": dynamic_registry}, f, ensure_ascii=False, indent=2)

    print(f"Wrote registry: {registry_out}")
    print(f"Wrote profiles: {profiles_out}")
    print(f"Wrote occurrences: {occurrences_out}")
    print(f"Wrote scenes: {scenes_out}")
    print(f"Wrote environment route: {env_route_out}")
    print(f"Wrote dynamic subjects: {dynamic_out}")


if __name__ == "__main__":
    main()
