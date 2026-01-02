import argparse
import glob
import json
import os
import re


def parse_args():
    parser = argparse.ArgumentParser(
        description="Repair JSON errors from harvest_log.txt and merge into FULL_ACTOR_DB."
    )
    default_root = os.path.abspath(os.path.dirname(__file__))
    parser.add_argument("--root", default=default_root, help="Project root path.")
    parser.add_argument(
        "--filmsets",
        default=None,
        help="Filmsets path (defaults to <root>/filmsets).",
    )
    parser.add_argument(
        "--db-in",
        default=None,
        help="Input FULL_ACTOR_DB.json (defaults to <root>/FULL_ACTOR_DB.json).",
    )
    parser.add_argument(
        "--db-out",
        default=None,
        help="Output repaired DB (defaults to <root>/FULL_ACTOR_DB_repaired.json).",
    )
    parser.add_argument(
        "--log-in",
        default=None,
        help="Harvest log file (defaults to <root>/harvest_log.txt).",
    )
    parser.add_argument(
        "--report-out",
        default=None,
        help="Repair report JSON (defaults to <root>/HARVEST_REPAIR_LOG.json).",
    )
    return parser.parse_args()


def extract_json_block(text):
    fenced = extract_fenced_block(text, "json") or extract_fenced_block(text, None)
    if fenced:
        return fenced.strip() or None
    return extract_balanced_from_text(text)


def extract_fenced_block(text, fence_tag):
    if fence_tag:
        pattern = r"```%s\s*(.*?)```" % re.escape(fence_tag)
    else:
        pattern = r"```\s*(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        return None
    return match.group(1)


def extract_balanced_from_text(text):
    for start in range(len(text)):
        if text[start] != "{":
            continue
        end = find_balanced_json(text, start)
        if end is None:
            continue
        candidate = text[start : end + 1]
        return candidate
    return None


def find_balanced_json(text, start_idx):
    depth = 0
    in_string = False
    escape = False
    for i in range(start_idx, len(text)):
        ch = text[i]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == "\"":
                in_string = False
            continue
        if ch == "\"":
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i
    return None


def fix_mismatched_brackets(text):
    chars = list(text)
    stack = []
    in_string = False
    escape = False
    changes = []
    for i, ch in enumerate(chars):
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == "\"":
                in_string = False
            continue
        if ch == "\"":
            in_string = True
            continue
        if ch in "{[":
            stack.append(ch)
            continue
        if ch in "}]":
            if not stack:
                continue
            expected = "}" if stack[-1] == "{" else "]"
            if ch != expected:
                changes.append({"pos": i, "from": ch, "to": expected})
                chars[i] = expected
            stack.pop()
    return "".join(chars), changes


def repair_json_text(text):
    cleaned = text.strip().replace("\ufeff", "")
    if "\u201c" in cleaned or "\u201d" in cleaned:
        cleaned = cleaned.replace("\u201c", "\"").replace("\u201d", "\"")
    if "\u2018" in cleaned or "\u2019" in cleaned:
        cleaned = cleaned.replace("\u2018", "'").replace("\u2019", "'")
    cleaned = re.sub(r",(\s*[}\]])", r"\\1", cleaned)
    cleaned, bracket_changes = fix_mismatched_brackets(cleaned)
    return cleaned, bracket_changes


def parse_log(log_path):
    errors = []
    missing = []
    with open(log_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if line.startswith("[JSON ERROR]"):
                payload = line.split("]", 1)[1].strip()
                left = payload.split(":", 1)[0].strip()
                if "/" in left:
                    chapter_id, subfolder = left.split("/", 1)
                    errors.append((chapter_id, subfolder))
            elif line.startswith("[NO JSON]"):
                left = line.split("]", 1)[1].strip()
                if "/" in left:
                    chapter_id, subfolder = left.split("/", 1)
                    missing.append((chapter_id, subfolder))
    return errors, missing


def resolve_paths(filmsets, chapter_id, subfolder):
    base = os.path.join(filmsets, chapter_id, subfolder)
    if subfolder == "visual_abc":
        return glob.glob(os.path.join(base, "**", "analysis_llm.txt"), recursive=True)
    path = os.path.join(base, "analysis_llm.txt")
    if os.path.exists(path):
        return [path]
    return glob.glob(os.path.join(base, "**", "analysis_llm.txt"), recursive=True)


def normalize_name(name):
    return str(name).strip().title()


def ensure_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def actor_entry_exists(entries, entry):
    for existing in entries:
        if (
            existing.get("chapter") == entry.get("chapter")
            and existing.get("source_subfolder") == entry.get("source_subfolder")
            and existing.get("role") == entry.get("role")
            and existing.get("visualTraits") == entry.get("visualTraits")
            and existing.get("changes") == entry.get("changes")
        ):
            return True
    return False


def scene_entry_exists(entries, entry):
    for existing in entries:
        if (
            existing.get("chapter") == entry.get("chapter")
            and existing.get("title") == entry.get("title")
            and existing.get("location") == entry.get("location")
            and existing.get("action") == entry.get("action")
            and existing.get("actors_involved") == entry.get("actors_involved")
        ):
            return True
    return False


def main():
    args = parse_args()
    root = os.path.abspath(args.root)
    filmsets = args.filmsets or os.path.join(root, "filmsets")
    db_in = args.db_in or os.path.join(root, "FULL_ACTOR_DB.json")
    db_out = args.db_out or os.path.join(root, "FULL_ACTOR_DB_repaired.json")
    log_in = args.log_in or os.path.join(root, "harvest_log.txt")
    report_out = args.report_out or os.path.join(root, "HARVEST_REPAIR_LOG.json")

    with open(db_in, "r", encoding="utf-8") as f:
        master_db = json.load(f)

    errors, missing = parse_log(log_in)
    targets = set()
    for chapter_id, subfolder in errors:
        for path in resolve_paths(filmsets, chapter_id, subfolder):
            targets.add(path)

    report = {
        "targets": len(targets),
        "parsed": 0,
        "repaired": 0,
        "missing_json": [],
        "invalid_json": [],
        "repaired_files": [],
        "actors_added": 0,
        "scenes_added": 0,
        "no_json_from_log": missing,
    }

    for path in sorted(targets):
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        json_block = extract_json_block(content)
        if not json_block:
            report["missing_json"].append(path)
            continue

        try:
            data = json.loads(json_block)
            repaired = False
            bracket_changes = []
        except json.JSONDecodeError:
            repaired_text, bracket_changes = repair_json_text(json_block)
            try:
                data = json.loads(repaired_text)
                repaired = True
            except json.JSONDecodeError as exc:
                report["invalid_json"].append({"path": path, "error": str(exc)})
                continue

        if not isinstance(data, dict) or (
            "actors" not in data and "scenes" not in data
        ):
            report["invalid_json"].append(
                {"path": path, "error": "missing actors/scenes"}
            )
            continue

        report["parsed"] += 1
        if repaired:
            report["repaired"] += 1
            report["repaired_files"].append(
                {"path": path, "bracket_fixes": bracket_changes}
            )

        chapter_id, subfolder = extract_chapter_and_type(path)
        if chapter_id is None:
            continue

        actors = data.get("actors") or []
        id_to_name = {}
        for actor in actors:
            if not isinstance(actor, dict):
                continue
            if actor.get("id") and actor.get("name"):
                id_to_name[actor["id"]] = actor["name"]

        for actor in actors:
            if not isinstance(actor, dict):
                continue
            name_raw = actor.get("name") or actor.get("id")
            if not name_raw:
                continue
            name = normalize_name(name_raw)
            entry = {
                "chapter": chapter_id,
                "source_subfolder": subfolder,
                "role": actor.get("role", ""),
                "visualTraits": actor.get("visualTraits")
                or actor.get("visual_traits")
                or actor.get("visual_state")
                or [],
                "changes": actor.get("changes") or [],
            }

            if name not in master_db["actors"]:
                master_db["actors"][name] = []
            if not actor_entry_exists(master_db["actors"][name], entry):
                master_db["actors"][name].append(entry)
                report["actors_added"] += 1

        scenes = data.get("scenes") or []
        for scene in scenes:
            if not isinstance(scene, dict):
                continue
            raw_actors = scene.get("actorsInvolved") or scene.get("actors_involved")
            raw_actors = raw_actors or scene.get("actors") or []
            raw_actors = ensure_list(raw_actors)
            resolved = []
            for ref in raw_actors:
                ref_name = id_to_name.get(ref, ref)
                if ref_name:
                    resolved.append(normalize_name(ref_name))

            entry = {
                "chapter": chapter_id,
                "title": scene.get("title", ""),
                "location": scene.get("location", ""),
                "action": ensure_list(scene.get("action")),
                "actors_involved": resolved,
            }

            if not scene_entry_exists(master_db["scenes"], entry):
                master_db["scenes"].append(entry)
                report["scenes_added"] += 1

    with open(db_out, "w", encoding="utf-8") as f:
        json.dump(master_db, f, indent=2)
    with open(report_out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("Done.")
    print(f"Repaired DB: {db_out}")
    print(f"Report: {report_out}")


def extract_chapter_and_type(path):
    match = re.search(r"chapter_\\d+[\\\\/][^\\\\/]+", path)
    if not match:
        return None, None
    parts = match.group(0).split(os.sep)
    if len(parts) < 2:
        parts = match.group(0).replace("/", os.sep).split(os.sep)
    if len(parts) >= 2:
        return parts[0], parts[1]
    return None, None


if __name__ == "__main__":
    main()
