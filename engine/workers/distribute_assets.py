import argparse
import json
import os
import re
import shutil

# --- CONFIGURATION ---
ROOT_PATH = r"C:\Users\sasch\henoch"
DEFAULT_SOURCE_DIR = os.path.join(ROOT_PATH, "produced_assets", "asset_bible")
DEFAULT_FILMSETS_DIR = os.path.join(ROOT_PATH, "filmsets")
DEFAULT_ASSET_BIBLE = os.path.join(ROOT_PATH, "ASSET_BIBLE.md")
DEFAULT_PROP_DB = os.path.join(ROOT_PATH, "ACTOR_PROP_DB.json")
DEFAULT_ENV_DB = os.path.join(ROOT_PATH, "ENVIRONMENT_ASSETS.json")
IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp")
CATEGORY_ALIASES = {
    "character": "characters",
    "characters": "characters",
    "char": "characters",
    "actor": "characters",
    "actors": "characters",
    "prop": "props",
    "props": "props",
    "environment": "environments",
    "environments": "environments",
    "env": "environments",
    "envs": "environments",
    "location": "environments",
    "locations": "environments",
    "character_group": "characters",
    "character_fx": "characters",
    "character_effect": "character_fx",
    "character_effects": "character_fx",
    "ui": "ui_concept",
    "ui_hud": "ui_hud",
    "ui_overlay": "ui_overlay",
    "ui_interface": "ui_interface",
    "ui_element": "ui_element",
    "ui_fx": "ui_fx",
    "ui_vfx": "ui_vfx",
    "event_fx": "event_fx",
    "concept_vfx": "concept_vfx",
    "visual_fx": "visual_fx",
    "visual_effect": "visual_effect",
    "celestial_body": "celestial_body",
    "entity_group": "entity_group",
}


def parse_categories(value):
    if not value:
        return []
    parts = []
    for entry in value:
        parts.extend([p.strip().lower() for p in entry.split(",") if p.strip()])
    return [normalize_category(part) for part in parts if part]


def normalize_category(value):
    if not value:
        return ""
    lowered = re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")
    return CATEGORY_ALIASES.get(lowered, lowered)


def category_matches(category, filters):
    if not filters:
        return True
    if not category:
        return False
    normalized = normalize_category(category)
    for raw in filters:
        if not raw:
            continue
        needle = normalize_category(raw)
        if not needle:
            continue
        if normalized == needle:
            return True
        if normalized.startswith(needle + "_"):
            return True
        if needle in normalized:
            return True
    return False


def slugify(value):
    if not value:
        return ""
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def parse_chapter_list(text):
    if not text:
        return []
    cleaned = text.replace("\u2013", "-").replace("\u2014", "-").replace("_", " ")
    chapters = []
    for match in re.finditer(r"(\d{1,3})\s*-\s*(\d{1,3})", cleaned):
        start = _safe_chapter(match.group(1))
        end = _safe_chapter(match.group(2))
        if start and end:
            if start <= end:
                chapters.extend(range(start, end + 1))
            else:
                chapters.extend(range(end, start + 1))
    cleaned = re.sub(r"(\d{1,3})\s*-\s*(\d{1,3})", " ", cleaned)
    for match in re.finditer(r"\b(\d{1,3})\b", cleaned):
        chapter = _safe_chapter(match.group(1))
        if chapter:
            chapters.append(chapter)
    return sorted(set(chapters))


def extract_chapter_from_id(asset_id):
    if not asset_id:
        return None
    match = re.search(r"CH(\d{1,3})", asset_id, re.IGNORECASE)
    if match:
        return _safe_chapter(match.group(1))
    match = re.search(r"[_\-](\d{2,3})[_\-]", asset_id)
    if match:
        return _safe_chapter(match.group(1))
    match = re.search(r"[_\-](\d{2,3})$", asset_id)
    if match:
        return _safe_chapter(match.group(1))
    return None


def _safe_chapter(value):
    try:
        num = int(value)
    except ValueError:
        return None
    if 1 <= num <= 108:
        return num
    return None


def load_asset_index(asset_bible_path):
    print("Scanning ASSET_BIBLE.md for context...")
    asset_index = {}

    if not os.path.exists(asset_bible_path):
        print("Warning: ASSET_BIBLE.md not found.")
        return {}

    header_pattern = re.compile(
        r'^##\s+\[(?P<category>.*?)\]\s+.*?\(ID:\s*(?P<asset_id>.*?)\)',
        re.MULTILINE,
    )
    chapter_patterns = [
        re.compile(r'\bCHAPTERS?\b[^\d]*(\d[\d\s,&\-\u2013\u2014_]*)', re.IGNORECASE),
        re.compile(r'\bKAPITEL\b[^\d]*(\d[\d\s,&\-\u2013\u2014_]*)', re.IGNORECASE),
        re.compile(r'\bCH\b\s*([0-9]{1,3}(?:\s*[-,&_]\s*[0-9]{1,3})*)', re.IGNORECASE),
        re.compile(r'\bCH(\d{1,3})\b', re.IGNORECASE),
    ]

    with open(asset_bible_path, 'r', encoding='utf-8') as f:
        content = f.read()

    chapter_markers = []
    offset = 0
    for line in content.splitlines(True):
        if line.lstrip().startswith("#"):
            for pattern in chapter_patterns:
                match = pattern.search(line)
                if match:
                    chapters = parse_chapter_list(match.group(1))
                    if chapters:
                        chapter_markers.append((offset, chapters))
                        break
        offset += len(line)

    def chapters_for_offset(pos):
        current = []
        for marker_pos, chapters in chapter_markers:
            if marker_pos <= pos:
                current = chapters
            else:
                break
        return current

    for match in header_pattern.finditer(content):
        category = match.group("category").strip()
        asset_id = match.group("asset_id").strip()
        chapter = extract_chapter_from_id(asset_id)
        chapters = [chapter] if chapter else chapters_for_offset(match.start())
        asset_index[asset_id] = {
            "chapter": chapter,
            "chapters": chapters,
            "category": category,
        }

    print(f"Mapped {len(asset_index)} assets to chapters.")
    return asset_index


def normalize_asset_id(filename):
    stem, _ = os.path.splitext(filename)
    stem = re.sub(r"__r\d{2}$", "", stem, flags=re.IGNORECASE)
    stem = re.sub(r"_\d{5}_?$", "", stem)
    return stem


def resolve_category(asset_id, asset_index, source_category):
    entry = asset_index.get(asset_id)
    if entry and entry.get("category"):
        return normalize_category(entry["category"])
    return normalize_category(source_category)


def get_chapter_from_filename(filename, asset_index):
    asset_id = normalize_asset_id(filename)
    if asset_id in asset_index:
        return asset_index[asset_id].get("chapter")

    match = re.search(r'CH(\d{1,3})', filename, re.IGNORECASE)
    if match:
        return _safe_chapter(match.group(1))

    match = re.search(r'[_\-](\d{2,3})[_\-]', filename)
    if match:
        return _safe_chapter(match.group(1))

    return None


def build_prop_usage_map(prop_db_path):
    if not prop_db_path or not os.path.exists(prop_db_path):
        return {}
    with open(prop_db_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    usage = {}
    for actor in data.get("actors", {}).values():
        for hint in actor.get("prop_hints", []):
            key = hint.get("prop_key") or hint.get("name")
            if not key:
                continue
            slug = slugify(key)
            chapters = usage.setdefault(slug, set())
            for example in hint.get("examples", []):
                chapter_raw = example.get("chapter", "")
                match = re.search(r"(\d{1,3})", chapter_raw)
                chapter = _safe_chapter(match.group(1)) if match else None
                if chapter:
                    chapters.add(chapter)
    return {key: sorted(values) for key, values in usage.items()}


def build_env_usage_map(env_db_path):
    if not env_db_path or not os.path.exists(env_db_path):
        return {}
    with open(env_db_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    usage = {}
    for env_key, entry in data.get("environments", {}).items():
        meta = entry.get("meta", {})
        appearance = meta.get("appearance", "")
        chapters = parse_chapter_list(appearance)
        if chapters:
            usage[slugify(env_key)] = chapters
            tag = meta.get("tag")
            if tag:
                usage[slugify(tag)] = chapters
    return usage


def match_usage_chapters(asset_id, usage_map):
    if not usage_map:
        return []
    slug = slugify(asset_id)
    for prefix in ("prop_", "props_", "env_", "environment_"):
        if slug.startswith(prefix):
            slug = slug[len(prefix):]
            break
    if slug in usage_map:
        return usage_map[slug]
    for key, chapters in usage_map.items():
        if key and key in slug:
            return chapters
    return []


def resolve_chapter_targets(asset_id, filename, asset_index, usage_map):
    targets = []
    entry = asset_index.get(asset_id)
    if entry:
        if entry.get("chapters"):
            targets.extend(entry["chapters"])
        elif entry.get("chapter"):
            targets.append(entry["chapter"])
    if not targets:
        chapter = get_chapter_from_filename(filename, asset_index)
        if chapter:
            targets.append(chapter)
    if usage_map:
        targets.extend(match_usage_chapters(asset_id, usage_map))
    return sorted(set(targets))


def safe_transfer(source, dest_folder, copy=False):
    os.makedirs(dest_folder, exist_ok=True)
    filename = os.path.basename(source)
    dest_path = os.path.join(dest_folder, filename)

    if os.path.exists(dest_path):
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(dest_path):
            new_name = f"{base}_copy{counter}{ext}"
            dest_path = os.path.join(dest_folder, new_name)
            counter += 1
        print(f"Duplicate found. Renaming to {os.path.basename(dest_path)}")

    try:
        if copy:
            shutil.copy2(source, dest_path)
        else:
            shutil.move(source, dest_path)
        return True
    except Exception as e:
        print(f"Error moving {filename}: {e}")
        return False


def iter_source_files(source_dir):
    for root, _, files in os.walk(source_dir):
        for filename in files:
            if filename.lower().endswith(IMAGE_EXTS):
                yield root, filename


def extract_parent_asset_id(rel_root):
    if not rel_root or rel_root == ".":
        return ""
    parts = rel_root.split(os.sep)
    if len(parts) >= 2:
        return parts[1]
    return ""


def distribute_files(source_dir, filmsets_dir, asset_bible_path, categories, layout, copy, dry_run, prop_db_path, env_db_path, use_parent_id):
    if not os.path.exists(source_dir):
        print(f"Source directory not found: {source_dir}")
        return

    asset_index = load_asset_index(asset_bible_path)
    prop_usage = build_prop_usage_map(prop_db_path)
    env_usage = build_env_usage_map(env_db_path)

    moved_count = 0
    global_count = 0
    skipped_count = 0

    for root, filename in iter_source_files(source_dir):
        rel_root = os.path.relpath(root, source_dir)
        first_part = rel_root.split(os.sep)[0].lower() if rel_root != "." else ""
        source_category = first_part if first_part else ""

        asset_id = normalize_asset_id(filename)
        parent_asset_id = extract_parent_asset_id(rel_root)
        if use_parent_id and parent_asset_id:
            if parent_asset_id in asset_index:
                asset_id = parent_asset_id
            elif asset_id not in asset_index and normalize_category(source_category) == source_category:
                asset_id = parent_asset_id
        category = resolve_category(asset_id, asset_index, source_category)
        if categories and not category_matches(category, categories):
            skipped_count += 1
            continue

        usage_map = {}
        if category == "props":
            usage_map = prop_usage
        elif category == "environments":
            usage_map = env_usage

        chapter_targets = resolve_chapter_targets(asset_id, filename, asset_index, usage_map)
        if not chapter_targets:
            chapter_targets = [None]

        for chapter_num in chapter_targets:
            chapter_folder = f"chapter_{chapter_num:03d}" if chapter_num else "chapter_000"
            target_dir = os.path.join(filmsets_dir, chapter_folder, "produced_assets")
            if layout == "flat":
                pass
            else:
                sub = category if category else "uncategorized"
                target_dir = os.path.join(target_dir, "asset_bible", sub)
                if layout == "asset" and asset_id:
                    target_dir = os.path.join(target_dir, asset_id)

            if dry_run:
                print(f"[DRY] {filename} -> {chapter_folder} ({category or 'unknown'})")
                continue

            ok = safe_transfer(os.path.join(root, filename), target_dir, copy=copy)
            if ok and chapter_num:
                moved_count += 1
            elif ok:
                global_count += 1

    print("\nDistribution Complete.")
    print(f"Moved to Chapters: {moved_count}")
    print(f"Moved to Global (000): {global_count}")
    print(f"Skipped (filter): {skipped_count}")
    print(f"Total Processed: {moved_count + global_count}")


def main():
    parser = argparse.ArgumentParser(description="Distribute asset-bible images into chapter folders.")
    parser.add_argument("--source", default=DEFAULT_SOURCE_DIR, help="Source directory to scan")
    parser.add_argument("--filmsets", default=DEFAULT_FILMSETS_DIR, help="Filmsets root directory")
    parser.add_argument("--asset-bible", default=DEFAULT_ASSET_BIBLE, help="Asset bible path")
    parser.add_argument("--prop-db", default=DEFAULT_PROP_DB, help="Prop usage source (ACTOR_PROP_DB.json)")
    parser.add_argument("--env-db", default=DEFAULT_ENV_DB, help="Env usage source (ENVIRONMENT_ASSETS.json)")
    parser.add_argument("--no-prop-db", action="store_true", help="Ignore prop usage mapping")
    parser.add_argument("--no-env-db", action="store_true", help="Ignore env usage mapping")
    parser.add_argument("--category", action="append", help="Filter categories (chars, props, envs)")
    parser.add_argument(
        "--layout",
        choices=("category", "asset", "flat"),
        default="category",
        help="Output layout (default: category)",
    )
    parser.add_argument("--flat", action="store_true", help="(Deprecated) Same as --layout flat")
    parser.add_argument("--no-parent-id", action="store_true", help="Ignore asset ID folder names when distributing")
    move_group = parser.add_mutually_exclusive_group()
    move_group.add_argument("--copy", action="store_true", help="Copy instead of move (default)")
    move_group.add_argument("--move", action="store_true", help="Move instead of copy")
    parser.add_argument("--dry-run", action="store_true", help="Print intended moves only")
    args = parser.parse_args()

    categories = parse_categories(args.category)
    copy = not args.move
    layout = "flat" if args.flat else args.layout
    prop_db_path = None if args.no_prop_db else args.prop_db
    env_db_path = None if args.no_env_db else args.env_db
    distribute_files(
        source_dir=args.source,
        filmsets_dir=args.filmsets,
        asset_bible_path=args.asset_bible,
        categories=categories,
        layout=layout,
        copy=copy,
        dry_run=args.dry_run,
        prop_db_path=prop_db_path,
        env_db_path=env_db_path,
        use_parent_id=not args.no_parent_id,
    )


if __name__ == "__main__":
    main()
