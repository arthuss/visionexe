import os
import re
import json
import argparse
import shutil
from gradio_client import Client, handle_file

# CONFIG
BASE_PATH = r"C:\Users\sasch\henoch\filmsets"
DEFAULT_MEDIA_DIRNAME = "Media"
DEFAULT_NEG_PROMPT = "music, low quality, noise, static, distorted voice"

def load_script_text(script_path):
    if not os.path.exists(script_path):
        return ""
    with open(script_path, "r", encoding="utf-8") as f:
        return f.read()

def extract_section(block, marker):
    start = block.find(marker)
    if start == -1:
        return ""
    start = block.find("\n", start)
    if start == -1:
        return ""
    start += 1
    next_marker = re.search(r"^###\s+", block[start:], re.M)
    end = start + next_marker.start() if next_marker else len(block)
    return block[start:end].strip()

def parse_scene_header(block):
    header_line = ""
    for line in block.splitlines():
        if line.strip().startswith("## "):
            header_line = line.strip()
            break
    if not header_line:
        return None
    match = re.search(
        r"\[ACT\s+(?P<act>\d+)\]\s+\[SCENE\s+(?P<scene>[\d\.]+)\]\s+\[Timecode:\s*(?P<time>[^\]]+)\]\s+\[(?P<title>[^\]]+)\]",
        header_line,
    )
    if not match:
        return None
    return {
        "act": int(match.group("act")),
        "scene_id": match.group("scene"),
        "timecode": match.group("time").strip(),
        "title": match.group("title").strip(),
    }

def parse_scenes_from_script(script_text):
    scenes = []
    for block in script_text.split("\n---"):
        if "## [ACT" not in block:
            continue
        header = parse_scene_header(block)
        if not header:
            continue
        scenes.append({
            **header,
            "start_image_prompt": extract_section(block, "### 1. START IMAGE PROMPT"),
            "audio_prompt": extract_section(block, "### 3. AUDIO PROMPT"),
        })
    return scenes

def normalize_scene_slug(act, scene_id):
    parts = scene_id.split(".")
    sub = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
    return f"scene_{act:02d}_{sub:02d}"

def find_scene_video(media_dir, scene_id, act):
    slug = normalize_scene_slug(act, scene_id)
    scene_id_clean = scene_id.replace(".", "_")
    candidates = [
        f"{slug}.mp4",
        f"scene_{act}_{scene_id_clean}.mp4",
        f"scene_{scene_id}.mp4",
        f"scene_{scene_id_clean}.mp4",
        f"{scene_id_clean}.mp4",
    ]
    for name in candidates:
        path = os.path.join(media_dir, name)
        if os.path.exists(path):
            return path
    for name in os.listdir(media_dir):
        if not name.lower().endswith(".mp4"):
            continue
        lower = name.lower()
        if f"scene_{scene_id}".lower() in lower or scene_id_clean in lower:
            return os.path.join(media_dir, name)
    return None

def build_audio_prompt(audio_prompt, start_image_prompt, include_image_prompt):
    prompt = audio_prompt.strip() if audio_prompt.strip() else "Industrial ambient sound"
    if include_image_prompt and start_image_prompt:
        prompt = f"{prompt}\n\nScene visual reference (start image prompt):\n{start_image_prompt}"
    return prompt

def init_client():
    hf_token = os.getenv("HF_TOKEN")
    if hf_token:
        return Client("tencent/HunyuanVideo-Foley", hf_token=hf_token)
    return Client("tencent/HunyuanVideo-Foley")

def process_foley_for_chapter(chapter_num, base_path, media_dir, output_dir, include_image_prompt, dry_run):
    chapter_folder = f"chapter_{chapter_num:03d}"
    chapter_path = os.path.join(base_path, chapter_folder)
    script_path = os.path.join(chapter_path, "DREHBUCH_HOLLYWOOD.md")
    media_dir = media_dir or os.path.join(chapter_path, DEFAULT_MEDIA_DIRNAME)
    output_dir = output_dir or media_dir

    if not os.path.exists(script_path):
        print(f"Fehler: Drehbuch nicht gefunden: {script_path}")
        return
    if not os.path.exists(media_dir):
        print(f"Fehler: Media-Ordner nicht gefunden: {media_dir}")
        return
    os.makedirs(output_dir, exist_ok=True)

    script_text = load_script_text(script_path)
    scenes = parse_scenes_from_script(script_text)
    if not scenes:
        print("Fehler: Keine Szenen im Drehbuch gefunden.")
        return

    client = init_client()
    print("Verbinde mit Hunyuan-Foley API...")

    for scene in scenes:
        scene_id = scene["scene_id"]
        act = scene["act"]
        video_input = find_scene_video(media_dir, scene_id, act)
        if not video_input:
            print(f"Ueberspringe Szene {scene_id}: Kein Video gefunden.")
            continue

        audio_prompt = build_audio_prompt(
            scene.get("audio_prompt", ""),
            scene.get("start_image_prompt", ""),
            include_image_prompt,
        )
        scene_slug = normalize_scene_slug(act, scene_id)
        output_path = os.path.join(output_dir, f"{scene_slug}_foley.mp4")

        print(f"Verarbeite Audio fuer Szene {scene_id}...")
        print(f"Video: {os.path.basename(video_input)}")
        print(f"Prompt: {audio_prompt}")

        if dry_run:
            continue

        try:
            result = client.predict(
                video_file=handle_file(video_input),
                text_prompt=audio_prompt,
                neg_prompt=DEFAULT_NEG_PROMPT,
                guidance_scale=4.5,
                inference_steps=50,
                sample_nums=1,
                api_name="/process_inference",
            )
            temp_video_path = result[0]["video"]
            shutil.copy(temp_video_path, output_path)
            print(f"Erfolg: {output_path} erstellt.")
        except Exception as e:
            print(f"Fehler bei Szene {scene_id}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Foley generator for chapter scripts.")
    parser.add_argument("chapter", type=int, help="Chapter number (e.g. 74)")
    parser.add_argument("--base-path", default=BASE_PATH)
    parser.add_argument("--media-dir", default=None)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--no-image-prompt", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    process_foley_for_chapter(
        chapter_num=args.chapter,
        base_path=args.base_path,
        media_dir=args.media_dir,
        output_dir=args.output_dir,
        include_image_prompt=not args.no_image_prompt,
        dry_run=args.dry_run,
    )
