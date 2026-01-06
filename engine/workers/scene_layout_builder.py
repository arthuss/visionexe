import argparse
import json
import math
import re
from pathlib import Path

from visionexe_paths import ensure_dir, load_story_config, resolve_path


SHOT_PRESETS = {
    "extreme_close_up": {"lens_mm": 100, "distance_m": 0.35},
    "close_up": {"lens_mm": 85, "distance_m": 0.6},
    "medium_close_up": {"lens_mm": 70, "distance_m": 0.9},
    "medium": {"lens_mm": 50, "distance_m": 1.4},
    "wide": {"lens_mm": 35, "distance_m": 3.0},
    "full_body": {"lens_mm": 35, "distance_m": 3.0},
    "extreme_wide": {"lens_mm": 24, "distance_m": 8.0},
    "establishing": {"lens_mm": 24, "distance_m": 10.0},
}

DEFAULT_ANCHORS = [
    {"id": "CENTER", "label": "Center"},
    {"id": "LEFT", "label": "Left"},
    {"id": "RIGHT", "label": "Right"},
    {"id": "FOREGROUND", "label": "Foreground"},
    {"id": "BACKGROUND", "label": "Background"},
]


def slugify(value: str) -> str:
    value = value.strip().upper()
    value = re.sub(r"[^A-Z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value)
    return value.strip("_")


def normalize_name(value: str) -> str:
    return re.sub(r"\s+", " ", str(value).strip()).lower()


def load_jsonl(path: Path) -> list[dict]:
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


def load_profiles(path: Path) -> tuple[dict, dict]:
    profiles_by_id = {}
    profiles_by_name = {}
    for profile in load_jsonl(path):
        profile_id = profile.get("id")
        if profile_id:
            profiles_by_id[profile_id] = profile
        name = profile.get("name")
        if name:
            profiles_by_name[normalize_name(name)] = profile
        for alias in profile.get("aliases", []) or []:
            profiles_by_name[normalize_name(alias)] = profile
    return profiles_by_id, profiles_by_name


def pick_state(profile: dict, chapter, segment_label: str, scene_label: str):
    if not profile:
        return None
    states = profile.get("states") or []
    for state in states:
        if scene_label and scene_label in state.get("scene_labels", []):
            return state
    for state in states:
        if segment_label and segment_label in state.get("segment_labels", []):
            return state
    for state in states:
        start = state.get("chapter_start")
        end = state.get("chapter_end")
        if chapter is None or start is None or end is None:
            continue
        try:
            chapter_int = int(chapter)
        except (TypeError, ValueError):
            continue
        if int(start) <= chapter_int <= int(end):
            return state
    return states[0] if states else None


def parse_camera_hint(camera_text: str) -> dict:
    if not camera_text:
        return {}
    match = re.search(r"(\d{2,3})\s*mm", camera_text)
    payload = {}
    if match:
        payload["lens_mm"] = int(match.group(1))
    if "macro" in camera_text.lower():
        payload["distance_m"] = 0.3
    if any(word in camera_text.lower() for word in ["dolly", "pan", "tilt", "orbit"]):
        payload["mode"] = "moving"
    return payload


def camera_from_regie(regie: dict, primary_anchor_id: str) -> dict:
    shot_type = str(regie.get("shot_type") or "").strip()
    framing = str(regie.get("framing") or "").strip()
    camera_text = str(regie.get("camera") or "").strip()
    shot_key = normalize_name(framing or shot_type).replace(" ", "_")
    preset = SHOT_PRESETS.get(shot_key, {})
    camera = {
        "shot_type": shot_type or "",
        "framing": framing or "",
        "mode": "static",
        "lens_mm": preset.get("lens_mm", 50),
        "distance_m": preset.get("distance_m", 2.0),
        "height_m": 1.6,
        "target_anchor": normalize_anchor_id(primary_anchor_id, "center"),
    }
    camera.update(parse_camera_hint(camera_text))
    camera["camera_text"] = camera_text

    low_angle = "low" in shot_key or "low angle" in camera_text.lower()
    high_angle = "high" in shot_key or "high angle" in camera_text.lower()
    if low_angle:
        camera["height_m"] = 1.0
    if high_angle:
        camera["height_m"] = 2.2
    return camera


def anchor_position_for(anchor_id: str, index: int, total: int, radius: float):
    anchor_lower = anchor_id.lower()
    if "center" in anchor_lower:
        return {"x": 0.0, "y": 0.0, "z": 0.0}
    if "left" in anchor_lower:
        return {"x": -radius, "y": 0.0, "z": 0.0}
    if "right" in anchor_lower:
        return {"x": radius, "y": 0.0, "z": 0.0}
    if "foreground" in anchor_lower or "front" in anchor_lower:
        return {"x": 0.0, "y": -radius, "z": 0.0}
    if "background" in anchor_lower or "back" in anchor_lower:
        return {"x": 0.0, "y": radius, "z": 0.0}
    if total <= 0:
        return {"x": 0.0, "y": 0.0, "z": 0.0}
    angle = (2.0 * math.pi * index) / total
    return {"x": radius * math.cos(angle), "y": radius * math.sin(angle), "z": 0.0}


def normalize_anchor_id(value: str, fallback: str) -> str:
    if value:
        return slugify(value)
    return slugify(fallback)


def build_anchor_list(regie: dict, blocking: dict | None, radius: float):
    anchors = []
    anchor_map = {}

    for entry in regie.get("prop_placements", []) or []:
        anchor_id = normalize_anchor_id(entry.get("anchor"), "anchor")
        if anchor_id not in anchor_map:
            anchor = {"id": anchor_id, "label": entry.get("anchor", anchor_id), "source": "regie"}
            anchors.append(anchor)
            anchor_map[anchor_id] = anchor

    actor_block = regie.get("actor_block") or {}
    for key in ["anchor", "approach_target"]:
        anchor_id = normalize_anchor_id(actor_block.get(key), key)
        if anchor_id not in anchor_map and actor_block.get(key):
            anchor = {"id": anchor_id, "label": actor_block.get(key), "source": "regie"}
            anchors.append(anchor)
            anchor_map[anchor_id] = anchor

    if blocking:
        for idx, anchor in enumerate(blocking.get("anchors", []) or [], start=1):
            anchor_id = normalize_anchor_id(anchor.get("id") or anchor.get("description"), f"anchor_{idx:02d}")
            if anchor_id in anchor_map:
                continue
            label = anchor.get("id") or anchor.get("description") or anchor_id
            anchors.append({"id": anchor_id, "label": label, "source": "blocking", "description": anchor.get("description", "")})
            anchor_map[anchor_id] = anchors[-1]

    if not anchors:
        for anchor in DEFAULT_ANCHORS:
            anchor_id = normalize_anchor_id(anchor["id"], anchor["id"])
            anchors.append({"id": anchor_id, "label": anchor["label"], "source": "default"})
            anchor_map[anchor_id] = anchors[-1]

    for idx, anchor in enumerate(anchors):
        anchor["position"] = anchor_position_for(anchor["id"], idx, len(anchors), radius)

    return anchors, anchor_map


def normalize_actor_entry(actor) -> dict:
    if isinstance(actor, str):
        return {"name": actor}
    if isinstance(actor, dict):
        return actor
    return {}


def find_profile_for(name: str, profiles_by_id: dict, profiles_by_name: dict):
    if not name:
        return None
    profile = profiles_by_name.get(normalize_name(name))
    if profile:
        return profile
    subject_id = f"CHAR_{slugify(name)}"
    return profiles_by_id.get(subject_id)


def build_actor_entries(scene: dict, regie: dict, anchors: list, anchor_map: dict,
                        profiles_by_id: dict, profiles_by_name: dict):
    actors = []
    actor_entries = []
    for actor in regie.get("actors") or scene.get("actors") or []:
        normalized = normalize_actor_entry(actor)
        if normalized:
            actors.append(normalized)

    fallback_anchor_cycle = [a["id"] for a in anchors]
    fallback_index = 0

    for actor in actors:
        name = actor.get("name") or actor.get("id") or ""
        presence = actor.get("presence") or "on_screen"
        focus = actor.get("focus") or "secondary"
        phase = actor.get("phase") or ""
        anchor_id = actor.get("anchor") or ""
        if not anchor_id and focus == "primary":
            anchor_id = "center"
        if not anchor_id:
            anchor_id = fallback_anchor_cycle[fallback_index % len(fallback_anchor_cycle)]
            fallback_index += 1
        anchor_id = normalize_anchor_id(anchor_id, "center")
        if anchor_id not in anchor_map:
            anchor_map[anchor_id] = {"id": anchor_id, "label": anchor_id, "source": "auto", "position": anchor_position_for(anchor_id, len(anchor_map), len(anchor_map) + 1, 2.0)}
            anchors.append(anchor_map[anchor_id])

        profile = find_profile_for(name, profiles_by_id, profiles_by_name)
        state = pick_state(profile, scene.get("chapter"), scene.get("segment_label", ""), scene.get("scene_label", ""))
        actor_entries.append({
            "name": name,
            "subject_id": profile.get("id") if profile else "",
            "state_id": state.get("state_id") if state else "",
            "focus": focus,
            "presence": presence,
            "phase": phase,
            "anchor_id": anchor_id,
        })

    return actor_entries


def build_prop_entries(regie: dict, anchor_map: dict, anchors: list):
    props = []
    for prop in regie.get("props") or []:
        if isinstance(prop, str):
            props.append({"id": prop, "mode": "scene"})
        elif isinstance(prop, dict):
            props.append(prop)

    for entry in regie.get("prop_placements", []) or []:
        props.append(entry)

    prop_entries = []
    for prop in props:
        prop_id = prop.get("id") or prop.get("name") or prop.get("prop") or ""
        anchor_id = normalize_anchor_id(prop.get("anchor") or "center", "center")
        if anchor_id not in anchor_map:
            anchor_map[anchor_id] = {"id": anchor_id, "label": anchor_id, "source": "auto", "position": anchor_position_for(anchor_id, len(anchor_map), len(anchor_map) + 1, 2.0)}
            anchors.append(anchor_map[anchor_id])
        prop_entries.append({
            "id": prop_id,
            "mode": prop.get("mode") or "scene",
            "anchor_id": anchor_id,
            "offset": prop.get("offset") or [0.0, 0.0],
            "scale": prop.get("scale", 1.0),
            "attached_to": prop.get("attached_to") or "",
            "socket": prop.get("socket") or "",
        })
    return prop_entries


def build_paths(blocking: dict | None, anchor_map: dict, anchors: list):
    paths_out = []
    if not blocking:
        return paths_out
    for path in blocking.get("paths", []) or []:
        if not isinstance(path, dict):
            continue
        start_anchor = normalize_anchor_id(path.get("start_anchor"), "start")
        end_anchor = normalize_anchor_id(path.get("end_anchor"), "end")
        for anchor_id in (start_anchor, end_anchor):
            if anchor_id not in anchor_map:
                anchor_map[anchor_id] = {"id": anchor_id, "label": anchor_id, "source": "blocking", "position": anchor_position_for(anchor_id, len(anchor_map), len(anchor_map) + 1, 2.0)}
                anchors.append(anchor_map[anchor_id])
        paths_out.append({
            "actor": path.get("actor", ""),
            "start_anchor": start_anchor,
            "end_anchor": end_anchor,
            "motion": path.get("motion") or "unknown",
            "duration_sec": path.get("duration_sec"),
            "notes": path.get("notes") or "",
        })
    return paths_out


def extract_regie_subset(regie: dict) -> dict:
    if not isinstance(regie, dict):
        return {}
    keep = ["shot_type", "framing", "camera", "mood", "director_intent", "start_image_mode", "start_image_keywords", "voice_words_max"]
    return {key: regie.get(key) for key in keep if key in regie}


def build_blocking_index(records: list[dict]) -> dict:
    index = {}
    for record in records:
        chapter = record.get("chapter")
        segment_label = record.get("segment_label")
        if not segment_label:
            continue
        for block in record.get("analysis_blocks", []) or []:
            if not isinstance(block, dict):
                continue
            blocking = block.get("blocking")
            if not isinstance(blocking, dict):
                continue
            key = (chapter, segment_label)
            payload = index.setdefault(key, {"anchors": [], "paths": []})
            payload["anchors"].extend(blocking.get("anchors", []) or [])
            payload["paths"].extend(blocking.get("paths", []) or [])
    return index


def default_timeline_id(story_config: dict) -> str:
    label = story_config.get("timeline_label", "timeline")
    padding = int(story_config.get("timeline_index_padding", 2))
    return f"{label}_{1:0{padding}d}"


def main():
    parser = argparse.ArgumentParser(description="Build scene layout plans from scene instructions + analysis.")
    parser.add_argument("--story-root", help="Story root path (defaults to engine_config default_story_root).")
    parser.add_argument("--story-config", help="Path to story_config.json (overrides story-root).")
    parser.add_argument("--scene-instructions", help="Override scene_instructions.jsonl path.")
    parser.add_argument("--analysis-master", help="Override analysis_master.jsonl path.")
    parser.add_argument("--profiles", help="Override profiles.jsonl path.")
    parser.add_argument("--output", help="Output scene layout JSONL path.")
    parser.add_argument("--timeline", help="Timeline id (default timeline_01).")
    parser.add_argument("--radius", type=float, default=2.0, help="Default anchor radius in meters.")
    args = parser.parse_args()

    story_config, _, repo_root = load_story_config(
        story_root=args.story_root,
        story_config_path=args.story_config,
    )

    subjects_root = resolve_path(story_config.get("subjects_root"), repo_root)
    ensure_dir(subjects_root)

    scene_instructions_path = resolve_path(args.scene_instructions or story_config.get("scene_instructions_path"), repo_root)
    if not scene_instructions_path or not scene_instructions_path.exists():
        raise SystemExit("scene_instructions_path is missing.")

    analysis_master_path = resolve_path(args.analysis_master or story_config.get("analysis_master_path"), repo_root)
    if not analysis_master_path or not analysis_master_path.exists():
        raise SystemExit("analysis_master_path is missing.")

    profiles_path = resolve_path(args.profiles or f"{subjects_root}/profiles.jsonl", repo_root)
    profiles_by_id, profiles_by_name = load_profiles(profiles_path)

    timeline_id = args.timeline or default_timeline_id(story_config)
    if args.output:
        output_path = resolve_path(args.output, repo_root)
    elif args.timeline or not story_config.get("scene_layout_path"):
        output_path = resolve_path(f"{subjects_root}/timelines/{timeline_id}/scene_layout.jsonl", repo_root)
    else:
        output_path = resolve_path(story_config.get("scene_layout_path"), repo_root)
    ensure_dir(output_path.parent)

    analysis_records = load_jsonl(analysis_master_path)
    blocking_index = build_blocking_index(analysis_records)

    scene_records = [r for r in load_jsonl(scene_instructions_path) if r.get("record_type") == "scene"]

    layouts = []
    for scene in scene_records:
        regie = scene.get("regie") or {}
        blocking = blocking_index.get((scene.get("chapter"), scene.get("segment_label")))
        anchors, anchor_map = build_anchor_list(regie, blocking, args.radius)
        actor_entries = build_actor_entries(scene, regie, anchors, anchor_map, profiles_by_id, profiles_by_name)
        prop_entries = build_prop_entries(regie, anchor_map, anchors)
        paths = build_paths(blocking, anchor_map, anchors)

        primary_anchor = normalize_anchor_id("center", "center")
        if actor_entries:
            primary = next((actor for actor in actor_entries if actor.get("focus") == "primary"), actor_entries[0])
            if primary.get("anchor_id"):
                primary_anchor = primary["anchor_id"]

        layout = {
            "scene_id": scene.get("scene_id"),
            "timeline_id": timeline_id,
            "chapter": scene.get("chapter"),
            "act": scene.get("act"),
            "scene_number": scene.get("scene_number"),
            "segment_label": scene.get("segment_label"),
            "scene_label": scene.get("scene_label"),
            "title": scene.get("title"),
            "environment": scene.get("environment"),
            "anchors": anchors,
            "actors": actor_entries,
            "props": prop_entries,
            "paths": paths,
            "camera_plan": camera_from_regie(regie, primary_anchor),
            "regie": extract_regie_subset(regie),
            "source_path": scene.get("source_path"),
        }
        layouts.append(layout)

    with output_path.open("w", encoding="utf-8") as handle:
        for layout in layouts:
            handle.write(json.dumps(layout, ensure_ascii=False) + "\n")

    print(f"Wrote scene layout: {output_path} ({len(layouts)} scenes)")


if __name__ == "__main__":
    main()
