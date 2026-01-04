import json
import sys
from pathlib import Path

try:
    import RLPy
except ImportError:
    raise SystemExit("RLPy not available. Run this script inside iClone.")

sys.path.append(str(Path(__file__).resolve().parent))
from iclone_config import load_config  # noqa: E402


def _resolve_root_key(name):
    if not name:
        return None
    key = f"ETemplateRootFolder_{name}"
    if hasattr(RLPy, key):
        return getattr(RLPy, key)
    if hasattr(RLPy, name):
        return getattr(RLPy, name)
    return None


def _walk_folders(root_folder, recursive):
    visited = set()
    stack = [root_folder]
    while stack:
        folder = stack.pop()
        if folder in visited:
            continue
        visited.add(folder)
        yield folder
        if recursive:
            for sub in RLPy.RApplication.GetContentFoldersInFolder(folder):
                if sub not in visited:
                    stack.append(sub)


def _collect_files(root_key, root_folder, scope, recursive, max_files):
    entries = []
    for folder in _walk_folders(root_folder, recursive):
        for file_path in RLPy.RApplication.GetContentFilesInFolder(folder):
            content_id = None
            try:
                content_id = RLPy.RApplication.GetContentId(file_path)
            except Exception:
                content_id = None
            entries.append(
                {
                    "root_key": root_key,
                    "scope": scope,
                    "folder": folder,
                    "path": file_path,
                    "content_id": content_id,
                }
            )
            if max_files and len(entries) >= max_files:
                return entries
    return entries


def main():
    config, config_path = load_config()
    settings = config.get("content_index", {})
    root_keys = settings.get("root_keys") or []
    include_default = bool(settings.get("include_default", True))
    include_custom = bool(settings.get("include_custom", True))
    recursive = bool(settings.get("recursive", True))
    max_files = settings.get("max_files")
    output_path = settings.get("output_path")

    results = []
    missing = []
    for name in root_keys:
        enum_value = _resolve_root_key(name)
        if enum_value is None:
            missing.append(name)
            continue

        if include_default:
            default_folder = RLPy.RApplication.GetDefaultContentFolder(enum_value)
            if default_folder:
                results.extend(
                    _collect_files(
                        name,
                        default_folder,
                        "default",
                        recursive,
                        max_files,
                    )
                )

        if include_custom:
            custom_folder = RLPy.RApplication.GetCustomContentFolder(enum_value)
            if custom_folder:
                results.extend(
                    _collect_files(
                        name,
                        custom_folder,
                        "custom",
                        recursive,
                        max_files,
                    )
                )

    payload = {
        "ok": True,
        "config_path": str(config_path),
        "root_keys": root_keys,
        "missing_keys": missing,
        "total_files": len(results),
        "entries": results,
    }

    output = json.dumps(payload, indent=2, ensure_ascii=False)
    print(output)
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(output, encoding="utf-8")


if __name__ == "__main__":
    main()
