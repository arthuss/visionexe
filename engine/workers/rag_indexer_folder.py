import argparse
import hashlib
import json
import os
import re
import time
import uuid

from rag_utils import load_config, embed_texts, request_json, qdrant_headers

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CHECKPOINT_PATH = os.path.join(ROOT_PATH, "rag_folder_checkpoint.json")
DEFAULT_SKIP_DIRS = {"__pycache__", ".git", ".venv", "venv", "node_modules"}


def read_text(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            return handle.read()
    except OSError:
        return ""


def parse_extensions(value):
    if not value:
        return [".md", ".json", ".txt", ".csv"]
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


def detect_chapter_from_filename(filename):
    stem = os.path.splitext(filename)[0]
    match = re.match(r"^(\d{1,3})(?:$|[^0-9])", stem)
    if not match:
        return ""
    try:
        number = int(match.group(1))
    except ValueError:
        return ""
    if number <= 0:
        return ""
    return f"chapter_{number:03d}"


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


def stable_point_id(payload):
    raw = f"{payload.get('path')}|{payload.get('kind')}|{payload.get('chunk')}"
    return str(uuid.uuid5(uuid.NAMESPACE_URL, raw))


def gather_folder_docs(root_dir, max_chars, overlap, extensions, skip_dirs, infer_chapter):
    docs = []
    root_dir = os.path.abspath(root_dir)
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
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
            chapter_value = detect_chapter_from_filename(filename) if infer_chapter else ""
            payload = {
                "chapter": chapter_value or "global",
                "scene": "",
                "kind": "folder_doc",
                "source": filename,
                "root": root_dir,
                "path": path,
                "path_rel": os.path.relpath(path, root_dir),
                "mtime": os.path.getmtime(path),
                "size": os.path.getsize(path)
            }
            docs.extend(build_document(content, payload, max_chars, overlap))
    return docs


def build_run_signature(config, root_dir, extensions, max_chars, overlap):
    payload = {
        "collection": config.get("collection"),
        "qdrant_url": config.get("qdrant_url"),
        "embedding_model": config.get("embedding", {}).get("model"),
        "embedding_endpoint": config.get("embedding", {}).get("endpoint"),
        "root_dir": os.path.abspath(root_dir),
        "extensions": list(extensions),
        "max_chars": int(max_chars),
        "overlap": int(overlap)
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
    return embed_texts(config, texts)


def main():
    parser = argparse.ArgumentParser(description="Index a folder into Qdrant for RAG.")
    parser.add_argument("--root", required=True, help="Root folder to index")
    parser.add_argument("--config", default=os.path.join(ROOT_PATH, "rag_config_small.json"), help="Config JSON path")
    parser.add_argument("--extensions", default="md,json,txt,csv", help="File extensions to index")
    parser.add_argument("--skip-dir", action="append", help="Directory name to skip (repeatable)")
    parser.add_argument("--max-chars", type=int, default=1800, help="Max characters per chunk")
    parser.add_argument("--overlap", type=int, default=200, help="Overlap between chunks")
    parser.add_argument("--batch-size", type=int, default=8, help="Embedding batch size")
    parser.add_argument("--reset", action="store_true", help="Drop and recreate collection")
    parser.add_argument("--dry-run", action="store_true", help="Only print what would be indexed")
    parser.add_argument("--no-infer-chapter", action="store_true", help="Disable chapter inference from numeric filenames")
    parser.add_argument("--checkpoint-file", default=DEFAULT_CHECKPOINT_PATH, help="Resume checkpoint file path")
    resume_group = parser.add_mutually_exclusive_group()
    resume_group.add_argument("--resume", action="store_true", help="Resume from checkpoint if available (default)")
    resume_group.add_argument("--no-resume", action="store_true", help="Disable resume checkpoint")
    parser.add_argument("--keep-checkpoint", action="store_true", help="Keep checkpoint file after successful run")
    args = parser.parse_args()

    root_dir = args.root
    if not os.path.exists(root_dir):
        print(f"Root not found: {root_dir}")
        return

    config = load_config(args.config)
    extensions = parse_extensions(args.extensions)
    skip_dirs = set(DEFAULT_SKIP_DIRS)
    if args.skip_dir:
        skip_dirs.update({entry.strip() for entry in args.skip_dir if entry.strip()})

    infer_chapter = not args.no_infer_chapter
    documents = gather_folder_docs(root_dir, args.max_chars, args.overlap, extensions, skip_dirs, infer_chapter)

    if args.dry_run:
        print(f"Would index {len(documents)} chunks from {root_dir}.")
        return

    if not documents:
        print("No documents found to index.")
        return

    test_vector = embed_texts(config, ["dimension check"])[0]
    ensure_collection(config, len(test_vector), args.reset)

    resume_enabled = not args.no_resume
    checkpoint_path = args.checkpoint_file
    signature = build_run_signature(config, root_dir, extensions, args.max_chars, args.overlap)
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
                    "root_dir": os.path.abspath(root_dir),
                    "extensions": list(extensions),
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
