import argparse
import json
import time
from pathlib import Path

from visionexe_paths import load_story_config, resolve_path


def read_lines(path: Path):
    return path.read_text(encoding="utf-8", errors="ignore").splitlines()


def parse_bvh(path: Path):
    lines = read_lines(path)
    joint_order = []
    offsets = {}
    channels = {}
    current_joint = None

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("ROOT ") or line.startswith("JOINT "):
            parts = line.split()
            name = parts[1] if len(parts) > 1 else f"Joint_{len(joint_order):03d}"
            joint_order.append(name)
            current_joint = name
            i += 1
            continue
        if line.startswith("OFFSET ") and current_joint:
            parts = line.split()
            offsets[current_joint] = [float(parts[1]), float(parts[2]), float(parts[3])]
        if line.startswith("CHANNELS ") and current_joint:
            parts = line.split()
            count = int(parts[1])
            channels[current_joint] = parts[2:2 + count]
        if line.startswith("MOTION"):
            break
        i += 1

    frame_count = 0
    frame_time = 0.0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("Frames:"):
            frame_count = int(line.split(":", 1)[1].strip())
        if line.startswith("Frame Time:"):
            frame_time = float(line.split(":", 1)[1].strip())
            i += 1
            break
        i += 1

    channel_total = sum(len(channels.get(name, [])) for name in joint_order)
    values = []
    while i < len(lines) and len(values) < channel_total:
        line = lines[i].strip()
        if line:
            values.extend([float(val) for val in line.split()])
        i += 1

    if len(values) < channel_total:
        raise ValueError(f"BVH frame data incomplete: expected {channel_total}, got {len(values)}")

    idx = 0
    pose = {}
    for name in joint_order:
        joint_channels = channels.get(name, [])
        joint_values = values[idx:idx + len(joint_channels)]
        idx += len(joint_channels)
        rotation = {"x": 0.0, "y": 0.0, "z": 0.0}
        translation = {"x": 0.0, "y": 0.0, "z": 0.0}
        rotation_order = []
        for channel, value in zip(joint_channels, joint_values):
            axis = channel[0].lower()
            if channel.endswith("position"):
                translation[axis] = float(value)
            elif channel.endswith("rotation"):
                rotation[axis] = float(value)
                rotation_order.append(axis.upper())
        pose[name] = {
            "rotation": rotation,
            "translation": translation,
            "rotation_order": "".join(rotation_order) or "ZXY",
            "channels": joint_channels,
            "offset": offsets.get(name, [0.0, 0.0, 0.0]),
        }

    return {
        "joint_order": joint_order,
        "offsets": offsets,
        "channels": channels,
        "frame_time": frame_time,
        "frame_count": frame_count,
        "pose": pose,
    }


def normalize_root_name(parsed: dict) -> dict:
    joint_order = parsed.get("joint_order") or []
    if not joint_order:
        return parsed
    root_name = joint_order[0]
    if str(root_name).lower() != "hips":
        return parsed
    if "Joint_000" in joint_order:
        return parsed
    new_name = "Joint_000"
    joint_order[0] = new_name
    for key in ("offsets", "channels", "pose"):
        data = parsed.get(key) or {}
        if root_name in data:
            data[new_name] = data.pop(root_name)
            continue
        for existing in list(data.keys()):
            if str(existing).lower() == "hips":
                data[new_name] = data.pop(existing)
                break
    return parsed


def infer_coverage(joint_count: int) -> str:
    if joint_count <= 20:
        return "upper_body"
    return "full_body"


def load_mapping(path: Path | None):
    if not path or not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_mapping_template(path: Path, joint_order: list[str], source_name: str, rotation_order: str):
    joint_map = {name: "" for name in joint_order}
    payload = {
        "schema_version": "pose_mapping_v1",
        "source": {
            "name": source_name,
            "notes": "Joint order comes from BVH hierarchy (depth-first).",
            "rotation_order": rotation_order,
        },
        "target": {
            "name": "cc4",
            "notes": "Fill in CC4 bone names per joint.",
        },
        "joint_map": joint_map,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def to_relpath(path: Path, repo_root: Path) -> str:
    try:
        return str(path.relative_to(repo_root)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def update_pose_library(library_path: Path, pose_id: str, pose_path: Path, repo_root: Path, coverage: str):
    payload = None
    if library_path.exists():
        payload = json.loads(library_path.read_text(encoding="utf-8"))
    if not payload:
        payload = {
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "category": "pose",
            "count": 0,
            "items": [],
        }
    items = payload.get("items", [])
    entry = {
        "id": pose_id,
        "label": pose_id.replace("_", " "),
        "path": to_relpath(pose_path, repo_root),
        "category": "pose",
        "source": "sam3_bvh",
        "notes": "",
        "tags": [coverage],
    }
    items = [item for item in items if item.get("id") != pose_id]
    items.append(entry)
    payload["items"] = items
    payload["count"] = len(items)
    library_path.parent.mkdir(parents=True, exist_ok=True)
    library_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Import SAM3 BVH pose and build a mapping stub.")
    parser.add_argument("--input", required=True, help="Input BVH file.")
    parser.add_argument("--output", help="Output JSON path for the parsed pose.")
    parser.add_argument("--pose-id", help="Pose ID (defaults to BVH stem).")
    parser.add_argument("--coverage", help="Override coverage (upper_body/full_body).")
    parser.add_argument("--mapping", help="Pose mapping JSON path.")
    parser.add_argument("--write-mapping-template", action="store_true", help="Write mapping template and exit.")
    parser.add_argument("--library-out", help="Append pose entry to pose_library.json.")
    parser.add_argument("--story-root", help="Story root path.")
    parser.add_argument("--story-config", help="Path to story_config.json.")
    args = parser.parse_args()

    story_config, _, repo_root = load_story_config(
        story_root=args.story_root,
        story_config_path=args.story_config,
    )

    input_path = resolve_path(args.input, repo_root)
    parsed = normalize_root_name(parse_bvh(Path(input_path)))

    pose_id = args.pose_id or Path(input_path).stem
    coverage = args.coverage or infer_coverage(len(parsed["joint_order"]))

    mapping_path = resolve_path(args.mapping or "engine/config/pose_mappings/sam3_bvh_to_cc4.json", repo_root)
    mapping = load_mapping(Path(mapping_path))

    if args.write_mapping_template or not mapping:
        mapping = write_mapping_template(Path(mapping_path), parsed["joint_order"], "sam3_bvh", "ZXY")
        if args.write_mapping_template:
            print(f"Wrote mapping template: {mapping_path}")
            return

    joint_map = mapping.get("joint_map", {}) if mapping else {}
    mapped_pose = {}
    unmapped = []
    for name in parsed["joint_order"]:
        target = joint_map.get(name)
        if not target:
            unmapped.append(name)
            continue
        mapped_pose[target] = parsed["pose"][name]

    output_path = Path(resolve_path(args.output or f"{input_path}.pose.json", repo_root))
    payload = {
        "schema_version": "pose_bvh_v1",
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "pose_id": pose_id,
        "coverage": coverage,
        "source": {
            "path": str(input_path),
            "frame_time": parsed["frame_time"],
            "frame_count": parsed["frame_count"],
            "joint_order": parsed["joint_order"],
        },
        "pose": parsed["pose"],
        "mapping": {
            "path": str(mapping_path),
            "mapped_count": len(mapped_pose),
            "unmapped": unmapped,
        },
        "mapped_pose": {
            "target": mapping.get("target", {}).get("name", "cc4") if mapping else "cc4",
            "bones": mapped_pose,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote pose JSON: {output_path}")

    if args.library_out:
        library_path = Path(resolve_path(args.library_out, repo_root))
        if library_path.exists() and library_path.is_dir():
            library_path = library_path / "pose_library.json"
        elif library_path.suffix.lower() != ".json" and not library_path.exists():
            library_path.mkdir(parents=True, exist_ok=True)
            library_path = library_path / "pose_library.json"
        update_pose_library(library_path, pose_id, output_path, Path(repo_root), coverage)
        print(f"Updated pose library: {library_path}")


if __name__ == "__main__":
    main()
