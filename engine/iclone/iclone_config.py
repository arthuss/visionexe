import json
import os
from pathlib import Path


DEFAULT_CONFIG = {
    "remote": {
        "host": "127.0.0.1",
        "port": 8123,
    },
    "md_probe": {
        "run_command_test": False,
        "start_md": False,
        "avatar": None,
        "output_path": None,
    },
    "content_index": {
        "root_keys": ["MotionDirector"],
        "include_default": True,
        "include_custom": True,
        "recursive": True,
        "max_files": None,
        "output_path": None,
    },
}


def _deep_merge(base, override):
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _config_path():
    env_path = os.environ.get("ICLONE_CONFIG_PATH")
    if env_path:
        return Path(env_path)
    return Path(__file__).resolve().parent / "iclone_config.json"


def load_config():
    path = _config_path()
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        data = {}
    return _deep_merge(DEFAULT_CONFIG, data), path
