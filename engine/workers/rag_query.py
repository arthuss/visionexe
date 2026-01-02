import argparse
import json
import os

from rag_utils import load_config, embed_texts, request_json, qdrant_headers

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))


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


def build_filter(chapter, scene, kind):
    must = []
    if chapter:
        must.append({"key": "chapter", "match": {"value": chapter}})
    if scene:
        must.append({"key": "scene", "match": {"value": scene}})
    if kind:
        must.append({"key": "kind", "match": {"value": kind}})
    if not must:
        return None
    return {"must": must}


def search(config, query, chapter, scene, kind, limit):
    vector = embed_texts(config, [query])[0]
    payload = {
        "vector": vector,
        "limit": limit,
        "with_payload": True
    }
    qfilter = build_filter(chapter, scene, kind)
    if qfilter:
        payload["filter"] = qfilter
    headers = qdrant_headers(config)
    url = f"{config['qdrant_url']}/collections/{config['collection']}/points/search"
    status, data = request_json("POST", url, payload=payload, headers=headers)
    if status < 200 or status >= 300:
        raise RuntimeError(f"Search failed: {status} {data}")
    return data.get("result", [])


def main():
    parser = argparse.ArgumentParser(description="Query chapter memory (Qdrant).")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--chapter", help="Chapter filter (e.g. 96 or chapter_096)")
    parser.add_argument("--scene", help="Scene filter (e.g. 1.1 or 01_01)")
    parser.add_argument("--kind", help="Kind filter (screenplay, analysis, concept, audio_meta, monologue, media, checklist)")
    parser.add_argument("--limit", type=int, default=6, help="Max results")
    parser.add_argument("--config", default=os.path.join(ROOT_PATH, "rag_config.json"), help="Config JSON path")
    parser.add_argument("--json", action="store_true", help="Print raw JSON response")
    args = parser.parse_args()

    config = load_config(args.config)
    chapter = normalize_chapter(args.chapter) if args.chapter else ""
    scene = normalize_scene(args.scene) if args.scene else ""

    results = search(config, args.query, chapter, scene, args.kind, args.limit)

    if args.json:
        print(json.dumps(results, indent=2))
        return

    for idx, hit in enumerate(results, 1):
        payload = hit.get("payload", {})
        snippet = payload.get("text", "").replace("\n", " ")[:200]
        print(f"[{idx}] score={hit.get('score'):.4f} kind={payload.get('kind')} chapter={payload.get('chapter')} scene={payload.get('scene')}")
        print(f"     path={payload.get('path_rel') or payload.get('path')}")
        if snippet:
            print(f"     {snippet}")


if __name__ == "__main__":
    main()
