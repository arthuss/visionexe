from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

DOC_SOURCES = [
    "README.md",
    "README_pipeline.md",
    "docs/_index.md",
    "docs/workers.md",
    "docs/workflows.md",
    "docs/workspaces.md",
    "docs/queues.md",
    "docs/geez_analysis_methodology.md",
    "docs/scene_building.md",
    "docs/video_docking.md",
    "docs/iclone_bridge.md",
    "docs/motion_director_flow.md",
    "docs/reallusion_pipeline.md",
    "docs/rlpy_hidden_api.md",
]

CONFIG_GLOBS = [
    "engine/config/*.json",
    "engine/config/pose_mappings/*.json",
    "stories/template/config/*.json",
    "stories/template/config/timelines/*.json",
]

INVENTORY_SETS = [
    ("Engine workers", "engine/workers", "*.py"),
    ("Engine scripts", "engine/scripts", "*.ps1"),
    ("Engine launchers", "engine/launchers", "*.ps1"),
    ("Engine tools", "engine/tools", "*.py"),
    ("Workflows", "engine/workflows", "*.json"),
    ("Analysis rules", "engine/analysis/rules", "*.py"),
]

DIR_COUNTS = [
    "stories/template/filmsets",
    "stories/template/subjects",
    "stories/template/subjects/timelines",
    "stories/template/data",
]

SKIP_DIR_PARTS = {"__pycache__", ".git", ".venv", "node_modules"}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def code_fence_label(path: Path) -> str:
    ext = path.suffix.lower()
    return {
        ".json": "json",
        ".jsonl": "jsonl",
        ".md": "md",
        ".ps1": "powershell",
        ".py": "python",
        ".txt": "text",
    }.get(ext, "text")


def should_skip(path: Path) -> bool:
    return any(part in SKIP_DIR_PARTS for part in path.parts)


def list_inventory(root: Path, pattern: str) -> list[Path]:
    return sorted(
        [p for p in root.rglob(pattern) if p.is_file() and not should_skip(p)],
        key=lambda p: rel(p),
    )


def count_files(root: Path) -> int:
    if not root.exists():
        return 0
    count = 0
    for path in root.rglob("*"):
        if path.is_file() and not should_skip(path):
            count += 1
    return count


def render_section(title: str, body: str) -> str:
    return f"## {title}\n\n{body.rstrip()}\n"


def render_inventory(title: str, paths: list[Path]) -> str:
    if not paths:
        return render_section(title, "_No files found._")
    lines = "\n".join(f"- `{rel(path)}`" for path in paths)
    return render_section(title, lines)


def render_workspaces_summary(path: Path) -> str:
    if not path.exists():
        return render_section("External Workspaces", "_Workspaces registry not found._")
    data = json.loads(read_text(path))
    lines = []
    for workspace in data.get("workspaces", []):
        ws_id = workspace.get("id", "unknown")
        name = workspace.get("name", "")
        host = workspace.get("host", "")
        category = workspace.get("category", "")
        start = workspace.get("start_command") or "none"
        apis = workspace.get("apis", [])
        api_summary = ", ".join(
            f"{api.get('type', 'api')}:{api.get('base_url', '')}"
            for api in apis
        ) or "none"
        lines.append(
            f"- `{ws_id}`: {name} | host={host} | category={category} | apis={api_summary} | start={start}"
        )
    if not lines:
        lines = ["_No workspaces defined._"]
    return render_section("External Workspaces (registry summary)", "\n".join(lines))


def collect_sections(sections_dir: Path) -> list[Path]:
    if not sections_dir.exists():
        return []
    return sorted(sections_dir.glob("*.md"), key=lambda p: p.name)


def collect_config_files() -> list[Path]:
    files: list[Path] = []
    for pattern in CONFIG_GLOBS:
        files.extend(ROOT.glob(pattern))
    unique = {p.resolve() for p in files if p.is_file()}
    return sorted(unique, key=lambda p: rel(p))


def collect_doc_files() -> list[Path]:
    files = [ROOT / doc for doc in DOC_SOURCES]
    return [path for path in files if path.exists()]


def build_compendium(sections_dir: Path, output_path: Path) -> None:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = ["# Workspace Compendium", ""]
    lines.append(f"_Generated: {timestamp}_")
    lines.append("")
    lines.append(
        "This file is generated. Edit the section files in `docs/compendium_sections/` "
        "or the source docs/configs, then re-run the build script."
    )
    lines.append("")

    for section in collect_sections(sections_dir):
        lines.append(render_section(rel(section), read_text(section)))

    lines.append(render_section("Directory Counts", "\n".join(
        f"- `{path}`: {count_files(ROOT / path)} files"
        for path in DIR_COUNTS
    )))

    for title, root_rel, pattern in INVENTORY_SETS:
        root = ROOT / root_rel
        lines.append(render_inventory(title, list_inventory(root, pattern)))

    lines.append(render_workspaces_summary(ROOT / "engine/config/workspaces.json"))

    config_files = collect_config_files()
    if config_files:
        lines.append("## Config Snapshots")
        lines.append("")
        for path in config_files:
            label = code_fence_label(path)
            lines.append(f"### {rel(path)}")
            lines.append(f"```{label}")
            lines.append(read_text(path).rstrip())
            lines.append("```")
            lines.append("")

    doc_files = collect_doc_files()
    if doc_files:
        lines.append("## Documentation Snapshots")
        lines.append("")
        for path in doc_files:
            lines.append(f"### {rel(path)}")
            lines.append(read_text(path).rstrip())
            lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the single-file Workspace Compendium."
    )
    parser.add_argument(
        "--sections-dir",
        default=str(ROOT / "docs/compendium_sections"),
        help="Directory containing compendium section files.",
    )
    parser.add_argument(
        "--output",
        default=str(ROOT / "docs/WORKSPACE_COMPENDIUM.md"),
        help="Output path for the compiled compendium.",
    )
    args = parser.parse_args()
    build_compendium(Path(args.sections_dir), Path(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
