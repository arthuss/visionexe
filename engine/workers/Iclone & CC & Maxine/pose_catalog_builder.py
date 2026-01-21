import argparse
import json
import os
import re

ROOT_PATH = r"C:\Users\sasch\henoch"
DEFAULT_OUTPUT = os.path.join(ROOT_PATH, "pose_catalog.json")
DEFAULT_ROOTS = [
    r"C:\Users\sasch\avatar\avatar-studio@1.0.1+1.0.642.bf3ef250.gl.windows-x86_64.release\exported\Animations",
    r"C:\Users\sasch\avatar\ACE\tools\avatar_configurator\template_scene\Core_Assets\Animations",
]
VALID_EXTS = (".usd", ".usda", ".fbx", ".anim")

TAG_ALIASES = {
    "idle": "idle",
    "stand": "idle",
    "standing": "idle",
    "walk": "walk",
    "step": "walk",
    "forward": "forward",
    "back": "back",
    "left": "left",
    "right": "right",
    "turn": "turn",
    "rotate": "turn",
    "talk": "talk",
    "talking": "talk",
    "listen": "listen",
    "listening": "listen",
    "think": "think",
    "thinking": "think",
    "gesture": "gesture",
    "facial": "facial",
    "posture": "posture",
}


def slugify(value):
    if not value:
        return ""
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def extract_tags(path_parts):
    tags = set()
    for part in path_parts:
        tokens = re.split(r"[_\-\s]+", part)
        for token in tokens:
            if not token:
                continue
            normalized = TAG_ALIASES.get(token.lower())
            if normalized:
                tags.add(normalized)
    return sorted(tags)


def build_catalog(roots, output_path):
    poses = []
    used_ids = set()

    for root in roots:
        if not os.path.isdir(root):
            print(f"Skip (missing): {root}")
            continue
        root_label = "avatar_studio" if "avatar-studio@" in root else "ace"

        for dirpath, _, filenames in os.walk(root):
            rel_dir = os.path.relpath(dirpath, root)
            for name in filenames:
                if not name.lower().endswith(VALID_EXTS):
                    continue
                base = os.path.splitext(name)[0]
                pose_id = slugify(base)
                if not pose_id:
                    continue
                original_id = pose_id
                counter = 2
                while pose_id in used_ids:
                    pose_id = f"{original_id}_{counter}"
                    counter += 1
                used_ids.add(pose_id)

                path_parts = [root_label] + [p for p in rel_dir.split(os.sep) if p and p != "."] + [base]
                tags = extract_tags(path_parts)
                if root_label:
                    tags.append(root_label)

                poses.append(
                    {
                        "pose_id": pose_id,
                        "source_path": os.path.join(dirpath, name),
                        "source_root": root,
                        "source_label": root_label,
                        "tags": sorted(set(tags)),
                        "keypoints": None,
                    }
                )

    payload = {
        "schema_version": "pose_catalog_v1",
        "pose_count": len(poses),
        "poses": poses,
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=True)

    print(f"Wrote: {output_path}")
    print(f"Poses: {len(poses)}")


def main():
    parser = argparse.ArgumentParser(description="Build a pose catalog from animation assets.")
    parser.add_argument("--root", action="append", help="Root folder to scan for poses.")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Output catalog JSON path.")
    args = parser.parse_args()

    roots = args.root or DEFAULT_ROOTS
    build_catalog(roots, args.output)


if __name__ == "__main__":
    main()
