import argparse
import csv
import json
import os
import time

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG = os.path.join(ROOT_PATH, "env_audit_config.json")


def load_json(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None


def load_config(path):
    config = load_json(path) or {}
    return {
        "mapping_csv": config.get("mapping_csv", "Environments/mapping.csv"),
        "output_root": config.get("output_root", "produced_assets"),
        "fallback_env_root": config.get("fallback_env_root", "Environments"),
        "image_exts": config.get("image_exts", [".png", ".jpg", ".jpeg", ".webp"])
    }


def count_images(folder, prefix, exts):
    if not os.path.isdir(folder):
        return 0
    count = 0
    for name in os.listdir(folder):
        if not name.lower().endswith(tuple(exts)):
            continue
        if prefix and not name.startswith(prefix):
            continue
        count += 1
    return count


def build_audit(config):
    mapping_path = os.path.join(ROOT_PATH, config["mapping_csv"])
    if not os.path.exists(mapping_path):
        raise RuntimeError(f"Missing mapping file: {mapping_path}")

    results = []
    with open(mapping_path, "r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            filename = row.get("Image_Filename")
            target = row.get("Target_Folder_Name")
            if not filename or not target:
                continue
            stem = os.path.splitext(filename)[0]
            prefix = f"Env_{target}_{stem}_MV"
            output_dir = os.path.join(ROOT_PATH, config["output_root"], target)
            fallback_dir = os.path.join(ROOT_PATH, config["fallback_env_root"], target)
            output_count = count_images(output_dir, prefix, config["image_exts"])
            fallback_count = count_images(fallback_dir, prefix, config["image_exts"])
            total = output_count + fallback_count
            status = "ok" if total > 0 else "missing"
            results.append({
                "target_folder": target,
                "source_image": filename,
                "prefix": prefix,
                "output_dir": output_dir,
                "fallback_dir": fallback_dir,
                "count": total,
                "status": status
            })

    return results


def write_outputs(results, output_json, output_summary):
    payload = {
        "generated_at": int(time.time()),
        "items": results
    }
    with open(output_json, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)

    lines = ["# Environment Audit Summary", ""]
    for item in results:
        lines.append(f"- {item['target_folder']} / {item['source_image']}: {item['status']} ({item['count']})")
    with open(output_summary, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description="Audit environment outputs.")
    parser.add_argument("--config", default=DEFAULT_CONFIG, help="Config JSON path")
    parser.add_argument("--output-json", default="env_audit.json", help="Output JSON path")
    parser.add_argument("--output-summary", default="env_audit_summary.md", help="Output summary path")
    args = parser.parse_args()

    config = load_config(args.config)
    results = build_audit(config)
    output_json = os.path.join(ROOT_PATH, args.output_json)
    output_summary = os.path.join(ROOT_PATH, args.output_summary)
    write_outputs(results, output_json, output_summary)
    print(f"Wrote {output_json}")


if __name__ == "__main__":
    main()
