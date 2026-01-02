import argparse
import json
import os
import re


def parse_args():
    parser = argparse.ArgumentParser(
        description="Harvest existing analysis_llm.txt JSON into master actor/scene DBs."
    )
    default_root = os.path.abspath(os.path.dirname(__file__))
    parser.add_argument("--root", default=default_root, help="Project root path.")
    parser.add_argument(
        "--filmsets",
        default=None,
        help="Filmsets path (defaults to <root>/filmsets).",
    )
    parser.add_argument(
        "--actors-out",
        default=None,
        help="Output path for ACTOR_MASTER_DB.json.",
    )
    parser.add_argument(
        "--scenes-out",
        default=None,
        help="Output path for SCENE_MASTER_DB.json.",
    )
    parser.add_argument(
        "--stats-out",
        default=None,
        help="Output path for HARVEST_STATS.json.",
    )
    parser.add_argument(
        "--log-out",
        default=None,
        help="Output path for HARVEST_LOG.json.",
    )
    parser.add_argument(
        "--include-type",
        action="append",
        default=[],
        help="Include only these source types (comma-separated or repeat).",
    )
    parser.add_argument(
        "--exclude-type",
        action="append",
        default=[],
        help="Exclude these source types (comma-separated or repeat).",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=0,
        help="Limit number of files for a quick test run.",
    )
    parser.add_argument(
        "--keep-raw",
        action="store_true",
        help="Store raw actor/scene payloads in output.",
    )
    parser.add_argument(
        "--name-map",
        default=None,
        help="Optional JSON file with name normalization mapping.",
    )
    return parser.parse_args()


def split_types(values):
    types = []
    for v in values or []:
        types.extend([t.strip() for t in v.split(",") if t.strip()])
    return types


def type_matches(type_name, patterns):
    for p in patterns:
        if type_name == p or type_name.startswith(p):
            return True
    return False


def extract_chapter_and_type(path):
    match = re.search(r"chapter_(\d+)[\\/]+([^\\/]+)", path)
    if not match:
        return None, None
    return int(match.group(1)), match.group(2)


def find_balanced_json(text, start_idx):
    depth = 0
    in_string = False
    escape = False
    for i in range(start_idx, len(text)):
        c = text[i]
        if in_string:
            if escape:
                escape = False
            elif c == "\\":
                escape = True
            elif c == "\"":
                in_string = False
            continue
        if c == "\"":
            in_string = True
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i
    return None


def extract_json_block(text):
    fenced = re.search(r"```json\s*({.*?})\s*```", text, re.DOTALL)
    if fenced:
        return fenced.group(1)
    fenced = re.search(r"```\s*({.*?})\s*```", text, re.DOTALL)
    if fenced:
        return fenced.group(1)

    for i, ch in enumerate(text):
        if ch != "{":
            continue
        end_idx = find_balanced_json(text, i)
        if end_idx is None:
            continue
        candidate = text[i : end_idx + 1]
        try:
            json.loads(candidate)
            return candidate
        except json.JSONDecodeError:
            continue
    return None


def load_name_map(path):
    if not path:
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {str(k).lower(): str(v) for k, v in data.items()}
    except Exception:
        return {}


def normalize_name(name, name_map):
    if not name:
        return None
    cleaned = " ".join(str(name).strip().split())
    mapped = name_map.get(cleaned.lower())
    return mapped or cleaned


def coerce_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def collect_files(root):
    files = []
    for base, _, filenames in os.walk(root):
        for filename in filenames:
            if filename == "analysis_llm.txt":
                files.append(os.path.join(base, filename))
    return sorted(files)


def main():
    args = parse_args()
    root = os.path.abspath(args.root)
    filmsets_path = args.filmsets or os.path.join(root, "filmsets")
    actors_out = args.actors_out or os.path.join(root, "ACTOR_MASTER_DB.json")
    scenes_out = args.scenes_out or os.path.join(root, "SCENE_MASTER_DB.json")
    stats_out = args.stats_out or os.path.join(root, "HARVEST_STATS.json")
    log_out = args.log_out or os.path.join(root, "HARVEST_LOG.json")

    include_types = split_types(args.include_type)
    exclude_types = split_types(args.exclude_type)
    name_map = load_name_map(args.name_map)

    files = collect_files(filmsets_path)
    if args.max_files and args.max_files > 0:
        files = files[: args.max_files]

    stats = {
        "files_total": len(files),
        "files_processed": 0,
        "files_parsed": 0,
        "files_missing_json": 0,
        "files_invalid_json": 0,
        "actors_total": 0,
        "scenes_total": 0,
        "by_type": {},
    }
    log = {
        "missing_json": [],
        "invalid_json": [],
        "skipped": [],
    }

    actor_db = {}
    scenes_by_chapter = {}

    for idx, path in enumerate(files, start=1):
        chapter_num, source_type = extract_chapter_and_type(path)
        if source_type is None:
            log["skipped"].append({"path": path, "reason": "no_chapter_match"})
            continue
        stats["by_type"][source_type] = stats["by_type"].get(source_type, 0) + 1

        if include_types and not type_matches(source_type, include_types):
            log["skipped"].append({"path": path, "reason": "filtered_out"})
            continue
        if exclude_types and type_matches(source_type, exclude_types):
            log["skipped"].append({"path": path, "reason": "filtered_out"})
            continue

        stats["files_processed"] += 1
        if stats["files_processed"] % 100 == 0:
            print(f"Processed {stats['files_processed']} files...")

        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception as exc:
            log["invalid_json"].append({"path": path, "error": str(exc)})
            stats["files_invalid_json"] += 1
            continue

        json_block = extract_json_block(content)
        if not json_block:
            stats["files_missing_json"] += 1
            log["missing_json"].append({"path": path})
            continue

        try:
            data = json.loads(json_block)
        except json.JSONDecodeError as exc:
            stats["files_invalid_json"] += 1
            log["invalid_json"].append(
                {"path": path, "error": str(exc), "snippet": json_block[:200]}
            )
            continue

        stats["files_parsed"] += 1
        rel_path = os.path.relpath(path, root)

        actors = data.get("actors") or []
        if isinstance(actors, dict):
            actors = list(actors.values())

        id_to_name = {}
        for actor in actors:
            if not isinstance(actor, dict):
                continue
            raw_name = actor.get("name") or actor.get("id")
            name = normalize_name(raw_name, name_map)
            if not name:
                continue
            if actor.get("id") and actor.get("name"):
                id_to_name[actor["id"]] = actor["name"]

            visual_traits = (
                actor.get("visualTraits")
                or actor.get("visual_traits")
                or actor.get("visual_state")
            )
            appearance = {
                "chapter": chapter_num,
                "source_type": source_type,
                "source_path": rel_path,
                "role": actor.get("role"),
                "visual_traits": visual_traits,
                "changes": actor.get("changes"),
            }
            if args.keep_raw:
                appearance["raw"] = actor

            actor_entry = actor_db.setdefault(
                name, {"name": name, "by_chapter": {}, "appearances": []}
            )
            actor_entry["appearances"].append(appearance)
            chapter_key = str(chapter_num)
            actor_entry["by_chapter"].setdefault(chapter_key, []).append(appearance)
            stats["actors_total"] += 1

        scenes = data.get("scenes") or []
        for scene in scenes:
            if not isinstance(scene, dict):
                continue
            raw_actors = scene.get("actorsInvolved") or scene.get("actors") or []
            raw_actors = coerce_list(raw_actors)
            resolved = []
            for ref in raw_actors:
                name = id_to_name.get(ref, ref)
                name = normalize_name(name, name_map)
                if name:
                    resolved.append(name)

            scene_entry = {
                "chapter": chapter_num,
                "source_type": source_type,
                "source_path": rel_path,
                "scene_id": scene.get("id"),
                "verse": scene.get("verse"),
                "title": scene.get("title"),
                "location": scene.get("location"),
                "action": scene.get("action"),
                "actors_involved": resolved,
                "actors_involved_raw": raw_actors,
            }
            if args.keep_raw:
                scene_entry["raw"] = scene

            chapter_key = str(chapter_num)
            scenes_by_chapter.setdefault(chapter_key, []).append(scene_entry)
            stats["scenes_total"] += 1

    with open(actors_out, "w", encoding="utf-8") as f:
        json.dump(actor_db, f, indent=2)
    with open(scenes_out, "w", encoding="utf-8") as f:
        json.dump(scenes_by_chapter, f, indent=2)
    with open(stats_out, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
    with open(log_out, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)

    print("Done.")
    print(f"Actors DB: {actors_out}")
    print(f"Scenes DB: {scenes_out}")
    print(f"Stats: {stats_out}")
    print(f"Log: {log_out}")


if __name__ == "__main__":
    main()
