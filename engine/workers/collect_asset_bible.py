import argparse
import os
import re
import shutil

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
DEFAULT_SOURCE = os.path.join(ROOT_PATH, "produced_assets")
DEFAULT_ASSET_BIBLE = os.path.join(ROOT_PATH, "ASSET_BIBLE.md")
DEFAULT_OUTPUT = os.path.join(ROOT_PATH, "produced_assets", "asset_bible")

IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp")

CATEGORY_ALIASES = {
    "character": "characters",
    "characters": "characters",
    "char": "characters",
    "actor": "characters",
    "actors": "characters",
    "character_group": "characters",
    "character_fx": "characters",
    "character_effect": "characters",
    "prop": "props",
    "props": "props",
    "environment": "environments",
    "environments": "environments",
    "env": "environments",
    "location": "environments",
    "vfx": "vfx",
    "fx": "vfx",
    "visual_fx": "visual_fx",
    "visual_effect": "visual_effect",
    "concept_vfx": "concept_vfx",
    "event_fx": "event_fx",
    "ui": "ui_concept",
    "ui_concept": "ui_concept",
    "ui_element": "ui_element",
    "ui_interface": "ui_interface",
    "ui_overlay": "ui_overlay",
    "ui_hud": "ui_hud",
    "ui_fx": "ui_fx",
    "ui_vfx": "ui_vfx",
    "celestial_body": "celestial_body",
    "entity_group": "entity_group",
}

PREFIX_CATEGORY = [
    ("ui_hud", "ui_hud"),
    ("ui_overlay", "ui_overlay"),
    ("ui_interface", "ui_interface"),
    ("ui_element", "ui_element"),
    ("ui_vfx", "ui_vfx"),
    ("ui_fx", "ui_fx"),
    ("ui_", "ui_concept"),
    ("vfx_", "vfx"),
    ("fx_", "vfx"),
    ("env_", "environments"),
    ("environment_", "environments"),
    ("prop_", "props"),
    ("props_", "props"),
    ("char_", "characters"),
    ("character_", "characters"),
    ("veh_", "vehicle"),
    ("vehicle_", "vehicle"),
    ("mob_", "mob"),
    ("npc_", "npc"),
    ("entity_", "entity"),
    ("creature_", "creature"),
    ("structure_", "structure"),
    ("mechanism_", "mechanism"),
    ("substance_", "substance"),
    ("phenomenon_", "phenomenon"),
    ("cel_", "celestial_body"),
]

DEFAULT_EXCLUDES = {"asset_bible", "lora_training", "video", ".venv"}


def normalize_token(text):
    return re.sub(r"[^a-z0-9]+", "", str(text or "").lower())


def normalize_category(text):
    if not text:
        return ""
    token = re.sub(r"[^a-z0-9]+", "_", str(text or "").lower()).strip("_")
    return CATEGORY_ALIASES.get(token, token)


def normalize_asset_filename(filename):
    stem = os.path.splitext(filename)[0]
    stem = re.sub(r"__r\d{2}$", "", stem, flags=re.IGNORECASE)
    stem = re.sub(r"_\d{5}_?$", "", stem)
    return stem


def parse_asset_bible(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as handle:
        content = handle.read()
    header_pattern = re.compile(
        r"^##\s+\[(?P<category>.*?)\]\s+(?P<name>.*?)\s+\(ID:\s*(?P<id>.*?)\)\s*$",
        re.M,
    )
    assets = []
    for match in header_pattern.finditer(content):
        assets.append({
            "id": match.group("id").strip(),
            "name": match.group("name").strip(),
            "category": match.group("category").strip(),
        })
    return assets


def match_asset(assets, stem_token):
    best = None
    best_score = 0
    for asset in assets:
        id_token = asset.get("id_token")
        name_token = asset.get("name_token")
        if id_token and (id_token in stem_token or stem_token in id_token):
            score = 1000 + len(id_token)
            if score > best_score:
                best_score = score
                best = asset
        if name_token and (name_token in stem_token or stem_token in name_token):
            score = len(name_token)
            if score > best_score:
                best_score = score
                best = asset
    return best


def detect_category_from_stem(stem):
    token = normalize_token(stem)
    for prefix, category in PREFIX_CATEGORY:
        if token.startswith(prefix):
            return category
    return ""


def should_skip_file(filename, skip_patterns):
    if not skip_patterns:
        return False
    for pattern in skip_patterns:
        if re.search(pattern, filename, re.IGNORECASE):
            return True
    return False


def safe_copy(source, dest_folder, allow_duplicates, move):
    os.makedirs(dest_folder, exist_ok=True)
    filename = os.path.basename(source)
    dest_path = os.path.join(dest_folder, filename)
    if os.path.exists(dest_path):
        if not allow_duplicates:
            return False, dest_path
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(dest_path):
            dest_path = os.path.join(dest_folder, f"{base}_copy{counter}{ext}")
            counter += 1
    if move:
        shutil.move(source, dest_path)
    else:
        shutil.copy2(source, dest_path)
    return True, dest_path


def iter_images(source_dir, excludes):
    for root, dirs, files in os.walk(source_dir):
        dirs[:] = [d for d in dirs if d not in excludes]
        for filename in files:
            if filename.lower().endswith(IMAGE_EXTS):
                yield root, filename


def main():
    parser = argparse.ArgumentParser(description="Collect produced assets into asset_bible categories.")
    parser.add_argument("--source", default=DEFAULT_SOURCE, help="Source root to scan for images")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="asset_bible output root")
    parser.add_argument("--asset-bible", default=DEFAULT_ASSET_BIBLE, help="ASSET_BIBLE.md path")
    parser.add_argument("--layout", choices=("flat", "by-asset"), default="flat", help="Output layout")
    parser.add_argument("--move", action="store_true", help="Move files instead of copy")
    parser.add_argument("--allow-duplicates", action="store_true", help="Allow duplicate filenames (auto-rename)")
    parser.add_argument("--include-unmatched", action="store_true", help="Also place files without asset matches")
    parser.add_argument("--skip-pattern", action="append", help="Regex pattern to skip filenames")
    parser.add_argument("--exclude", action="append", help="Exclude directory name from scan")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without copying")
    args = parser.parse_args()

    assets = parse_asset_bible(args.asset_bible)
    for asset in assets:
        asset["id_token"] = normalize_token(asset["id"])
        asset["name_token"] = normalize_token(asset["name"])

    excludes = set(DEFAULT_EXCLUDES)
    if args.exclude:
        excludes.update({entry.strip() for entry in args.exclude if entry.strip()})

    skip_patterns = args.skip_pattern or []
    if not skip_patterns:
        skip_patterns = ["comfyui"]

    matched = 0
    skipped = 0
    unmatched = 0

    for root, filename in iter_images(args.source, excludes):
        if os.path.abspath(root).startswith(os.path.abspath(args.output)):
            continue
        if should_skip_file(filename, skip_patterns):
            skipped += 1
            continue

        stem = normalize_asset_filename(filename)
        stem_token = normalize_token(stem)
        match = match_asset(assets, stem_token)

        if match:
            asset_id = match["id"]
            category = normalize_category(match["category"])
        else:
            category = detect_category_from_stem(stem)
            asset_id = stem
            if not category and not args.include_unmatched:
                unmatched += 1
                continue

        category = category or "uncategorized"
        if args.layout == "by-asset":
            dest_dir = os.path.join(args.output, category, asset_id)
        else:
            dest_dir = os.path.join(args.output, category)

        if args.dry_run:
            print(f"[DRY] {os.path.join(root, filename)} -> {dest_dir}")
            matched += 1
            continue

        ok, _ = safe_copy(os.path.join(root, filename), dest_dir, args.allow_duplicates, args.move)
        if ok:
            matched += 1
        else:
            skipped += 1

    print("Collection complete.")
    print(f"Matched/copied: {matched}")
    print(f"Skipped: {skipped}")
    print(f"Unmatched: {unmatched}")


if __name__ == "__main__":
    main()
