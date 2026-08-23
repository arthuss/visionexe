import argparse
import csv
import json
import os
import sys
from pathlib import Path

try:
    import psycopg2
except ImportError:
    print("psycopg2 is required. Install it before running this script.")
    sys.exit(1)


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
    parser = argparse.ArgumentParser(
        description="Check sync between Postgres vector_documents and Qdrant collections."
    )
    parser.add_argument("--collection", default=None, help="Single collection to check.")
    parser.add_argument("--collections", default="*", help="Comma list or * for all.")
    parser.add_argument("--compare-ids", action="store_true", help="Compare IDs when counts are small.")
    parser.add_argument("--max-ids", type=int, default=50000, help="Max IDs per collection for full compare.")
    parser.add_argument("--show-ids", action="store_true", help="Show a sample of missing IDs.")
    parser.add_argument("--show-ids-limit", type=int, default=20)
    parser.add_argument(
        "--dump-path",
        help="Write ids/titles to a file (csv or jsonl). Use {collection} for multi-collection runs.",
    )
    parser.add_argument("--dump-format", choices=["csv", "jsonl"], default="csv")
    parser.add_argument("--dump-source", choices=["pg", "qdrant"], default="pg")
    parser.add_argument("--dump-limit", type=int, default=0, help="Limit rows written (0 = all).")
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


def list_qdrant_collections(base_url):
    data = qdrant_request("GET", f"{base_url}/collections")
    return [item["name"] for item in data.get("result", {}).get("collections", [])]


def qdrant_count(base_url, collection):
    payload = {"exact": True}
    data = qdrant_request("POST", f"{base_url}/collections/{collection}/points/count", payload)
    return data.get("result", {}).get("count")


def qdrant_iter_ids(base_url, collection, limit=512):
    url = f"{base_url}/collections/{collection}/points/scroll"
    offset = None
    while True:
        payload = {
            "limit": limit,
            "with_payload": False,
            "with_vectors": False,
        }
        if offset is not None:
            payload["offset"] = offset
        data = qdrant_request("POST", url, payload)
        result = data.get("result", {})
        points = result.get("points", [])
        for point in points:
            point_id = point.get("id")
            if point_id is not None:
                yield str(point_id)
        offset = result.get("next_page_offset")
        if offset is None or not points:
            return


def qdrant_iter_points(base_url, collection, limit=512):
    url = f"{base_url}/collections/{collection}/points/scroll"
    offset = None
    while True:
        payload = {
            "limit": limit,
            "with_payload": True,
            "with_vectors": False,
        }
        if offset is not None:
            payload["offset"] = offset
        data = qdrant_request("POST", url, payload)
        result = data.get("result", {})
        points = result.get("points", [])
        for point in points:
            yield point
        offset = result.get("next_page_offset")
        if offset is None or not points:
            return


def list_pg_collections(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT DISTINCT collection FROM vector_documents ORDER BY collection;")
        return [row[0] for row in cur.fetchall()]


def pg_count(conn, collection):
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM vector_documents WHERE collection = %s;", (collection,))
        return int(cur.fetchone()[0])


def pg_ids(conn, collection):
    with conn.cursor() as cur:
        cur.execute("SELECT id::text FROM vector_documents WHERE collection = %s;", (collection,))
        return {row[0] for row in cur.fetchall()}


def dump_pg(conn, collection, path, fmt, limit):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with conn.cursor() as cur:
        if limit and limit > 0:
            cur.execute(
                "SELECT id::text, title, collection FROM vector_documents WHERE collection = %s ORDER BY title LIMIT %s;",
                (collection, limit),
            )
        else:
            cur.execute(
                "SELECT id::text, title, collection FROM vector_documents WHERE collection = %s ORDER BY title;",
                (collection,),
            )
        rows = cur.fetchall()

    if fmt == "jsonl":
        with path.open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps({"id": row[0], "title": row[1], "collection": row[2]}, ensure_ascii=False) + "\n")
        return len(rows)

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["id", "title", "collection"])
        for row in rows:
            writer.writerow(row)
    return len(rows)


def dump_qdrant(base_url, collection, path, fmt, limit):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0

    if fmt == "csv":
        handle = path.open("w", encoding="utf-8", newline="")
        writer = csv.writer(handle)
        writer.writerow(["id", "title", "collection"])
    else:
        handle = path.open("w", encoding="utf-8")
        writer = None

    try:
        for point in qdrant_iter_points(base_url, collection):
            point_id = point.get("id")
            payload = point.get("payload") or {}
            title = payload.get("title") or ""
            collection_value = payload.get("collection") or collection
            if fmt == "jsonl":
                handle.write(
                    json.dumps(
                        {
                            "id": str(point_id),
                            "title": title,
                            "collection": collection_value,
                            "payload": payload,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
            else:
                writer.writerow([str(point_id), title, collection_value])
            count += 1
            if limit and count >= limit:
                break
    finally:
        handle.close()
    return count


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

    conn = psycopg2.connect(host=db_host, port=db_port, dbname=db_name, user=db_user, password=db_password)
    try:
        pg_collections = list_pg_collections(conn)
    except Exception as exc:
        conn.close()
        raise RuntimeError(f"Failed to read Postgres collections: {exc}") from exc

    try:
        qdrant_collections = list_qdrant_collections(qdrant_url)
    except Exception as exc:
        conn.close()
        raise RuntimeError(f"Failed to read Qdrant collections: {exc}") from exc

    if args.collection:
        collections = [args.collection]
    else:
        if args.collections.strip() == "*":
            collections = sorted(set(pg_collections) | set(qdrant_collections))
        else:
            collections = [item.strip() for item in args.collections.split(",") if item.strip()]

    if not collections:
        print("No collections to check.")
        conn.close()
        return

    only_pg = sorted(set(pg_collections) - set(qdrant_collections))
    only_qdrant = sorted(set(qdrant_collections) - set(pg_collections))
    if args.collections.strip() == "*":
        if only_pg:
            print(f"PG only: {', '.join(only_pg)}")
        if only_qdrant:
            print(f"Qdrant only: {', '.join(only_qdrant)}")

    for collection in collections:
        pg_total = pg_count(conn, collection)
        qdrant_total = None
        if collection in qdrant_collections:
            qdrant_total = qdrant_count(qdrant_url, collection)
        status = "OK"
        if qdrant_total is None:
            status = "MISSING_QDRANT"
        elif pg_total != qdrant_total:
            status = "COUNT_MISMATCH"
        print(f"{collection}: pg={pg_total} qdrant={qdrant_total} status={status}")

        if not args.compare_ids:
            continue
        if qdrant_total is None:
            continue
        if pg_total > args.max_ids or qdrant_total > args.max_ids:
            print(f"  skip id compare (count too large; use --max-ids to override)")
            continue

        pg_set = pg_ids(conn, collection)
        qdrant_set = set(qdrant_iter_ids(qdrant_url, collection))
        missing_qdrant = sorted(pg_set - qdrant_set)
        missing_pg = sorted(qdrant_set - pg_set)
        print(f"  missing in Qdrant: {len(missing_qdrant)}")
        print(f"  missing in PG: {len(missing_pg)}")
        if args.show_ids:
            if missing_qdrant:
                print("  sample missing in Qdrant:")
                for item in missing_qdrant[: args.show_ids_limit]:
                    print(f"    {item}")
            if missing_pg:
                print("  sample missing in PG:")
                for item in missing_pg[: args.show_ids_limit]:
                    print(f"    {item}")

        if args.dump_path:
            dump_target = args.dump_path
            if "{collection}" in dump_target:
                dump_target = dump_target.replace("{collection}", collection)
            elif len(collections) > 1:
                raise RuntimeError("Use {collection} in --dump-path when checking multiple collections.")
            if args.dump_source == "pg":
                written = dump_pg(conn, collection, dump_target, args.dump_format, args.dump_limit)
            else:
                if collection not in qdrant_collections:
                    print("  skip dump: collection missing in Qdrant")
                    continue
                written = dump_qdrant(qdrant_url, collection, dump_target, args.dump_format, args.dump_limit)
            print(f"  dumped {written} rows -> {dump_target}")

    conn.close()


if __name__ == "__main__":
    main()
