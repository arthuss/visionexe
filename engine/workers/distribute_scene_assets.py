import argparse
import json
import os
import re
import shutil
import unicodedata

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
DEFAULT_FILMSETS = os.path.join(ROOT_PATH, "filmsets")
DEFAULT_ASSET_REGISTRY = os.path.join(ROOT_PATH, "asset_registry.json")
DEFAULT_ASSET_BIBLE = os.path.join(ROOT_PATH, "ASSET_BIBLE.md")
DEFAULT_ASSET_BIBLE_DIR = os.path.join(ROOT_PATH, "produced_assets", "asset_bible")
DEFAULT_ACTOR_TRAINING_ROOT = os.path.join(ROOT_PATH, "produced_assets", "lora_training", "actors")
DEFAULT_OUTPUT_SUBDIR = os.path.join("produced_assets", "scene_assets")

IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp")
CHAPTER_PATTERNS = [
    re.compile(r"\bCHAPTERS?\b[^\d]*(\d[\d\s,&\-\u2013\u2014_]*)", re.IGNORECASE),
    re.compile(r"\bKAPITEL\b[^\d]*(\d[\d\s,&\-\u2013\u2014_]*)", re.IGNORECASE),
    re.compile(r"\bCH\b\s*([0-9]{1,3}(?:\s*[-,&_]\s*[0-9]{1,3})*)", re.IGNORECASE),
    re.compile(r"\bCH(\d{1,3})\b", re.IGNORECASE),
]


def normalize_token(text):
    cleaned = unicodedata.normalize("NFKD", str(text or "")).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "", cleaned.lower())


def tokenize_words(text):
    cleaned = unicodedata.normalize("NFKD", str(text or "")).encode("ascii", "ignore").decode("ascii")
    return [w for w in re.split(r"[^a-z0-9]+", cleaned.lower()) if w]


def slugify(value):
    text = unicodedata.normalize("NFKD", str(value or "")).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_") or "unknown"


def normalize_category(text):
    if not text:
        return "uncategorized"
    return re.sub(r"[^a-z0-9]+", "_", str(text).lower()).strip("_") or "uncategorized"


def read_text(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except OSError:
        return ""


def parse_asset_bible(path):
    content = read_text(path)
    if not content:
        return []
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


def parse_chapter_list(text):
    if not text:
        return []
    cleaned = text.replace("\u2013", "-").replace("\u2014", "-").replace("_", " ")
    chapters = []
    for match in re.finditer(r"(\d{1,3})\s*-\s*(\d{1,3})", cleaned):
        start = int(match.group(1))
        end = int(match.group(2))
        if start > end:
            start, end = end, start
        chapters.extend(range(start, end + 1))
    cleaned = re.sub(r"(\d{1,3})\s*-\s*(\d{1,3})", " ", cleaned)
    for match in re.finditer(r"\b(\d{1,3})\b", cleaned):
        num = int(match.group(1))
        if 1 <= num <= 108:
            chapters.append(num)
    return sorted(set(chapters))


def parse_asset_bible_blocks(path):
    content = read_text(path)
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
        assets.append({
            "id": match.group("id").strip(),
            "category": match.group("category").strip(),
            "block": block,
        })
    return assets


def build_chapter_map(asset_bible_path):
    chapter_map = {}
    assets = parse_asset_bible_blocks(asset_bible_path)
    for asset in assets:
        block = asset.get("block", "")
        chapters = []
        for line in block.splitlines():
            for pattern in CHAPTER_PATTERNS:
                match = pattern.search(line)
                if match:
                    chapters.extend(parse_chapter_list(match.group(1)))
        chapters = sorted(set(chapters))
        if chapters:
            chapter_map[asset["id"]] = chapters
    return chapter_map


def load_phase_index(path):
    if not path or not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (json.JSONDecodeError, OSError):
        return {}
    actors = payload.get("actors") if isinstance(payload, dict) else None
    if not isinstance(actors, dict):
        return {}
    phase_index = {}
    for actor_name, data in actors.items():
        phases = data.get("phases") if isinstance(data, dict) else None
        if not isinstance(phases, list):
            continue
        actor_norm = normalize_token(actor_name)
        if not actor_norm:
            continue
        for phase in phases:
            if not isinstance(phase, dict):
                continue
            name = phase.get("name")
            ranges = parse_chapter_list(phase.get("chapters"))
            if name and ranges:
                phase_index.setdefault(actor_norm, []).append({"name": name, "ranges": ranges})
    return phase_index


def phase_for_chapter(phase_index, actor_name, chapter_num):
    if not phase_index or not actor_name or chapter_num is None:
        return None
    actor_norm = normalize_token(actor_name)
    if not actor_norm:
        return None
    for phase in phase_index.get(actor_norm, []):
        for entry in phase.get("ranges", []):
            if isinstance(entry, int):
                if entry == chapter_num:
                    return phase.get("name")
                continue
            if isinstance(entry, (list, tuple)) and len(entry) == 2:
                start, end = entry
                if start <= chapter_num <= end:
                    return phase.get("name")
    return None


def normalize_asset_filename(filename):
    stem = os.path.splitext(filename)[0]
    stem = re.sub(r"__r\d{2}$", "", stem, flags=re.IGNORECASE)
    stem = re.sub(r"_\d{5}_?$", "", stem)
    return stem


def scan_asset_bible_outputs(base_dir):
    outputs = {}
    if not base_dir or not os.path.isdir(base_dir):
        return outputs
    for category in os.listdir(base_dir):
        category_path = os.path.join(base_dir, category)
        if not os.path.isdir(category_path):
            continue
        subdirs = [d for d in os.listdir(category_path) if os.path.isdir(os.path.join(category_path, d))]
        if subdirs:
            for subdir in subdirs:
                sub_path = os.path.join(category_path, subdir)
                files = []
                for root, _, filenames in os.walk(sub_path):
                    for filename in filenames:
                        if filename.lower().endswith(IMAGE_EXTS):
                            files.append(os.path.join(root, filename))
                if files:
                    entry = outputs.setdefault(subdir, {"category": category, "files": []})
                    entry["files"].extend(files)
        else:
            for filename in os.listdir(category_path):
                if not filename.lower().endswith(IMAGE_EXTS):
                    continue
                asset_id = normalize_asset_filename(filename)
                entry = outputs.setdefault(asset_id, {"category": category, "files": []})
                entry["files"].append(os.path.join(category_path, filename))
    return outputs


def load_registry(path, asset_bible_path, asset_bible_dir):
    chapter_map = build_chapter_map(asset_bible_path)
    if path and os.path.exists(path):
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        assets = payload.get("assets", [])
        normalized = []
        for entry in assets:
            if not entry.get("id"):
                continue
            chapters = chapter_map.get(entry.get("id"), [])
            normalized.append({
                "id": entry.get("id"),
                "name": entry.get("name") or entry.get("id"),
                "category": entry.get("category") or entry.get("category_slug"),
                "outputs": entry.get("asset_bible_outputs") or [],
                "asset_dir": entry.get("asset_bible_dir") or "",
                "chapters": chapters,
            })
        return normalized
    assets = parse_asset_bible(asset_bible_path)
    outputs = scan_asset_bible_outputs(asset_bible_dir)
    merged = []
    for asset in assets:
        entry = outputs.get(asset["id"])
        files = entry.get("files", []) if entry else []
        merged.append({
            "id": asset["id"],
            "name": asset["name"],
            "category": asset.get("category"),
            "outputs": [os.path.relpath(path, ROOT_PATH) for path in files],
            "asset_dir": "",
            "chapters": chapter_map.get(asset["id"], []),
        })
    for asset_id, entry in outputs.items():
        if any(item["id"] == asset_id for item in merged):
            continue
        merged.append({
            "id": asset_id,
            "name": asset_id,
            "category": entry.get("category"),
            "outputs": [os.path.relpath(path, ROOT_PATH) for path in entry.get("files", [])],
            "asset_dir": "",
            "chapters": chapter_map.get(asset_id, []),
        })
    return merged


def build_asset_index(assets):
    for asset in assets:
        asset["id_token"] = normalize_token(asset.get("id"))
        asset["name_token"] = normalize_token(asset.get("name"))
        asset["id_words"] = tokenize_words(asset.get("id"))
        asset["name_words"] = tokenize_words(asset.get("name"))
        asset["category_slug"] = normalize_category(asset.get("category"))
    return assets


def match_assets(query, assets, max_matches, chapter_num=None, category_allow=None, category_deny=None):
    token = normalize_token(query)
    words = tokenize_words(query)
    if not token and not words:
        return []
    matches = []
    for asset in assets:
        category = asset.get("category_slug")
        if category_allow and category not in category_allow:
            continue
        if category_deny and category in category_deny:
            continue
        if chapter_num and asset.get("chapters"):
            if chapter_num not in asset["chapters"]:
                continue
        id_token = asset.get("id_token")
        name_token = asset.get("name_token")
        score = 0
        if id_token and (id_token in token or token in id_token):
            score = 1000 + len(id_token)
        elif name_token and (name_token in token or token in name_token):
            score = len(name_token)
        elif words:
            asset_words = set(asset.get("id_words", []) + asset.get("name_words", []))
            overlap = asset_words.intersection(words)
            if overlap:
                score = len(overlap) * 10 + sum(len(word) for word in overlap)
        if score:
            matches.append((score, asset))
    matches.sort(key=lambda item: (-item[0], item[1].get("id") or ""))
    if max_matches <= 0:
        return []
    return [asset for _, asset in matches[:max_matches]]


def get_chapters(chapter_arg, filmsets_root):
    all_chapters = sorted([d for d in os.listdir(filmsets_root) if d.startswith("chapter_")])
    if chapter_arg == "all":
        return all_chapters
    selected = []
    parts = str(chapter_arg).split(",")
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = part.split("-", 1)
            if start.isdigit() and end.isdigit():
                for num in range(int(start), int(end) + 1):
                    name = f"chapter_{num:03d}"
                    if name in all_chapters:
                        selected.append(name)
        elif part.isdigit():
            name = f"chapter_{int(part):03d}"
            if name in all_chapters:
                selected.append(name)
    return sorted(set(selected))


def extract_regie_json(text):
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("REGIE_JSON:"):
            payload = line.split(":", 1)[1].strip()
            try:
                return json.loads(payload)
            except json.JSONDecodeError:
                return {}
    return {}


def iter_scenes(script_text):
    scene_splits = re.split(r"(^##\s+\[ACT\s+\d+\]\s+\[SCENE\s+[\d\.]+\])", script_text, flags=re.M)
    current_header = ""
    for part in scene_splits:
        if part.strip().startswith("## [ACT"):
            current_header = part.strip()
            continue
        if not current_header:
            continue
        match = re.search(r"\[SCENE\s+([\d\.]+)\]", current_header)
        scene_num = match.group(1) if match else "0.0"
        yield scene_num, part


def safe_copy(source, dest_folder, allow_duplicates, move):
    os.makedirs(dest_folder, exist_ok=True)
    filename = os.path.basename(source)
    dest_path = os.path.join(dest_folder, filename)
    if os.path.exists(dest_path):
        if not allow_duplicates:
            return False
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(dest_path):
            dest_path = os.path.join(dest_folder, f"{base}_copy{counter}{ext}")
            counter += 1
    if move:
        shutil.move(source, dest_path)
    else:
        shutil.copy2(source, dest_path)
    return True


def extract_variant(filename):
    match = re.search(r"__r(\d{2})", filename, re.IGNORECASE)
    if match:
        return f"r{match.group(1)}"
    return "base"


def parse_timeline(value):
    if not value:
        return "all"
    text = str(value).strip().lower()
    if text in ("all", "base", "none"):
        return text
    if text.isdigit():
        return f"r{int(text):02d}"
    match = re.match(r"r(\d{2})", text)
    if match:
        return f"r{match.group(1)}"
    return text


def iter_training_images(actor_root, actor_name, phase_name):
    if not actor_root or not actor_name or not phase_name:
        return []
    actor_slug = slugify(actor_name)
    phase_slug = slugify(phase_name)
    base_dir = os.path.join(actor_root, actor_slug, phase_slug)
    if not os.path.isdir(base_dir):
        return []
    images = []
    for root, _, filenames in os.walk(base_dir):
        for filename in filenames:
            if filename.lower().endswith(IMAGE_EXTS):
                images.append(os.path.join(root, filename))
    return sorted(set(images))


def resolve_asset_files(asset):
    files = []
    outputs = asset.get("outputs") or []
    for rel in outputs:
        path = os.path.join(ROOT_PATH, rel)
        if os.path.exists(path):
            files.append(path)
    asset_dir = asset.get("asset_dir")
    if asset_dir:
        full_dir = os.path.join(ROOT_PATH, asset_dir)
        if os.path.isdir(full_dir):
            for root, _, filenames in os.walk(full_dir):
                for filename in filenames:
                    if filename.lower().endswith(IMAGE_EXTS):
                        files.append(os.path.join(root, filename))
    return sorted(set(files))


def main():
    parser = argparse.ArgumentParser(description="Distribute assets per scene based on REGIE_JSON.")
    parser.add_argument("--chapter", default="all", help="Chapter range (e.g. 1-5) or all")
    parser.add_argument("--filmsets", default=DEFAULT_FILMSETS, help="Filmsets root")
    parser.add_argument("--asset-registry", default=DEFAULT_ASSET_REGISTRY, help="asset_registry.json path")
    parser.add_argument("--asset-bible", default=DEFAULT_ASSET_BIBLE, help="ASSET_BIBLE.md path")
    parser.add_argument("--asset-bible-dir", default=DEFAULT_ASSET_BIBLE_DIR, help="produced_assets/asset_bible path")
    parser.add_argument("--lora-training-set", default=os.path.join(ROOT_PATH, "LORA_TRAINING_SET.json"), help="LORA_TRAINING_SET.json path")
    parser.add_argument("--actor-root", default=DEFAULT_ACTOR_TRAINING_ROOT, help="Actor training images root")
    parser.add_argument("--output-subdir", default=DEFAULT_OUTPUT_SUBDIR, help="Subdir under produced_assets")
    parser.add_argument("--max-matches", type=int, default=1, help="Max asset matches per token")
    parser.add_argument("--include-actors", action="store_true", help="Include actor entries from REGIE_JSON")
    parser.add_argument("--actor-source", choices=("training", "asset", "both"), default="training", help="Source for actor assets")
    parser.add_argument("--report-unmatched", action="store_true", help="Log tokens with no asset matches")
    parser.add_argument("--timeline", default="all", help="Timeline variant: all | none | base | <number> | rNN")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without copying")
    parser.add_argument("--move", action="store_true", help="Move instead of copy")
    parser.add_argument("--allow-duplicates", action="store_true", help="Allow duplicate filenames (auto-rename)")
    args = parser.parse_args()

    assets = load_registry(args.asset_registry, args.asset_bible, args.asset_bible_dir)
    assets = build_asset_index(assets)
    phase_index = load_phase_index(args.lora_training_set)
    chapters = get_chapters(args.chapter, args.filmsets)
    total = 0

    for chapter in chapters:
        script_path = os.path.join(args.filmsets, chapter, "DREHBUCH_HOLLYWOOD.md")
        if not os.path.exists(script_path):
            continue
        script_text = read_text(script_path)
        for scene_num, scene_text in iter_scenes(script_text):
            regie = extract_regie_json(scene_text)
            if not isinstance(regie, dict):
                continue
            tokens = []
            env_name = regie.get("environment")
            if isinstance(env_name, str):
                tokens.append(("environment", env_name))
            for prop in regie.get("props") or []:
                if isinstance(prop, str):
                    tokens.append(("prop", prop))
                elif isinstance(prop, dict) and prop.get("name"):
                    tokens.append(("prop", prop["name"]))
            if args.include_actors:
                for actor in regie.get("actors") or []:
                    if isinstance(actor, dict) and actor.get("name"):
                        tokens.append(("actor", actor["name"], actor))
            if not tokens:
                continue

            scene_dir = os.path.join(args.filmsets, chapter, args.output_subdir, f"scene_{scene_num}")
            chapter_num = int(chapter.split("_")[1]) if "_" in chapter else None
            timeline = parse_timeline(args.timeline)
            for token_entry in tokens:
                token_type = token_entry[0]
                token_value = token_entry[1]
                actor_meta = token_entry[2] if len(token_entry) > 2 else None
                category_allow = None
                category_deny = None
                if token_type == "environment":
                    category_allow = {"environments"}
                elif token_type == "actor":
                    category_allow = {"characters"}
                elif token_type == "prop":
                    category_deny = {"environments", "characters"}
                actor_files = []
                actor_phase = None
                if token_type == "actor" and args.actor_source in ("training", "both"):
                    actor_phase = phase_for_chapter(phase_index, token_value, chapter_num)
                    if not actor_phase and isinstance(actor_meta, dict):
                        actor_phase = actor_meta.get("phase") or actor_meta.get("state")
                    actor_files = iter_training_images(args.actor_root, token_value, actor_phase)

                matches = []
                if token_type != "actor" or args.actor_source in ("asset", "both"):
                    matches = match_assets(token_value, assets, args.max_matches, chapter_num, category_allow, category_deny)

                if actor_files:
                    actor_slug = slugify(token_value)
                    phase_slug = slugify(actor_phase)
                    base_dest = os.path.join(scene_dir, "characters", f"{actor_slug}__{phase_slug}")
                    variant = "base"
                    if timeline not in ("all", "none") and timeline != variant:
                        actor_files = []
                    for file_path in actor_files:
                        dest_dir = base_dest
                        if timeline == "all":
                            dest_dir = os.path.join(scene_dir, f"timeline_{variant}", "characters", f"{actor_slug}__{phase_slug}")
                        if args.dry_run:
                            print(f"[DRY] {file_path} -> {dest_dir}")
                            total += 1
                            continue
                        ok = safe_copy(file_path, dest_dir, args.allow_duplicates, args.move)
                        if ok:
                            total += 1
                for asset in matches:
                    files = resolve_asset_files(asset)
                    if not files:
                        continue
                    base_dest = os.path.join(scene_dir, asset.get("category_slug") or "uncategorized", asset.get("id"))
                    for file_path in files:
                        variant = extract_variant(os.path.basename(file_path))
                        if timeline not in ("all", "none"):
                            if variant != timeline:
                                continue
                        dest_dir = base_dest
                        if timeline == "all":
                            dest_dir = os.path.join(scene_dir, f"timeline_{variant}", asset.get("category_slug") or "uncategorized", asset.get("id"))
                        if args.dry_run:
                            print(f"[DRY] {file_path} -> {dest_dir}")
                            total += 1
                            continue
                        ok = safe_copy(file_path, dest_dir, args.allow_duplicates, args.move)
                        if ok:
                            total += 1
                if args.report_unmatched and not matches and not actor_files:
                    print(f"[NO MATCH] {chapter} scene {scene_num} {token_type}: {token_value}")

    print(f"Scene distribution complete. Files copied/moved: {total}")


if __name__ == "__main__":
    main()
