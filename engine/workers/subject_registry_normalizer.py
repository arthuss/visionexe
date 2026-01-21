import argparse
import json
from collections import defaultdict
from pathlib import Path

from visionexe_paths import load_story_config, resolve_path


def normalize_key(value: str) -> str:
    if not value:
        return ""
    return str(value).strip().lower()


def load_json(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def load_jsonl(path: Path):
    items = []
    if not path.exists():
        return items
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return items


def write_jsonl(path: Path, items: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for item in items:
            handle.write(json.dumps(item, ensure_ascii=False) + "\n")


def build_redirects(log_payload: dict):
    redirects = {}
    for rename in log_payload.get("renames") or []:
        old_id = rename.get("old_id")
        new_id = rename.get("new_id")
        if old_id and new_id:
            redirects[old_id] = new_id
    for merge in log_payload.get("merges") or []:
        canonical_id = merge.get("canonical_id")
        for merge_id in merge.get("merge_ids") or []:
            if merge_id and canonical_id:
                redirects[merge_id] = canonical_id
    return redirects


def resolve_canonical(subject_id: str, redirects: dict) -> str:
    current = subject_id
    visited = set()
    while current in redirects and current not in visited:
        visited.add(current)
        current = redirects[current]
    return current


def merge_registry(entries: list[dict], redirects: dict, invalid_ids: set):
    merged = {}
    for entry in entries:
        subject_id = entry.get("id")
        if not subject_id or subject_id in invalid_ids:
            continue
        canonical = resolve_canonical(subject_id, redirects)
        if canonical in invalid_ids:
            continue
        target = merged.setdefault(canonical, dict(entry))
        target["id"] = canonical
        target["name"] = target.get("name") or entry.get("name")
        target["type"] = target.get("type") or entry.get("type")
        target["occurrence_count"] = int(target.get("occurrence_count") or 0) + int(entry.get("occurrence_count") or 0)
        first_ch = entry.get("first_chapter")
        last_ch = entry.get("last_chapter")
        if first_ch is not None:
            if target.get("first_chapter") is None or first_ch < target.get("first_chapter"):
                target["first_chapter"] = first_ch
        if last_ch is not None:
            if target.get("last_chapter") is None or last_ch > target.get("last_chapter"):
                target["last_chapter"] = last_ch
        target["is_dynamic"] = bool(target.get("is_dynamic")) or bool(entry.get("is_dynamic"))
    return list(merged.values())


def merge_states(states: list[dict]):
    merged = {}
    for state in states:
        if not isinstance(state, dict):
            continue
        state_id = state.get("state_id") or state.get("label") or "default"
        key = normalize_key(state_id)
        target = merged.setdefault(key, dict(state))
        target["state_id"] = target.get("state_id") or state_id
        target["label"] = target.get("label") or state.get("label") or state_id
        start = state.get("chapter_start")
        end = state.get("chapter_end")
        if start is not None:
            if target.get("chapter_start") is None or start < target.get("chapter_start"):
                target["chapter_start"] = start
        if end is not None:
            if target.get("chapter_end") is None or end > target.get("chapter_end"):
                target["chapter_end"] = end
        for field in ("segment_labels", "scene_labels", "source_ids", "notes"):
            values = target.get(field) or []
            incoming = state.get(field) or []
            combined = list(dict.fromkeys(values + incoming))
            target[field] = combined
    return list(merged.values())


def merge_profiles(profiles: list[dict], redirects: dict, invalid_ids: set, alias_log: dict):
    merged = {}
    for profile in profiles:
        subject_id = profile.get("id")
        if not subject_id or subject_id in invalid_ids:
            continue
        canonical = resolve_canonical(subject_id, redirects)
        if canonical in invalid_ids:
            continue
        target = merged.setdefault(canonical, dict(profile))
        target["id"] = canonical
        target["name"] = target.get("name") or profile.get("name")
        target["type"] = target.get("type") or profile.get("type")
        for field in ("aliases", "roles", "visual_traits", "changes", "notes", "sources"):
            values = target.get(field) or []
            incoming = profile.get(field) or []
            combined = list(dict.fromkeys(values + incoming))
            target[field] = combined
        target["occurrence_count"] = int(target.get("occurrence_count") or 0) + int(profile.get("occurrence_count") or 0)
        target["is_dynamic"] = bool(target.get("is_dynamic")) or bool(profile.get("is_dynamic"))
        if target.get("state_policy") != "phases" and profile.get("state_policy") == "phases":
            target["state_policy"] = "phases"
        states = merge_states((target.get("states") or []) + (profile.get("states") or []))
        target["states"] = states

    for canonical_id, aliases in alias_log.items():
        if canonical_id in merged:
            target = merged[canonical_id]
            values = target.get("aliases") or []
            combined = list(dict.fromkeys(values + aliases))
            target["aliases"] = combined
    return list(merged.values())


def merge_occurrences(occurrences: list[dict], redirects: dict, invalid_ids: set):
    merged = []
    for occ in occurrences:
        subject_id = occ.get("subject_id")
        if not subject_id or subject_id in invalid_ids:
            continue
        canonical = resolve_canonical(subject_id, redirects)
        if canonical in invalid_ids:
            continue
        occ = dict(occ)
        occ["subject_id"] = canonical
        merged.append(occ)
    return merged


def main():
    parser = argparse.ArgumentParser(description="Normalize subject registry using a merge log.")
    parser.add_argument("--story-root", help="Story root path (defaults to engine_config default_story_root).")
    parser.add_argument("--story-config", help="Path to story_config.json (overrides story-root).")
    parser.add_argument("--merge-log", help="Merge log JSON path override.")
    parser.add_argument("--registry", help="Registry JSON path override.")
    parser.add_argument("--profiles", help="profiles.jsonl path override.")
    parser.add_argument("--occurrences", help="occurrences.jsonl path override.")
    parser.add_argument("--dry-run", action="store_true", help="Print counts without writing.")
    args = parser.parse_args()

    story_config, _story_root, repo_root = load_story_config(
        story_root=args.story_root,
        story_config_path=args.story_config,
    )

    subjects_root = resolve_path(story_config.get("subjects_root"), repo_root)
    registry_path = resolve_path(args.registry or (subjects_root / "registry.json"), repo_root)
    profiles_path = resolve_path(args.profiles or (subjects_root / "profiles.jsonl"), repo_root)
    occurrences_path = resolve_path(args.occurrences or (subjects_root / "occurrences.jsonl"), repo_root)
    merge_log_path = resolve_path(args.merge_log or (subjects_root / "registry_merge_log.json"), repo_root)

    log_payload = load_json(merge_log_path)
    if not log_payload:
        raise SystemExit(f"Merge log not found or invalid: {merge_log_path}")

    redirects = build_redirects(log_payload)
    invalid_ids = {entry.get("id") for entry in (log_payload.get("invalid") or []) if entry.get("id")}
    alias_log = defaultdict(list)
    for entry in log_payload.get("aliases") or []:
        canonical_id = entry.get("canonical_id")
        aliases = entry.get("aliases") or []
        if canonical_id:
            alias_log[canonical_id].extend([a for a in aliases if a])

    registry = load_json(registry_path) or []
    profiles = load_jsonl(profiles_path)
    occurrences = load_jsonl(occurrences_path)

    merged_registry = merge_registry(registry, redirects, invalid_ids)
    merged_profiles = merge_profiles(profiles, redirects, invalid_ids, alias_log)
    merged_occurrences = merge_occurrences(occurrences, redirects, invalid_ids)

    if args.dry_run:
        print(f"registry: {len(registry)} -> {len(merged_registry)}")
        print(f"profiles: {len(profiles)} -> {len(merged_profiles)}")
        print(f"occurrences: {len(occurrences)} -> {len(merged_occurrences)}")
        return

    registry_path.write_text(json.dumps(merged_registry, ensure_ascii=False, indent=2), encoding="utf-8")
    write_jsonl(profiles_path, merged_profiles)
    write_jsonl(occurrences_path, merged_occurrences)

    print(f"Updated registry: {registry_path}")
    print(f"Updated profiles: {profiles_path}")
    print(f"Updated occurrences: {occurrences_path}")


if __name__ == "__main__":
    main()
