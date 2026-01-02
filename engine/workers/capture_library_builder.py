import argparse
import json
import time
from pathlib import Path

from visionexe_paths import ensure_dir, load_story_config, resolve_path


VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".webm", ".avi"}
AUDIO_EXTS = {".wav", ".mp3", ".flac", ".m4a", ".ogg"}


def iter_media(root: Path, exts: set[str]):
    if not root.exists():
        return []
    items = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() in exts:
            items.append(path)
    return items


def to_relpath(path: Path, repo_root: Path) -> str:
    try:
        return str(path.relative_to(repo_root)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def build_entry(path: Path, category: str, repo_root: Path):
    return {
        "id": path.stem,
        "label": path.stem.replace("_", " "),
        "path": to_relpath(path, repo_root),
        "category": category,
        "source": "capture",
        "notes": "",
        "tags": [],
    }


def build_payload(items, story_config, capture_root: Path, category: str):
    return {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "story_id": story_config.get("story_id"),
        "capture_root": str(capture_root),
        "category": category,
        "count": len(items),
        "items": items,
    }


def main():
    parser = argparse.ArgumentParser(description="Index capture media into pose/viseme libraries.")
    parser.add_argument("--story-root", help="Story root path (defaults to engine_config default_story_root).")
    parser.add_argument("--story-config", help="Path to story_config.json (overrides story-root).")
    parser.add_argument("--capture-root", help="Override capture root.")
    parser.add_argument("--poses-out", help="Output pose library JSON path.")
    parser.add_argument("--visemes-out", help="Output viseme library JSON path.")
    args = parser.parse_args()

    story_config, _, repo_root = load_story_config(
        story_root=args.story_root,
        story_config_path=args.story_config,
    )

    data_root = story_config.get("data_root") or "stories/template/data"
    data_root = resolve_path(data_root, repo_root)
    capture_root = resolve_path(args.capture_root or story_config.get("capture_root") or f"{data_root}/capture", repo_root)

    subjects_root = resolve_path(story_config.get("subjects_root"), repo_root)
    ensure_dir(subjects_root)

    poses_out = resolve_path(
        args.poses_out or story_config.get("pose_library_path") or f"{subjects_root}/pose_library.json",
        repo_root,
    )
    visemes_out = resolve_path(
        args.visemes_out or story_config.get("viseme_library_path") or f"{subjects_root}/viseme_library.json",
        repo_root,
    )

    poses_root = capture_root / "poses"
    phonemes_root = capture_root / "phonemes"

    pose_files = iter_media(poses_root, VIDEO_EXTS | AUDIO_EXTS)
    viseme_files = iter_media(phonemes_root, VIDEO_EXTS | AUDIO_EXTS)

    pose_items = [build_entry(path, "pose", repo_root) for path in pose_files]
    viseme_items = [build_entry(path, "phoneme", repo_root) for path in viseme_files]

    poses_out.write_text(
        json.dumps(build_payload(pose_items, story_config, capture_root, "pose"), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    visemes_out.write_text(
        json.dumps(build_payload(viseme_items, story_config, capture_root, "phoneme"), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote pose library: {poses_out}")
    print(f"Wrote viseme library: {visemes_out}")


if __name__ == "__main__":
    main()
