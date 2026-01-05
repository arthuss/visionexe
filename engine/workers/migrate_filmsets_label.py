import argparse
import re
import shutil
from pathlib import Path

from visionexe_paths import load_story_config, resolve_path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Migrate filmsets folder labels (e.g. chapter_### -> story_###)."
    )
    parser.add_argument("--story-root", help="Story root path.")
    parser.add_argument("--story-config", help="Path to story_config.json.")
    parser.add_argument("--source-label", default="chapter", help="Existing label to migrate from.")
    parser.add_argument("--target-label", help="Target label (defaults to story_config chapter_label).")
    parser.add_argument("--chapter-padding", type=int, help="Index padding (defaults to story_config).")
    parser.add_argument("--mode", choices=("move", "copy"), default="move", help="Move or copy folders.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing targets.")
    parser.add_argument("--no-fallback-copy", action="store_true", help="Disable copy fallback when move fails.")
    parser.add_argument("--update-paths", action="store_true", help="Update stored paths under data root.")
    parser.add_argument("--paths-root", help="Override root for path updates (defaults to story_root/data).")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without changing files.")
    return parser.parse_args()


def iter_source_dirs(filmsets_root: Path, source_label: str):
    pattern = re.compile(rf"^{re.escape(source_label)}_(\d+)$")
    for path in sorted(filmsets_root.glob(f"{source_label}_*")):
        if not path.is_dir():
            continue
        match = pattern.match(path.name)
        if not match:
            continue
        try:
            idx = int(match.group(1))
        except ValueError:
            continue
        yield path, idx


def update_paths(root: Path, source_label: str, target_label: str, dry_run: bool):
    if not root or not root.exists():
        return
    src_back = f"\\filmsets\\{source_label}_".encode("utf-8")
    tgt_back = f"\\filmsets\\{target_label}_".encode("utf-8")
    src_fwd = f"/filmsets/{source_label}_".encode("utf-8")
    tgt_fwd = f"/filmsets/{target_label}_".encode("utf-8")

    exts = {".csv", ".json", ".jsonl", ".md", ".txt"}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in exts:
            continue
        data = path.read_bytes()
        updated = data.replace(src_back, tgt_back).replace(src_fwd, tgt_fwd)
        if updated == data:
            continue
        if dry_run:
            print(f"[dry-run] update paths in {path}")
        else:
            path.write_bytes(updated)
            print(f"Updated paths in {path}")


def main():
    args = parse_args()
    story_config, story_root, repo_root = load_story_config(
        story_root=args.story_root,
        story_config_path=args.story_config,
    )

    filmsets_root = story_config.get("filmsets_root")
    if not filmsets_root:
        raise SystemExit("filmsets_root is not configured.")
    filmsets_root = resolve_path(filmsets_root, repo_root)

    target_label = args.target_label or story_config.get("chapter_label", "chapter")
    chapter_padding = args.chapter_padding or int(story_config.get("chapter_index_padding", 3))

    if args.source_label == target_label:
        print("Source and target labels match; nothing to migrate.")
        return

    for src, idx in iter_source_dirs(filmsets_root, args.source_label):
        target_name = f"{target_label}_{idx:0{chapter_padding}d}"
        dst = filmsets_root / target_name
        if dst.exists():
            if args.overwrite:
                if args.dry_run:
                    print(f"[dry-run] remove existing {dst}")
                else:
                    shutil.rmtree(dst)
            else:
                print(f"Skip {src} -> {dst} (target exists)")
                continue
        if args.dry_run:
            print(f"[dry-run] {args.mode} {src} -> {dst}")
            continue
        if args.mode == "move":
            try:
                src.rename(dst)
                print(f"Moved {src.name} -> {dst.name}")
            except PermissionError as exc:
                if args.no_fallback_copy:
                    raise
                shutil.copytree(src, dst)
                print(f"Copied (move failed: {exc}) {src.name} -> {dst.name}")
        else:
            shutil.copytree(src, dst)
            print(f"Copied {src.name} -> {dst.name}")

    if args.update_paths:
        paths_root = args.paths_root
        if paths_root:
            paths_root = resolve_path(paths_root, repo_root)
        else:
            data_root = story_config.get("data_root") or (story_root / "data")
            paths_root = resolve_path(str(data_root), repo_root)
        update_paths(paths_root, args.source_label, target_label, args.dry_run)


if __name__ == "__main__":
    main()
