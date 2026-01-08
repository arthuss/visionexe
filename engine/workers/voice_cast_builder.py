import argparse
import copy
import http.client
import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

from visionexe_paths import ensure_dir, load_story_config, resolve_path


NARRATOR_RE = re.compile(r"^NARRATOR_TEXT:\s*(.+)$", re.MULTILINE)
MONOLOGUE_RE = re.compile(r"^MONOLOGUE_JSON:\s*(\{.*\})\s*$", re.MULTILINE)
DIALOG_HEADER_RE = re.compile(r"^\*\*Dialog:\*\*\s*(.*)$")
SPEAKER_LINE_RE = re.compile(r"^\s*([^:]{1,64})\s*:\s*(.+)$")
GEEZ_CHAR_RE = re.compile(r"[\u1200-\u137F]")

FEM_SUFFIXES = ("\u1275", "\u1273", "\u120b")
MALE_SUFFIXES = ("\u12a4\u120d", "\u12ad")

DEFAULT_VOICE_MIX_TEMPLATES = {
    "male": {
        "de": {
            "model": "mtl",
            "speaker_mix": {
                "new_name": "",
                "sources": [{"speaker_id": "master_male_de", "weight": 1.0}],
            },
        },
        "en": {
            "model": "mtl",
            "speaker_mix": {
                "new_name": "",
                "sources": [{"speaker_id": "master_male_en", "weight": 1.0}],
            },
        },
    },
    "female": {
        "de": {
            "model": "mtl",
            "speaker_mix": {
                "new_name": "",
                "sources": [{"speaker_id": "master_female_de", "weight": 1.0}],
            },
        },
        "en": {
            "model": "mtl",
            "speaker_mix": {
                "new_name": "",
                "sources": [{"speaker_id": "master_female_en", "weight": 1.0}],
            },
        },
    },
    "unknown": {
        "de": {
            "model": "mtl",
            "speaker_mix": {
                "new_name": "",
                "sources": [{"speaker_id": "master_neutral_de", "weight": 1.0}],
            },
        },
        "en": {
            "model": "mtl",
            "speaker_mix": {
                "new_name": "",
                "sources": [{"speaker_id": "master_neutral_en", "weight": 1.0}],
            },
        },
    },
}

DEFAULT_TTS_SPEAKERS_ENDPOINT = "http://localhost:8000/speakers"


def normalize_speaker_id(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", name.strip())
    cleaned = cleaned.strip("_").lower()
    return cleaned or "unknown"


def contains_geez(text: str) -> bool:
    return bool(GEEZ_CHAR_RE.search(text))


def detect_geez_gender(name: str):
    normalized = name.strip()
    if not normalized or not contains_geez(normalized):
        return "unknown", "none"
    if any(normalized.endswith(suffix) for suffix in FEM_SUFFIXES):
        return "female", "geez_suffix"
    if any(normalized.endswith(suffix) for suffix in MALE_SUFFIXES):
        return "male", "geez_suffix"
    return "unknown", "geez_suffix"


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def parse_narrator(text: str):
    match = NARRATOR_RE.search(text)
    if not match:
        return None
    line = match.group(1).strip()
    return line or None


def parse_monologues(text: str):
    match = MONOLOGUE_RE.search(text)
    if not match:
        return {}
    payload = match.group(1).strip()
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return {}
    actors = data.get("actors")
    if not isinstance(actors, dict):
        return {}
    results = {}
    for actor, entries in actors.items():
        if not actor:
            continue
        if not isinstance(entries, list):
            continue
        lines = []
        for entry in entries:
            if isinstance(entry, dict):
                text_line = str(entry.get("text", "")).strip()
                if text_line:
                    lines.append(text_line)
        if lines:
            results[actor] = lines
    return results


def parse_dialog(text: str):
    speakers = {}
    lines = text.splitlines()
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        header = DIALOG_HEADER_RE.match(line)
        if not header:
            idx += 1
            continue
        inline = header.group(1).strip()
        dialog_lines = []
        if inline and inline not in {"-", "—"}:
            dialog_lines.append(inline)
        idx += 1
        while idx < len(lines):
            candidate = lines[idx]
            if candidate.startswith("### ") or candidate.startswith("## ["):
                break
            if candidate.strip() == "":
                break
            dialog_lines.append(candidate.strip())
            idx += 1
        for dialog_line in dialog_lines:
            match = SPEAKER_LINE_RE.match(dialog_line)
            if not match:
                continue
            name = match.group(1).strip()
            spoken = match.group(2).strip()
            if not name:
                continue
            speakers.setdefault(name, []).append(spoken)
        continue
    return speakers


def merge_speaker(speakers, name, speaker_type, chapter_id, samples, gender, gender_source, tts_profiles):
    speaker_id = normalize_speaker_id(name)
    entry = speakers.setdefault(
        speaker_id,
        {
            "id": speaker_id,
            "display_name": name.strip(),
            "aliases": [],
            "types": set(),
            "chapters": set(),
            "count": 0,
            "samples": [],
            "gender": "unknown",
            "gender_source": "none",
            "tts": {"language_profiles": {}},
        },
    )
    if name.strip() not in entry["aliases"]:
        entry["aliases"].append(name.strip())
    entry["types"].add(speaker_type)
    entry["chapters"].add(chapter_id)
    entry["count"] += len(samples)
    if gender and gender != "unknown" and entry["gender"] == "unknown":
        entry["gender"] = gender
        entry["gender_source"] = gender_source or entry["gender_source"]
    if isinstance(tts_profiles, dict):
        for language, profile in tts_profiles.items():
            entry["tts"]["language_profiles"].setdefault(language, profile)
    for sample in samples:
        if sample and sample not in entry["samples"]:
            entry["samples"].append(sample)


def list_chapters(filmsets_root: Path, label: str):
    pattern = f"{label}_*"
    chapters = []
    for path in filmsets_root.glob(pattern):
        if path.is_dir():
            chapters.append(path)
    return sorted(chapters)


def fetch_tts_speakers(endpoint: str, timeout: int = 10):
    try:
        req = urllib.request.Request(endpoint, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError, http.client.RemoteDisconnected):
        return []
    if isinstance(payload, dict):
        speakers = payload.get("speakers")
        if isinstance(speakers, list):
            return speakers
        return []
    if isinstance(payload, list):
        return payload
    return []


def extract_master_speakers(speakers):
    results = []
    for speaker in speakers:
        if isinstance(speaker, str):
            results.append({"id": speaker, "label": speaker})
            continue
        if not isinstance(speaker, dict):
            continue
        speaker_id = speaker.get("speaker_id") or speaker.get("id") or ""
        label = speaker.get("name") or speaker.get("label") or speaker_id
        results.append({"id": str(speaker_id), "label": str(label)})
    return results


def detect_master_gender(label: str):
    lowered = label.lower()
    if "female" in lowered or "frau" in lowered:
        return "female"
    if "male" in lowered or "mann" in lowered:
        return "male"
    if "neutral" in lowered or "neut" in lowered:
        return "unknown"
    return "unknown"


def detect_master_language(label: str):
    lowered = label.lower()
    if "de" in lowered or "german" in lowered or "deutsch" in lowered:
        return "de"
    if "en" in lowered or "english" in lowered:
        return "en"
    return "unknown"


def pick_master_id(index, gender: str, language: str):
    candidates = index.get(gender, {}).get(language, [])
    if candidates:
        return candidates[0]
    candidates = index.get(gender, {}).get("unknown", [])
    if candidates:
        return candidates[0]
    candidates = index.get("unknown", {}).get(language, [])
    if candidates:
        return candidates[0]
    candidates = index.get("unknown", {}).get("unknown", [])
    if candidates:
        return candidates[0]
    return ""


def build_voice_templates_from_speakers(speakers):
    templates = copy.deepcopy(DEFAULT_VOICE_MIX_TEMPLATES)
    masters = [s for s in extract_master_speakers(speakers) if "[master]" in s["label"].lower()]
    if not masters:
        return templates
    index = {"male": {"de": [], "en": [], "unknown": []}, "female": {"de": [], "en": [], "unknown": []}, "unknown": {"de": [], "en": [], "unknown": []}}
    for master in masters:
        gender = detect_master_gender(master["label"])
        language = detect_master_language(master["label"])
        index[gender][language].append(master["id"])
    for gender in templates:
        for language in templates[gender]:
            master_id = pick_master_id(index, gender, language)
            if master_id:
                templates[gender][language]["speaker_mix"]["sources"] = [{"speaker_id": master_id, "weight": 1.0}]
    return templates


def load_voice_mix_templates(story_config: dict, repo_root: Path):
    endpoint = story_config.get("tts_speakers_endpoint", DEFAULT_TTS_SPEAKERS_ENDPOINT)
    speakers = fetch_tts_speakers(endpoint)
    if speakers:
        return build_voice_templates_from_speakers(speakers)
    templates_path = story_config.get("voice_mix_templates_path")
    if templates_path:
        resolved = resolve_path(templates_path, repo_root)
        if resolved and resolved.exists():
            try:
                payload = json.loads(resolved.read_text(encoding="utf-8"))
                if isinstance(payload, dict):
                    return payload
            except json.JSONDecodeError:
                pass
    return copy.deepcopy(DEFAULT_VOICE_MIX_TEMPLATES)


def build_mix_profile(template: dict, speaker_id: str, language: str):
    profile = copy.deepcopy(template)
    if not isinstance(profile, dict):
        return {}
    if "speaker_mix" in profile and isinstance(profile["speaker_mix"], dict):
        mix = profile["speaker_mix"]
        if not mix.get("new_name"):
            mix["new_name"] = f"{speaker_id}_{language}"
    return profile


def build_voice_cast(story_config: dict, story_root: Path, repo_root: Path):
    filmsets_root = resolve_path(story_config.get("filmsets_root"), repo_root)
    if not filmsets_root:
        filmsets_root = story_root / "filmsets"
    label = story_config.get("chapter_label", "story")
    chapters = list_chapters(filmsets_root, label)
    mix_templates = load_voice_mix_templates(story_config, repo_root)

    speakers = {}
    for chapter_dir in chapters:
        chapter_id = chapter_dir.name
        script_path = chapter_dir / "DREHBUCH_HOLLYWOOD.md"
        text = read_text(script_path)
        if not text:
            continue

        narrator = parse_narrator(text)
        if narrator:
            gender, gender_source = detect_geez_gender("Narrator")
            tts_profiles = {
                "de": build_mix_profile(mix_templates["unknown"]["de"], "narrator", "de"),
                "en": build_mix_profile(mix_templates["unknown"]["en"], "narrator", "en"),
            }
            merge_speaker(
                speakers,
                "Narrator",
                "narrator",
                chapter_id,
                [narrator[:240]],
                gender,
                gender_source,
                tts_profiles,
            )

        for actor, lines in parse_monologues(text).items():
            gender, gender_source = detect_geez_gender(actor)
            profile_key = gender if gender in mix_templates else "unknown"
            tts_profiles = {
                "de": build_mix_profile(mix_templates[profile_key]["de"], normalize_speaker_id(actor), "de"),
                "en": build_mix_profile(mix_templates[profile_key]["en"], normalize_speaker_id(actor), "en"),
            }
            merge_speaker(speakers, actor, "monologue", chapter_id, lines[:3], gender, gender_source, tts_profiles)

        dialog_map = parse_dialog(text)
        for actor, lines in dialog_map.items():
            gender, gender_source = detect_geez_gender(actor)
            profile_key = gender if gender in mix_templates else "unknown"
            tts_profiles = {
                "de": build_mix_profile(mix_templates[profile_key]["de"], normalize_speaker_id(actor), "de"),
                "en": build_mix_profile(mix_templates[profile_key]["en"], normalize_speaker_id(actor), "en"),
            }
            merge_speaker(speakers, actor, "dialog", chapter_id, lines[:3], gender, gender_source, tts_profiles)

    output = []
    for entry in speakers.values():
        entry["types"] = sorted(entry["types"])
        entry["chapters"] = sorted(entry["chapters"])
        output.append(entry)
    output.sort(key=lambda item: item["id"])
    return output


def main():
    parser = argparse.ArgumentParser(description="Build voice cast from screenplays.")
    parser.add_argument("--story-root", default="", help="Path to story root.")
    parser.add_argument("--story-config", default="", help="Path to story_config.json.")
    parser.add_argument("--output", default="", help="Output path (defaults to subjects/voice_cast.json).")
    args = parser.parse_args()

    story_config, story_root, repo_root = load_story_config(
        story_root=args.story_root or None,
        story_config_path=args.story_config or None,
    )
    subjects_root = resolve_path(story_config.get("subjects_root"), repo_root)
    if not subjects_root:
        subjects_root = story_root / "subjects"
    output_path = resolve_path(args.output, repo_root) if args.output else subjects_root / "voice_cast.json"
    ensure_dir(output_path.parent)

    cast = build_voice_cast(story_config, story_root, repo_root)
    payload = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "story_id": story_config.get("story_id", ""),
        "speaker_count": len(cast),
        "speakers": cast,
    }
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote voice cast: {output_path}")


if __name__ == "__main__":
    main()
