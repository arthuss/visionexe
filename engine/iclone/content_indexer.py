import json
import sys
from pathlib import Path

try:
    import RLPy
except ImportError:
    raise SystemExit("RLPy not available. Run this script inside iClone.")

sys.path.append(str(Path(__file__).resolve().parent))
from iclone_config import load_config  # noqa: E402


def _discover_enum_keys():
    keys = {}
    for attr in dir(RLPy):
        if attr.startswith("ETemplateRootFolder_"):
            keys[attr] = getattr(RLPy, attr)
            # Map suffix "Props" -> value
            suffix = attr.replace("ETemplateRootFolder_", "")
            if suffix:
                keys[suffix] = getattr(RLPy, attr)
    return keys


def _resolve_root_key(name, known_keys):
    if not name:
        return None, None
    
    # Try exact match or suffix match in known keys
    if name in known_keys:
        return known_keys[name], name
    
    # Try constructing the key name (e.g. if name is "MotionDirector", look for "ETemplateRootFolder_MotionDirector")
    candidate = f"ETemplateRootFolder_{name}"
    if candidate in known_keys:
        return known_keys[candidate], candidate

    return None, None


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
            try:
                subfolders = RLPy.RApplication.GetContentFoldersInFolder(folder)
                for sub in subfolders:
                    if sub not in visited:
                        stack.append(sub)
            except Exception:
                pass


def _collect_files(root_key, root_folder, scope, recursive, max_files):
    entries = []
    for folder in _walk_folders(root_folder, recursive):
        try:
            files = RLPy.RApplication.GetContentFilesInFolder(folder)
        except Exception:
            continue
            
        for file_path in files:
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

    known_keys = _discover_enum_keys()
    
    results = []
    missing_enums = []
    
    # Pre-calculate common paths for fallback
    template_root = None
    custom_root = None
    try:
        template_root = RLPy.RApplication.GetTemplateDataPath()
    except: pass
    try:
        custom_root = RLPy.RApplication.GetCustomDataPath()
    except: pass

    for name in root_keys:
        enum_value, resolved_name = _resolve_root_key(name, known_keys)
        
        found_any = False
        
        # Strategy A: Use Enum if found
        if enum_value is not None:
            if include_default:
                try:
                    default_folder = RLPy.RApplication.GetDefaultContentFolder(enum_value)
                    if default_folder:
                        results.extend(_collect_files(name, default_folder, "default", recursive, max_files))
                        found_any = True
                except Exception:
                    pass

            if include_custom:
                try:
                    custom_folder = RLPy.RApplication.GetCustomContentFolder(enum_value)
                    if custom_folder:
                        results.extend(_collect_files(name, custom_folder, "custom", recursive, max_files))
                        found_any = True
                except Exception:
                    pass
        
        # Strategy B: Fallback to folder name append if Enum failed or produced no results (and it's a "custom" name like MotionDirector?)
        # Actually, only fallback if Enum was NOT found. If Enum found but folder empty, that's valid.
        if enum_value is None:
            missing_enums.append(name)
            # Try path fallback
            fallback_found = False
            if include_default and template_root:
                candidate = str(Path(template_root) / name)
                if Path(candidate).exists():
                    results.extend(_collect_files(name, candidate, "default", recursive, max_files))
                    fallback_found = True
            
            if include_custom and custom_root:
                candidate = str(Path(custom_root) / name)
                if Path(candidate).exists():
                    results.extend(_collect_files(name, candidate, "custom", recursive, max_files))
                    fallback_found = True
            
            if fallback_found:
                # Remove from missing if we found it via fallback
                missing_enums.pop()

    payload = {
        "ok": True,
        "config_path": str(config_path),
        "root_keys": root_keys,
        "missing_keys": missing_enums,
        "available_enum_keys": list(known_keys.keys()),
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
