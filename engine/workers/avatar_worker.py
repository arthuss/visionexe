import os
import re
import sys
import json
import argparse

try:
    import maxine_pose_adapter as pose_adapter
except ImportError:
    pose_adapter = None

DEFAULT_BASE_PATH = r"C:\Users\sasch\henoch\filmsets"
DEFAULT_FPS = 24
DEFAULT_WIDTH = 1080
DEFAULT_HEIGHT = 1920
DEFAULT_COLOR_SPACE = "linear_rec709"


def parse_scene_selector(value):
    if not value:
        return None
    value = value.strip()
    if value.startswith("scene_"):
        return value
    match = re.match(r"^(\d+)(?:\.(\d+))?$", value)
    if match:
        act = int(match.group(1))
        sub = int(match.group(2) or 0)
        return f"scene_{act:02d}_{sub:02d}"
    return None


def resolve_scene_path(chapter_path, media_dir, value):
    if not value:
        return ""
    if os.path.isabs(value) or value.startswith("\\\\"):
        return value
    normalized = value.replace("/", "\\")
    if normalized.lower().startswith("media\\"):
        return os.path.join(chapter_path, normalized)
    if "\\" in normalized:
        return os.path.join(chapter_path, normalized)
    return os.path.join(media_dir, normalized)


def load_audio_meta(path):
    if not path or not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"Warnung: Konnte Audio Meta nicht lesen: {path} ({exc})")
        return {}


def collect_scene_slugs(chapter_path):
    slugs = set()
    audio_dir = os.path.join(chapter_path, "audio")
    if os.path.isdir(audio_dir):
        for name in os.listdir(audio_dir):
            if name.endswith("_audio_meta.json"):
                slugs.add(name.replace("_audio_meta.json", ""))

    media_dir = os.path.join(chapter_path, "Media")
    if os.path.isdir(media_dir):
        for name in os.listdir(media_dir):
            match = re.match(r"^(scene_\d{2}_\d{2})", name)
            if match:
                slugs.add(match.group(1))

    return sorted(slugs)


def build_manifest(
    chapter_path,
    media_dir,
    slug,
    fps,
    width,
    height,
    color_space,
    overrides=None,
):
    overrides = overrides or {}
    source_video = overrides.get("source_video") or os.path.join(media_dir, f"{slug}.mp4")
    if source_video and not os.path.exists(source_video):
        source_video = ""

    manifest = {
        "scene_id": slug,
        "fps": fps,
        "resolution": [width, height],
        "format": "exr",
        "color_space": color_space,
        "normal_space": "camera",
        "normal_encoding": "signed",
        "depth_units": "meters",
        "depth_near": 0.1,
        "depth_far": 50.0,
        "motion_units": "pixels_per_frame",
        "source_video": source_video,
        "camera_curve": overrides.get("camera_curve")
        or os.path.join(media_dir, f"{slug}_cam_curve.json"),
        "body_pose": overrides.get("body_pose")
        or os.path.join(media_dir, f"{slug}_body_pose.json"),
        "head_pose": overrides.get("head_pose")
        or os.path.join(media_dir, f"{slug}_head_pose.json"),
        "passes": {
            "normal": overrides.get("normal")
            or os.path.join(media_dir, f"{slug}_avatar_normal.exr"),
            "depth": overrides.get("depth")
            or os.path.join(media_dir, f"{slug}_avatar_depth.exr"),
            "motion": overrides.get("motion")
            or os.path.join(media_dir, f"{slug}_avatar_motion.exr"),
            "mask": overrides.get("mask")
            or os.path.join(media_dir, f"{slug}_avatar_mask.exr"),
            "albedo": overrides.get("albedo")
            or os.path.join(media_dir, f"{slug}_avatar_albedo.exr"),
            "uv": overrides.get("uv")
            or os.path.join(media_dir, f"{slug}_avatar_uv.exr"),
            "id": overrides.get("id")
            or os.path.join(media_dir, f"{slug}_avatar_id.exr"),
        },
    }
    return manifest


def write_manifest(path, manifest):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=True)


def validate_scene_inputs(
    slug,
    source_video,
    camera_curve,
    body_pose,
    head_pose,
    source_audio,
    require_video,
    require_camera,
    require_pose,
    require_head_pose,
    require_audio,
):
    missing = []
    if require_video and (not source_video or not os.path.exists(source_video)):
        missing.append(("video", source_video or f"{slug}.mp4"))
    if require_camera and (not camera_curve or not os.path.exists(camera_curve)):
        missing.append(("camera_curve", camera_curve or f"{slug}_cam_curve.json"))
    if require_pose and (not body_pose or not os.path.exists(body_pose)):
        missing.append(("body_pose", body_pose or f"{slug}_body_pose.json"))
    if require_head_pose and (not head_pose or not os.path.exists(head_pose)):
        missing.append(("head_pose", head_pose or f"{slug}_head_pose.json"))
    if require_audio and (not source_audio or not os.path.exists(source_audio)):
        missing.append(("source_audio", source_audio or f"{slug}_voice.wav"))
    return missing


def convert_bodytrack_to_pose(source_path, output_path, fps):
    if not pose_adapter:
        print("Warnung: maxine_pose_adapter.py nicht gefunden.")
        return False
    try:
        lines = pose_adapter.load_bodytrack_txt(source_path)
        frames = pose_adapter.parse_frame_lines(lines)
        payload = pose_adapter.build_payload(source_path, fps, frames)
    except (OSError, ValueError) as exc:
        print(f"Warnung: BodyTrack Konvertierung fehlgeschlagen: {exc}")
        return False

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=True)
    print(f"Wrote: {output_path}")
    return True


def run(
    chapter_num,
    scene_selector,
    base_path,
    media_dir,
    fps,
    width,
    height,
    color_space,
    require_video,
    require_camera,
    require_pose,
    require_head_pose,
    convert_bodytrack,
    strict,
    dry_run,
):
    chapter_folder = f"chapter_{chapter_num:03d}"
    chapter_path = os.path.join(base_path, chapter_folder)
    if not os.path.isdir(chapter_path):
        print(f"Fehler: Kapitelordner nicht gefunden: {chapter_path}")
        return

    media_dir = media_dir or os.path.join(chapter_path, "Media")
    os.makedirs(media_dir, exist_ok=True)

    if scene_selector:
        slugs = [scene_selector]
    else:
        slugs = collect_scene_slugs(chapter_path)

    if not slugs:
        print("Keine Szenen gefunden. Nutze --scene oder erzeuge audio meta Dateien.")
        return

    had_error = False

    for slug in slugs:
        meta_path = os.path.join(chapter_path, "audio", f"{slug}_audio_meta.json")
        meta = load_audio_meta(meta_path)
        facesync = meta.get("facesync", {}) if isinstance(meta, dict) else {}
        gbuffer = meta.get("gbuffer", {}) if isinstance(meta, dict) else {}
        passes = gbuffer.get("passes", {}) if isinstance(gbuffer, dict) else {}

        source_video = resolve_scene_path(
            chapter_path,
            media_dir,
            facesync.get("target_media") or os.path.join(media_dir, f"{slug}.mp4"),
        )
        source_audio = resolve_scene_path(
            chapter_path,
            media_dir,
            facesync.get("source_audio") or os.path.join(media_dir, f"{slug}_voice.wav"),
        )
        camera_curve = resolve_scene_path(
            chapter_path,
            media_dir,
            gbuffer.get("camera_curve") or os.path.join(media_dir, f"{slug}_cam_curve.json"),
        )
        body_pose = resolve_scene_path(
            chapter_path,
            media_dir,
            gbuffer.get("body_pose") or os.path.join(media_dir, f"{slug}_body_pose.json"),
        )
        pose_source = resolve_scene_path(
            chapter_path,
            media_dir,
            gbuffer.get("pose_source") or os.path.join(media_dir, f"{slug}_bodytrack.txt"),
        )
        head_pose = resolve_scene_path(
            chapter_path,
            media_dir,
            gbuffer.get("head_pose") or os.path.join(media_dir, f"{slug}_head_pose.json"),
        )

        if convert_bodytrack and pose_source and os.path.exists(pose_source):
            if not os.path.exists(body_pose):
                convert_bodytrack_to_pose(pose_source, body_pose, fps)

        require_audio = bool(facesync.get("enabled"))
        effective_require_head_pose = require_head_pose or bool(facesync.get("enabled"))
        missing = validate_scene_inputs(
            slug,
            source_video,
            camera_curve,
            body_pose,
            head_pose,
            source_audio,
            require_video=require_video,
            require_camera=require_camera,
            require_pose=require_pose,
            require_head_pose=effective_require_head_pose,
            require_audio=require_audio,
        )
        if missing:
            missing_summary = ", ".join([f"{key}: {path}" for key, path in missing])
            print(f"Missing inputs for {slug}: {missing_summary}")
            if strict:
                had_error = True
                continue

        overrides = {
            "source_video": source_video,
            "camera_curve": camera_curve,
            "body_pose": body_pose,
            "head_pose": head_pose,
            "normal": resolve_scene_path(
                chapter_path, media_dir, passes.get("normal") or os.path.join(media_dir, f"{slug}_avatar_normal.exr")
            ),
            "depth": resolve_scene_path(
                chapter_path, media_dir, passes.get("depth") or os.path.join(media_dir, f"{slug}_avatar_depth.exr")
            ),
            "motion": resolve_scene_path(
                chapter_path, media_dir, passes.get("motion") or os.path.join(media_dir, f"{slug}_avatar_motion.exr")
            ),
            "mask": resolve_scene_path(
                chapter_path, media_dir, passes.get("mask") or os.path.join(media_dir, f"{slug}_avatar_mask.exr")
            ),
            "albedo": resolve_scene_path(
                chapter_path, media_dir, passes.get("albedo") or os.path.join(media_dir, f"{slug}_avatar_albedo.exr")
            ),
            "uv": resolve_scene_path(
                chapter_path, media_dir, passes.get("uv") or os.path.join(media_dir, f"{slug}_avatar_uv.exr")
            ),
            "id": resolve_scene_path(
                chapter_path, media_dir, passes.get("id") or os.path.join(media_dir, f"{slug}_avatar_id.exr")
            ),
        }

        manifest = build_manifest(
            chapter_path,
            media_dir,
            slug,
            fps,
            width,
            height,
            color_space,
            overrides=overrides,
        )
        manifest_path = os.path.join(media_dir, f"{slug}_avatar_manifest.json")
        if dry_run:
            print(f"Dry run: {manifest_path}")
            print(json.dumps(manifest, indent=2))
            continue
        write_manifest(manifest_path, manifest)
        print(f"Wrote: {manifest_path}")

    if had_error and strict:
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Avatar G-buffer contract stub.")
    parser.add_argument("chapter", type=int, help="Chapter number (e.g. 74)")
    parser.add_argument("--scene", default=None, help="Scene id (e.g. 1.1 or scene_01_01)")
    parser.add_argument("--base-path", default=DEFAULT_BASE_PATH)
    parser.add_argument("--media-dir", default=None)
    parser.add_argument("--fps", type=int, default=DEFAULT_FPS)
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH)
    parser.add_argument("--height", type=int, default=DEFAULT_HEIGHT)
    parser.add_argument("--color-space", default=DEFAULT_COLOR_SPACE)
    parser.add_argument("--require-video", action="store_true", default=True)
    parser.add_argument("--no-require-video", action="store_false", dest="require_video")
    parser.add_argument("--require-camera", action="store_true", default=True)
    parser.add_argument("--no-require-camera", action="store_false", dest="require_camera")
    parser.add_argument("--require-pose", action="store_true", default=True)
    parser.add_argument("--no-require-pose", action="store_false", dest="require_pose")
    parser.add_argument("--require-head-pose", action="store_true", default=False)
    parser.add_argument("--convert-bodytrack", action="store_true", help="Convert BodyTrackApp txt to body_pose.json if missing")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    scene_slug = parse_scene_selector(args.scene) if args.scene else None

    run(
        chapter_num=args.chapter,
        scene_selector=scene_slug,
        base_path=args.base_path,
        media_dir=args.media_dir,
        fps=args.fps,
        width=args.width,
        height=args.height,
        color_space=args.color_space,
        require_video=args.require_video,
        require_camera=args.require_camera,
        require_pose=args.require_pose,
        require_head_pose=args.require_head_pose,
        convert_bodytrack=args.convert_bodytrack,
        strict=args.strict,
        dry_run=args.dry_run,
    )
