import argparse
import json
import os
import unicodedata
import time

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG = os.path.join(ROOT_PATH, "prop_audit_config.json")


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
        "queue_path": config.get("queue_path", "LORA_PROP_QUEUE.json"),
        "image_exts": config.get("image_exts", [".png", ".jpg", ".jpeg", ".webp"])
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


def build_audit(config, queue):
    groups = {}
    for item in queue or []:
        if not isinstance(item, dict):
            continue
        if item.get("entity_type") != "prop":
            continue
        actor_slug = item.get("actor_slug") or slugify(item.get("entity_name"))
        prop_slug = item.get("prop_slug") or slugify(item.get("prop_name"))
        key = (actor_slug, prop_slug)
        entry = groups.setdefault(key, {
            "actor": item.get("entity_name") or actor_slug,
            "actor_slug": actor_slug,
            "prop": item.get("prop_name") or prop_slug,
            "prop_slug": prop_slug,
            "output_dir": item.get("output_dir"),
            "expected_images": 0,
        })
        entry["output_dir"] = entry["output_dir"] or item.get("output_dir")
        entry["expected_images"] += int(item.get("expected_outputs") or 1)

    results = []
    for (actor_slug, prop_slug), entry in groups.items():
        output_dir = entry.get("output_dir") or os.path.join(
            ROOT_PATH, "produced_assets", "lora_training", "actors", actor_slug, "props", prop_slug
        )
        prefix = f"prop__{prop_slug}__{actor_slug}"
        image_count = count_images(output_dir, prefix, config["image_exts"])
        status = "ok" if image_count >= entry["expected_images"] else "missing"
        results.append({
            "actor": entry["actor"],
            "actor_slug": actor_slug,
            "prop": entry["prop"],
            "prop_slug": prop_slug,
            "output_dir": output_dir,
            "expected_images": entry["expected_images"],
            "image_count": image_count,
            "status": status
        })

    return sorted(results, key=lambda r: (r["actor_slug"], r["prop_slug"]))


def write_outputs(results, output_json, output_summary):
    payload = {
        "generated_at": int(time.time()),
        "items": results
    }
    with open(output_json, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)

    lines = ["# Prop LoRA Audit Summary", ""]
    for item in results:
        actor = ascii_label(item["actor"])
        prop = ascii_label(item["prop"])
        images = f"{item['image_count']}/{item['expected_images']}"
        lines.append(f"- {actor} / {prop}: {images} ({item['status']})")
    with open(output_summary, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description="Audit prop LoRA training outputs.")
    parser.add_argument("--config", default=DEFAULT_CONFIG, help="Config JSON path")
    parser.add_argument("--output-json", default="prop_audit.json", help="Output JSON path")
    parser.add_argument("--output-summary", default="prop_audit_summary.md", help="Output summary path")
    args = parser.parse_args()

    config = load_config(args.config)
    queue_path = os.path.join(ROOT_PATH, config["queue_path"])
    queue = load_json(queue_path)
    if queue is None:
        raise RuntimeError(f"Missing queue file: {queue_path}")

    results = build_audit(config, queue)
    output_json = os.path.join(ROOT_PATH, args.output_json)
    output_summary = os.path.join(ROOT_PATH, args.output_summary)
    write_outputs(results, output_json, output_summary)
    print(f"Wrote {output_json}")


if __name__ == "__main__":
    main()
