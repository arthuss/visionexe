import argparse
import csv
from pathlib import Path

from visionexe_paths import ensure_dir, load_story_config, resolve_path


DEFAULT_LOCATIONS = [
    "Sinai_Port_V1",
    "Hermon_Ingress_Hub",
    "Root_Mainframe_Hall",
    "Cold_Storage_Caves",
    "Core_Cluster_Mountains",
    "Gold_Master_Eden",
    "Atmospheric_IO_Gates",
    "Gehenna_Data_Sink",
    "Desert_Transition",
    "Rift_Valley_Black",
    "Rift_Valley_Yellow",
    "Ethiopian_Highlands",
    "Socotra_Coast",
    "The_North_Ice",
    "Astronomical_Desert",
]


def load_locations(path: Path | None):
    if not path or not path.exists():
        return DEFAULT_LOCATIONS
    lines = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        value = raw.strip()
        if not value or value.startswith("#"):
            continue
        lines.append(value)
    return lines or DEFAULT_LOCATIONS


def main():
    parser = argparse.ArgumentParser(description="Set up environment folders + mapping CSV.")
    parser.add_argument("--story-root", help="Story root path.")
    parser.add_argument("--story-config", help="Path to story_config.json.")
    parser.add_argument("--environments-root", help="Override environments root.")
    parser.add_argument("--locations", help="Optional locations list file.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing mapping.csv.")
    args = parser.parse_args()

    story_config, _, repo_root = load_story_config(
        story_root=args.story_root,
        story_config_path=args.story_config,
    )

    env_root_value = args.environments_root or story_config.get("environments_root")
    if not env_root_value:
        raise SystemExit("environments_root is not configured.")
    env_root = resolve_path(env_root_value, repo_root)
    ensure_dir(env_root)

    locations_path = resolve_path(args.locations, repo_root) if args.locations else None
    locations = load_locations(locations_path)

    print("--- Setting up Environment Folders ---")
    for loc in locations:
        folder_path = env_root / loc
        ensure_dir(folder_path)
        print(f"Created: {loc}")

    mapping_file = env_root / "mapping.csv"
    images = [p.name for p in env_root.iterdir() if p.suffix.lower() in {".png", ".jpg", ".jpeg"}]
    images.sort()

    if mapping_file.exists() and not args.force:
        print("mapping.csv already exists. Use --force to overwrite.")
        return

    print(f"Found {len(images)} images.")
    with mapping_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Image_Filename", "Target_Folder_Name", "Notes"])
        for img in images:
            writer.writerow([img, "", ""])

    print(f"Done. Fill in targets at: {mapping_file}")


if __name__ == "__main__":
    main()
