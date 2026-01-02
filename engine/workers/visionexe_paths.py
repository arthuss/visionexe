import json
from pathlib import Path


def resolve_engine_root() -> Path:
    return Path(__file__).resolve().parents[1]


def resolve_repo_root() -> Path:
    return resolve_engine_root().parent


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def resolve_path(path_value: str, repo_root: Path) -> Path:
    if not path_value:
        return None
    candidate = Path(path_value)
    if candidate.is_absolute():
        return candidate
    return repo_root / candidate


def load_engine_config(engine_root: Path | None = None) -> dict:
    engine_root = engine_root or resolve_engine_root()
    config_path = engine_root / "config" / "engine_config.json"
    return load_json(config_path)


def load_story_config(
    story_root: str | None = None,
    story_config_path: str | None = None,
    engine_root: Path | None = None,
) -> tuple[dict, Path, Path]:
    engine_root = engine_root or resolve_engine_root()
    repo_root = engine_root.parent
    engine_config = load_engine_config(engine_root)

    if story_config_path:
        config_path = resolve_path(story_config_path, repo_root)
        story_root_path = config_path.parent.parent
    else:
        if story_root:
            story_root_path = resolve_path(story_root, repo_root)
        else:
            story_root_path = resolve_path(engine_config.get("default_story_root"), repo_root)
        config_path = story_root_path / "config" / "story_config.json"

    config = load_json(config_path)
    return config, story_root_path, repo_root


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)
