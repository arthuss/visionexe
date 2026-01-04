import argparse
import json
import os
import time
from pathlib import Path


DEFAULT_LIBRARY_ROOT = Path(
    os.environ.get("REALLUSION_LIBRARY_ROOT", r"C:\Users\Public\Documents\Reallusion")
)
DEFAULT_INDEX_NAME = "reallusion_library_index.json"

EXTENSION_MAP = {
    ".italk": {"category": "expression", "asset_type": "talk"},
    ".imotionplus": {"category": "motion", "asset_type": "motion_plus"},
    ".imotion": {"category": "motion", "asset_type": "motion"},
    ".imd": {"category": "motion_director", "asset_type": "motion_director"},
    ".imddata": {"category": "motion_director", "asset_type": "motion_director_data"},
    ".imdprop": {"category": "motion_director", "asset_type": "motion_director_prop"},
    ".imdturntostop": {"category": "motion_director", "asset_type": "motion_director_turntostop"},
    ".ipath": {"category": "motion_path", "asset_type": "path"},
    ".iterrain": {"category": "terrain", "asset_type": "terrain"},
    ".iavatar": {"category": "character", "asset_type": "avatar"},
}


def normalize_extensions(raw: str | None) -> set[str] | None:
    if not raw:
        return None
    items = set()
    for part in raw.split(","):
        part = part.strip().lower()
        if not part:
            continue
        if not part.startswith("."):
            part = f".{part}"
        items.add(part)
    return items or None


def iter_assets(root: Path, include_unknown: bool, extensions: set[str] | None):
    if not root.exists():
        return []
    items = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        ext = path.suffix.lower()
        if extensions is not None:
            if ext not in extensions:
                continue
        elif ext not in EXTENSION_MAP:
            if not include_unknown or not ext.startswith(".i"):
                continue
        items.append(path)
    return items


def build_entry(path: Path, root: Path):
    rel = path.relative_to(root)
    ext = path.suffix.lower()
    meta = EXTENSION_MAP.get(ext, {"category": "unknown", "asset_type": "unknown"})
    folder = "/".join(rel.parts[:-1])
    collection = rel.parts[0] if rel.parts else ""
    return {
        "id": rel.as_posix(),
        "name": path.stem,
        "label": path.stem.replace("_", " "),
        "path": rel.as_posix(),
        "ext": ext,
        "category": meta["category"],
        "asset_type": meta["asset_type"],
        "collection": collection,
        "folder": folder,
        "size_bytes": path.stat().st_size,
        "modified_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(path.stat().st_mtime)),
        "tags": [],
    }


def summarize(entries):
    counts = {"total": len(entries), "by_category": {}, "by_type": {}}
    for entry in entries:
        counts["by_category"][entry["category"]] = counts["by_category"].get(entry["category"], 0) + 1
        counts["by_type"][entry["asset_type"]] = counts["by_type"].get(entry["asset_type"], 0) + 1
    return counts


def main():
    parser = argparse.ArgumentParser(description="Index Reallusion library assets into a JSON catalog.")
    parser.add_argument("--library-root", help="Reallusion library root path.")
    parser.add_argument("--output", help="Output JSON path.")
    parser.add_argument(
        "--extensions",
        help="Comma-separated extensions to include (overrides defaults). Example: imd,imddata,italk",
    )
    parser.add_argument("--include-unknown", action="store_true", help="Include unknown .i* extensions.")
    args = parser.parse_args()

    library_root = Path(args.library_root) if args.library_root else DEFAULT_LIBRARY_ROOT
    output_path = Path(args.output) if args.output else library_root / DEFAULT_INDEX_NAME
    extensions = normalize_extensions(args.extensions)

    if not library_root.exists():
        raise SystemExit(f"Library root not found: {library_root}")

    assets = iter_assets(library_root, args.include_unknown, extensions)
    entries = [build_entry(path, library_root) for path in assets]
    entries.sort(key=lambda item: item["id"])

    payload = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "library_root": str(library_root),
        "index_root": str(output_path.parent),
        "counts": summarize(entries),
        "items": entries,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote Reallusion library index: {output_path}")


if __name__ == "__main__":
    main()
