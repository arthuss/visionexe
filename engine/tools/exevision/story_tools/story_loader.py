import argparse
import glob
import json
import os
import re
import sys
import uuid
from datetime import datetime
from pathlib import Path

try:
    import psycopg2
    from psycopg2.extras import Json
except ImportError:
    print("psycopg2 is required. Install it before running this script.")
    sys.exit(1)

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None


REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

try:
    from engine.workers.visionexe_paths import load_story_config as load_story_config_engine
    from engine.workers.visionexe_paths import resolve_path as resolve_path_engine
except ImportError:
    load_story_config_engine = None
    resolve_path_engine = None


def load_env(paths):
    for path in paths:
        if not path or not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"')
                if key and key not in os.environ:
                    os.environ[key] = value


def env(name, default=None):
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value


def parse_args():
    parser = argparse.ArgumentParser(description="Load story data into Postgres + Qdrant.")
    parser.add_argument(
        "--mode",
        default="chapters",
        help="chapters, analysis, subjects, all, or comma-separated list",
    )
    parser.add_argument("--story-config", default=None)
    parser.add_argument("--story-id", default=None)
    parser.add_argument("--timeline-id", default=None)
    parser.add_argument("--analysis-master", default=None)
    parser.add_argument("--subjects-root", default=None)
    parser.add_argument("--subjects-include", default="registry,profiles,scenes,environment_route,dynamic_subjects")
    parser.add_argument("--text-collection", default=None)
    parser.add_argument(
        "--data-dir",
        default=os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "data", "Story1-Henoch"),
    )
    parser.add_argument("--pattern", default="chapter_*.txt")
    parser.add_argument("--book-id", default="Story1-Henoch")
    parser.add_argument("--collection-prefix", default="chapter_")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-qdrant", action="store_true")
    parser.add_argument("--no-postgres", action="store_true")
    parser.add_argument("--embedding-endpoint", default=None)
    parser.add_argument("--embedding-model", default=None)
    parser.add_argument("--embedding-dimension", type=int, default=None)
    return parser.parse_args()


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def resolve_path_value(path_value, repo_root):
    if not path_value:
        return None
    if resolve_path_engine:
        return resolve_path_engine(path_value, repo_root)
    candidate = Path(path_value)
    if candidate.is_absolute():
        return candidate
    return repo_root / candidate


def load_story_config_fallback(story_config_path):
    repo_root = REPO_ROOT
    if story_config_path:
        config_path = resolve_path_value(story_config_path, repo_root)
        story_root_path = config_path.parent.parent
    else:
        engine_config_path = repo_root / "engine" / "config" / "engine_config.json"
        engine_config = load_json(engine_config_path)
        story_root_path = resolve_path_value(engine_config.get("default_story_root"), repo_root)
        config_path = story_root_path / "config" / "story_config.json"
    config = load_json(config_path)
    return config, story_root_path, repo_root


def resolve_story_config(story_config_path):
    if load_story_config_engine:
        try:
            return load_story_config_engine(story_config_path=story_config_path)
        except Exception:
            pass
    return load_story_config_fallback(story_config_path)


def parse_modes(value):
    parts = [part.strip().lower() for part in value.split(",") if part.strip()]
    if not parts:
        return {"chapters"}
    if "all" in parts:
        return {"chapters", "analysis", "subjects"}
    return set(parts)


def parse_list(value):
    if not value:
        return []
    return [part.strip() for part in str(value).split(",") if part.strip()]


def normalize_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


def compact_list(value, limit=20):
    items = normalize_list(value)
    if not items:
        return ""
    if limit and len(items) > limit:
        items = items[:limit] + [f"...(+{len(items) - limit} more)"]
    return "; ".join(items)


def append_field(parts, label, value):
    if value is None:
        return
    text = str(value).strip()
    if not text:
        return
    parts.append(f"{label}: {text}")


def resolve_chapter_id(filename):
    base = os.path.splitext(os.path.basename(filename))[0]
    match = re.search(r"chapter_(\d+)", base, re.IGNORECASE)
    if match:
        return match.group(1).lstrip("0") or match.group(1)
    return base


def split_chunks(text):
    lines = text.splitlines()
    has_blank = any(not line.strip() for line in lines)

    chunks = []
    if has_blank:
        current = []
        for line in lines:
            if line.strip():
                current.append(line.rstrip())
            elif current:
                chunks.append("\n".join(current).strip())
                current = []
        if current:
            chunks.append("\n".join(current).strip())
    else:
        for line in lines:
            stripped = line.strip()
            if stripped:
                chunks.append(stripped)

    results = []
    for chunk in chunks:
        verse_id = None
        first_line = chunk.splitlines()[0].strip()
        match = re.match(r"^(\d+[.:]\d+)", first_line)
        if match:
            verse_id = match.group(1)
        results.append({"text": chunk, "verse_id": verse_id})

    return results


def ensure_dim(vector, target_dim):
    if target_dim is None or len(vector) == target_dim:
        return vector
    if len(vector) > target_dim:
        return vector[:target_dim]
    return vector + [0.0] * (target_dim - len(vector))


def normalize_payload_value(value):
    if value is None:
        return ""
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (list, tuple)):
        return [normalize_payload_value(item) for item in value if item is not None]
    if isinstance(value, dict):
        return value
    return str(value)


def normalize_chapter_id(value):
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def embed_texts(texts, endpoint, model, target_dim):
    if endpoint:
        embeddings = embed_via_http(endpoint, texts)
    else:
        if model is None:
            raise RuntimeError("Embedding model not available. Install sentence-transformers or set EMBEDDING_ENDPOINT.")
        embeddings = model.encode(texts, normalize_embeddings=True).tolist()

    return [ensure_dim(vec, target_dim) for vec in embeddings]


def embed_via_http(endpoint, texts):
    import urllib.request

    payload = json.dumps({"inputs": texts}).encode("utf-8")
    request = urllib.request.Request(endpoint, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=60) as response:
        body = response.read().decode("utf-8")

    data = json.loads(body)
    if isinstance(data, list):
        return data
    if "embeddings" in data:
        return data["embeddings"]
    if "data" in data:
        return [item["embedding"] for item in data["data"]]
    if "embedding" in data:
        return [data["embedding"]]

    raise RuntimeError("Unexpected embedding response")


def ensure_schema(conn, embedding_dim):
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vector_documents (
                id UUID PRIMARY KEY,
                collection VARCHAR(100) NOT NULL,
                title VARCHAR(500) NOT NULL,
                content TEXT NOT NULL,
                embedding VECTOR({embedding_dim}),
                metadata JSONB,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
            """
        )
        cur.execute("CREATE INDEX IF NOT EXISTS idx_vector_documents_collection ON vector_documents(collection);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_vector_documents_embedding ON vector_documents USING ivfflat (embedding vector_cosine_ops);")
    conn.commit()


def qdrant_request(method, url, payload=None):
    import urllib.request

    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=60) as response:
        body = response.read().decode("utf-8")

    if not body:
        return {}
    return json.loads(body)


def qdrant_create_collection(base_url, name, vector_size):
    url = f"{base_url}/collections/{name}"
    payload = {
        "vectors": {
            "size": vector_size,
            "distance": "Cosine"
        }
    }
    try:
        qdrant_request("PUT", url, payload)
    except Exception:
        pass


def qdrant_upsert(base_url, name, points):
    url = f"{base_url}/collections/{name}/points?wait=true"
    payload = {"points": points}
    qdrant_request("PUT", url, payload)


def iter_jsonl(path):
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def iter_chapter_docs(files, collection_prefix, book_id, story_id, timeline_id, global_collection=None):
    for path in files:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            text = handle.read()

        chapter_id = resolve_chapter_id(path)
        collection = global_collection or f"{collection_prefix}{chapter_id}"
        chunks = split_chunks(text)

        for index, chunk in enumerate(chunks, start=1):
            title = f"{collection} chunk {index}"
            metadata = {
                "doc_kind": "chapter_chunk",
                "book_id": book_id,
                "chapter_id": chapter_id,
                "chunk_index": index,
                "verse_id": chunk.get("verse_id"),
                "source_file": os.path.basename(path),
            }
            if story_id:
                metadata["story_id"] = story_id
            if timeline_id:
                metadata["timeline_id"] = timeline_id

            yield {
                "title": title,
                "content": chunk.get("text", ""),
                "collection": collection,
                "metadata": metadata,
            }


def iter_analysis_docs(path, story_id, timeline_id, collection):
    if not path or not os.path.exists(path):
        return
    for record in iter_jsonl(path):
        summary = (record.get("summary") or "").strip()
        content = summary
        if not content:
            content = (record.get("raw_content") or "").strip()
        if not content:
            blocks = record.get("analysis_blocks")
            if blocks:
                content = json.dumps(blocks, ensure_ascii=False)
        if not content:
            continue

        chapter = record.get("chapter")
        chapter_id = normalize_chapter_id(chapter)
        scene_id = record.get("scene_id") or record.get("scene_label")
        segment_label = record.get("segment_label") or ""
        title = f"analysis {chapter} {segment_label}".strip()
        metadata = {
            "doc_kind": "analysis_master",
            "story_id": story_id,
            "timeline_id": timeline_id,
            "chapter": chapter,
            "chapter_id": chapter_id,
            "segment_index": record.get("segment_index"),
            "segment_label": segment_label,
            "segment_type": record.get("segment_type"),
            "scene_index": record.get("scene_index"),
            "scene_label": record.get("scene_label"),
            "scene_id": scene_id,
            "source_id": record.get("source_id"),
            "source_path": record.get("source_path"),
        }
        if "analysis_blocks" in record:
            metadata["analysis_blocks"] = record.get("analysis_blocks")
        if "analysis_layers" in record:
            metadata["analysis_layers"] = record.get("analysis_layers")
        if "analysis_paths" in record:
            metadata["analysis_paths"] = record.get("analysis_paths")

        yield {
            "title": title,
            "content": content,
            "collection": collection,
            "metadata": metadata,
        }


def build_profile_content(profile):
    parts = []
    append_field(parts, "name", profile.get("name"))
    append_field(parts, "type", profile.get("type"))
    roles = compact_list(profile.get("roles"))
    if roles:
        parts.append(f"roles: {roles}")
    traits = compact_list(profile.get("visual_traits"))
    if traits:
        parts.append(f"visual_traits: {traits}")
    changes = compact_list(profile.get("changes"))
    if changes:
        parts.append(f"changes: {changes}")
    notes = compact_list(profile.get("notes"))
    if notes:
        parts.append(f"notes: {notes}")
    return "\n".join(parts).strip()


def build_scene_content(scene):
    parts = []
    append_field(parts, "title", scene.get("title"))
    append_field(parts, "location", scene.get("location"))
    action = scene.get("action")
    if isinstance(action, list):
        action = "; ".join([str(item).strip() for item in action if str(item).strip()])
    append_field(parts, "action", action)
    actors = compact_list(scene.get("actors_involved"))
    if actors:
        parts.append(f"actors: {actors}")
    return "\n".join(parts).strip()


def build_registry_content(item):
    parts = []
    append_field(parts, "name", item.get("name"))
    append_field(parts, "type", item.get("type"))
    append_field(parts, "occurrence_count", item.get("occurrence_count"))
    append_field(parts, "first_chapter", item.get("first_chapter"))
    append_field(parts, "last_chapter", item.get("last_chapter"))
    append_field(parts, "is_dynamic", item.get("is_dynamic"))
    return "\n".join(parts).strip()


def build_dynamic_content(item):
    parts = []
    append_field(parts, "name", item.get("name"))
    append_field(parts, "type", item.get("type"))
    append_field(parts, "first_chapter", item.get("first_chapter"))
    append_field(parts, "last_chapter", item.get("last_chapter"))
    return "\n".join(parts).strip()


def build_environment_route_content(item):
    parts = []
    append_field(parts, "location", item.get("location"))
    append_field(parts, "sequence", item.get("sequence"))
    append_field(parts, "scene_id", item.get("scene_id"))
    return "\n".join(parts).strip()


def build_asset_bible_content(item):
    content = item.get("markdown")
    if content:
        return str(content).strip()
    parts = []
    append_field(parts, "name", item.get("name"))
    append_field(parts, "type", item.get("type"))
    return "\n".join(parts).strip()


def build_subject_index(subjects_root):
    root = Path(subjects_root) if subjects_root else None
    index = {}
    if not root or not root.exists():
        return index

    registry_path = root / "registry.json"
    if registry_path.exists():
        for item in load_json(registry_path):
            subject_id = item.get("id")
            if not subject_id:
                continue
            entry = index.setdefault(subject_id, {})
            if "subject_type" not in entry and item.get("type"):
                entry["subject_type"] = item.get("type")

    profiles_path = root / "profiles.jsonl"
    if profiles_path.exists():
        for profile in iter_jsonl(profiles_path):
            subject_id = profile.get("id")
            if not subject_id:
                continue
            entry = index.setdefault(subject_id, {})
            if profile.get("type"):
                entry["subject_type"] = profile.get("type")
            roles = normalize_list(profile.get("roles"))
            if roles:
                entry["roles"] = roles

    return index


def iter_subject_docs(subjects_root, include, story_id, timeline_id, collection, subject_index=None):
    root = Path(subjects_root) if subjects_root else None
    if not root or not root.exists():
        return

    include_set = {item.lower() for item in include}
    subject_index = subject_index or {}

    registry_path = root / "registry.json"
    if "registry" in include_set and registry_path.exists():
        for item in load_json(registry_path):
            subject_id = item.get("id")
            content = build_registry_content(item)
            if not content:
                continue
            metadata = {
                "doc_kind": "subject_registry",
                "story_id": story_id,
                "timeline_id": timeline_id,
                "owner_kind": "subject",
                "owner_id": subject_id,
                "subject_type": item.get("type"),
            }
            yield {
                "title": f"registry {subject_id}",
                "content": content,
                "collection": collection,
                "metadata": metadata,
            }

    profiles_path = root / "profiles.jsonl"
    if "profiles" in include_set and profiles_path.exists():
        for profile in iter_jsonl(profiles_path):
            subject_id = profile.get("id")
            content = build_profile_content(profile)
            if not content:
                continue
            metadata = {
                "doc_kind": "subject_profile",
                "story_id": story_id,
                "timeline_id": timeline_id,
                "owner_kind": "subject",
                "owner_id": subject_id,
                "subject_type": profile.get("type"),
                "is_dynamic": profile.get("is_dynamic"),
                "state_policy": profile.get("state_policy"),
            }
            yield {
                "title": f"profile {subject_id}",
                "content": content,
                "collection": collection,
                "metadata": metadata,
            }

    scenes_path = root / "scenes.jsonl"
    if "scenes" in include_set and scenes_path.exists():
        for scene in iter_jsonl(scenes_path):
            scene_id = scene.get("scene_id")
            content = build_scene_content(scene)
            if not content:
                continue
            chapter_id = normalize_chapter_id(scene.get("chapter"))
            metadata = {
                "doc_kind": "scene",
                "story_id": story_id,
                "timeline_id": timeline_id,
                "owner_kind": "scene",
                "owner_id": scene_id,
                "chapter": scene.get("chapter"),
                "chapter_id": chapter_id,
                "segment_label": scene.get("segment_label"),
                "segment_type": scene.get("segment_type"),
                "source_id": scene.get("source_id"),
                "scene_id": scene_id,
            }
            yield {
                "title": f"scene {scene_id}",
                "content": content,
                "collection": collection,
                "metadata": metadata,
            }

    env_route_path = root / "environment_route.jsonl"
    if "environment_route" in include_set and env_route_path.exists():
        for entry in iter_jsonl(env_route_path):
            scene_id = entry.get("scene_id")
            content = build_environment_route_content(entry)
            if not content:
                continue
            chapter_id = normalize_chapter_id(entry.get("chapter"))
            metadata = {
                "doc_kind": "environment_route",
                "story_id": story_id,
                "timeline_id": timeline_id,
                "owner_kind": "scene",
                "owner_id": scene_id,
                "chapter": entry.get("chapter"),
                "chapter_id": chapter_id,
                "segment_label": entry.get("segment_label"),
                "scene_id": scene_id,
            }
            yield {
                "title": f"environment route {scene_id}",
                "content": content,
                "collection": collection,
                "metadata": metadata,
            }

    dynamic_path = root / "dynamic_subjects.json"
    if "dynamic_subjects" in include_set and dynamic_path.exists():
        dynamic_data = load_json(dynamic_path)
        for item in dynamic_data.get("subjects", []):
            subject_id = item.get("id")
            content = build_dynamic_content(item)
            if not content:
                continue
            metadata = {
                "doc_kind": "dynamic_subject",
                "story_id": story_id,
                "timeline_id": timeline_id,
                "owner_kind": "subject",
                "owner_id": subject_id,
                "subject_type": item.get("type"),
                "is_dynamic": item.get("is_dynamic"),
            }
            yield {
                "title": f"dynamic {subject_id}",
                "content": content,
                "collection": collection,
                "metadata": metadata,
            }

    occurrences_path = root / "occurrences.jsonl"
    if "occurrences" in include_set and occurrences_path.exists():
        for occ in iter_jsonl(occurrences_path):
            subject_id = occ.get("subject_id")
            content = f"subject_id: {subject_id}"
            phase_id = occ.get("phase_id") or occ.get("phase")
            subject_meta = subject_index.get(subject_id, {})
            chapter_id = normalize_chapter_id(occ.get("chapter"))
            metadata = {
                "doc_kind": "occurrence",
                "story_id": story_id,
                "timeline_id": timeline_id,
                "owner_kind": "subject",
                "owner_id": subject_id,
                "subject_id": subject_id,
                "subject_type": subject_meta.get("subject_type"),
                "roles": subject_meta.get("roles", []),
                "chapter": occ.get("chapter"),
                "chapter_id": chapter_id,
                "segment_label": occ.get("segment_label"),
                "segment_type": occ.get("segment_type"),
                "scene_label": occ.get("scene_label"),
                "scene_id": occ.get("scene_label"),
                "source_id": occ.get("source_id"),
            }
            if phase_id:
                metadata["phase_id"] = phase_id
            yield {
                "title": f"occurrence {subject_id}",
                "content": content,
                "collection": collection,
                "metadata": metadata,
            }

    asset_cards_path = root / "asset_bible_cards.jsonl"
    if "asset_bible_cards" in include_set and asset_cards_path.exists():
        for item in iter_jsonl(asset_cards_path):
            subject_id = item.get("id")
            content = build_asset_bible_content(item)
            if not content:
                continue
            metadata = {
                "doc_kind": "asset_bible_card",
                "story_id": story_id,
                "timeline_id": timeline_id,
                "owner_kind": "subject",
                "owner_id": subject_id,
                "subject_type": item.get("type"),
            }
            yield {
                "title": f"asset card {subject_id}",
                "content": content,
                "collection": collection,
                "metadata": metadata,
            }


def main():
    load_env([
        os.path.join(os.path.dirname(__file__), ".env"),
        os.path.join(os.path.dirname(__file__), "..", ".env"),
        os.path.join(os.path.dirname(__file__), "..", "vector_mcp", ".env"),
    ])

    args = parse_args()
    modes = parse_modes(args.mode)

    story_config, _story_root, repo_root = resolve_story_config(args.story_config)
    story_id = args.story_id or story_config.get("story_id") or args.book_id
    timeline_id = args.timeline_id or story_config.get("timeline_default")

    analysis_master_path = args.analysis_master or story_config.get("analysis_master_path")
    analysis_master_path = resolve_path_value(analysis_master_path, repo_root) if analysis_master_path else None

    subjects_root = args.subjects_root or story_config.get("subjects_root")
    subjects_root = resolve_path_value(subjects_root, repo_root) if subjects_root else None

    global_collection = args.text_collection or env("QDRANT_TEXT_COLLECTION") or env("QDRANT_COLLECTION")
    if ("analysis" in modes or "subjects" in modes) and not global_collection:
        global_collection = "vx_text_qwen3e2b_v1"

    if args.no_qdrant and args.no_postgres:
        print("Both backends are disabled. Use --no-qdrant or --no-postgres instead of both.")
        return

    db_host = env("VECTOR_DB_HOST", env("DB_HOST", "localhost"))
    db_port = int(env("VECTOR_DB_PORT", env("DB_PORT", "5432")))
    db_name = env("VECTOR_DB_NAME", env("DB_NAME", "exegetos"))
    db_user = env("VECTOR_DB_USER", env("ADMIN_USER", env("AGENT_USER", "vector_admin")))
    db_password = env("VECTOR_DB_PASSWORD", env("ADMIN_PASSWORD", env("AGENT_PASSWORD", "change_me")))

    qdrant_host = env("QDRANT_HOST", "localhost")
    qdrant_port = int(env("QDRANT_HTTP_PORT", env("QDRANT_PORT", "6333")))
    qdrant_url = f"http://{qdrant_host}:{qdrant_port}"

    embedding_endpoint = args.embedding_endpoint or env("EMBEDDING_ENDPOINT")
    embedding_dim = args.embedding_dimension or int(env("EMBEDDING_DIMENSION", "1024"))

    model_name = args.embedding_model or env("EMBEDDING_MODEL")
    model = None
    if not embedding_endpoint:
        if SentenceTransformer is None:
            raise RuntimeError("sentence-transformers not installed and no EMBEDDING_ENDPOINT provided")
        if not model_name:
            model_name = os.path.join(os.path.dirname(__file__), "..", "Qwen3-Embedding-0.6B")
        model = SentenceTransformer(model_name)

    conn = None
    if not args.no_postgres and not args.dry_run:
        conn = psycopg2.connect(host=db_host, port=db_port, dbname=db_name, user=db_user, password=db_password)
        ensure_schema(conn, embedding_dim)

    created_collections = set()
    total_docs = 0

    def store_batch(batch):
        nonlocal total_docs
        if not batch:
            return
        texts = [item["content"] for item in batch]
        embeddings = embed_texts(texts, embedding_endpoint, model, embedding_dim)
        now = datetime.utcnow().isoformat() + "Z"

        if conn is not None and not args.no_postgres and not args.dry_run:
            with conn.cursor() as cur:
                for item, vector in zip(batch, embeddings):
                    doc_id = item["id"]
                    cur.execute(
                        """
                        INSERT INTO vector_documents (id, collection, title, content, embedding, metadata, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW());
                        """,
                        (
                            doc_id,
                            item["collection"],
                            item["title"],
                            item["content"],
                            vector,
                            Json(item["metadata"]),
                        ),
                    )

        qdrant_batches = {}
        for item, vector in zip(batch, embeddings):
            payload = {
                "title": item["title"],
                "content": item["content"],
                "collection": item["collection"],
                "created_at": now,
                "updated_at": now,
            }
            for key, value in item["metadata"].items():
                payload[key] = normalize_payload_value(value)
            point = {
                "id": str(item["id"]),
                "vector": vector,
                "payload": payload,
            }
            qdrant_batches.setdefault(item["collection"], []).append(point)

        if not args.no_qdrant and not args.dry_run:
            for collection_name, points in qdrant_batches.items():
                if collection_name not in created_collections:
                    qdrant_create_collection(qdrant_url, collection_name, embedding_dim)
                    created_collections.add(collection_name)
                qdrant_upsert(qdrant_url, collection_name, points)

        if conn is not None:
            conn.commit()

        total_docs += len(batch)

    def push_documents(iterator):
        batch = []
        for item in iterator:
            content = (item.get("content") or "").strip()
            if not content:
                continue
            doc = {
                "id": uuid.uuid4(),
                "title": item["title"],
                "content": content,
                "collection": item["collection"],
                "metadata": item.get("metadata", {}),
            }
            batch.append(doc)
            if len(batch) >= args.batch_size:
                store_batch(batch)
                batch = []
        if batch:
            store_batch(batch)

    if "chapters" in modes:
        files = sorted(glob.glob(os.path.join(args.data_dir, args.pattern)))
        if files:
            chapter_collection = global_collection if global_collection else None
            push_documents(iter_chapter_docs(
                files,
                args.collection_prefix,
                args.book_id,
                story_id,
                timeline_id,
                chapter_collection,
            ))
        else:
            print("No chapter files found.")

    if "analysis" in modes:
        if analysis_master_path and os.path.exists(analysis_master_path):
            collection = global_collection or "vx_text_qwen3e2b_v1"
            push_documents(iter_analysis_docs(str(analysis_master_path), story_id, timeline_id, collection))
        else:
            print("analysis_master.jsonl not found. Skipping analysis mode.")

    if "subjects" in modes:
        include = parse_list(args.subjects_include)
        if subjects_root and os.path.exists(subjects_root):
            collection = global_collection or "vx_text_qwen3e2b_v1"
            subject_index = build_subject_index(subjects_root)
            push_documents(iter_subject_docs(str(subjects_root), include, story_id, timeline_id, collection, subject_index))
        else:
            print("subjects root not found. Skipping subjects mode.")

    if conn is not None:
        conn.close()

    print(f"Total documents stored: {total_docs}")


if __name__ == "__main__":
    main()
