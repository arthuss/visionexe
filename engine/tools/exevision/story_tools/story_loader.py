import argparse
import glob
import json
import os
import re
import sys
import uuid
from datetime import datetime

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
    parser = argparse.ArgumentParser(description="Load chapter files into Postgres + Qdrant.")
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


def main():
    load_env([
        os.path.join(os.path.dirname(__file__), ".env"),
        os.path.join(os.path.dirname(__file__), "..", ".env"),
        os.path.join(os.path.dirname(__file__), "..", "vector_mcp", ".env"),
    ])

    args = parse_args()

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

    files = sorted(glob.glob(os.path.join(args.data_dir, args.pattern)))
    if not files:
        print("No chapter files found.")
        return

    conn = None
    if not args.no_postgres and not args.dry_run:
        conn = psycopg2.connect(host=db_host, port=db_port, dbname=db_name, user=db_user, password=db_password)
        ensure_schema(conn, embedding_dim)

    total_chunks = 0

    for path in files:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            text = handle.read()

        chapter_id = resolve_chapter_id(path)
        collection = f"{args.collection_prefix}{chapter_id}"
        chunks = split_chunks(text)

        if not chunks:
            continue

        texts = [chunk["text"] for chunk in chunks]
        embeddings = embed_texts(texts, embedding_endpoint, model, embedding_dim)

        now = datetime.utcnow().isoformat() + "Z"
        points = []

        for index, chunk in enumerate(chunks, start=1):
            doc_id = str(uuid.uuid4())
            title = f"{collection} chunk {index}"
            metadata = {
                "book_id": args.book_id,
                "chapter_id": chapter_id,
                "chunk_index": index,
                "verse_id": chunk["verse_id"],
                "source_file": os.path.basename(path)
            }

            if conn is not None and not args.no_postgres and not args.dry_run:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO vector_documents (id, collection, title, content, embedding, metadata, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW());
                        """,
                        (
                            doc_id,
                            collection,
                            title,
                            chunk["text"],
                            embeddings[index - 1],
                            Json(metadata)
                        )
                    )

            point = {
                "id": doc_id,
                "vector": embeddings[index - 1],
                "payload": {
                    "title": title,
                    "content": chunk["text"],
                    "collection": collection,
                    "created_at": now,
                    "updated_at": now,
                    **{k: "" if v is None else str(v) for k, v in metadata.items()}
                }
            }
            points.append(point)

            if len(points) >= args.batch_size:
                if not args.no_qdrant and not args.dry_run:
                    qdrant_create_collection(qdrant_url, collection, embedding_dim)
                    qdrant_upsert(qdrant_url, collection, points)
                points = []

        if points and not args.no_qdrant and not args.dry_run:
            qdrant_create_collection(qdrant_url, collection, embedding_dim)
            qdrant_upsert(qdrant_url, collection, points)

        if conn is not None:
            conn.commit()

        total_chunks += len(chunks)
        print(f"Loaded {len(chunks)} chunks from {os.path.basename(path)}")

    if conn is not None:
        conn.close()

    print(f"Total chunks stored: {total_chunks}")


if __name__ == "__main__":
    main()
