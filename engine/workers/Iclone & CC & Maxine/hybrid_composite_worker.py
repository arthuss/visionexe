import argparse
import json
import os
import re
import urllib.request
import urllib.error

DEFAULT_BASE_PATH = r"C:\Users\sasch\henoch\filmsets"
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
    media_dir = os.path.join(chapter_path, "Media")
    if os.path.isdir(media_dir):
        for name in os.listdir(media_dir):
            match = re.match(r"^(scene_\d{2}_\d{2})", name)
            if match:
                slugs.add(match.group(1))
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


def build_manifest(chapter_num, slug, media_dir, meta, source_video, facesync_output, sam3_outputs):
    facesync = meta.get("facesync", {}) if isinstance(meta, dict) else {}
    gbuffer = meta.get("gbuffer", {}) if isinstance(meta, dict) else {}
    manifest_path = os.path.join(media_dir, f"{slug}_hybrid_manifest.json")

    manifest = {
        "scene_id": slug,
        "chapter": chapter_num,
        "source_video": source_video,
        "facesync": {
            "enabled": bool(facesync.get("enabled")),
            "method": facesync.get("method") or "a2f_3d",
            "output": facesync_output,
        },
        "gbuffer": {
            "enabled": bool(gbuffer.get("enabled")),
            "manifest": resolve_scene_path(os.path.dirname(media_dir), media_dir, gbuffer.get("manifest") or ""),
        },
        "sam3": {
            "enabled": bool(sam3_outputs),
            "outputs": sam3_outputs,
        },
        "composite": {
            "mode": "hybrid",
            "mask": sam3_outputs.get("mask") if isinstance(sam3_outputs, dict) else "",
        },
    }
    return manifest_path, manifest


def write_manifest(path, manifest):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=True)


def run(
    chapter_num,
    scene_selector,
    base_path,
    media_dir,
    sam3_endpoint,
    sam3_segment,
    sam3_mode,
    sam3_timeout,
    include_disabled,
    dry_run,
    queue_path,
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

        source_video = resolve_scene_path(
            chapter_path,
            media_dir,
            facesync.get("target_media") or os.path.join(media_dir, f"{slug}.mp4"),
        )
        facesync_output = resolve_scene_path(
            chapter_path,
            media_dir,
            facesync.get("output") or os.path.join(media_dir, f"{slug}_avatar.mp4"),
        )

        sam3_outputs = {}
        if sam3_endpoint:
            target_for_mask = facesync_output if os.path.exists(facesync_output) else source_video
            if target_for_mask and os.path.exists(target_for_mask):
                if dry_run:
                    sam3_outputs = {
                        "mask": os.path.join(media_dir, f"{slug}_{sam3_segment}_mask.png")
                    }
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
                    except (urllib.error.URLError, urllib.error.HTTPError) as exc:
                        print(f"SAM3 Fehler: {exc}")
                        sam3_outputs = {}

        manifest_path, manifest = build_manifest(
            chapter_num,
            slug,
            media_dir,
            meta,
            source_video,
            facesync_output,
            sam3_outputs,
        )

        jobs.append({"manifest": manifest_path, **manifest})
        if dry_run:
            print(json.dumps(manifest, indent=2))
        else:
            write_manifest(manifest_path, manifest)
            print(f"Wrote: {manifest_path}")

    if not jobs:
        print("Keine Hybrid-Jobs erzeugt.")
        return

    if queue_path:
        with open(queue_path, "w", encoding="utf-8") as f:
            json.dump(jobs, f, indent=2, ensure_ascii=True)
        print(f"Wrote queue: {queue_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build hybrid composite manifests per scene.")
    parser.add_argument("chapter", type=int, help="Chapter number (e.g. 74)")
    parser.add_argument("--scene", default=None, help="Scene id (e.g. 1.1 or scene_01_01)")
    parser.add_argument("--base-path", default=DEFAULT_BASE_PATH)
    parser.add_argument("--media-dir", default=None)
    parser.add_argument("--sam3-endpoint", default=DEFAULT_SAM3_ENDPOINT)
    parser.add_argument("--sam3-segment", default="face")
    parser.add_argument("--sam3-mode", nargs="+", default=["mask"])
    parser.add_argument("--sam3-timeout", type=int, default=120)
    parser.add_argument("--no-sam3", action="store_true", help="Disable SAM3 calls")
    parser.add_argument("--include-disabled", action="store_true", help="Include scenes where facesync.enabled is false")
    parser.add_argument("--queue", default=None, help="Optional queue output path")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    scene_slug = parse_scene_selector(args.scene) if args.scene else None
    sam3_endpoint = "" if args.no_sam3 else args.sam3_endpoint
    queue_path = args.queue
    if not queue_path:
        queue_path = os.path.join(
            args.media_dir or os.path.join(args.base_path, f"chapter_{args.chapter:03d}", "Media"),
            f"chapter_{args.chapter:03d}_hybrid_queue.json",
        )

    run(
        chapter_num=args.chapter,
        scene_selector=scene_slug,
        base_path=args.base_path,
        media_dir=args.media_dir,
        sam3_endpoint=sam3_endpoint,
        sam3_segment=args.sam3_segment,
        sam3_mode=args.sam3_mode,
        sam3_timeout=args.sam3_timeout,
        include_disabled=args.include_disabled,
        dry_run=args.dry_run,
        queue_path=queue_path,
    )
