# Chapter Briefing Builder
#
# Generates per-chapter briefings with three sections:
# 1) Linguistic Analysis (Ge'ez)
# 2) Technological Hypotheses & Simulation Theory
# 3) Storytelling Q1/Q2/Q3 (Action/Visuals/State-Change & Tone)
#
# Outputs:
# - filmsets/<chapter>/chapter_briefing.md
# - filmsets/<chapter>/analysis_linguistik/story.txt
# - filmsets/<chapter>/tech_hypothesen/story.txt
# - filmsets/<chapter>/visual_abc/story.txt
#
# Usage example:
#   python engine/workers/chapter_briefing_builder.py --story-config stories/template/config/story_config.json --use-gemini --model pro

import argparse
import glob
import json
import os
import re
import shlex
import shutil
import subprocess
import time
import urllib.request
from pathlib import Path

from visionexe_paths import ensure_dir, load_story_config, resolve_path


MODEL_NAME = "gpt-oss:20b"
OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"

SECTION_RE = re.compile(r"^###\s*(?P<num>\d+)\.\s*(?P<title>.+)$", re.MULTILINE)
CHAPTER_RE = re.compile(r"(?:chapter|story)_(\d+)", re.IGNORECASE)
WAVE_SECTION_RE = re.compile(
    r"^###\s+.*Integration in WAVE.*?(?=^###\s|\Z)",
    re.IGNORECASE | re.MULTILINE | re.DOTALL,
)


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")


def strip_wave_sections(text):
    if not text:
        return text
    cleaned = WAVE_SECTION_RE.sub("", text)
    return cleaned.strip()


def read_text(path: Path, include_wave: bool, max_chars: int | None):
    if not path or not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    if not include_wave:
        text = strip_wave_sections(text)
    if max_chars and len(text) > max_chars:
        return text[:max_chars].rstrip() + "\n[...trimmed...]"
    return text.strip()


def resolve_gemini_command():
    gemini_path = shutil.which("gemini") or shutil.which("gemini.cmd")
    if gemini_path:
        return [gemini_path]
    npx_path = shutil.which("npx") or shutil.which("npx.cmd")
    if npx_path:
        return [npx_path, "-y", "@google/gemini-cli"]
    return None


def resolve_copilot_command():
    override = os.environ.get("COPILOT_CMD") or os.environ.get("LLM_CMD")
    if override:
        cmd = shlex.split(override)
        if is_copilot_cmd(cmd):
            return cmd
        log("LLM_CMD/COPILOT_CMD ist kein Copilot-Aufruf, ignoriere Override.")

    copilot_path = shutil.which("copilot") or shutil.which("copilot.cmd")
    if copilot_path:
        return [copilot_path]

    home_dir = os.path.expanduser("~")
    npm_loader_glob = os.path.join(home_dir, ".copilot", "pkg", "universal", "*", "npm-loader.js")
    npm_loaders = glob.glob(npm_loader_glob)
    if npm_loaders:
        npm_loaders.sort(key=lambda p: [int(x) if x.isdigit() else x for x in os.path.basename(os.path.dirname(p)).split(".")])
        return ["node", npm_loaders[-1]]

    return None


def is_copilot_cmd(cmd):
    if not cmd:
        return False
    lowered = [os.path.basename(part).lower() for part in cmd]
    if "copilot" in lowered or "copilot.cmd" in lowered:
        return True
    return any(part.lower().endswith("npm-loader.js") for part in cmd)


def normalize_gemini_model(model: str | None):
    if not model:
        return None
    raw = str(model).strip()
    if not raw:
        return None
    normalized = raw.replace("_", "-")
    lowered = normalized.lower()
    if lowered in {"auto"}:
        return None
    if lowered in {"pro", "flash", "flash-lite"}:
        return lowered
    if lowered.startswith(("gemini-3", "gemini-2.5")):
        return normalized
    if lowered.startswith(("gemini-2.0", "gemini-1")):
        if "flash" in lowered:
            return "flash-lite" if "lite" in lowered else "flash"
        return "pro"
    return normalized


def normalize_copilot_model(model: str | None):
    if not model:
        return None
    lowered = str(model).strip().replace("_", "-").lower()
    if not lowered:
        return None
    if lowered in {"gemini-3-pro", "gemini-3-pro-preview"}:
        return "gemini-3-pro-preview"
    return model


def parse_gemini_response(raw_output: str | None):
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


def call_copilot(prompt: str, model: str | None):
    cmd = resolve_copilot_command()
    if not cmd:
        log("Copilot CLI nicht gefunden. Setze COPILOT_CMD oder installiere copilot in PATH.")
        return None
    normalized_model = normalize_copilot_model(model)
    if normalized_model and "--model" not in cmd and "-m" not in cmd:
        cmd = cmd + ["--model", normalized_model]
    uses_copilot = is_copilot_cmd(cmd)
    if uses_copilot:
        if "--silent" not in cmd and "-s" not in cmd:
            cmd = cmd + ["--silent"]
        if "--no-color" not in cmd:
            cmd = cmd + ["--no-color"]
        if "--no-custom-instructions" not in cmd:
            cmd = cmd + ["--no-custom-instructions"]
        if "--prompt" not in cmd and "-p" not in cmd:
            cmd = cmd + ["--prompt"]
        cmd = cmd + [prompt]
    try:
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
        if uses_copilot:
            stdout, stderr = process.communicate()
        else:
            stdout, stderr = process.communicate(input=prompt)
        if process.returncode != 0:
            log(f"Copilot Fehler: {stderr}")
            return None
        return parse_gemini_response(stdout)
    except OSError as exc:
        log(f"Copilot Start fehlgeschlagen: {exc}")
        return None


def call_gemini(prompt: str, model: str | None):
    cmd = resolve_gemini_command()
    if not cmd:
        log("Gemini CLI nicht gefunden (gemini/npx).")
        return None
    cmd = cmd + ["--output-format", "json"]
    normalized_model = normalize_gemini_model(model)
    if model and normalized_model is None:
        log("Gemini Modell 'auto' -> CLI Default (kein --model).")
    elif model and normalized_model and normalized_model != model:
        log(f"Gemini Modell '{model}' nicht kompatibel, nutze '{normalized_model}'.")
    if normalized_model:
        cmd += ["--model", normalized_model]
    try:
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
        stdout, stderr = process.communicate(input=prompt)
        if process.returncode != 0:
            log(f"Gemini Fehler: {stderr}")
            return None
        return parse_gemini_response(stdout)
    except OSError as exc:
        log(f"Gemini Start fehlgeschlagen: {exc}")
    return None


def call_ollama(prompt: str, model_name: str, ollama_url: str):
    data = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_ctx": 16384,
        },
    }
    try:
        req = urllib.request.Request(
            ollama_url,
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as response:
            resp_json = json.loads(response.read().decode("utf-8"))
            main_response = resp_json.get("response", "")
            return main_response.strip()
    except Exception as exc:
        log(f"Ollama request failed: {exc}")
        return None


def list_chapters(filmsets_root: Path, chapter_label: str):
    chapters = []
    if not filmsets_root.exists():
        return chapters
    for entry in filmsets_root.iterdir():
        if not entry.is_dir():
            continue
        match = CHAPTER_RE.search(entry.name)
        if not match:
            continue
        try:
            chapter_num = int(match.group(1))
        except ValueError:
            continue
        if entry.name.lower().startswith(chapter_label.lower() + "_"):
            chapters.append((chapter_num, entry))
    return sorted(chapters, key=lambda item: item[0])


def resolve_chapter_dir(filmsets_root: Path, chapter_label: str, padding: int, chapter_num: int):
    primary = filmsets_root / f"{chapter_label}_{chapter_num:0{padding}d}"
    if primary.exists():
        return primary
    fallback = filmsets_root / f"chapter_{chapter_num:0{padding}d}"
    if fallback.exists():
        return fallback
    return primary


def collect_segments(chapter_dir: Path, segment_label: str, include_wave: bool, max_segment_chars: int, max_analysis_chars: int):
    blocks = []
    segment_prefix = f"{segment_label}_"
    segment_dirs = sorted([d for d in chapter_dir.iterdir() if d.is_dir() and d.name.startswith(segment_prefix)])
    if not segment_dirs:
        segment_dirs = sorted([d for d in chapter_dir.iterdir() if d.is_dir() and d.name.startswith("verse_")])
    for seg_dir in segment_dirs:
        story_path = seg_dir / "story.txt"
        segment_path = seg_dir / "segment.txt"
        verse_path = seg_dir / "verse.txt"
        source_path = story_path if story_path.exists() else segment_path if segment_path.exists() else verse_path
        segment_text = read_text(source_path, include_wave, max_segment_chars)
        if not segment_text:
            continue
        analysis_path = seg_dir / "analysis_llm.txt"
        analysis_text = read_text(analysis_path, include_wave, max_analysis_chars)
        block = f"[{seg_dir.name}]\n{segment_text}"
        if analysis_text:
            block = f"{block}\n\n[ANALYSIS]\n{analysis_text}"
        blocks.append(block)
    return blocks


def build_prompt(chapter_num: int, chapter_text: str, segment_blocks: list[str]):
    segment_text = "\n\n".join(segment_blocks)
    return f"""
INPUT CONTEXT:
The text contains "Tech-Exegesis" of the Ethiopic Book of Enoch (1 Enoch), an ancient text (approx. 500 BC - 300 AD).
We interpret the books as layers of a Simulation Manual (OS):
1.  **Book of Watchers (1-36):** Hardware-Audit & Infiltration (Sinai Port, Hermon).
2.  **Book of Parables (37-71):** Software-Logic & Master-Controller (Son of Man, Crystal Mainframe).
3.  **Astronomical Book (72-82):** System-Clock & Timing (Sun/Moon logic).
4.  **Dream Visions (83-90):** Historical Heatmapping (Animal Apocalypse).
5.  **Epistle of Enoch (91-105):** Policy Update & User Maintenance.
    *   **Appendix (106-108):** Noah Prototype (Anomaly) & Final Persistence.
You are the chapter briefing writer for exeget:os.
Write in German. Use only the provided text and analysis. Do not invent details.
Use full sentences. Avoid tag lists. If information is missing, say unknown.
du bist nun ein linguistisches sprachtool das soezialisiert ist auf die übersetzung von ge ez texten
Output format (exact headings):
### 1. Linguistische Analyse
wort für wort satz für satz 
nun bist du ein visionär und querdenker der die technologische realität hinter den texten erklärt
### 2. Technologische Hypothesen
wir erklären wunder durch technologische konzepte, basierend auf dem text und logischen schlüssen der modernen wissenschaft

### 3. Storytelling Q1/Q2/Q3
Q1: Was passiert konkret (Handlung und Kausalitaet)?
Q2: Was muss visuell gezeigt werden (Akteure, Orte, Props, Physik)?
Q3: Was aendert sich ueber die Szene und was ist der Regie-Ton (Tempo, Fokus, Audio)?


INPUT
CHAPTER: {chapter_num}

CHAPTER TEXT:
{chapter_text}

SEGMENTS + ANALYSIS:
{segment_text}
""".strip()


def split_sections(text: str):
    sections = {}
    matches = list(SECTION_RE.finditer(text))
    if not matches:
        return {"full": text.strip()}
    for idx, match in enumerate(matches):
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        num = match.group("num")
        sections[num] = text[start:end].strip()
    return sections


def write_section(chapter_dir: Path, folder_name: str, content: str):
    target_dir = chapter_dir / folder_name
    ensure_dir(target_dir)
    story_path = target_dir / "story.txt"
    story_path.write_text(content.strip() + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Build chapter briefings with Linguistics, Tech, and Storytelling Q1/Q2/Q3.")
    parser.add_argument("--story-root", help="Story root path.")
    parser.add_argument("--story-config", help="Path to story_config.json.")
    parser.add_argument("--filmsets-root", help="Optional filmsets root override.")
    parser.add_argument("--start", type=int, help="Start chapter number.")
    parser.add_argument("--end", type=int, help="End chapter number.")
    parser.add_argument("--resume", action="store_true", help="Skip chapters with existing chapter_briefing.md.")
    parser.add_argument("--include-wave", action="store_true", help="Keep Integration in WAVE sections.")
    parser.add_argument("--use-gemini", action="store_true", help="Use Gemini CLI instead of Ollama.")
    parser.add_argument("--model", help="Override model name.")
    parser.add_argument("--ollama-url", help="Override Ollama URL.")
    parser.add_argument("--max-story-chars", type=int, default=8000, help="Max chars from chapter story text.")
    parser.add_argument("--max-segment-chars", type=int, default=2000, help="Max chars per segment.")
    parser.add_argument("--max-analysis-chars", type=int, default=4000, help="Max chars per segment analysis.")
    args = parser.parse_args()

    story_config, story_root, repo_root = load_story_config(
        story_root=args.story_root,
        story_config_path=args.story_config,
    )

    filmsets_root = resolve_path(args.filmsets_root or story_config.get("filmsets_root"), repo_root)
    if not filmsets_root:
        filmsets_root = story_root / "filmsets"

    chapter_label = story_config.get("chapter_label", "chapter")
    chapter_padding = int(story_config.get("chapter_index_padding", 3))
    segment_label = story_config.get("segment_label", "segment")

    if args.start or args.end:
        start = args.start or 1
        end = args.end or start
        chapters = [(num, resolve_chapter_dir(filmsets_root, chapter_label, chapter_padding, num)) for num in range(start, end + 1)]
    else:
        chapters = list_chapters(filmsets_root, chapter_label)

    if not chapters:
        raise SystemExit(f"No chapters found under {filmsets_root}")

    if args.use_gemini:
        model_name = args.model or os.environ.get("GEMINI_MODEL")
    else:
        model_name = args.model or MODEL_NAME
    ollama_url = args.ollama_url or OLLAMA_API_URL

    for chapter_num, chapter_dir in chapters:
        if not chapter_dir.exists():
            log(f"Skip missing chapter dir: {chapter_dir}")
            continue
        briefing_path = chapter_dir / "chapter_briefing.md"
        if args.resume and briefing_path.exists():
            log(f"Skip (resume): {briefing_path}")
            continue

        story_path = chapter_dir / "story.txt"
        chapter_text = read_text(story_path, args.include_wave, args.max_story_chars)
        if not chapter_text:
            chapter_text = read_text(chapter_dir / "chapter.txt", args.include_wave, args.max_story_chars)

        segments = collect_segments(
            chapter_dir,
            segment_label,
            args.include_wave,
            args.max_segment_chars,
            args.max_analysis_chars,
        )

        prompt = build_prompt(chapter_num, chapter_text, segments)
        log(f"Briefing chapter {chapter_num:03d}...")
        if args.use_gemini:
            response = call_gemini(prompt, model_name)
            if response is None:
                log("Gemini fehlgeschlagen, versuche Copilot Fallback.")
                response = call_copilot(prompt, model_name)
        else:
            response = call_ollama(prompt, model_name, ollama_url)
        if not response:
            log(f"Failed to generate briefing for chapter {chapter_num:03d}")
            continue

        ensure_dir(chapter_dir)
        briefing_path.write_text(response.strip() + "\n", encoding="utf-8")

        sections = split_sections(response)
        write_section(chapter_dir, "analysis_linguistik", sections.get("1", "").strip() or "[missing]")
        write_section(chapter_dir, "tech_hypothesen", sections.get("2", "").strip() or "[missing]")
        write_section(chapter_dir, "visual_abc", sections.get("3", "").strip() or "[missing]")
        log(f"Wrote briefing: {briefing_path}")


if __name__ == "__main__":
    main()
