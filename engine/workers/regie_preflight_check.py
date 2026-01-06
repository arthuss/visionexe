import argparse
import json
import re
from pathlib import Path

from visionexe_paths import load_story_config, resolve_path


HEADER_RE = re.compile(r"\[ACT\s+(?P<act>\d+)\]\s+\[SCENE\s+(?P<scene>[\d\.]+)\]", re.IGNORECASE)


def iter_scene_blocks(text: str):
    for block in text.split("\n---"):
        if "## [ACT" in block:
            yield block


def extract_scene_id(block: str) -> str | None:
    for line in block.splitlines():
        line = line.strip()
        if line.startswith("## "):
            match = HEADER_RE.search(line)
            if match:
                return f"{match.group('act')}-{match.group('scene')}"
            break
    return None


def has_regie(block: str) -> bool:
    if "### 0. REGIE" in block:
        return True
    if "REGIE_JSON:" in block:
        return True
    return False


def chapter_folder(filmsets_root: Path, label: str, padding: int, chapter: int) -> Path | None:
    folder = filmsets_root / f"{label}_{chapter:0{padding}d}"
    if folder.exists():
        return folder
    if label.lower() != "chapter":
        fallback = filmsets_root / f"chapter_{chapter:03d}"
        if fallback.exists():
            return fallback
    return None


def main():
    parser = argparse.ArgumentParser(description="Scan screenplays for missing REGIE_JSON blocks.")
    parser.add_argument("--story-root", help="Story root path (defaults to engine_config default_story_root).")
    parser.add_argument("--story-config", help="Path to story_config.json (overrides story-root).")
    parser.add_argument("--start", type=int, default=1, help="Start chapter number.")
    parser.add_argument("--end", type=int, default=108, help="End chapter number.")
    parser.add_argument("--output", help="Optional JSON output path.")
    args = parser.parse_args()

    story_config, story_root, repo_root = load_story_config(
        story_root=args.story_root,
        story_config_path=args.story_config,
    )

    filmsets_root = resolve_path(story_config.get("filmsets_root"), repo_root)
    if not filmsets_root:
        raise SystemExit("filmsets_root missing in story_config.json")

    chapter_label = story_config.get("chapter_label", "chapter")
    chapter_padding = int(story_config.get("chapter_index_padding", 3))

    missing = []
    ok = []
    invalid = []

    for chapter in range(args.start, args.end + 1):
        folder = chapter_folder(filmsets_root, chapter_label, chapter_padding, chapter)
        if not folder:
            invalid.append({"chapter": chapter, "status": "missing_folder"})
            continue

        screenplay_path = folder / "DREHBUCH_HOLLYWOOD.md"
        if not screenplay_path.exists():
            invalid.append({"chapter": chapter, "path": str(screenplay_path), "status": "missing_script"})
            continue

        try:
            text = screenplay_path.read_text(encoding="utf-8")
        except OSError as exc:
            invalid.append({"chapter": chapter, "path": str(screenplay_path), "status": f"read_error:{exc}"})
            continue

        blocks = list(iter_scene_blocks(text))
        if not blocks:
            invalid.append({"chapter": chapter, "path": str(screenplay_path), "status": "no_scenes"})
            continue

        missing_scenes = []
        for block in blocks:
            if not has_regie(block):
                scene_id = extract_scene_id(block) or "unknown"
                missing_scenes.append(scene_id)

        if missing_scenes:
            missing.append(
                {
                    "chapter": chapter,
                    "path": str(screenplay_path),
                    "total_scenes": len(blocks),
                    "missing_scenes": missing_scenes,
                }
            )
        else:
            ok.append({"chapter": chapter, "path": str(screenplay_path), "total_scenes": len(blocks)})

    summary = {
        "story_root": str(story_root),
        "filmsets_root": str(filmsets_root),
        "chapter_label": chapter_label,
        "chapter_padding": chapter_padding,
        "range": {"start": args.start, "end": args.end},
        "missing_regie": missing,
        "ok": ok,
        "invalid": invalid,
    }

    if args.output:
        output_path = resolve_path(args.output, repo_root)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote regie preflight: {output_path}")
    else:
        print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
