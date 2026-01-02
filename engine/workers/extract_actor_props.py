import argparse
import json
import os
import re
import unicodedata

ROOT_PATH = os.path.abspath(r"C:\Users\sasch\henoch")
ASSET_BIBLE = os.path.join(ROOT_PATH, "ASSET_BIBLE.md")
FULL_ACTOR_DB = os.path.join(ROOT_PATH, "FULL_ACTOR_DB.json")

OUTPUT_DB = os.path.join(ROOT_PATH, "ACTOR_PROP_DB.json")
OUTPUT_MD = os.path.join(ROOT_PATH, "ACTOR_PROP_SUMMARY.md")

ACTOR_DIR = os.path.join(ROOT_PATH, "produced_assets", "lora_training", "actors")

ACTOR_SECTION_RE = re.compile(r"^## \[(?P<type>[A-Z_]+)\] (?P<name>.+?)(?: \\(ID:.*\\))?$")
PROPS_HEADER_RE = re.compile(r"^###\\s+3\\.\\s+PROPS\\s*&\\s*EQUIPMENT", re.IGNORECASE)
HEADER_RE = re.compile(r"^(##|###)\\s+")

ACTOR_TYPES = {"CHARACTER", "CREATURE"}

ALIASES = [
    ("henoch", "henoch"),
    ("enoch", "henoch"),
    ("azazel", "azazel"),
    ("uriel", "uriel"),
    ("michael", "michael"),
    ("gabriel", "gabriel"),
    ("kernel", "kernel"),
    ("system admin", "system_admin"),
    ("time architect", "timearchitect"),
    ("biopunk prophet", "biopunk_prophet"),
    ("exeget:os", "exeget_os"),
    ("exeget os", "exeget_os"),
    ("earth", "earth"),
]

PROP_HINT_PATTERNS = [
    ("obsidian tablet", "Obsidian Tablet"),
    ("stone tablet", "Stone Tablet"),
    ("glass tablet", "Glass Tablet"),
    ("tablet", "Tablet"),
    ("glove", "Glove"),
    ("gauntlet", "Gauntlet"),
    ("staff", "Staff"),
    ("rod", "Rod"),
    ("visor", "Visor"),
    ("helmet", "Helmet"),
    ("mask", "Mask"),
    ("sword", "Sword"),
    ("dagger", "Dagger"),
    ("shackles", "Shackles"),
    ("chains", "Chains"),
    ("crown", "Crown"),
    ("halo", "Halo"),
    ("serum", "Serum"),
    ("syringe", "Syringe"),
    ("vial", "Vial"),
    ("orb", "Orb"),
    ("cube", "Cube"),
    ("dodecahedron", "Dodecahedron"),
    ("monolith", "Monolith"),
    ("amulet", "Amulet"),
    ("ring", "Ring"),
    ("scroll", "Scroll"),
    ("horns", "Horns"),
    ("antenna", "Antenna"),
]


def slugify(text):
    if text is None:
        return "unknown"
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_").lower()
    return text or "unknown"


def map_actor_slug(name, existing_slugs):
    if not name:
        return "unknown"
    lowered = name.lower()
    for key, slug in ALIASES:
        if key in lowered:
            return slug
    slug = slugify(name)
    if existing_slugs and slug in existing_slugs:
        return slug
    return slug


def parse_prop_line(line):
    text = line.strip().lstrip("*- ").strip()
    if not text:
        return None
    if text.lower().startswith("n/a"):
        return None

    bold_match = re.match(r"\\*\\*(.+?)\\*\\*\\s*[:\\-–]?\\s*(.*)$", text)
    if bold_match:
        name = bold_match.group(1).strip()
        desc = bold_match.group(2).strip()
        return name, desc

    if ":" in text:
        name, desc = text.split(":", 1)
        return name.strip(), desc.strip()

    return text.strip(), ""


def extract_props_from_asset_bible(path, existing_slugs, only_existing):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    actors = {}
    current_actor = None
    current_type = None
    in_props = False

    for line in lines:
        header_match = ACTOR_SECTION_RE.match(line.strip())
        if header_match:
            current_type = header_match.group("type").strip().upper()
            current_actor = header_match.group("name").strip()
            in_props = False
            continue

        if HEADER_RE.match(line) and not PROPS_HEADER_RE.match(line):
            in_props = False

        if PROPS_HEADER_RE.match(line):
            in_props = True
            continue

        if not in_props or not current_actor or current_type not in ACTOR_TYPES:
            continue

        if not line.strip().startswith(("*", "-")):
            continue

        parsed = parse_prop_line(line)
        if not parsed:
            continue

        prop_name, prop_desc = parsed
        actor_slug = map_actor_slug(current_actor, existing_slugs)

        if only_existing and existing_slugs and actor_slug not in existing_slugs:
            continue

        actor_entry = actors.setdefault(actor_slug, {
            "display_names": set(),
            "props": [],
            "prop_hints": [],
        })

        actor_entry["display_names"].add(current_actor)
        prop_key = slugify(prop_name)

        if any(p.get("prop_key") == prop_key for p in actor_entry["props"]):
            continue

        actor_entry["props"].append({
            "name": prop_name,
            "description": prop_desc,
            "prop_key": prop_key,
            "source": "asset_bible",
        })

    for actor in actors.values():
        actor["display_names"] = sorted(actor["display_names"])

    return actors


def extract_prop_hints(full_db_path, actors, existing_slugs, only_existing):
    if not os.path.exists(full_db_path):
        return

    with open(full_db_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    actor_entries = data.get("actors", {})
    patterns = [(re.compile(re.escape(pat), re.IGNORECASE), name) for pat, name in PROP_HINT_PATTERNS]

    for raw_name, entries in actor_entries.items():
        actor_slug = map_actor_slug(raw_name, existing_slugs)
        if only_existing and existing_slugs and actor_slug not in existing_slugs:
            continue

        actor_entry = actors.setdefault(actor_slug, {
            "display_names": sorted(set([raw_name])),
            "props": [],
            "prop_hints": [],
        })
        if raw_name not in actor_entry["display_names"]:
            actor_entry["display_names"].append(raw_name)

        hints = {p["prop_key"]: p for p in actor_entry.get("prop_hints", [])}

        def normalize_list(value):
            if value is None:
                return []
            if isinstance(value, list):
                return value
            if isinstance(value, dict):
                return [json.dumps(value, ensure_ascii=True)]
            return [value]

        for item in entries:
            traits = normalize_list(item.get("visualTraits"))
            changes = normalize_list(item.get("changes"))
            text = " ".join([str(t) for t in traits + changes])
            if not text:
                continue

            for regex, canonical_name in patterns:
                if not regex.search(text):
                    continue
                prop_key = slugify(canonical_name)
                hint = hints.get(prop_key)
                if not hint:
                    hint = {
                        "name": canonical_name,
                        "description": "",
                        "prop_key": prop_key,
                        "source": "full_actor_db",
                        "examples": [],
                    }
                    hints[prop_key] = hint

                if len(hint["examples"]) < 3:
                    hint["examples"].append({
                        "chapter": item.get("chapter"),
                        "text": text[:200],
                    })

        actor_entry["prop_hints"] = list(hints.values())


def build_prop_index(actors):
    index = {}
    for actor_slug, payload in actors.items():
        for group in ("props", "prop_hints"):
            for prop in payload.get(group, []):
                prop_key = prop.get("prop_key")
                if not prop_key:
                    continue
                entry = index.setdefault(prop_key, {
                    "name": prop.get("name"),
                    "actors": set(),
                    "sources": set(),
                })
                entry["actors"].add(actor_slug)
                entry["sources"].add(prop.get("source"))

    for entry in index.values():
        entry["actors"] = sorted(entry["actors"])
        entry["sources"] = sorted(entry["sources"])

    return index


def write_summary(path, actors):
    lines = ["# Actor Props Summary", ""]
    for actor_slug in sorted(actors.keys()):
        actor = actors[actor_slug]
        display = actor.get("display_names", [actor_slug])
        lines.append(f"## {display[0]} ({actor_slug})")

        props = actor.get("props", [])
        if props:
            lines.append("### Props (Asset Bible)")
            for prop in props:
                desc = f" - {prop.get('description')}" if prop.get("description") else ""
                lines.append(f"- {prop['name']}{desc}")

        hints = actor.get("prop_hints", [])
        if hints:
            lines.append("### Props (Hints from FULL_ACTOR_DB)")
            for prop in hints:
                lines.append(f"- {prop['name']} (hint)")
        lines.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description="Extract actor props from ASSET_BIBLE and analysis.")
    parser.add_argument("--include-hints", action="store_true", help="Scan FULL_ACTOR_DB for prop hints")
    parser.add_argument("--only-existing", action="store_true", help="Only keep actors that exist in produced_assets")
    args = parser.parse_args()

    if not os.path.exists(ASSET_BIBLE):
        print(f"Missing ASSET_BIBLE: {ASSET_BIBLE}")
        return

    existing_slugs = set()
    if os.path.exists(ACTOR_DIR):
        existing_slugs = {d for d in os.listdir(ACTOR_DIR) if os.path.isdir(os.path.join(ACTOR_DIR, d))}

    actors = extract_props_from_asset_bible(ASSET_BIBLE, existing_slugs, args.only_existing)
    if args.include_hints:
        extract_prop_hints(FULL_ACTOR_DB, actors, existing_slugs, args.only_existing)

    props_index = build_prop_index(actors)

    payload = {
        "actors": actors,
        "props": props_index,
        "stats": {
            "actors_total": len(actors),
            "props_total": len(props_index),
        },
    }

    with open(OUTPUT_DB, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=True)

    write_summary(OUTPUT_MD, actors)

    print(f"Wrote: {OUTPUT_DB}")
    print(f"Wrote: {OUTPUT_MD}")


if __name__ == "__main__":
    main()
