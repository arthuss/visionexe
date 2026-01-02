import argparse
import json
import os
import re

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
DEFAULT_SCRIPT = os.path.join(ROOT_PATH, "filmsets")
ASSET_BIBLE_PATH = os.path.join(ROOT_PATH, "ASSET_BIBLE.md")
ASSET_BIBLE_DIR = os.path.join(ROOT_PATH, "produced_assets", "asset_bible")
FULL_ACTOR_DB_PATH = os.path.join(ROOT_PATH, "FULL_ACTOR_DB_repaired.json")
SCENE_MASTER_DB_PATH = os.path.join(ROOT_PATH, "SCENE_MASTER_DB.json")
FULL_EXPORT_CSV_PATH = os.path.join(ROOT_PATH, "1henoch_full_export.csv")


def load_text(path):
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def save_text(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def normalize_token(text):
    return re.sub(r"[^a-z0-9]+", "", str(text or "").lower())


def normalize_path(path):
    return str(path or "").replace("/", "\\").lower()


def parse_chapter_number(value):
    if value is None:
        return None
    text = str(value)
    match = re.search(r"(\d{1,3})", text)
    if not match:
        return None
    num = int(match.group(1))
    if 1 <= num <= 108:
        return num
    return None


def extract_field(block, label):
    pattern = re.compile(rf"^\*\*{re.escape(label)}:\*\*\s*(.+)$", re.M)
    match = pattern.search(block)
    if not match:
        return ""
    return match.group(1).strip()


def extract_section(block, header):
    start = block.find(header)
    if start == -1:
        return ""
    start = block.find("\n", start)
    if start == -1:
        return ""
    start += 1
    next_marker = re.search(r"^###\s+", block[start:], re.M)
    end = start + next_marker.start() if next_marker else len(block)
    return block[start:end].strip()


def parse_asset_bible(path):
    content = load_text(path)
    if not content:
        return []
    header_pattern = re.compile(
        r"^##\s+\[(?P<category>.*?)\]\s+(?P<name>.*?)\s+\(ID:\s*(?P<id>.*?)\)\s*$",
        re.M,
    )
    matches = list(header_pattern.finditer(content))
    assets = []
    for idx, match in enumerate(matches):
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(content)
        block = content[start:end].strip()
        description = extract_field(block, "Description")
        tags = extract_field(block, "Tags")
        key_features = ""
        key_match = re.search(r"\*\*Key Features:\*\*\s*(.+)$", block, re.M)
        if key_match:
            key_features = key_match.group(1).strip()
        props_section = extract_section(block, "### 3. PROPS & EQUIPMENT")
        props_lines = []
        if props_section:
            for line in props_section.splitlines():
                line = line.strip()
                if line.startswith("*"):
                    props_lines.append(re.sub(r"^\*\s*", "", line))
        keywords_section = extract_section(block, "### 4. AI PROMPT KEYWORDS")
        asset = {
            "id": match.group("id").strip(),
            "name": match.group("name").strip(),
            "category": match.group("category").strip(),
            "description": description,
            "tags": tags,
            "key_features": key_features,
            "props": props_lines,
            "keywords": keywords_section.strip(),
            "block": block,
        }
        asset["name_norm"] = normalize_token(asset["name"])
        asset["id_norm"] = normalize_token(asset["id"])
        assets.append(asset)
    return assets


def normalize_asset_filename(filename):
    stem = os.path.splitext(filename)[0]
    stem = re.sub(r"__r\d{2}$", "", stem, flags=re.IGNORECASE)
    stem = re.sub(r"_\d{5}_?$", "", stem)
    return stem


def build_asset_folder_index(base_dir):
    if not base_dir or not os.path.isdir(base_dir):
        return {}
    index = {}
    for category in os.listdir(base_dir):
        category_path = os.path.join(base_dir, category)
        if not os.path.isdir(category_path):
            continue
        for root, _, files in os.walk(category_path):
            for filename in files:
                if not filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                    continue
                asset_id = normalize_asset_filename(filename)
                slug = normalize_token(asset_id)
                if not slug:
                    continue
                entry = index.setdefault(slug, {"categories": set(), "ids": set()})
                entry["categories"].add(category)
                entry["ids"].add(asset_id)
    return index


def load_full_export_csv(path):
    if not path or not os.path.exists(path):
        return {}
    export_map = {}
    import csv
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            source_path = row.get("Source Path") or row.get("source_path")
            content = row.get("Content") or row.get("content")
            if not source_path or not content:
                continue
            export_map[normalize_path(source_path)] = content
    return export_map


def load_full_actor_db(path):
    if not path or not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    actors = data.get("actors") if isinstance(data, dict) else {}
    actor_map = {}
    if not isinstance(actors, dict):
        return actor_map
    for actor_name, entries in actors.items():
        if not isinstance(entries, list):
            continue
        actor_norm = normalize_token(actor_name)
        if not actor_norm:
            continue
        cleaned = []
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            chapter_num = parse_chapter_number(entry.get("chapter"))
            cleaned.append({
                "chapter": chapter_num,
                "source_subfolder": entry.get("source_subfolder"),
                "role": entry.get("role"),
                "visual_traits": entry.get("visualTraits") or entry.get("visual_traits") or [],
                "changes": entry.get("changes") or [],
            })
        actor_map[actor_norm] = cleaned
    return actor_map


def load_scene_master_db(path):
    if not path or not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        return {}
    scene_index = {}
    for chapter_key, entries in data.items():
        chapter_num = parse_chapter_number(chapter_key)
        if chapter_num is None or not isinstance(entries, list):
            continue
        cleaned = []
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            location = entry.get("location") or ""
            actors = entry.get("actors_involved") or []
            if isinstance(actors, str):
                actors = [actors]
            cleaned.append({
                "location": location,
                "location_norm": normalize_token(location),
                "action": entry.get("action") or [],
                "actors_involved": actors,
                "actors_norm": [normalize_token(a) for a in actors if a],
                "source_path": entry.get("source_path"),
            })
        scene_index[chapter_num] = cleaned
    return scene_index


def parse_regie_json(block):
    regie_line = None
    for line in block.splitlines():
        if line.strip().startswith("REGIE_JSON:"):
            regie_line = line.strip()
            break
    if not regie_line:
        return None, None
    json_text = regie_line.split("REGIE_JSON:", 1)[1].strip()
    if json_text.startswith("{") and json_text.endswith("}"):
        try:
            return regie_line, json.loads(json_text)
        except json.JSONDecodeError:
            return regie_line, None
    return regie_line, None


def find_asset_matches(block_text, regie_data, assets):
    matches = []
    if not assets:
        return matches
    scene_text = block_text.lower()
    props = regie_data.get("props") or []
    env_name = regie_data.get("environment") or ""
    focus_tokens = [p for p in props if p] + ([env_name] if env_name else [])
    focus_norms = [normalize_token(t) for t in focus_tokens if t]

    for asset in assets:
        name = asset["name"].lower()
        asset_id = asset["id"].lower()
        if asset_id and asset_id in scene_text:
            matches.append(asset)
            continue
        if name and name in scene_text:
            matches.append(asset)
            continue
        for token_norm in focus_norms:
            if not token_norm:
                continue
            if token_norm in asset["name_norm"] or asset["name_norm"] in token_norm:
                matches.append(asset)
                break
    unique = {}
    for asset in matches:
        unique[asset["id"]] = asset
    return list(unique.values())


def match_folder_assets(regie_data, folder_index):
    if not folder_index:
        return []
    tokens = []
    for name in extract_actor_names(regie_data):
        tokens.append(normalize_token(name))
    for prop in regie_data.get("props") or []:
        token = prop.get("name") if isinstance(prop, dict) else prop
        tokens.append(normalize_token(token))
    env_name = regie_data.get("environment") or ""
    tokens.append(normalize_token(env_name))
    tokens = [t for t in tokens if t]
    matches = []
    for token in tokens:
        for slug, entry in folder_index.items():
            if token in slug or slug in token:
                matches.append({
                    "slug": slug,
                    "categories": sorted(entry["categories"]),
                    "ids": sorted(entry["ids"]),
                })
    unique = {}
    for match in matches:
        unique[match["slug"]] = match
    return list(unique.values())

def extract_actor_names(regie_data):
    actors = regie_data.get("actors") or []
    names = []
    for actor in actors:
        if isinstance(actor, dict):
            name = actor.get("name")
        else:
            name = actor
        if name:
            names.append(name)
    return names


def guess_actor_source_path(chapter_num, source_subfolder):
    if not chapter_num or not source_subfolder:
        return None
    chapter_folder = f"chapter_{chapter_num:03d}"
    return os.path.join(ROOT_PATH, "filmsets", chapter_folder, source_subfolder, "analysis_llm.txt")


def build_actor_context(regie_data, actor_map, chapter_num, max_traits, max_changes):
    if not actor_map or not chapter_num:
        return []
    results = []
    for actor_name in extract_actor_names(regie_data):
        actor_norm = normalize_token(actor_name)
        if not actor_norm:
            continue
        entries = [e for e in actor_map.get(actor_norm, []) if e.get("chapter") == chapter_num]
        if not entries:
            continue
        traits = []
        changes = []
        sources = []
        role = None
        for entry in entries:
            role = role or entry.get("role")
            for trait in entry.get("visual_traits") or []:
                if trait and trait not in traits:
                    traits.append(trait)
            for change in entry.get("changes") or []:
                if change and change not in changes:
                    changes.append(change)
            source_path = guess_actor_source_path(chapter_num, entry.get("source_subfolder"))
            if source_path and source_path not in sources:
                sources.append(source_path)
        result = {
            "name": actor_name,
            "role": role,
            "visual_traits": traits[:max_traits],
            "changes": changes[:max_changes],
            "sources": sources,
        }
        results.append(result)
    return results


def match_scene_context(regie_data, scene_index, chapter_num, max_actions):
    if not scene_index or not chapter_num:
        return []
    entries = scene_index.get(chapter_num) or []
    if not entries:
        return []
    env_norm = normalize_token(regie_data.get("environment") or "")
    actor_norms = [normalize_token(name) for name in extract_actor_names(regie_data)]
    best = []
    for entry in entries:
        score = 0
        location_norm = entry.get("location_norm")
        if env_norm and location_norm and (env_norm in location_norm or location_norm in env_norm):
            score += 2
        overlap = len(set(actor_norms) & set(entry.get("actors_norm") or []))
        score += overlap
        if score > 0:
            best.append((score, entry))
    if not best:
        return []
    best.sort(key=lambda item: item[0], reverse=True)
    entry = best[0][1]
    actions = entry.get("action") or []
    return [{
        "location": entry.get("location"),
        "actions": actions[:max_actions] if isinstance(actions, list) else actions,
        "actors_involved": entry.get("actors_involved"),
        "source_path": entry.get("source_path"),
    }]


def build_snippet_map(source_paths, export_map, max_snippets, snippet_chars):
    snippets = {}
    if not export_map:
        return snippets
    for path in source_paths:
        if not path:
            continue
        norm = normalize_path(path)
        content = export_map.get(norm)
        if not content:
            continue
        snippet = content.strip().replace("\n", " ")
        snippet = snippet[:snippet_chars].rstrip()
        if snippet:
            snippets[path] = snippet
        if len(snippets) >= max_snippets:
            break
    return snippets


def merge_context(
    regie_data,
    matched_assets,
    folder_matches,
    chapter_num,
    actor_map,
    scene_index,
    export_map,
    max_assets=8,
    max_traits=8,
    max_changes=8,
    max_actions=6,
    max_snippets=4,
    snippet_chars=500,
):
    if not matched_assets:
        asset_changed = False
    else:
        asset_changed = True
    regie_data = dict(regie_data)
    context = dict(regie_data.get("context_metadata") or {})
    existing_assets = context.get("assets") or []
    existing_ids = {a.get("id") for a in existing_assets if isinstance(a, dict)}
    new_assets = []
    for asset in matched_assets:
        if asset["id"] in existing_ids:
            continue
        new_assets.append({
            "id": asset["id"],
            "name": asset["name"],
            "category": asset["category"],
            "description": asset["description"],
            "tags": asset["tags"],
            "key_features": asset["key_features"],
            "props": asset["props"],
        })
    if new_assets:
        merged_assets = existing_assets + new_assets
        context["assets"] = merged_assets[:max_assets]

    categories = {a.get("category") for a in context.get("assets", []) if isinstance(a, dict)}
    for match in folder_matches:
        for category in match.get("categories", []):
            categories.add(category)
    if categories:
        context["asset_categories"] = sorted(c for c in categories if c)
    if folder_matches:
        context["asset_folder_matches"] = folder_matches[:max_assets]

    actor_context = build_actor_context(regie_data, actor_map, chapter_num, max_traits, max_changes)
    if actor_context:
        context["actor_context"] = actor_context

    scene_context = match_scene_context(regie_data, scene_index, chapter_num, max_actions)
    if scene_context:
        context["scene_context"] = scene_context

    source_paths = []
    for actor in actor_context:
        source_paths.extend(actor.get("sources") or [])
    for scene in scene_context:
        source_path = scene.get("source_path")
        if source_path:
            source_paths.append(source_path)
    source_paths = [p for p in source_paths if p]
    if source_paths:
        snippets = build_snippet_map(source_paths, export_map, max_snippets, snippet_chars)
        if snippets:
            context["analysis_snippets"] = snippets

    regie_data["context_metadata"] = context
    changed = asset_changed or bool(actor_context) or bool(scene_context) or bool(context.get("analysis_snippets"))
    return regie_data, changed


def update_block(
    block,
    assets,
    folder_index,
    chapter_num,
    actor_map,
    scene_index,
    export_map,
    max_assets=8,
    max_traits=8,
    max_changes=8,
    max_actions=6,
    max_snippets=4,
    snippet_chars=500,
):
    regie_line, regie_data = parse_regie_json(block)
    if not regie_line or not regie_data:
        return block, False
    matches = find_asset_matches(block, regie_data, assets)
    folder_matches = match_folder_assets(regie_data, folder_index)
    regie_data, changed = merge_context(
        regie_data,
        matches,
        folder_matches,
        chapter_num,
        actor_map,
        scene_index,
        export_map,
        max_assets=max_assets,
        max_traits=max_traits,
        max_changes=max_changes,
        max_actions=max_actions,
        max_snippets=max_snippets,
        snippet_chars=snippet_chars,
    )
    if not changed:
        return block, False
    new_line = "REGIE_JSON: " + json.dumps(regie_data, ensure_ascii=False)
    updated = []
    replaced = False
    for line in block.splitlines():
        if not replaced and line.strip().startswith("REGIE_JSON:"):
            updated.append(new_line)
            replaced = True
        else:
            updated.append(line)
    return "\n".join(updated), True


def list_chapters(base_path, chapter_args):
    if chapter_args:
        return [f"chapter_{ch:03d}" for ch in chapter_args]
    candidates = [
        d for d in os.listdir(base_path)
        if d.startswith("chapter_") and os.path.isdir(os.path.join(base_path, d))
    ]
    return sorted(candidates)


def process_script(
    script_text,
    assets,
    folder_index,
    chapter_num,
    actor_map,
    scene_index,
    export_map,
    max_assets=8,
    max_traits=8,
    max_changes=8,
    max_actions=6,
    max_snippets=4,
    snippet_chars=500,
):
    blocks = script_text.split("\n---")
    updated_blocks = []
    changed = 0
    for block in blocks:
        if "REGIE_JSON:" not in block:
            updated_blocks.append(block)
            continue
        new_block, updated = update_block(
            block,
            assets,
            folder_index,
            chapter_num,
            actor_map,
            scene_index,
            export_map,
            max_assets=max_assets,
            max_traits=max_traits,
            max_changes=max_changes,
            max_actions=max_actions,
            max_snippets=max_snippets,
            snippet_chars=snippet_chars,
        )
        if updated:
            changed += 1
        updated_blocks.append(new_block)
    return "\n---\n".join(updated_blocks), changed


def main():
    parser = argparse.ArgumentParser(description="Inject Asset Bible context into REGIE_JSON blocks.")
    parser.add_argument("chapters", nargs="*", type=int, help="Chapter numbers (e.g. 1 2 3).")
    parser.add_argument("--base-path", default=DEFAULT_SCRIPT, help="Base filmsets path.")
    parser.add_argument("--asset-bible", default=ASSET_BIBLE_PATH, help="Path to ASSET_BIBLE.md")
    parser.add_argument("--asset-folder", default=ASSET_BIBLE_DIR, help="Path to produced asset_bible folder")
    parser.add_argument("--no-asset-folder", action="store_true", help="Disable asset folder matching")
    parser.add_argument("--full-actor-db", default=FULL_ACTOR_DB_PATH, help="Path to FULL_ACTOR_DB_repaired.json")
    parser.add_argument("--scene-master-db", default=SCENE_MASTER_DB_PATH, help="Path to SCENE_MASTER_DB.json")
    parser.add_argument("--full-export", default=FULL_EXPORT_CSV_PATH, help="Path to 1henoch_full_export.csv")
    parser.add_argument("--max-assets", type=int, default=8, help="Max asset entries per scene.")
    parser.add_argument("--max-actor-traits", type=int, default=8, help="Max actor visual traits per scene.")
    parser.add_argument("--max-actor-changes", type=int, default=8, help="Max actor changes per scene.")
    parser.add_argument("--max-scene-actions", type=int, default=6, help="Max scene action entries per scene.")
    parser.add_argument("--max-snippets", type=int, default=4, help="Max analysis snippets per scene.")
    parser.add_argument("--snippet-chars", type=int, default=500, help="Max chars per analysis snippet.")
    parser.add_argument("--dry-run", action="store_true", help="Print changes without writing.")
    args = parser.parse_args()

    assets = parse_asset_bible(args.asset_bible)
    if not assets:
        print(f"[ERR] No assets parsed from {args.asset_bible}")
        return
    folder_index = {} if args.no_asset_folder else build_asset_folder_index(args.asset_folder)
    actor_map = load_full_actor_db(args.full_actor_db)
    scene_index = load_scene_master_db(args.scene_master_db)
    export_map = load_full_export_csv(args.full_export)

    chapters = list_chapters(args.base_path, args.chapters)
    for chapter in chapters:
        script_path = os.path.join(args.base_path, chapter, "DREHBUCH_HOLLYWOOD.md")
        if not os.path.exists(script_path):
            print(f"[WARN] Skip {chapter}: no script found.")
            continue
        script_text = load_text(script_path)
        chapter_num = parse_chapter_number(chapter)
        updated_text, changed = process_script(
            script_text,
            assets,
            folder_index,
            chapter_num,
            actor_map,
            scene_index,
            export_map,
            max_assets=args.max_assets,
            max_traits=args.max_actor_traits,
            max_changes=args.max_actor_changes,
            max_actions=args.max_scene_actions,
            max_snippets=args.max_snippets,
            snippet_chars=args.snippet_chars,
        )
        if args.dry_run:
            print(f"[DRY] {chapter}: {changed} scene(s) would be updated.")
            continue
        if changed > 0:
            save_text(script_path, updated_text)
            print(f"[OK] {chapter}: injected context into {changed} scene(s).")
        else:
            print(f"[SKIP] {chapter}: no changes.")


if __name__ == "__main__":
    main()
