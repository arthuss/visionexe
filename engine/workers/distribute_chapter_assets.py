import argparse
import os
import re
import shutil

from visionexe_paths import load_story_config, resolve_path


DEFAULT_SOURCE = r"\\wsl.localhost\Ubuntu24Old\root\comfy\ComfyUI\output"
DEFAULT_SUBDIR = os.path.join("produced_assets", "chapter_assets")

IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp")
VIDEO_EXTS = (".mp4", ".mov", ".webm")

ASSET_PATTERN = re.compile(r"^CH(?P<chapter>\d{3})_SC(?P<scene>[0-9.]+)_(?P<atype>[A-Z]+)")


def normalize_type(value):
    if not value:
        return "misc"
    lowered = value.lower()
    if lowered.startswith("image"):
        return "image"
    if lowered.startswith("video"):
        return "video"
    return lowered


def normalize_timeline_tag(value, padding):
    if value is None:
        return None
    raw = str(value).strip().lower()
    if not raw:
        return None
    if raw.startswith("r") and raw[1:].isdigit():
        return f"{int(raw[1:]):0{padding}d}"
    if raw.isdigit():
        return f"{int(raw):0{padding}d}"
    digits = re.sub(r"[^0-9]", "", raw)
    if digits:
        return f"{int(digits):0{padding}d}"
    return None


def scene_to_segment(scene_value):
    if scene_value is None:
        return None
    raw = str(scene_value)
    if raw.isdigit():
        return int(raw)
    if "." in raw:
        head = raw.split(".", 1)[0]
        if head.isdigit():
            return int(head)
    return None


def normalize_scene_token(scene_value, padding):
    if scene_value is None:
        return None
    raw = str(scene_value).strip()
    if not raw:
        return None
    if raw.isdigit():
        return f"{int(raw):0{padding}d}"
    if "." in raw:
        parts = [p for p in raw.split(".") if p]
        if parts and all(p.isdigit() for p in parts):
            return "_".join(f"{int(p):0{padding}d}" for p in parts)
    digits = re.sub(r"[^0-9]+", "_", raw).strip("_")
    if digits and digits.replace("_", "").isdigit():
        return "_".join(f"{int(p):0{padding}d}" for p in digits.split("_") if p)
    return re.sub(r"[^0-9A-Za-z]+", "_", raw).strip("_")


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


def iter_outputs(source_dir):
    for root, _, files in os.walk(source_dir):
        for filename in files:
            if filename.lower().endswith(IMAGE_EXTS + VIDEO_EXTS):
                yield root, filename


def chapter_filter(value):
    if not value or value == "all":
        return None
    digits = re.sub(r"[^0-9]", "", value)
    if len(digits) >= 3:
        digits = digits[-3:]
    return digits.zfill(3)


def main():
    parser = argparse.ArgumentParser(description="Distribute chapter prompt outputs into filmsets.")
    parser.add_argument("--story-root", help="Story root path.")
    parser.add_argument("--story-config", help="Path to story_config.json.")
    parser.add_argument("--source", default=DEFAULT_SOURCE, help="Source directory (ComfyUI output).")
    parser.add_argument("--subdir", default=DEFAULT_SUBDIR, help="Subfolder under segment/timeline.")
    parser.add_argument("--chapter", default="all", help="Chapter number (e.g. 96) or all.")
    parser.add_argument("--type", choices=("all", "image", "video"), default="all", help="Filter by type.")
    parser.add_argument("--layout", choices=("segment", "chapter"), default="segment", help="Folder layout.")
    parser.add_argument("--by-scene", action="store_true", help="Force scene subfolders regardless of config.")
    parser.add_argument("--no-scene", action="store_true", help="Disable scene subfolders.")
    parser.add_argument("--timeline", help="Filter by timeline tag (e.g. 1 or r01).")
    parser.add_argument("--segment", help="Explicit segment index for layout=segment.")
    parser.add_argument("--move", action="store_true", help="Move files instead of copy.")
    parser.add_argument("--allow-duplicates", action="store_true", help="Allow duplicate filenames (auto-rename).")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without copying.")
    args = parser.parse_args()

    story_config, _, repo_root = load_story_config(
        story_root=args.story_root,
        story_config_path=args.story_config,
    )

    filmsets_root = resolve_path(story_config.get("filmsets_root"), repo_root)
    if not os.path.exists(args.source):
        print(f"Source not found: {args.source}")
        return

    segment_label = story_config.get("segment_label", "segment")
    segment_padding = int(story_config.get("segment_index_padding", 3))
    scene_label = story_config.get("scene_label", "scene")
    scene_padding = int(story_config.get("scene_index_padding", 3))
    scene_default = bool(story_config.get("scene_layout_default", False))
    timeline_label = story_config.get("timeline_label", "timeline")
    timeline_padding = int(story_config.get("timeline_index_padding", 2))

    wanted_chapter = chapter_filter(args.chapter)
    timeline_tag = normalize_timeline_tag(args.timeline, timeline_padding)
    target_type = args.type
    moved = 0
    skipped = 0

    for root, filename in iter_outputs(args.source):
        match = ASSET_PATTERN.match(filename)
        if not match:
            continue
        if timeline_tag and f"__r{timeline_tag}" not in filename and f"__{timeline_tag}" not in filename:
            continue
        chapter = match.group("chapter")
        scene = match.group("scene")
        if wanted_chapter and chapter != wanted_chapter:
            continue
        asset_type = normalize_type(match.group("atype"))
        if target_type != "all" and asset_type != target_type:
            continue

        chapter_folder = f"chapter_{chapter}"
        dest_parts = [filmsets_root, chapter_folder]

        if args.layout == "segment":
            segment_index = int(args.segment) if args.segment and str(args.segment).isdigit() else None
            if segment_index is None:
                segment_index = scene_to_segment(scene)
            if segment_index is None:
                segment_index = 0
            segment_folder = f"{segment_label}_{segment_index:0{segment_padding}d}"
            dest_parts.append(segment_folder)

        use_scene = (scene_default or args.by_scene) and not args.no_scene
        if use_scene:
            scene_token = normalize_scene_token(scene, scene_padding)
            if not scene_token:
                scene_token = f"{0:0{scene_padding}d}"
            dest_parts.append(f"{scene_label}_{scene_token}")

        if timeline_tag:
            dest_parts.append(f"{timeline_label}_{timeline_tag}")

        if args.subdir:
            dest_parts.append(args.subdir)

        dest_parts.append(asset_type)
        dest_folder = os.path.join(*dest_parts)

        if args.dry_run:
            print(f"[DRY] {os.path.join(root, filename)} -> {dest_folder}")
            moved += 1
            continue

        ok = safe_copy(os.path.join(root, filename), dest_folder, args.allow_duplicates, args.move)
        if ok:
            moved += 1
        else:
            skipped += 1

    print("Distribution complete.")
    print(f"Copied/moved: {moved}")
    print(f"Skipped: {skipped}")


if __name__ == "__main__":
    main()
