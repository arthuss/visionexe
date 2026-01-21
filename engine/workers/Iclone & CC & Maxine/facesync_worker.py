import argparse
import json
import os
import re
import urllib.error
import urllib.request

DEFAULT_BASE_PATH = r"C:\Users\sasch\henoch\filmsets"
DEFAULT_QUEUE = r"C:\Users\sasch\henoch\facesync_queue.json"
DEFAULT_SAM3_ENDPOINT = "http://127.0.0.1:8765/sam3/process"


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


def collect_scene_slugs(chapter_path):
    slugs = set()
    audio_dir = os.path.join(chapter_path, "audio")
    if os.path.isdir(audio_dir):
        for name in os.listdir(audio_dir):
            if name.endswith("_audio_meta.json"):
                slugs.add(name.replace("_audio_meta.json", ""))
    return sorted(slugs)


def load_audio_meta(path):
    if not path or not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"Warnung: Konnte Audio Meta nicht lesen: {path} ({exc})")
        return {}

def post_json(url, payload, timeout_sec):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout_sec) as response:
        body = response.read().decode("utf-8")
        return json.loads(body)


def run_sam3(endpoint, mp4_path, segment_target, mode, return_path, timeout_sec):
    payload = {
        "mp4_path": mp4_path,
        "segment_target": segment_target,
        "mode": mode,
        "return_path": return_path,
    }
    response = post_json(endpoint, payload, timeout_sec)
    outputs = response.get("outputs") if isinstance(response, dict) else None
    return outputs or {}


def build_job(chapter_path, media_dir, slug, meta, enable_sam3, sam3_outputs, mask_output):
    facesync = meta.get("facesync", {}) if isinstance(meta, dict) else {}
    method = facesync.get("method") or "a2f_3d"
    source_audio = resolve_scene_path(
        chapter_path, media_dir, facesync.get("source_audio") or os.path.join(media_dir, f"{slug}_voice.wav")
    )
    target_media = resolve_scene_path(
        chapter_path, media_dir, facesync.get("target_media") or os.path.join(media_dir, f"{slug}.mp4")
    )
    output_media = resolve_scene_path(
        chapter_path, media_dir, facesync.get("output") or os.path.join(media_dir, f"{slug}_avatar.mp4")
    )
    mask_output = resolve_scene_path(
        chapter_path, media_dir, facesync.get("mask") or mask_output
    )

    job = {
        "scene_id": slug,
        "method": method,
        "source_audio": source_audio,
        "target_media": target_media,
        "output": output_media,
        "mask": mask_output,
        "sam3": {
            "enabled": bool(enable_sam3),
            "mask_output": mask_output,
            "outputs": sam3_outputs or {},
        },
    }
    return job


def write_jobs(queue_path, jobs):
    if not jobs:
        print("Keine FaceSync Jobs gefunden.")
        return
    os.makedirs(os.path.dirname(queue_path), exist_ok=True)
    with open(queue_path, "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2, ensure_ascii=True)
    print(f"Wrote: {queue_path}")
    print(f"Jobs: {len(jobs)}")


def run(
    chapter_num,
    scene_selector,
    base_path,
    media_dir,
    queue_path,
    include_disabled,
    enable_sam3,
    sam3_endpoint,
    sam3_segment,
    sam3_mode,
    sam3_timeout,
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
        print("Keine Szenen gefunden. Nutze --scene oder erstelle audio meta Dateien.")
        return

    jobs = []
    for slug in slugs:
        meta_path = os.path.join(chapter_path, "audio", f"{slug}_audio_meta.json")
        meta = load_audio_meta(meta_path)
        facesync = meta.get("facesync", {}) if isinstance(meta, dict) else {}
        enabled = bool(facesync.get("enabled"))
        if not enabled and not include_disabled:
            continue
        facesync = meta.get("facesync", {}) if isinstance(meta, dict) else {}
        target_media = resolve_scene_path(
            chapter_path, media_dir, facesync.get("target_media") or os.path.join(media_dir, f"{slug}.mp4")
        )
        output_media = resolve_scene_path(
            chapter_path, media_dir, facesync.get("output") or os.path.join(media_dir, f"{slug}_avatar.mp4")
        )
        mask_output = os.path.join(media_dir, f"{slug}_{sam3_segment}_mask.png")
        sam3_outputs = {}
        if enable_sam3 and sam3_endpoint:
            target_for_mask = output_media if os.path.exists(output_media) else target_media
            if target_for_mask and os.path.exists(target_for_mask):
                if dry_run:
                    sam3_outputs = {"mask": mask_output}
                else:
                    try:
                        sam3_outputs = run_sam3(
                            sam3_endpoint,
                            target_for_mask,
                            sam3_segment,
                            sam3_mode,
                            media_dir,
                            sam3_timeout,
                        )
                        if sam3_outputs.get("mask"):
                            mask_output = sam3_outputs["mask"]
                    except (urllib.error.URLError, urllib.error.HTTPError) as exc:
                        print(f"SAM3 Fehler: {exc}")
            else:
                print(f"Warnung: SAM3 Input fehlt für {slug}: {target_for_mask}")
        job = build_job(
            chapter_path,
            media_dir,
            slug,
            meta,
            enable_sam3,
            sam3_outputs,
            mask_output,
        )
        jobs.append(job)
        if dry_run:
            print(json.dumps(job, indent=2))

    if dry_run:
        return
    write_jobs(queue_path, jobs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare FaceSync jobs for A2F/LivePortrait.")
    parser.add_argument("chapter", type=int, help="Chapter number (e.g. 74)")
    parser.add_argument("--scene", default=None, help="Scene id (e.g. 1.1 or scene_01_01)")
    parser.add_argument("--base-path", default=DEFAULT_BASE_PATH)
    parser.add_argument("--media-dir", default=None)
    parser.add_argument("--queue", default=DEFAULT_QUEUE)
    parser.add_argument("--include-disabled", action="store_true", help="Include scenes where facesync.enabled is false")
    parser.add_argument("--sam3", action="store_true", help="Enable SAM3 mask generation")
    parser.add_argument("--sam3-endpoint", default=DEFAULT_SAM3_ENDPOINT)
    parser.add_argument("--sam3-segment", default="face")
    parser.add_argument("--sam3-mode", nargs="+", default=["mask"])
    parser.add_argument("--sam3-timeout", type=int, default=120)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    scene_slug = parse_scene_selector(args.scene) if args.scene else None

    run(
        chapter_num=args.chapter,
        scene_selector=scene_slug,
        base_path=args.base_path,
        media_dir=args.media_dir,
        queue_path=args.queue,
        include_disabled=args.include_disabled,
        enable_sam3=args.sam3,
        sam3_endpoint=args.sam3_endpoint,
        sam3_segment=args.sam3_segment,
        sam3_mode=args.sam3_mode,
        sam3_timeout=args.sam3_timeout,
        dry_run=args.dry_run,
    )
