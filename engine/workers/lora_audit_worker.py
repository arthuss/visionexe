import argparse
import json
import os
import unicodedata
import time

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG = os.path.join(ROOT_PATH, "lora_audit_config.json")
LORA_SET_PATH = os.path.join(ROOT_PATH, "LORA_TRAINING_SET.json")
LORA_QUEUE_PATH = os.path.join(ROOT_PATH, "LORA_TRAINING_QUEUE.json")


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
        "actor_image_root": config.get("actor_image_root", "produced_assets/lora_training/actors"),
        "training_data_root": config.get("training_data_root", "training_data/lora_training/actors"),
        "lora_root": config.get("lora_root", "produced_assets/lora_training/actors"),
        "image_exts": config.get("image_exts", [".png", ".jpg", ".jpeg", ".webp"]),
        "min_images_per_phase": int(config.get("min_images_per_phase", 1))
    }


def normalize_key(value):
    text = unicodedata.normalize("NFKD", str(value or "")).encode("ascii", "ignore").decode("ascii")
    return "".join(ch.lower() if ch.isalnum() else " " for ch in text).strip()


def slugify(value):
    text = unicodedata.normalize("NFKD", str(value or "")).encode("ascii", "ignore").decode("ascii")
    slug = []
    prev_underscore = False
    for ch in text.lower():
        if ch.isalnum():
            slug.append(ch)
            prev_underscore = False
        else:
            if not prev_underscore:
                slug.append("_")
                prev_underscore = True
    result = "".join(slug).strip("_")
    return result or "unknown"


def ascii_label(value):
    return unicodedata.normalize("NFKD", str(value or "")).encode("ascii", "ignore").decode("ascii")


def count_images(folder, exts):
    if not os.path.isdir(folder):
        return 0
    count = 0
    for name in os.listdir(folder):
        if os.path.splitext(name)[1].lower() in exts:
            count += 1
    return count


def load_queue_index(queue_data):
    index = {}
    if not isinstance(queue_data, list):
        return index
    for item in queue_data:
        if not isinstance(item, dict):
            continue
        if item.get("entity_type") != "actor":
            continue
        actor = item.get("entity_name") or ""
        phase = item.get("phase_name") or ""
        key = (normalize_key(actor), normalize_key(phase))
        index[key] = index.get(key, 0) + 1
    return index


def find_lora_matches(lora_root, actor_name, phase_name):
    matches = []
    if not os.path.isdir(lora_root):
        return matches
    actor_key = normalize_key(actor_name)
    phase_key = normalize_key(phase_name)
    for name in os.listdir(lora_root):
        if not name.lower().endswith(".safetensors"):
            continue
        norm = normalize_key(name)
        if actor_key and actor_key in norm and (not phase_key or phase_key in norm):
            matches.append(os.path.join(lora_root, name))
    return sorted(matches)


def build_audit(config, lora_set, lora_queue):
    actors = lora_set.get("actors", {}) if isinstance(lora_set, dict) else {}
    queue_index = load_queue_index(lora_queue)
    results = []
    for actor_name, info in actors.items():
        phases = info.get("phases", []) if isinstance(info, dict) else []
        for phase in phases:
            phase_name = phase.get("name") if isinstance(phase, dict) else ""
            actor_slug = slugify(actor_name)
            phase_slug = slugify(phase_name)
            image_dir = os.path.join(ROOT_PATH, config["actor_image_root"], actor_slug, phase_slug)
            training_dir = os.path.join(ROOT_PATH, config["training_data_root"], actor_slug, phase_slug)
            image_count = count_images(image_dir, config["image_exts"])
            expected_images = queue_index.get((normalize_key(actor_name), normalize_key(phase_name)), 0)
            if expected_images <= 0:
                expected_images = config["min_images_per_phase"]
            lora_matches = find_lora_matches(os.path.join(ROOT_PATH, config["lora_root"]), actor_name, phase_name)

            image_status = "ok" if image_count >= expected_images else "missing"
            lora_status = "ok" if lora_matches else "missing"

            results.append({
                "actor": actor_name,
                "phase": phase_name,
                "actor_slug": actor_slug,
                "phase_slug": phase_slug,
                "image_dir": image_dir,
                "training_dir": training_dir,
                "image_count": image_count,
                "expected_images": expected_images,
                "lora_matches": lora_matches,
                "status": {
                    "images": image_status,
                    "lora": lora_status
                }
            })
    return results


def write_outputs(results, output_json, output_summary):
    payload = {
        "generated_at": int(time.time()),
        "items": results
    }
    with open(output_json, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)

    lines = ["# LoRA Audit Summary", ""]
    for item in results:
        actor = ascii_label(item["actor"])
        phase = ascii_label(item["phase"])
        images = f"{item['image_count']}/{item['expected_images']}"
        status = f"images={item['status']['images']}, lora={item['status']['lora']}"
        lines.append(f"- {actor} / {phase}: {images} ({status})")
    with open(output_summary, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description="Audit actor LoRA training assets.")
    parser.add_argument("--config", default=DEFAULT_CONFIG, help="Config JSON path")
    parser.add_argument("--output-json", default="lora_audit.json", help="Output JSON path")
    parser.add_argument("--output-summary", default="lora_audit_summary.md", help="Output summary path")
    args = parser.parse_args()

    config = load_config(args.config)
    lora_set = load_json(LORA_SET_PATH)
    if not lora_set:
        raise RuntimeError("LORA_TRAINING_SET.json not found or invalid.")
    lora_queue = load_json(LORA_QUEUE_PATH)

    results = build_audit(config, lora_set, lora_queue)
    output_json = os.path.join(ROOT_PATH, args.output_json)
    output_summary = os.path.join(ROOT_PATH, args.output_summary)
    write_outputs(results, output_json, output_summary)
    print(f"Wrote {output_json}")


if __name__ == "__main__":
    main()
