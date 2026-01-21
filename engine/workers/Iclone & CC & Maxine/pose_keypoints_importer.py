import argparse
import json
import os

DEFAULT_CATALOG = r"C:\Users\sasch\henoch\pose_catalog.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_keypoints(raw):
    if raw is None:
        return None
    if isinstance(raw, list) and raw and all(isinstance(item, (int, float)) for item in raw):
        if len(raw) % 4 != 0:
            return None
        grouped = []
        for idx in range(0, len(raw), 4):
            grouped.append([float(v) for v in raw[idx:idx + 4]])
        return grouped
    if isinstance(raw, list) and raw and all(isinstance(item, (list, tuple)) for item in raw):
        grouped = []
        for item in raw:
            if len(item) != 4:
                return None
            grouped.append([float(v) for v in item])
        return grouped
    return None


def extract_items(payload):
    if isinstance(payload, dict):
        if "poses" in payload and isinstance(payload["poses"], list):
            return payload["poses"]
        if "pose_id" in payload and "keypoints" in payload:
            return [payload]
        items = []
        for key, value in payload.items():
            if isinstance(value, (list, tuple)):
                items.append({"pose_id": key, "keypoints": value})
        return items
    if isinstance(payload, list):
        return payload
    return []


def load_keypoint_items(paths):
    items = []
    for path in paths:
        payload = load_json(path)
        items.extend(extract_items(payload))
    return items


def collect_inputs(path_or_dir):
    if os.path.isdir(path_or_dir):
        return [
            os.path.join(path_or_dir, name)
            for name in os.listdir(path_or_dir)
            if name.lower().endswith(".json")
        ]
    return [path_or_dir]


def update_catalog(catalog_path, inputs, allow_new, dry_run):
    if not os.path.exists(catalog_path):
        raise FileNotFoundError(f"Pose catalog not found: {catalog_path}")

    catalog = load_json(catalog_path)
    poses = catalog.get("poses", [])
    index = {pose.get("pose_id"): pose for pose in poses if pose.get("pose_id")}

    updated = 0
    added = 0
    skipped = 0

    items = load_keypoint_items(inputs)
    for item in items:
        pose_id = item.get("pose_id")
        keypoints = normalize_keypoints(item.get("keypoints"))
        if not pose_id or not keypoints:
            skipped += 1
            continue
        pose = index.get(pose_id)
        if not pose:
            if not allow_new:
                skipped += 1
                continue
            pose = {"pose_id": pose_id, "source_path": "", "source_root": "", "tags": []}
            poses.append(pose)
            index[pose_id] = pose
            added += 1
        pose["keypoints"] = keypoints
        updated += 1

    catalog["pose_count"] = len(poses)

    if dry_run:
        print(f"Dry run: updated={updated}, added={added}, skipped={skipped}")
        return

    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=True)

    print(f"Updated: {catalog_path}")
    print(f"Updated poses: {updated}, Added: {added}, Skipped: {skipped}")


def main():
    parser = argparse.ArgumentParser(description="Import pose keypoints into pose_catalog.json")
    parser.add_argument("--catalog", default=DEFAULT_CATALOG)
    parser.add_argument("--input", required=True, help="JSON file or folder with pose keypoints")
    parser.add_argument("--allow-new", action="store_true", help="Add pose IDs not in catalog")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    inputs = collect_inputs(args.input)
    update_catalog(args.catalog, inputs, args.allow_new, args.dry_run)


if __name__ == "__main__":
    main()
