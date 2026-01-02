import argparse
import json
import os
import shutil
import time
from datetime import datetime

from gradio_client import Client, handle_file

IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp")
WSL_PREFIX = "\\\\wsl.localhost\\"


def clean_filename(name):
    clean = "".join(c for c in name if c.isalnum() or c in ("_", "-"))
    clean = clean.replace(" ", "_")
    while "__" in clean:
        clean = clean.replace("__", "_")
    return clean.strip("_").lower() or "unnamed"


def list_leaf_image_dirs(root_dir):
    image_dirs = set()
    for dirpath, _, filenames in os.walk(root_dir):
        if any(f.lower().endswith(IMAGE_EXTS) for f in filenames):
            image_dirs.add(dirpath)

    leaf_dirs = []
    for d in image_dirs:
        if not any(other != d and other.startswith(d + os.sep) for other in image_dirs):
            leaf_dirs.append(d)

    return sorted(leaf_dirs)


def build_caption(template, actor, phase):
    return template.format(actor=actor, phase=phase)


def normalize_download_path(value):
    if isinstance(value, dict):
        return value.get("path") or value.get("name")
    if isinstance(value, str):
        return value
    return None


def resolve_mode(input_root, mode):
    if mode != "auto":
        return mode
    normalized = os.path.normpath(input_root).lower()
    if os.path.basename(normalized) == "environments" or os.sep + "environments" + os.sep in normalized:
        return "env"
    return "actor"


def translate_wsl_path(path, wsl_root):
    if not path:
        return None
    if path.startswith("/") and wsl_root:
        wsl_root = wsl_root.rstrip("\\/")
        return wsl_root + path.replace("/", "\\")
    return path


def wait_for_path(path, timeout_sec, poll_sec):
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        if os.path.exists(path):
            return path
        time.sleep(poll_sec)
    return None


def find_latest_safetensor(root_dir, since_ts):
    if not root_dir or not os.path.isdir(root_dir):
        return None
    newest = None
    newest_time = 0
    for name in os.listdir(root_dir):
        if not name.lower().endswith(".safetensors"):
            continue
        path = os.path.join(root_dir, name)
        try:
            mtime = os.path.getmtime(path)
        except OSError:
            continue
        if mtime >= since_ts and mtime >= newest_time:
            newest_time = mtime
            newest = path
    return newest


def wait_for_remote_output(root_dir, since_ts, timeout_sec, poll_sec):
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        candidate = find_latest_safetensor(root_dir, since_ts)
        if candidate:
            return candidate
        time.sleep(poll_sec)
    return None


def save_lora_file(source_path, out_path, copy_only=False):
    if not source_path or not os.path.exists(source_path):
        return False
    if os.path.abspath(source_path) == os.path.abspath(out_path):
        return True
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    is_wsl = source_path.startswith(WSL_PREFIX)
    if copy_only or is_wsl:
        shutil.copy2(source_path, out_path)
    else:
        shutil.move(source_path, out_path)
    return True


def log_entry(log_file, entry):
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=True) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Queue LoRA training jobs via Gradio API.")
    parser.add_argument("--server", default="http://127.0.0.1:7860", help="Gradio server URL")
    parser.add_argument("--input-root", default=r"C:\Users\sasch\henoch\produced_assets\lora_training\actors")
    parser.add_argument("--output-root", default=r"C:\Users\sasch\henoch\produced_assets\lora_training\loras")
    parser.add_argument("--mode", choices=["auto", "actor", "env"], default="auto", help="Training mode")
    parser.add_argument("--min-images", type=int, default=8, help="Minimum images required to train")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of jobs (0 = all)")
    parser.add_argument("--sleep", type=float, default=1.0, help="Seconds to sleep between jobs")
    parser.add_argument("--poll-seconds", type=float, default=2.0, help="Polling interval for output files")
    parser.add_argument("--timeout-seconds", type=float, default=600.0, help="Wait timeout for output files")
    parser.add_argument("--remote-output-root", default="", help="Optional remote output directory to poll")
    parser.add_argument("--wsl-root", default="", help="WSL UNC root (e.g. \\\\wsl.localhost\\Ubuntu22Old)")
    parser.add_argument("--copy-only", action="store_true", help="Copy output instead of moving")
    parser.add_argument("--dry-run", action="store_true", help="List jobs without training")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing LoRA files")
    parser.add_argument("--caption-template", default="{actor} {phase}", help="Caption template")
    parser.add_argument("--log-file", default=r"C:\Users\sasch\henoch\lora_training_runs.jsonl")
    args = parser.parse_args()

    input_root = os.path.abspath(args.input_root)
    output_root = os.path.abspath(args.output_root)
    os.makedirs(output_root, exist_ok=True)
    mode = resolve_mode(input_root, args.mode)

    leaf_dirs = list_leaf_image_dirs(input_root)
    if args.limit > 0:
        leaf_dirs = leaf_dirs[: args.limit]

    print(f"Found {len(leaf_dirs)} training folders.")
    if args.dry_run:
        for d in leaf_dirs:
            print(d)
        return

    client = Client(args.server)

    success = 0
    skipped = 0
    failed = 0

    for idx, folder in enumerate(leaf_dirs, start=1):
        rel = os.path.relpath(folder, input_root)
        parts = rel.split(os.sep)
        actor = parts[0] if parts else "unknown"
        phase = "_".join(parts[1:]) if len(parts) > 1 else "default"
        category = "actor"
        prop_name = ""
        if mode == "env":
            category = "environment"
            actor = clean_filename(rel.replace(os.sep, "_"))
            phase = "environment"
        elif len(parts) > 2 and parts[1].lower() == "props":
            category = "prop"
            prop_name = "_".join(parts[2:])
            phase = f"prop_{prop_name}"

        safe_actor = clean_filename(actor)
        safe_phase = clean_filename(phase)
        if category == "environment":
            out_dir = output_root
            out_name = f"env__{safe_actor}.safetensors"
        else:
            out_dir = os.path.join(output_root, safe_actor)
            os.makedirs(out_dir, exist_ok=True)
            if category == "prop" and prop_name:
                safe_prop = clean_filename(prop_name)
                out_name = f"prop__{safe_prop}__{safe_actor}.safetensors"
            else:
                out_name = f"{safe_actor}__{safe_phase}.safetensors"
        out_path = os.path.join(out_dir, out_name)

        if os.path.exists(out_path) and not args.overwrite:
            print(f"[{idx}/{len(leaf_dirs)}] SKIP (exists): {out_name}")
            skipped += 1
            continue

        image_files = [
            os.path.join(folder, f)
            for f in sorted(os.listdir(folder))
            if f.lower().endswith(IMAGE_EXTS)
        ]
        if len(image_files) < args.min_images:
            print(f"[{idx}/{len(leaf_dirs)}] SKIP (not enough images): {folder}")
            skipped += 1
            continue

        caption = build_caption(args.caption_template, actor, phase)
        input_images = [{"image": handle_file(p), "caption": caption} for p in image_files]

        print(f"[{idx}/{len(leaf_dirs)}] TRAIN: {actor} / {phase} ({len(image_files)} imgs)")
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "actor": actor,
            "phase": phase,
            "folder": folder,
            "output": out_path,
            "status": "started",
            "count": len(image_files),
        }
        log_entry(args.log_file, entry)
        job_start = time.time()

        try:
            result = client.predict(input_images=input_images, api_name="/generate_lora")
            lora_path, download_path = result[0], result[1]
            local_path = normalize_download_path(download_path)
            local_path = translate_wsl_path(local_path, args.wsl_root)
            saved = False

            if local_path:
                candidate = wait_for_path(local_path, args.timeout_seconds, args.poll_seconds)
                if candidate:
                    saved = save_lora_file(candidate, out_path, copy_only=args.copy_only)

            if not saved and args.remote_output_root:
                remote_path = wait_for_remote_output(
                    args.remote_output_root,
                    job_start,
                    args.timeout_seconds,
                    args.poll_seconds
                )
                if remote_path:
                    saved = save_lora_file(remote_path, out_path, copy_only=True)

            if saved:
                print(f"  -> Saved: {out_path}")
                entry.update({"status": "ok", "remote_path": lora_path})
                log_entry(args.log_file, entry)
                success += 1
            else:
                print("  [ERR] Output file not found. Check server output or remote output dir.")
                entry.update({"status": "error", "remote_path": lora_path})
                log_entry(args.log_file, entry)
                failed += 1
        except Exception as e:
            print(f"  [ERR] Training failed: {e}")
            entry.update({"status": "error", "error": str(e)})
            log_entry(args.log_file, entry)
            failed += 1

        time.sleep(args.sleep)

    print("\n--- DONE ---")
    print(f"Success: {success}, Skipped: {skipped}, Failed: {failed}")


if __name__ == "__main__":
    main()
