import argparse
import json
import os
import sys
import uuid
from datetime import datetime

try:
    import psycopg2
except ImportError:
    psycopg2 = None


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
    parser = argparse.ArgumentParser(description="Build inter-collection links using Qdrant search.")
    parser.add_argument("--collections", default="*")
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--threshold", type=float, default=0.75)
    parser.add_argument("--max-points", type=int, default=0)
    parser.add_argument("--output", default="intercollection_links.jsonl")
    parser.add_argument("--store-db", action="store_true")
    return parser.parse_args()


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


def list_collections(base_url):
    data = qdrant_request("GET", f"{base_url}/collections")
    return [item["name"] for item in data.get("result", {}).get("collections", [])]


def scroll_points(base_url, collection, limit=64, max_points=0):
    url = f"{base_url}/collections/{collection}/points/scroll"
    offset = None
    yielded = 0

    while True:
        payload = {
            "limit": limit,
            "with_vectors": True,
            "with_payload": True
        }
        if offset is not None:
            payload["offset"] = offset

        data = qdrant_request("POST", url, payload)
        result = data.get("result", {})
        points = result.get("points", [])

        for point in points:
            yield point
            yielded += 1
            if max_points and yielded >= max_points:
                return

        offset = result.get("next_page_offset")
        if offset is None or not points:
            return


def search_points(base_url, collection, vector, limit, threshold):
    url = f"{base_url}/collections/{collection}/points/search"
    payload = {
        "vector": vector,
        "limit": limit,
        "score_threshold": threshold,
        "with_payload": True
    }
    data = qdrant_request("POST", url, payload)
    return data.get("result", [])


def ensure_link_table(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS intercollection_links (
                link_id UUID PRIMARY KEY,
                source_id UUID NOT NULL,
                source_collection TEXT NOT NULL,
                target_id UUID NOT NULL,
                target_collection TEXT NOT NULL,
                score REAL NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            """
        )
        cur.execute("CREATE INDEX IF NOT EXISTS idx_intercollection_links_source ON intercollection_links(source_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_intercollection_links_target ON intercollection_links(target_id);")
    conn.commit()


def insert_link(conn, link):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO intercollection_links (link_id, source_id, source_collection, target_id, target_collection, score, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW());
            """,
            (
                link["link_id"],
                link["source_id"],
                link["source_collection"],
                link["target_id"],
                link["target_collection"],
                link["score"]
            )
        )


def main():
    load_env([
        os.path.join(os.path.dirname(__file__), ".env"),
        os.path.join(os.path.dirname(__file__), "..", ".env"),
        os.path.join(os.path.dirname(__file__), "..", "vector_mcp", ".env"),
    ])

    args = parse_args()

    qdrant_host = env("QDRANT_HOST", "localhost")
    qdrant_port = int(env("QDRANT_HTTP_PORT", env("QDRANT_PORT", "6333")))
    qdrant_url = f"http://{qdrant_host}:{qdrant_port}"

    collections = [c.strip() for c in args.collections.split(",") if c.strip()] if args.collections != "*" else None
    if collections is None:
        collections = list_collections(qdrant_url)

    if not collections:
        print("No collections found.")
        return

    conn = None
    if args.store_db:
        if psycopg2 is None:
            raise RuntimeError("psycopg2 is required to store links in Postgres")
        db_host = env("VECTOR_DB_HOST", env("DB_HOST", "localhost"))
        db_port = int(env("VECTOR_DB_PORT", env("DB_PORT", "5432")))
        db_name = env("VECTOR_DB_NAME", env("DB_NAME", "exegetos"))
        db_user = env("VECTOR_DB_USER", env("ADMIN_USER", env("AGENT_USER", "vector_admin")))
        db_password = env("VECTOR_DB_PASSWORD", env("ADMIN_PASSWORD", env("AGENT_PASSWORD", "change_me")))
        conn = psycopg2.connect(host=db_host, port=db_port, dbname=db_name, user=db_user, password=db_password)
        ensure_link_table(conn)

    output = open(args.output, "w", encoding="utf-8")
    link_count = 0

    for source_collection in collections:
        target_collections = [c for c in collections if c != source_collection]
        if not target_collections:
            continue

        for point in scroll_points(qdrant_url, source_collection, max_points=args.max_points):
            source_id = str(point.get("id"))
            vector = point.get("vector")
            if vector is None:
                continue

            for target_collection in target_collections:
                results = search_points(qdrant_url, target_collection, vector, args.limit, args.threshold)
                for result in results:
                    target_id = str(result.get("id"))
                    if not target_id:
                        continue

                    link = {
                        "link_id": str(uuid.uuid4()),
                        "source_id": source_id,
                        "source_collection": source_collection,
                        "target_id": target_id,
                        "target_collection": target_collection,
                        "score": result.get("score", 0.0),
                        "created_at": datetime.utcnow().isoformat() + "Z"
                    }

                    output.write(json.dumps(link) + "\n")
                    link_count += 1

                    if conn is not None:
                        insert_link(conn, link)

        if conn is not None:
            conn.commit()

    output.close()

    if conn is not None:
        conn.close()

    print(f"Generated {link_count} inter-collection links")


if __name__ == "__main__":
    main()
