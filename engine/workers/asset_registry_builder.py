import argparse
import json
import os
import re
import time

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
DEFAULT_ASSET_BIBLE = os.path.join(ROOT_PATH, "ASSET_BIBLE.md")
DEFAULT_ASSET_BIBLE_DIR = os.path.join(ROOT_PATH, "produced_assets", "asset_bible")
DEFAULT_LORA_TRAINING_SET = os.path.join(ROOT_PATH, "LORA_TRAINING_SET.json")
DEFAULT_LORA_TRAINING_QUEUE = os.path.join(ROOT_PATH, "LORA_TRAINING_QUEUE.json")
DEFAULT_LORA_PROP_QUEUE = os.path.join(ROOT_PATH, "LORA_PROP_QUEUE.json")
DEFAULT_ENV_ASSETS = os.path.join(ROOT_PATH, "ENVIRONMENT_ASSETS.json")
DEFAULT_LORA_ROOT = os.path.join(ROOT_PATH, "produced_assets", "lora_training")
DEFAULT_REGISTRY_OUT = os.path.join(ROOT_PATH, "asset_registry.json")
DEFAULT_ENV_BRIDGE_OUT = os.path.join(ROOT_PATH, "environment_bridge.json")

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


def normalize_token(text):
    return re.sub(r"[^a-z0-9]+", "", str(text or "").lower())


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "_", str(text or "").lower()).strip("_")


def normalize_asset_filename(filename):
    stem = os.path.splitext(filename)[0]
    stem = re.sub(r"__r\d{2}$", "", stem, flags=re.IGNORECASE)
    stem = re.sub(r"_\d{5}_?$", "", stem)
    return stem


def read_text(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except OSError:
        return ""


def load_json(path):
    if not path or not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def parse_asset_bible(path):
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
            "name": match.group("name").strip(),
            "category": match.group("category").strip(),
            "block": block,
        })
    return assets


def normalize_category(value):
    if not value:
        return ""
    token = re.sub(r"[^a-z0-9]+", "_", str(value or "").lower()).strip("_")
    return CATEGORY_ALIASES.get(token, token)


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


def load_training_set(path):
    data = load_json(path)
    if not isinstance(data, dict):
        return {"actors": {}, "locations": {}}
    return {
        "actors": data.get("actors", {}) if isinstance(data.get("actors"), dict) else {},
        "locations": data.get("locations", {}) if isinstance(data.get("locations"), dict) else {},
    }


def load_training_queue(path):
    data = load_json(path)
    if not isinstance(data, list):
        return []
    return data


def load_prop_queue(path):
    data = load_json(path)
    if not isinstance(data, list):
        return []
    return data


def scan_lora_files(lora_root):
    loras = []
    if not lora_root or not os.path.isdir(lora_root):
        return loras
    for root, _, filenames in os.walk(lora_root):
        for filename in filenames:
            if not filename.lower().endswith(".safetensors"):
                continue
            full_path = os.path.join(root, filename)
            rel_path = os.path.relpath(full_path, ROOT_PATH)
            loras.append({
                "path": full_path,
                "path_rel": rel_path,
                "slug": normalize_token(filename),
            })
    return loras


def find_lora_matches(entry, loras, category):
    tokens = {
        normalize_token(entry.get("id")),
        normalize_token(entry.get("name")),
        normalize_token(entry.get("asset_id")),
    }
    tokens = {t for t in tokens if t}
    matches = []
    for item in loras:
        slug = item["slug"]
        if category == "environments" and "env__" not in slug and "environment" not in slug:
            continue
        if category == "characters" and "env__" in slug:
            continue
        if any(token in slug for token in tokens):
            matches.append(item["path_rel"])
    return sorted(set(matches))


def build_actor_training_map(training_queue):
    mapping = {}
    for item in training_queue:
        if item.get("entity_type") != "actor":
            continue
        actor = item.get("entity_name")
        if not actor:
            continue
        actor_norm = normalize_token(actor)
        entry = mapping.setdefault(actor_norm, [])
        entry.append({
            "actor": actor,
            "phase": item.get("phase_name"),
            "output_dir": item.get("output_dir"),
            "training_target_dir": item.get("training_target_dir"),
            "workflow": item.get("workflow"),
        })
    return mapping


def build_prop_training_map(prop_queue):
    mapping = {}
    for item in prop_queue:
        prop = item.get("prop_name") or item.get("entity_name")
        if not prop:
            continue
        prop_norm = normalize_token(prop)
        entry = mapping.setdefault(prop_norm, [])
        entry.append({
            "prop": prop,
            "actor_slug": item.get("actor_slug"),
            "output_dir": item.get("output_dir"),
            "workflow": item.get("workflow"),
        })
    return mapping


def load_env_assets(path):
    data = load_json(path)
    if not isinstance(data, dict):
        return []
    envs = []
    for key, entry in data.get("environments", {}).items():
        meta = entry.get("meta", {})
        envs.append({
            "key": key,
            "folder": entry.get("folder"),
            "tag": meta.get("tag"),
            "appearance": meta.get("appearance"),
        })
    return envs


def match_env_geo(entry, env_assets):
    tokens = {
        normalize_token(entry.get("id")),
        normalize_token(entry.get("name")),
    }
    tokens = {t for t in tokens if t}
    best = None
    best_score = 0
    candidates = []
    for env in env_assets:
        options = [
            normalize_token(env.get("key")),
            normalize_token(env.get("folder")),
            normalize_token(env.get("tag")),
        ]
        options = [o for o in options if o]
        score = 0
        for token in tokens:
            for option in options:
                if token in option or option in token:
                    score = max(score, len(option))
        if score:
            candidates.append(env)
        if score > best_score:
            best_score = score
            best = env
    return best, candidates


def ensure_dir(path):
    if path:
        os.makedirs(path, exist_ok=True)


def main():
    parser = argparse.ArgumentParser(description="Build a unified asset registry.")
    parser.add_argument("--registry-out", default=DEFAULT_REGISTRY_OUT, help="Output registry JSON path")
    parser.add_argument("--env-bridge-out", default=DEFAULT_ENV_BRIDGE_OUT, help="Output environment bridge JSON path")
    parser.add_argument("--asset-bible", default=DEFAULT_ASSET_BIBLE, help="ASSET_BIBLE.md path")
    parser.add_argument("--asset-bible-dir", default=DEFAULT_ASSET_BIBLE_DIR, help="produced_assets/asset_bible path")
    parser.add_argument("--lora-training-set", default=DEFAULT_LORA_TRAINING_SET, help="LORA_TRAINING_SET.json path")
    parser.add_argument("--lora-training-queue", default=DEFAULT_LORA_TRAINING_QUEUE, help="LORA_TRAINING_QUEUE.json path")
    parser.add_argument("--lora-prop-queue", default=DEFAULT_LORA_PROP_QUEUE, help="LORA_PROP_QUEUE.json path")
    parser.add_argument("--env-assets", default=DEFAULT_ENV_ASSETS, help="ENVIRONMENT_ASSETS.json path")
    parser.add_argument("--lora-root", default=DEFAULT_LORA_ROOT, help="produced_assets/lora_training path")
    parser.add_argument("--create-dirs", action="store_true", help="Create missing training and asset folders")
    args = parser.parse_args()

    assets = parse_asset_bible(args.asset_bible)
    output_index = scan_asset_bible_outputs(args.asset_bible_dir)
    training_set = load_training_set(args.lora_training_set)
    training_queue = load_training_queue(args.lora_training_queue)
    prop_queue = load_prop_queue(args.lora_prop_queue)
    env_assets = load_env_assets(args.env_assets)
    loras = scan_lora_files(args.lora_root)

    registry = {}
    for asset in assets:
        category_slug = normalize_category(asset["category"])
        registry[asset["id"]] = {
            "id": asset["id"],
            "name": asset["name"],
            "category": asset["category"],
            "category_slug": category_slug,
            "asset_bible_block": asset["block"],
            "asset_bible_outputs": [],
            "asset_bible_dir": "",
            "lora_files": [],
            "training": {},
            "env_geo": {},
        }
        if category_slug:
            registry[asset["id"]]["asset_bible_dir"] = os.path.relpath(
                os.path.join(args.asset_bible_dir, category_slug, asset["id"]),
                ROOT_PATH,
            )
            if args.create_dirs:
                ensure_dir(os.path.join(ROOT_PATH, registry[asset["id"]]["asset_bible_dir"]))

    for asset_id, entry in output_index.items():
        asset = registry.get(asset_id)
        if not asset:
            category_slug = normalize_category(entry.get("category"))
            registry[asset_id] = {
                "id": asset_id,
                "name": asset_id,
                "category": entry.get("category"),
                "category_slug": category_slug,
                "asset_bible_block": "",
                "asset_bible_outputs": [],
                "asset_bible_dir": "",
                "lora_files": [],
                "training": {},
                "env_geo": {},
            }
            asset = registry[asset_id]
        files = [os.path.relpath(path, ROOT_PATH) for path in entry.get("files", [])]
        asset["asset_bible_outputs"] = sorted(set(asset["asset_bible_outputs"] + files))
        if entry.get("category"):
            asset["category"] = asset["category"] or entry["category"]
            asset["category_slug"] = asset.get("category_slug") or normalize_category(entry["category"])
        if asset.get("category_slug"):
            asset["asset_bible_dir"] = os.path.relpath(
                os.path.join(args.asset_bible_dir, asset["category_slug"], asset["id"]),
                ROOT_PATH,
            )
            if args.create_dirs:
                ensure_dir(os.path.join(ROOT_PATH, asset["asset_bible_dir"]))

    actor_training = build_actor_training_map(training_queue)
    prop_training = build_prop_training_map(prop_queue)

    for actor_name, data in training_set.get("actors", {}).items():
        actor_norm = normalize_token(actor_name)
        target = None
        for asset in registry.values():
            if normalize_token(asset.get("name")) == actor_norm:
                target = asset
                break
        if not target:
            asset_id = f"CHAR_{slugify(actor_name)}"
            target = registry.setdefault(asset_id, {
                "id": asset_id,
                "name": actor_name,
                "category": "characters",
                "category_slug": "characters",
                "asset_bible_block": "",
                "asset_bible_outputs": [],
                "asset_bible_dir": "",
                "lora_files": [],
                "training": {},
                "env_geo": {},
            })
        target["training"].setdefault("actor_phases", [])
        for phase in data.get("phases", []):
            phase_name = phase.get("name")
            phase_slug = slugify(phase_name)
            actor_slug = slugify(actor_name)
            default_dir = os.path.join(args.lora_root, "actors", actor_slug, phase_slug)
            phase_entry = {
                "phase": phase_name,
                "chapters": phase.get("chapters"),
                "keywords": phase.get("keywords"),
                "training_dir": os.path.relpath(default_dir, ROOT_PATH),
            }
            target["training"]["actor_phases"].append(phase_entry)
            if args.create_dirs:
                ensure_dir(default_dir)

        queue_entries = actor_training.get(actor_norm, [])
        if queue_entries:
            target["training"]["actor_queue"] = queue_entries

    for prop_norm, entries in prop_training.items():
        target = None
        for asset in registry.values():
            if normalize_token(asset.get("name")) == prop_norm or normalize_token(asset.get("id")) == prop_norm:
                target = asset
                break
        if not target:
            asset_id = f"PROP_{prop_norm.upper()}" if prop_norm else f"PROP_{len(registry)+1}"
            target = registry.setdefault(asset_id, {
                "id": asset_id,
                "name": asset_id,
                "category": "props",
                "category_slug": "props",
                "asset_bible_block": "",
                "asset_bible_outputs": [],
                "asset_bible_dir": "",
                "lora_files": [],
                "training": {},
                "env_geo": {},
            })
        target["training"]["prop_queue"] = entries
        if args.create_dirs:
            for entry in entries:
                ensure_dir(entry.get("output_dir"))

    env_bridge = []
    for asset in registry.values():
        if normalize_token(asset.get("category_slug")) != "environments":
            continue
        best, candidates = match_env_geo(asset, env_assets)
        asset["env_geo"] = {
            "best_match": best,
            "candidates": candidates,
        }
        if best:
            folder = best.get("folder") or best.get("key")
            env_bridge.append({
                "asset_id": asset.get("id"),
                "asset_name": asset.get("name"),
                "geo_key": best.get("key"),
                "geo_folder": f"Environments/{folder}" if folder else "",
                "geo_tag": best.get("tag"),
                "match_reason": "slug",
            })

    for asset in registry.values():
        category = normalize_token(asset.get("category_slug"))
        asset["lora_files"] = find_lora_matches(asset, loras, category)

    registry_payload = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "root": ROOT_PATH,
        "assets": sorted(registry.values(), key=lambda item: item.get("id") or ""),
    }
    with open(args.registry_out, "w", encoding="utf-8") as handle:
        json.dump(registry_payload, handle, indent=2, ensure_ascii=False)

    bridge_payload = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "root": ROOT_PATH,
        "bridge": env_bridge,
    }
    if args.env_bridge_out:
        with open(args.env_bridge_out, "w", encoding="utf-8") as handle:
            json.dump(bridge_payload, handle, indent=2, ensure_ascii=False)

    print(f"Wrote registry: {args.registry_out}")
    if args.env_bridge_out:
        print(f"Wrote env bridge: {args.env_bridge_out}")


if __name__ == "__main__":
    main()
