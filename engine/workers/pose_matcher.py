import argparse
import json
import math
import os
import re

DEFAULT_LIBRARY = r"C:\Users\sasch\henoch\pose_catalog.json"
DEFAULT_OUTPUT = r"C:\Users\sasch\henoch\pose_match.json"

KEYPOINTS_34 = [
    "pelvis",
    "left_hip",
    "right_hip",
    "torso",
    "left_knee",
    "right_knee",
    "neck",
    "left_ankle",
    "right_ankle",
    "left_big_toe",
    "right_big_toe",
    "left_small_toe",
    "right_small_toe",
    "left_heel",
    "right_heel",
    "nose",
    "left_eye",
    "right_eye",
    "left_ear",
    "right_ear",
    "left_shoulder",
    "right_shoulder",
    "left_elbow",
    "right_elbow",
    "left_wrist",
    "right_wrist",
    "left_pinky_knuckle",
    "right_pinky_knuckle",
    "left_middle_tip",
    "right_middle_tip",
    "left_index_knuckle",
    "right_index_knuckle",
    "left_thumb_tip",
    "right_thumb_tip",
]


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def iter_objects(data):
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        return
    for entry in data:
        for batch in entry.get("batches", []):
            frame_num = batch.get("frame_num")
            for obj in batch.get("objects", []):
                yield frame_num, obj


def select_object(data, object_id=None):
    best = None
    best_score = -1.0
    for frame_num, obj in iter_objects(data):
        if object_id is not None and obj.get("object_id") != object_id:
            continue
        pose = obj.get("pose3d") or obj.get("pose25d")
        if not pose:
            continue
        confidences = pose[3::4]
        if not confidences:
            continue
        score = sum(confidences) / len(confidences)
        if score > best_score:
            best_score = score
            best = (frame_num, obj)
    return best


def extract_pose(obj, pose_type):
    pose = obj.get(pose_type)
    if not pose:
        return None
    points = []
    for idx in range(0, len(pose), 4):
        x, y, z, conf = pose[idx:idx + 4]
        points.append((float(x), float(y), float(z), float(conf)))
    return points


def normalize_points(points, min_conf=0.15):
    pelvis_idx = 0
    left_hip_idx = 1
    right_hip_idx = 2
    left_shoulder_idx = 20
    right_shoulder_idx = 21

    if len(points) <= right_hip_idx:
        return points, 1.0

    pelvis = points[pelvis_idx]
    if pelvis[3] < min_conf:
        pelvis = max(points, key=lambda p: p[3])

    centered = []
    for x, y, z, conf in points:
        centered.append((x - pelvis[0], y - pelvis[1], z - pelvis[2], conf))

    scale = None
    if points[left_hip_idx][3] >= min_conf and points[right_hip_idx][3] >= min_conf:
        scale = distance(points[left_hip_idx], points[right_hip_idx])
    if not scale and points[left_shoulder_idx][3] >= min_conf and points[right_shoulder_idx][3] >= min_conf:
        scale = distance(points[left_shoulder_idx], points[right_shoulder_idx])
    if not scale or scale <= 1e-6:
        scale = 1.0

    normalized = []
    for x, y, z, conf in centered:
        normalized.append((x / scale, y / scale, z / scale, conf))
    return normalized, scale


def distance(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)


def pose_distance(a, b, min_conf=0.15):
    if len(a) != len(b):
        return None
    total = 0.0
    count = 0
    for pa, pb in zip(a, b):
        if pa[3] < min_conf or pb[3] < min_conf:
            continue
        total += (pa[0] - pb[0]) ** 2 + (pa[1] - pb[1]) ** 2 + (pa[2] - pb[2]) ** 2
        count += 1
    if count == 0:
        return None
    return total / float(count)


def derive_tags(points, min_conf=0.15):
    tags = set()
    nose_idx = 15
    left_eye_idx = 16
    right_eye_idx = 17
    left_wrist_idx = 24
    right_wrist_idx = 25
    left_shoulder_idx = 20
    right_shoulder_idx = 21

    face_conf = 0.0
    for idx in (nose_idx, left_eye_idx, right_eye_idx):
        if idx < len(points):
            face_conf += points[idx][3]
    if face_conf >= min_conf * 2:
        tags.add("front")
    else:
        tags.add("back")

    if (
        left_wrist_idx < len(points)
        and right_wrist_idx < len(points)
        and left_shoulder_idx < len(points)
        and right_shoulder_idx < len(points)
    ):
        lw, rw = points[left_wrist_idx], points[right_wrist_idx]
        ls, rs = points[left_shoulder_idx], points[right_shoulder_idx]
        if lw[3] >= min_conf and ls[3] >= min_conf and lw[1] < ls[1]:
            tags.add("arms_up")
        if rw[3] >= min_conf and rs[3] >= min_conf and rw[1] < rs[1]:
            tags.add("arms_up")
    return sorted(tags)


def match_by_tags(poses, desired_tags):
    matches = []
    desired = set(desired_tags or [])
    for pose in poses:
        pose_tags = set(pose.get("tags") or [])
        score = len(desired & pose_tags)
        matches.append((score, pose))
    matches.sort(key=lambda item: item[0], reverse=True)
    return matches


def run(pose_json, library_path, output_path, pose_type, object_id, min_conf, top_k):
    if not os.path.exists(pose_json):
        print(f"Pose JSON not found: {pose_json}")
        return
    if not os.path.exists(library_path):
        print(f"Pose library not found: {library_path}")
        return

    data = load_json(pose_json)
    selected = select_object(data, object_id)
    if not selected:
        print("No pose object found.")
        return

    frame_num, obj = selected
    points = extract_pose(obj, pose_type)
    if not points:
        print(f"Pose type not found: {pose_type}")
        return

    points, _ = normalize_points(points, min_conf=min_conf)
    derived_tags = derive_tags(points, min_conf=min_conf)

    library = load_json(library_path)
    poses = library.get("poses", [])
    scored = []
    used_keypoints = False
    for pose in poses:
        kp = pose.get("keypoints")
        if not kp:
            continue
        used_keypoints = True
        pose_points = [(float(x), float(y), float(z), float(conf)) for x, y, z, conf in kp]
        pose_points, _ = normalize_points(pose_points, min_conf=min_conf)
        dist = pose_distance(points, pose_points, min_conf=min_conf)
        if dist is None:
            continue
        scored.append((dist, pose))

    if used_keypoints and scored:
        scored.sort(key=lambda item: item[0])
        top = scored[:top_k]
        matches = [
            {"pose_id": item[1]["pose_id"], "score": item[0], "tags": item[1].get("tags", [])}
            for item in top
        ]
        method = "keypoint"
    else:
        tag_matches = match_by_tags(poses, derived_tags)
        top = tag_matches[:top_k]
        matches = [
            {"pose_id": item[1]["pose_id"], "score": item[0], "tags": item[1].get("tags", [])}
            for item in top
        ]
        method = "tag"

    payload = {
        "pose_json": pose_json,
        "pose_type": pose_type,
        "object_id": obj.get("object_id"),
        "frame_num": frame_num,
        "match_method": method,
        "derived_tags": derived_tags,
        "matches": matches,
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=True)
    print(f"Wrote: {output_path}")
    if matches:
        print(f"Top match: {matches[0]['pose_id']} (score={matches[0]['score']})")


def main():
    parser = argparse.ArgumentParser(description="Match a DeepStream pose to a pose catalog.")
    parser.add_argument("--pose-json", required=True, help="DeepStream pose JSON (pose25d/pose3d).")
    parser.add_argument("--library", default=DEFAULT_LIBRARY, help="Pose catalog JSON.")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Output match JSON.")
    parser.add_argument("--pose-type", default="pose3d", choices=["pose3d", "pose25d"])
    parser.add_argument("--object-id", type=int, default=None)
    parser.add_argument("--min-conf", type=float, default=0.15)
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    run(
        pose_json=args.pose_json,
        library_path=args.library,
        output_path=args.output,
        pose_type=args.pose_type,
        object_id=args.object_id,
        min_conf=args.min_conf,
        top_k=args.top_k,
    )


if __name__ == "__main__":
    main()
