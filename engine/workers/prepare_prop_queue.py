import argparse
import json
import os
import re
import unicodedata

ROOT_PATH = os.path.abspath(r"C:\Users\sasch\henoch")
INPUT_DB = os.path.join(ROOT_PATH, "ACTOR_PROP_DB.json")
OUTPUT_QUEUE = os.path.join(ROOT_PATH, "LORA_PROP_QUEUE.json")
OUTPUT_SUMMARY = os.path.join(ROOT_PATH, "LORA_PROP_QUEUE.md")

OUTPUT_ROOT = os.path.join(ROOT_PATH, "produced_assets", "lora_training", "actors")

DEFAULT_WORKFLOW = "wan22_image"

PROP_SHOTS = [
    "macro photography",
    "hero prop on pedestal",
    "in-hand close-up",
    "floating artifact",
    "technical blueprint render",
]

STYLE_HINT = "photorealistic, studio lighting, isolated object, high detail, 8k"


def slugify(text):
    if text is None:
        return "unknown"
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_").lower()
    return text or "unknown"


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def resolve_workflow(name):
    if not name:
        return ""
    if os.path.isabs(name) and os.path.exists(name):
        return name
    if not name.lower().endswith(".json"):
        name = name + ".json"
    candidate = os.path.join(ROOT_PATH, "workflows", name)
    return candidate if os.path.exists(candidate) else name


def make_prop_prompt(prop_name, description, actor_name, shot):
    parts = [prop_name]
    if description:
        parts.append(description)
    if actor_name:
        parts.append(f"associated with {actor_name}")
    parts.append(shot)
    parts.append(STYLE_HINT)
    return ", ".join([p for p in parts if p])


def main():
    parser = argparse.ArgumentParser(description="Prepare LoRA queue for props.")
    parser.add_argument("--include-hints", action="store_true", help="Include hint props from FULL_ACTOR_DB")
    parser.add_argument("--workflow", default=DEFAULT_WORKFLOW, help="Workflow name or full path")
    parser.add_argument("--variants", type=int, default=3, help="Number of shot variants per prop")
    args = parser.parse_args()

    if not os.path.exists(INPUT_DB):
        print(f"Missing input: {INPUT_DB}. Run extract_actor_props.py first.")
        return

    with open(INPUT_DB, "r", encoding="utf-8") as f:
        data = json.load(f)

    queue = []
    total = 0
    workflow = resolve_workflow(args.workflow)

    for actor_slug, payload in data.get("actors", {}).items():
        display_names = payload.get("display_names", [])
        actor_name = display_names[0] if display_names else actor_slug

        props = payload.get("props", [])
        if args.include_hints:
            props = props + payload.get("prop_hints", [])

        for prop in props:
            prop_name = prop.get("name") or "Unknown Prop"
            description = prop.get("description", "")
            prop_slug = slugify(prop_name)

            output_dir = os.path.join(OUTPUT_ROOT, actor_slug, "props", prop_slug)
            ensure_dir(output_dir)

            variants = PROP_SHOTS[: max(1, args.variants)]
            for idx, shot in enumerate(variants, start=1):
                prompt = make_prop_prompt(prop_name, description, actor_name, shot)
                base_name = f"prop__{prop_slug}__{actor_slug}__p{idx:02d}"
                queue.append({
                    "entity_type": "prop",
                    "entity_name": actor_name,
                    "actor_slug": actor_slug,
                    "prop_name": prop_name,
                    "prop_slug": prop_slug,
                    "prompt": prompt,
                    "output_dir": output_dir,
                    "output_basename": base_name,
                    "output_filename": base_name + ".png",
                    "workflow": workflow,
                    "expected_outputs": 1,
                })
                total += 1

    with open(OUTPUT_QUEUE, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2, ensure_ascii=True)

    with open(OUTPUT_SUMMARY, "w", encoding="utf-8") as f:
        f.write("# LoRA Prop Queue Summary\n\n")
        f.write(f"- Total jobs: {total}\n")
        f.write(f"- Workflow: {workflow}\n")
        f.write(f"- Variants per prop: {args.variants}\n")

    print(f"Wrote: {OUTPUT_QUEUE}")
    print(f"Wrote: {OUTPUT_SUMMARY}")


if __name__ == "__main__":
    main()
