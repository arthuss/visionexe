import argparse
import hashlib
import json
import os
import re
import time
import uuid
from pathlib import Path

from rag_utils import load_config, embed_texts, request_json, qdrant_headers
from visionexe_paths import load_story_config, resolve_repo_root

WORKER_ROOT = Path(__file__).resolve().parent
REPO_ROOT = resolve_repo_root()
CHECKLIST_PATH = REPO_ROOT / "engine" / "workers" / "building_scenes_and_chapters.md"
DEFAULT_CHECKPOINT_PATH = REPO_ROOT / "engine" / "workers" / "rag_checkpoint.json"
DEFAULT_CONFIG_PATH = REPO_ROOT / "engine" / "workers" / "rag_config_small.json"
FALLBACK_CONFIG_PATH = REPO_ROOT / "engine" / "scripts" / "rag_config_small.json"

SKIP_DIRS = {
    "produced_assets",
    "reference_images",
    "Media",
    "__pycache__",
    ".git"
}
REPO_SKIP_DIRS = set(SKIP_DIRS) | {"filmsets"}


def normalize_chapter(value):
    if not value:
        return ""
    if value.startswith("chapter_"):
        return value
    if value.isdigit():
        return f"chapter_{int(value):03d}"
    return value


def normalize_scene(value):
    if not value:
        return ""
    raw = str(value)
    if "_" in raw:
        parts = raw.split("_")
    elif "." in raw:
        parts = raw.split(".")
    else:
        return raw
    if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
        return f"{int(parts[0])}.{int(parts[1])}"
    return raw


def get_chapters(filmsets_path, chapter_arg, chapter_label, chapter_padding):
    all_chapters = sorted(
        [d for d in os.listdir(filmsets_path) if d.startswith(f"{chapter_label}_")]
    )
    if chapter_arg == "all":
        return all_chapters
    selected = []
    parts = chapter_arg.split(",")
    for part in parts:
        if "-" in part:
            start, end = map(int, part.split("-"))
            for i in range(start, end + 1):
                name = f"{chapter_label}_{i:0{chapter_padding}d}"
                if name in all_chapters:
                    selected.append(name)
        else:
            number = int(part)
            name = f"{chapter_label}_{number:0{chapter_padding}d}"
            if name in all_chapters:
                selected.append(name)
    return sorted(set(selected))


def read_text(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            return handle.read()
    except OSError:
        return ""


def chunk_text(text, max_chars, overlap):
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    buffer = ""
    for paragraph in paragraphs:
        if not buffer:
            buffer = paragraph
            continue
        if len(buffer) + 2 + len(paragraph) <= max_chars:
            buffer = f"{buffer}\n\n{paragraph}"
            continue
        chunks.extend(split_chunk(buffer, max_chars, overlap))
        buffer = paragraph
    if buffer:
        chunks.extend(split_chunk(buffer, max_chars, overlap))
    return chunks


def split_chunk(text, max_chars, overlap):
    if len(text) <= max_chars:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = max(0, end - overlap)
    return chunks


def parse_script_scenes(content):
    pattern = r"(^##\s+\[ACT\s+\d+\]\s+\[SCENE\s+[\d\.]+\].*$)"
    parts = re.split(pattern, content, flags=re.MULTILINE)
    scenes = []
    current_header = None
    current_scene = ""
    for part in parts:
        if part.strip().startswith("## [ACT"):
            current_header = part.strip()
            match = re.search(r"\[SCENE\s+([\d\.]+)\]", current_header)
            current_scene = match.group(1) if match else ""
            continue
        if current_header and part.strip():
            scenes.append((current_scene, f"{current_header}\n{part.strip()}"))
    return scenes


def find_analysis_files(chapter_path):
    for dirpath, dirnames, filenames in os.walk(chapter_path):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        if "analysis_llm.txt" in filenames:
            yield os.path.join(dirpath, "analysis_llm.txt")


def detect_scene_from_filename(filename):
    match = re.search(r"scene_(\d+)[_.](\d+)", filename)
    if match:
        return normalize_scene(f"{match.group(1)}.{match.group(2)}")
    return ""


def build_document(text, payload_base, max_chars, overlap):
    docs = []
    for chunk_index, chunk in enumerate(chunk_text(text, max_chars, overlap)):
        payload = payload_base.copy()
        payload["chunk"] = chunk_index
        payload["text"] = chunk
        docs.append({
            "text": chunk,
            "payload": payload
        })
    return docs


def gather_documents(filmsets_path, chapter, max_chars, overlap, include_media):
    docs = []
    chapter_path = os.path.join(filmsets_path, chapter)
    rel_chapter_path = os.path.relpath(chapter_path, str(REPO_ROOT))

    script_path = os.path.join(chapter_path, "DREHBUCH_HOLLYWOOD.md")
    if os.path.exists(script_path):
        content = read_text(script_path)
        for scene_id, scene_text in parse_script_scenes(content):
            payload = {
                "chapter": chapter,
                "scene": normalize_scene(scene_id),
                "kind": "screenplay",
                "source": "DREHBUCH_HOLLYWOOD.md",
                "path": script_path,
                "path_rel": os.path.relpath(script_path, str(REPO_ROOT)),
                "mtime": os.path.getmtime(script_path),
                "size": os.path.getsize(script_path)
            }
            docs.extend(build_document(scene_text, payload, max_chars, overlap))

    narration_path = os.path.join(chapter_path, "DREHBUCH_NARRATIV.md")
    if os.path.exists(narration_path):
        content = read_text(narration_path)
        payload = {
            "chapter": chapter,
            "scene": "",
            "kind": "narration_script",
            "source": "DREHBUCH_NARRATIV.md",
            "path": narration_path,
            "path_rel": os.path.relpath(narration_path, str(REPO_ROOT)),
            "mtime": os.path.getmtime(narration_path),
            "size": os.path.getsize(narration_path),
        }
        docs.extend(build_document(content, payload, max_chars, overlap))

    chapter_story_path = os.path.join(chapter_path, "story.txt")
    if os.path.exists(chapter_story_path):
        content = read_text(chapter_story_path)
        payload = {
            "chapter": chapter,
            "scene": "",
            "kind": "chapter_story",
            "source": "story.txt",
            "path": chapter_story_path,
            "path_rel": os.path.relpath(chapter_story_path, str(REPO_ROOT)),
            "mtime": os.path.getmtime(chapter_story_path),
            "size": os.path.getsize(chapter_story_path),
        }
        docs.extend(build_document(content, payload, max_chars, overlap))

    chapter_briefing_path = os.path.join(chapter_path, "chapter_briefing.md")
    if os.path.exists(chapter_briefing_path):
        content = read_text(chapter_briefing_path)
        payload = {
            "chapter": chapter,
            "scene": "",
            "kind": "chapter_briefing",
            "source": "chapter_briefing.md",
            "path": chapter_briefing_path,
            "path_rel": os.path.relpath(chapter_briefing_path, str(REPO_ROOT)),
            "mtime": os.path.getmtime(chapter_briefing_path),
            "size": os.path.getsize(chapter_briefing_path),
        }
        docs.extend(build_document(content, payload, max_chars, overlap))

    analysis_root_files = [
        "analysis_llm.txt",
        "analysis_llm_graphematic.txt",
        "analysis_llm_morphologic.txt",
        "analysis_llm_synthactic.txt",
        "analysis_llm_semantic_historical.txt",
    ]
    for filename in analysis_root_files:
        path = os.path.join(chapter_path, filename)
        if not os.path.exists(path):
            continue
        content = read_text(path)
        payload = {
            "chapter": chapter,
            "scene": "",
            "kind": "analysis_root",
            "source": filename,
            "path": path,
            "path_rel": os.path.relpath(path, str(REPO_ROOT)),
            "mtime": os.path.getmtime(path),
            "size": os.path.getsize(path),
        }
        docs.extend(build_document(content, payload, max_chars, overlap))

    for analysis_path in find_analysis_files(chapter_path):
        content = read_text(analysis_path)
        payload = {
            "chapter": chapter,
            "scene": "",
            "kind": "analysis",
            "source": "analysis_llm.txt",
            "path": analysis_path,
            "path_rel": os.path.relpath(analysis_path, str(REPO_ROOT)),
            "mtime": os.path.getmtime(analysis_path),
            "size": os.path.getsize(analysis_path)
        }
        docs.extend(build_document(content, payload, max_chars, overlap))

    concept_path = os.path.join(chapter_path, "concept_engine", "mechanic_concept.txt")
    if os.path.exists(concept_path):
        content = read_text(concept_path)
        payload = {
            "chapter": chapter,
            "scene": "",
            "kind": "concept",
            "source": "mechanic_concept.txt",
            "path": concept_path,
            "path_rel": os.path.relpath(concept_path, str(REPO_ROOT)),
            "mtime": os.path.getmtime(concept_path),
            "size": os.path.getsize(concept_path)
        }
        docs.extend(build_document(content, payload, max_chars, overlap))

    audio_folder = os.path.join(chapter_path, "audio")
    if os.path.isdir(audio_folder):
        for name in os.listdir(audio_folder):
            full_path = os.path.join(audio_folder, name)
            if not os.path.isfile(full_path):
                continue
            if name.endswith("_audio_meta.json") or name.endswith("_voice.json"):
                content = read_text(full_path)
                scene_id = detect_scene_from_filename(name)
                payload = {
                    "chapter": chapter,
                    "scene": scene_id,
                    "kind": "audio_meta",
                    "source": name,
                    "path": full_path,
                    "path_rel": os.path.relpath(full_path, str(REPO_ROOT)),
                    "mtime": os.path.getmtime(full_path),
                    "size": os.path.getsize(full_path)
                }
                docs.extend(build_document(content, payload, max_chars, overlap))
            if name.endswith("_monologue.txt"):
                content = read_text(full_path)
                scene_id = detect_scene_from_filename(name)
                payload = {
                    "chapter": chapter,
                    "scene": scene_id,
                    "kind": "monologue",
                    "source": name,
                    "path": full_path,
                    "path_rel": os.path.relpath(full_path, str(REPO_ROOT)),
                    "mtime": os.path.getmtime(full_path),
                    "size": os.path.getsize(full_path)
                }
                docs.extend(build_document(content, payload, max_chars, overlap))

    audio_audit_path = os.path.join(chapter_path, "audio_audit.json")
    if os.path.exists(audio_audit_path):
        content = read_text(audio_audit_path)
        payload = {
            "chapter": chapter,
            "scene": "",
            "kind": "audio_audit",
            "source": "audio_audit.json",
            "path": audio_audit_path,
            "path_rel": os.path.relpath(audio_audit_path, str(REPO_ROOT)),
            "mtime": os.path.getmtime(audio_audit_path),
            "size": os.path.getsize(audio_audit_path)
        }
        docs.extend(build_document(content, payload, max_chars, overlap))

    audio_audit_summary_path = os.path.join(chapter_path, "audio_audit_summary.md")
    if os.path.exists(audio_audit_summary_path):
        content = read_text(audio_audit_summary_path)
        payload = {
            "chapter": chapter,
            "scene": "",
            "kind": "audio_audit_summary",
            "source": "audio_audit_summary.md",
            "path": audio_audit_summary_path,
            "path_rel": os.path.relpath(audio_audit_summary_path, str(REPO_ROOT)),
            "mtime": os.path.getmtime(audio_audit_summary_path),
            "size": os.path.getsize(audio_audit_summary_path)
        }
        docs.extend(build_document(content, payload, max_chars, overlap))

    audit_path = os.path.join(chapter_path, "scene_audit.json")
    if os.path.exists(audit_path):
        content = read_text(audit_path)
        payload = {
            "chapter": chapter,
            "scene": "",
            "kind": "scene_audit",
            "source": "scene_audit.json",
            "path": audit_path,
            "path_rel": os.path.relpath(audit_path, str(REPO_ROOT)),
            "mtime": os.path.getmtime(audit_path),
            "size": os.path.getsize(audit_path)
        }
        docs.extend(build_document(content, payload, max_chars, overlap))

    audit_summary_path = os.path.join(chapter_path, "scene_audit_summary.md")
    if os.path.exists(audit_summary_path):
        content = read_text(audit_summary_path)
        payload = {
            "chapter": chapter,
            "scene": "",
            "kind": "scene_audit_summary",
            "source": "scene_audit_summary.md",
            "path": audit_summary_path,
            "path_rel": os.path.relpath(audit_summary_path, str(REPO_ROOT)),
            "mtime": os.path.getmtime(audit_summary_path),
            "size": os.path.getsize(audit_summary_path)
        }
        docs.extend(build_document(content, payload, max_chars, overlap))

    vision_dir = os.path.join(chapter_path, "vision")
    vision_audit_path = os.path.join(vision_dir, "vision_audit.json")
    vision_summary_path = os.path.join(vision_dir, "vision_audit_summary.md")
    if os.path.exists(vision_audit_path):
        content = read_text(vision_audit_path)
        payload = {
            "chapter": chapter,
            "scene": "",
            "kind": "vision_audit",
            "source": "vision_audit.json",
            "path": vision_audit_path,
            "path_rel": os.path.relpath(vision_audit_path, str(REPO_ROOT)),
            "mtime": os.path.getmtime(vision_audit_path),
            "size": os.path.getsize(vision_audit_path)
        }
        docs.extend(build_document(content, payload, max_chars, overlap))
    if os.path.exists(vision_summary_path):
        content = read_text(vision_summary_path)
        payload = {
            "chapter": chapter,
            "scene": "",
            "kind": "vision_audit_summary",
            "source": "vision_audit_summary.md",
            "path": vision_summary_path,
            "path_rel": os.path.relpath(vision_summary_path, str(REPO_ROOT)),
            "mtime": os.path.getmtime(vision_summary_path),
            "size": os.path.getsize(vision_summary_path)
        }
        docs.extend(build_document(content, payload, max_chars, overlap))

    if include_media:
        media_folder = os.path.join(chapter_path, "Media")
        if os.path.isdir(media_folder):
            for name in os.listdir(media_folder):
                full_path = os.path.join(media_folder, name)
                if not os.path.isfile(full_path):
                    continue
                scene_id = detect_scene_from_filename(name)
                ext = os.path.splitext(name)[1].lower().lstrip(".")
                text = f"Media file: {name} (.{ext}) in {rel_chapter_path}/Media"
                payload = {
                    "chapter": chapter,
                    "scene": scene_id,
                    "kind": "media",
                    "source": name,
                    "path": full_path,
                    "path_rel": os.path.relpath(full_path, str(REPO_ROOT)),
                    "mtime": os.path.getmtime(full_path),
                    "size": os.path.getsize(full_path),
                    "media_type": ext
                }
                docs.extend(build_document(text, payload, max_chars, overlap))
    return docs


def gather_checklist(max_chars, overlap):
    if not CHECKLIST_PATH.exists():
        return []
    content = read_text(str(CHECKLIST_PATH))
    payload = {
        "chapter": "global",
        "scene": "",
        "kind": "checklist",
        "source": "building_scenes_and_chapters.md",
        "path": str(CHECKLIST_PATH),
        "path_rel": os.path.relpath(str(CHECKLIST_PATH), str(REPO_ROOT)),
        "mtime": os.path.getmtime(CHECKLIST_PATH),
        "size": os.path.getsize(CHECKLIST_PATH)
    }
    return build_document(content, payload, max_chars, overlap)


def parse_extensions(value):
    if not value:
        return [".md", ".json", ".csv"]
    items = re.split(r"[,\s]+", str(value))
    exts = []
    for item in items:
        cleaned = item.strip().lower()
        if not cleaned:
            continue
        if not cleaned.startswith("."):
            cleaned = f".{cleaned}"
        exts.append(cleaned)
    return sorted(set(exts)) or [".md"]


def gather_repo_docs(max_chars, overlap, extensions):
    docs = []
    if not extensions:
        return docs
    for dirpath, dirnames, filenames in os.walk(str(REPO_ROOT)):
        dirnames[:] = [d for d in dirnames if d not in REPO_SKIP_DIRS]
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext not in extensions:
                continue
            path = os.path.join(dirpath, filename)
            if not os.path.isfile(path):
                continue
            content = read_text(path)
            if not content:
                continue
            payload = {
                "chapter": "global",
                "scene": "",
                "kind": "repo_doc",
                "source": filename,
                "path": path,
                "path_rel": os.path.relpath(path, str(REPO_ROOT)),
                "mtime": os.path.getmtime(path),
                "size": os.path.getsize(path)
            }
            docs.extend(build_document(content, payload, max_chars, overlap))
    return docs


def gather_global_docs(max_chars, overlap):
    docs = []
    global_files = [
        ("LORA_TRAINING_SET.json", "lora_training_set"),
        ("LORA_TRAINING_QUEUE.json", "lora_training_queue"),
        ("LORA_PROP_QUEUE.json", "lora_prop_queue"),
        ("ACTOR_PROP_DB.json", "actor_prop_db"),
        ("ACTOR_PROP_SUMMARY.md", "actor_prop_summary"),
        ("ENVIRONMENT_ASSETS.json", "environment_assets"),
        ("ENVIRONMENT_LABEL_TODO.md", "environment_label_todo"),
        ("lora_audit.json", "lora_audit"),
        ("lora_audit_summary.md", "lora_audit_summary"),
        ("prop_audit.json", "prop_audit"),
        ("prop_audit_summary.md", "prop_audit_summary"),
        ("env_audit.json", "env_audit"),
        ("env_audit_summary.md", "env_audit_summary")
    ]
    for filename, kind in global_files:
        path = os.path.join(str(REPO_ROOT), filename)
        if not os.path.exists(path):
            continue
        content = read_text(path)
        payload = {
            "chapter": "global",
            "scene": "",
            "kind": kind,
            "source": filename,
            "path": path,
            "path_rel": os.path.relpath(path, str(REPO_ROOT)),
            "mtime": os.path.getmtime(path),
            "size": os.path.getsize(path)
        }
        docs.extend(build_document(content, payload, max_chars, overlap))
    return docs


def stable_point_id(payload):
    raw = f"{payload.get('path')}|{payload.get('scene')}|{payload.get('kind')}|{payload.get('chunk')}"
    return str(uuid.uuid5(uuid.NAMESPACE_URL, raw))


def build_run_signature(config, chapters, max_chars, overlap, include_media):
    payload = {
        "collection": config.get("collection"),
        "qdrant_url": config.get("qdrant_url"),
        "embedding_model": config.get("embedding", {}).get("model"),
        "embedding_endpoint": config.get("embedding", {}).get("endpoint"),
        "chapters": list(chapters),
        "max_chars": int(max_chars),
        "overlap": int(overlap),
        "include_media": bool(include_media),
    }
    raw = json.dumps(payload, sort_keys=True)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def load_checkpoint(path):
    if not path or not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (json.JSONDecodeError, OSError):
        return None


def save_checkpoint(path, payload):
    if not path:
        return
    try:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
    except OSError:
        pass


def clear_checkpoint(path):
    if not path or not os.path.exists(path):
        return
    try:
        os.remove(path)
    except OSError:
        pass


def ensure_collection(config, vector_size, reset):
    headers = qdrant_headers(config)
    collection = config["collection"]
    url = f"{config['qdrant_url']}/collections/{collection}"
    timeout = config.get("qdrant_timeout_sec", 60)
    if reset:
        request_json("DELETE", url, headers=headers, timeout=timeout)
    status, _ = request_json("GET", url, headers=headers, timeout=timeout)
    if status == 200:
        return
    payload = {
        "vectors": {
            "size": vector_size,
            "distance": config.get("distance", "Cosine")
        }
    }
    status, data = request_json("PUT", url, payload=payload, headers=headers, timeout=timeout)
    if status < 200 or status >= 300:
        raise RuntimeError(f"Failed to create collection: {status} {data}")


def get_collection_points_count(config):
    headers = qdrant_headers(config)
    collection = config["collection"]
    url = f"{config['qdrant_url']}/collections/{collection}"
    timeout = config.get("qdrant_timeout_sec", 60)
    status, data = request_json("GET", url, headers=headers, timeout=timeout)
    if status != 200 or not isinstance(data, dict):
        return None
    result = data.get("result") if isinstance(data, dict) else None
    if not isinstance(result, dict):
        return None
    return result.get("points_count")


def upsert_points(config, points):
    headers = qdrant_headers(config)
    collection = config["collection"]
    url = f"{config['qdrant_url']}/collections/{collection}/points?wait=true"
    payload = {"points": points}
    timeout = config.get("qdrant_timeout_sec", 60)
    status, data = request_json("PUT", url, payload=payload, headers=headers, timeout=timeout)
    if status < 200 or status >= 300:
        raise RuntimeError(f"Upsert failed: {status} {data}")


def embed_batch(config, batch):
    texts = [doc["text"] for doc in batch]
    try:
        return embed_texts(config, texts)
    except RuntimeError as exc:
        message = str(exc).lower()
        if "input is too large" in message or "physical batch size" in message:
            if len(batch) == 1:
                raise RuntimeError(
                    "Embedding input too large. Re-run with smaller --max-chars."
                ) from exc
            vectors = []
            for doc in batch:
                vectors.extend(embed_texts(config, [doc["text"]]))
            return vectors
        raise


def main():
    parser = argparse.ArgumentParser(description="Index chapter data into Qdrant for RAG.")
    parser.add_argument("--chapter", default="all", help="Chapter number(s), e.g. 1, 1-5, all")
    parser.add_argument("--config", default="", help="Config JSON path")
    parser.add_argument("--story-root", help="Story root (defaults to engine_config default_story_root).")
    parser.add_argument("--story-config", help="Path to story_config.json (overrides story-root).")
    parser.add_argument("--filmsets-root", help="Override filmsets root (defaults to story_config).")
    parser.add_argument("--max-chars", type=int, default=1800, help="Max characters per chunk")
    parser.add_argument("--overlap", type=int, default=200, help="Overlap between chunks")
    parser.add_argument("--batch-size", type=int, default=8, help="Embedding batch size")
    parser.add_argument("--reset", action="store_true", help="Drop and recreate collection")
    parser.add_argument("--dry-run", action="store_true", help="Only print what would be indexed")
    parser.add_argument("--no-media", action="store_true", help="Skip Media folder entries")
    parser.add_argument("--no-repo-docs", action="store_true", help="Skip repo-level markdown/json/csv docs")
    parser.add_argument("--repo-extensions", default="md,json,csv", help="Repo doc extensions (comma/space separated)")
    parser.add_argument("--checkpoint-file", default=DEFAULT_CHECKPOINT_PATH, help="Resume checkpoint file path")
    resume_group = parser.add_mutually_exclusive_group()
    resume_group.add_argument("--resume", action="store_true", help="Resume from checkpoint if available (default)")
    resume_group.add_argument("--no-resume", action="store_true", help="Disable resume checkpoint")
    parser.add_argument("--keep-checkpoint", action="store_true", help="Keep checkpoint file after successful run")
    args = parser.parse_args()

    config_path = args.config
    if not config_path:
        config_path = str(DEFAULT_CONFIG_PATH if DEFAULT_CONFIG_PATH.exists() else FALLBACK_CONFIG_PATH)
    config = load_config(config_path)
    story_config, story_root, repo_root = load_story_config(
        story_root=args.story_root,
        story_config_path=args.story_config,
    )
    filmsets_root = args.filmsets_root or story_config.get("filmsets_root")
    filmsets_root = str(filmsets_root) if filmsets_root else ""
    if not filmsets_root:
        raise SystemExit("filmsets_root missing in story_config.json")
    filmsets_root = str(Path(filmsets_root)) if Path(filmsets_root).is_absolute() else str(repo_root / filmsets_root)
    chapter_label = story_config.get("chapter_label", "chapter")
    chapter_padding = int(story_config.get("chapter_index_padding", 3))
    chapters = get_chapters(filmsets_root, args.chapter, chapter_label, chapter_padding)
    include_media = not args.no_media
    include_repo_docs = not args.no_repo_docs
    repo_extensions = parse_extensions(args.repo_extensions)

    documents = gather_checklist(args.max_chars, args.overlap)
    documents.extend(gather_global_docs(args.max_chars, args.overlap))
    if include_repo_docs:
        documents.extend(gather_repo_docs(args.max_chars, args.overlap, repo_extensions))
    for chapter in chapters:
        documents.extend(gather_documents(filmsets_root, chapter, args.max_chars, args.overlap, include_media))

    if args.dry_run:
        print(f"Would index {len(documents)} chunks across {len(chapters)} chapters.")
        return

    if not documents:
        print("No documents found to index.")
        return

    test_vector = embed_texts(config, ["dimension check"])[0]
    ensure_collection(config, len(test_vector), args.reset)

    resume_enabled = not args.no_resume
    checkpoint_path = args.checkpoint_file
    signature = build_run_signature(config, chapters, args.max_chars, args.overlap, include_media)
    start_index = 0
    if args.reset and resume_enabled:
        clear_checkpoint(checkpoint_path)
    elif resume_enabled:
        checkpoint = load_checkpoint(checkpoint_path)
        if checkpoint:
            if checkpoint.get("signature") == signature:
                saved_next = checkpoint.get("next_index", 0)
                if isinstance(saved_next, int) and saved_next > 0:
                    if saved_next >= len(documents):
                        print("Checkpoint indicates indexing already completed.")
                        return
                    start_index = saved_next
                    print(f"Resuming from checkpoint: {start_index}/{len(documents)}")
            else:
                print("Checkpoint signature mismatch; starting from 0.")
        else:
            points_count = get_collection_points_count(config)
            if isinstance(points_count, int) and points_count >= len(documents):
                print(f"Collection already has {points_count} points (>= {len(documents)}).")
                print("Skipping reindex. Use --reset to rebuild.")
                return

    total = len(documents)
    for start in range(start_index, total, args.batch_size):
        batch = documents[start:start + args.batch_size]
        vectors = embed_batch(config, batch)
        points = []
        for doc, vector in zip(batch, vectors):
            payload = doc["payload"].copy()
            payload["hash"] = hashlib.sha1(doc["text"].encode("utf-8", errors="replace")).hexdigest()
            payload["indexed_at"] = int(time.time())
            points.append({
                "id": stable_point_id(payload),
                "vector": vector,
                "payload": payload
            })
        upsert_points(config, points)
        print(f"Indexed {min(start + args.batch_size, total)}/{total}")
        if resume_enabled:
            save_checkpoint(
                checkpoint_path,
                {
                    "signature": signature,
                    "collection": config.get("collection"),
                    "qdrant_url": config.get("qdrant_url"),
                    "embedding_model": config.get("embedding", {}).get("model"),
                    "embedding_endpoint": config.get("embedding", {}).get("endpoint"),
                    "max_chars": args.max_chars,
                    "overlap": args.overlap,
                    "batch_size": args.batch_size,
                    "include_media": include_media,
                    "chapters": chapters,
                    "total_docs": total,
                    "next_index": min(start + args.batch_size, total),
                    "updated_at": int(time.time()),
                },
            )

    print("Indexing complete.")
    if resume_enabled and not args.keep_checkpoint:
        clear_checkpoint(checkpoint_path)


if __name__ == "__main__":
    main()
