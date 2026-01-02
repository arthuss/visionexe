import os
import re
import json
import argparse
import subprocess
import shutil

DEFAULT_BASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "filmsets")


def load_text(path):
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def save_text(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def resolve_gemini_command():
    gemini_path = shutil.which("gemini") or shutil.which("gemini.cmd")
    if gemini_path:
        return f"\"{gemini_path}\""

    npx_path = shutil.which("npx") or shutil.which("npx.cmd")
    if npx_path:
        return f"\"{npx_path}\" -y @google/gemini-cli"

    return None


def parse_gemini_response(raw_output):
    if not raw_output:
        return None
    json_start = raw_output.find("{")
    if json_start == -1:
        return raw_output.strip()
    json_text = raw_output[json_start:]
    json_end = json_text.rfind("}")
    if json_end != -1:
        json_text = json_text[:json_end + 1]
    try:
        payload = json.loads(json_text)
        response = payload.get("response")
        if isinstance(response, str):
            return response.strip()
    except json.JSONDecodeError:
        return raw_output.strip()
    return None


def call_gemini(prompt):
    cmd = resolve_gemini_command()
    if not cmd:
        print("Gemini CLI nicht gefunden (gemini/npx).")
        return None
    cmd = f"{cmd} --output-format json"
    try:
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            shell=True,
        )
        stdout, stderr = process.communicate(input=prompt)
        if process.returncode != 0:
            print(f"Gemini Fehler: {stderr}")
            return None
        return parse_gemini_response(stdout)
    except FileNotFoundError:
        print("Gemini CLI nicht gefunden (gemini/npx).")
        return None


def extract_field(block, label):
    pattern = re.compile(rf"^\*\*{re.escape(label)}:\*\*\s*(.+)$", re.M)
    match = pattern.search(block)
    if not match:
        return ""
    return match.group(1).strip()


def extract_section(block, header):
    start = block.find(header)
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
        "header_line": header_line,
    }


def parse_regie_line(raw):
    if not raw:
        return None
    for line in raw.splitlines():
        line = line.strip()
        if line.startswith("REGIE_JSON:"):
            return line
    if "{" in raw and "}" in raw:
        json_text = raw[raw.find("{"): raw.rfind("}") + 1]
        return f"REGIE_JSON: {json_text}"
    return None


def build_regie_prompt(scene, action_text, dialog_text, start_image, video_prompt, concept_excerpt):
    return (
        "You generate compact REGIE metadata for an Exeget:OS scene.\n"
        "Return exactly ONE line with valid JSON:\n"
        "REGIE_JSON: {\"subject\":\"actor|environment|prop|interface|mixed\",\"shot_type\":\"establishing|insert|close_up|medium|wide|full_body\",\"framing\":\"extreme_close_up|close_up|medium|wide|full_body\",\"environment\":\"...\",\"env_change\":true,\"actors\":[{\"name\":\"Name\",\"phase\":\"Phase\",\"presence\":\"on_screen|off_screen\",\"focus\":\"primary|secondary\"}],\"props\":[\"Prop\"],\"prop_placements\":[{\"id\":\"PROP_NAME\",\"mode\":\"attach|scene|free\",\"anchor\":\"hand_r|hand_l|chest|back|pedestal_top|altar_center|table_top|floor_center\",\"offset\":[0.0,0.0],\"scale\":1.0}],\"actor_block\":{\"anchor\":\"entry_left|entry_right|center\",\"approach_target\":\"pedestal_top|altar_center|table_top|none\",\"stop_offset\":[0.0,0.0]},\"camera\":\"...\",\"mood\":[\"awe\"],\"director_intent\":\"Short, poetic intent sentence.\",\"start_image_keywords\":[\"keyword1\",\"keyword2\"],\"start_image_mode\":\"env_only|actor_in_env|actor_only|prop_only|ui_only|composite\",\"video_plan\":{\"start_comp\":{\"mode\":\"actor_first|env_first|composite\",\"actor_pose_id\":\"POSE_ID\",\"env_id\":\"ENV_ID\",\"props\":[\"PROP_ID\"],\"notes\":\"\"},\"motion_driver\":{\"type\":\"a2f|pose|liveportrait|none\",\"audio_id\":\"scene_audio_id\",\"pose_source\":\"data/capture/poses/pose_id.mp4\",\"driver_notes\":\"\"},\"reference_footage\":{\"id\":\"ref_id\",\"path\":\"data/reference/clip.mp4\",\"use\":\"lighting|motion|palette|none\",\"notes\":\"\"},\"overlay_badge\":{\"asset\":\"media/badges/geez_logo_v1.mov\",\"blend\":\"screen|overlay|normal\",\"opacity\":0.0,\"position\":\"top_right\",\"safe_margin\":0.04},\"provenance\":{\"source\":\"ai_assisted|live_action|mixed\",\"notes\":\"\"}},\"voice_words_max\":10}\n"
        "Rules:\n"
        "- JSON must be valid, double quotes only.\n"
        "- Use true/false for booleans.\n"
        "- Keep strings short.\n"
        "- director_intent should be one sentence, no tags.\n"
        "- start_image_keywords should be a short list of prompt triggers or empty [].\n"
        "- If a prop is held/worn, use mode=attach with anchor hand_r/hand_l/chest/back.\n"
        "- If a prop sits on a pedestal/table/altar, use mode=scene with anchor pedestal_top/table_top/altar_center.\n"
        "- If no reliable placement, return empty prop_placements or mode=free without anchor.\n"
        "- If unknown, use empty strings or empty arrays.\n"
        "\n"
        f"Scene: ACT {scene['act']} SCENE {scene['scene_id']} ({scene['title']})\n"
        f"Timecode: {scene['timecode']}\n"
        f"Action: {action_text}\n"
        f"Dialog: {dialog_text}\n"
        f"Start image prompt: {start_image}\n"
        f"Video prompt: {video_prompt}\n"
        f"Mechanic concept excerpt: {concept_excerpt}\n"
    )


def insert_regie_block(block, regie_line):
    if not regie_line:
        return block
    if "### 0. REGIE" in block:
        return block
    lines = block.splitlines()
    insert_idx = None
    for idx, line in enumerate(lines):
        if line.strip().startswith("**Dialog:**"):
            insert_idx = idx + 1
            break
    if insert_idx is None:
        for idx, line in enumerate(lines):
            if line.strip().startswith("**Action:**"):
                insert_idx = idx + 1
                break
    if insert_idx is None:
        for idx, line in enumerate(lines):
            if line.strip().startswith("## "):
                insert_idx = idx + 1
                break
    if insert_idx is None:
        insert_idx = len(lines)

    regie_lines = [
        "",
        "### 0. REGIE DATA (JSON)",
        regie_line,
        "",
    ]
    updated = lines[:insert_idx] + regie_lines + lines[insert_idx:]
    return "\n".join(updated)


def process_script(script_text, concept_excerpt, overwrite=False, dry_run=False):
    blocks = script_text.split("\n---")
    updated_blocks = []
    changed = 0

    for block in blocks:
        if "## [ACT" not in block:
            updated_blocks.append(block)
            continue
        if "### 0. REGIE" in block and not overwrite:
            updated_blocks.append(block)
            continue
        scene = parse_scene_header(block)
        if not scene:
            updated_blocks.append(block)
            continue

        action_text = extract_field(block, "Action")
        dialog_text = extract_field(block, "Dialog")
        start_image = extract_section(block, "### 1. START IMAGE PROMPT")
        video_prompt = extract_section(block, "### 2. VIDEO PROMPT")
        prompt = build_regie_prompt(scene, action_text, dialog_text, start_image[:800], video_prompt[:800], concept_excerpt)
        regie_raw = call_gemini(prompt)
        regie_line = parse_regie_line(regie_raw)
        if not regie_line:
            print(f"[WARN] Keine REGIE_JSON fuer Szene {scene['scene_id']}.")
            updated_blocks.append(block)
            continue
        if dry_run:
            print(f"[DRY] REGIE_JSON fuer Szene {scene['scene_id']}: {regie_line}")
            updated_blocks.append(block)
            continue
        updated_blocks.append(insert_regie_block(block, regie_line))
        changed += 1

    return "\n---\n".join(updated_blocks), changed


def list_chapters(base_path, chapter_args):
    if chapter_args:
        return [f"chapter_{ch:03d}" for ch in chapter_args]
    candidates = [
        d for d in os.listdir(base_path)
        if d.startswith("chapter_") and os.path.isdir(os.path.join(base_path, d))
    ]
    return sorted(candidates)


def main():
    parser = argparse.ArgumentParser(description="Generate REGIE_JSON blocks for screenplay scenes.")
    parser.add_argument("chapters", nargs="*", type=int, help="Chapter numbers (e.g. 1 2 3).")
    parser.add_argument("--base-path", default=DEFAULT_BASE_PATH)
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing REGIE blocks.")
    parser.add_argument("--dry-run", action="store_true", help="Show output without writing.")
    args = parser.parse_args()

    chapters = list_chapters(args.base_path, args.chapters)
    for chapter in chapters:
        chapter_path = os.path.join(args.base_path, chapter)
        script_path = os.path.join(chapter_path, "DREHBUCH_HOLLYWOOD.md")
        if not os.path.exists(script_path):
            print(f"[WARN] Skip {chapter}: no script found.")
            continue
        concept_path = os.path.join(chapter_path, "concept_engine", "mechanic_concept.txt")
        concept_text = load_text(concept_path)
        concept_excerpt = " ".join(concept_text.split())
        if len(concept_excerpt) > 1200:
            concept_excerpt = concept_excerpt[:1200].rstrip() + "..."

        script_text = load_text(script_path)
        updated_text, changed = process_script(
            script_text,
            concept_excerpt,
            overwrite=args.overwrite,
            dry_run=args.dry_run,
        )
        if args.dry_run:
            continue
        if changed > 0:
            save_text(script_path, updated_text)
            print(f"[OK] {chapter}: inserted {changed} REGIE block(s).")
        else:
            print(f"[SKIP] {chapter}: no changes.")


if __name__ == "__main__":
    main()
