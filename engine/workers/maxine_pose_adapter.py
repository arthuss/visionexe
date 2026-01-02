import os
import json
import argparse

DEFAULT_BASE_PATH = r"C:\Users\sasch\henoch\filmsets"
DEFAULT_FPS = 24
KEYPOINT_NAMES = [
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


def parse_scene_selector(value):
    if not value:
        return None
    value = value.strip()
    if value.startswith("scene_"):
        return value
    parts = value.split(".")
    if parts and parts[0].isdigit():
        act = int(parts[0])
        sub = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
        return f"scene_{act:02d}_{sub:02d}"
    return None


def load_bodytrack_txt(path):
    lines = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("//"):
                continue
            lines.append(line)
    return lines


def parse_frame_lines(lines):
    frames = []
    i = 0
    frame_idx = 0
    while i + 1 < len(lines):
        header = lines[i]
        data = lines[i + 1]
        i += 2

        header_tokens = [t for t in header.split(",") if t != ""]
        if len(header_tokens) < 2:
            continue
        try:
            body_detect_on = int(float(header_tokens[0])) == 1
            keypoint_detect_on = int(float(header_tokens[1])) == 1
        except ValueError:
            continue

        tokens = [t for t in data.split(",") if t != ""]
        if not tokens:
            continue

        try:
            num_people = int(float(tokens[0]))
        except ValueError:
            num_people = 0
        idx = 1

        bboxes = []
        for _ in range(num_people):
            if idx + 3 >= len(tokens):
                break
            try:
                x = float(tokens[idx])
                y = float(tokens[idx + 1])
                w = float(tokens[idx + 2])
                h = float(tokens[idx + 3])
            except ValueError:
                break
            bboxes.append([x, y, w, h])
            idx += 4

        num_keypoints = 0
        if idx < len(tokens):
            try:
                num_keypoints = int(float(tokens[idx]))
            except ValueError:
                num_keypoints = 0
        idx += 1

        keypoints = []
        for _ in range(num_keypoints):
            if idx + 1 >= len(tokens):
                break
            try:
                x = float(tokens[idx])
                y = float(tokens[idx + 1])
            except ValueError:
                break
            keypoints.append([x, y])
            idx += 2

        frames.append({
            "frame": frame_idx,
            "body_detect_on": body_detect_on,
            "keypoint_detect_on": keypoint_detect_on,
            "people": [{"bbox": bbox} for bbox in bboxes],
            "primary": {
                "bbox": bboxes[0] if bboxes else None,
                "keypoints_2d": keypoints,
            },
        })
        frame_idx += 1
    return frames


def build_payload(source_path, fps, frames):
    return {
        "source": {
            "type": "maxine_bodytrack_txt",
            "path": source_path,
        },
        "fps": fps,
        "keypoint_names": KEYPOINT_NAMES,
        "frames": frames,
        "notes": [
            "BodyTrackApp export provides 2D keypoints only.",
            "Keypoints are for the primary tracked person; bboxes may include multiple people.",
        ],
    }


def resolve_output_path(chapter_path, slug, output_path):
    if output_path:
        return output_path
    media_dir = os.path.join(chapter_path, "Media")
    os.makedirs(media_dir, exist_ok=True)
    return os.path.join(media_dir, f"{slug}_body_pose.json")


def run(input_path, chapter_num, scene_selector, output_path, fps, dry_run):
    if not os.path.exists(input_path):
        print(f"Fehler: Input nicht gefunden: {input_path}")
        return

    slug = parse_scene_selector(scene_selector) if scene_selector else None
    if chapter_num is None and not output_path:
        print("Fehler: --output oder --chapter/--scene erforderlich.")
        return

    chapter_path = None
    if chapter_num is not None:
        chapter_folder = f"chapter_{chapter_num:03d}"
        chapter_path = os.path.join(DEFAULT_BASE_PATH, chapter_folder)

    lines = load_bodytrack_txt(input_path)
    frames = parse_frame_lines(lines)
    payload = build_payload(input_path, fps, frames)

    output_path = resolve_output_path(chapter_path, slug, output_path) if chapter_path else output_path
    if dry_run:
        print(json.dumps(payload, indent=2))
        print(f"Output: {output_path}")
        return

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=True)
    print(f"Wrote: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Maxine BodyTrackApp txt output to pose JSON.")
    parser.add_argument("--input", required=True, help="BodyTrackApp output .txt file")
    parser.add_argument("--chapter", type=int, default=None, help="Chapter number for Media output")
    parser.add_argument("--scene", default=None, help="Scene id (e.g. 1.1 or scene_01_01)")
    parser.add_argument("--output", default=None, help="Explicit output JSON path")
    parser.add_argument("--fps", type=int, default=DEFAULT_FPS)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    run(
        input_path=args.input,
        chapter_num=args.chapter,
        scene_selector=args.scene,
        output_path=args.output,
        fps=args.fps,
        dry_run=args.dry_run,
    )
