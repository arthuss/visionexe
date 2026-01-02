import json
import os
import urllib.request
import urllib.error

DEFAULT_CONFIG = {
    "qdrant_url": "http://localhost:6335",
    "qdrant_api_key": "",
    "collection": "henoch_chapter_memory",
    "distance": "Cosine",
    "qdrant_timeout_sec": 180,
    "embedding": {
        "endpoint": "http://localhost:11434/api/embeddings",
        "model": "dengcao/Qwen3-Embedding-8B:Q4_K_M",
        "api": "ollama",
        "timeout_sec": 90,
        "api_key": ""
    }
}


def load_config(path):
    config = json.loads(json.dumps(DEFAULT_CONFIG))
    if path and os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
            merge_config(config, payload)
        except (json.JSONDecodeError, OSError):
            pass
    apply_env_overrides(config)
    return config


def merge_config(base, incoming):
    for key, value in incoming.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            merge_config(base[key], value)
        else:
            base[key] = value


def apply_env_overrides(config):
    qdrant_url = os.getenv("RAG_QDRANT_URL")
    if qdrant_url:
        config["qdrant_url"] = qdrant_url
    qdrant_key = os.getenv("RAG_QDRANT_API_KEY")
    if qdrant_key:
        config["qdrant_api_key"] = qdrant_key
    qdrant_timeout = os.getenv("RAG_QDRANT_TIMEOUT_SEC")
    if qdrant_timeout:
        try:
            config["qdrant_timeout_sec"] = int(qdrant_timeout)
        except ValueError:
            pass
    collection = os.getenv("RAG_COLLECTION")
    if collection:
        config["collection"] = collection
    embed_url = os.getenv("RAG_EMBEDDING_URL")
    if embed_url:
        config["embedding"]["endpoint"] = embed_url
    embed_model = os.getenv("RAG_EMBEDDING_MODEL")
    if embed_model:
        config["embedding"]["model"] = embed_model
    embed_key = os.getenv("RAG_EMBEDDING_API_KEY")
    if embed_key:
        config["embedding"]["api_key"] = embed_key
    embed_api = os.getenv("RAG_EMBEDDING_API")
    if embed_api:
        config["embedding"]["api"] = embed_api


def request_json(method, url, payload=None, headers=None, timeout=60):
    data = None
    request_headers = headers.copy() if headers else {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        request_headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=request_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read()
            return response.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as err:
        body = err.read()
        data = {}
        if body:
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                data = {"error": body.decode("utf-8", errors="replace")}
        return err.code, data


def qdrant_headers(config):
    headers = {}
    api_key = config.get("qdrant_api_key") or ""
    if api_key:
        headers["api-key"] = api_key
    return headers


def resolve_embedding_api(config):
    api = (config.get("embedding", {}).get("api") or "").strip().lower()
    if api:
        return api
    endpoint = (config.get("embedding", {}).get("endpoint") or "").lower()
    if "/api/embeddings" in endpoint or "/api/embed" in endpoint:
        return "ollama"
    return "openai"


def embed_texts_openai(config, texts):
    payload = {
        "model": config["embedding"]["model"],
        "input": texts,
    }
    headers = {}
    api_key = config["embedding"].get("api_key") or ""
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    try:
        status, data = request_json(
            "POST",
            config["embedding"]["endpoint"],
            payload,
            headers=headers,
            timeout=config["embedding"].get("timeout_sec", 90),
        )
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Embedding endpoint unreachable: {exc}") from exc
    if status < 200 or status >= 300:
        if status == 400 and "pooling type" in json.dumps(data).lower():
            raise RuntimeError(
                "Embedding API rejected the model (pooling type none). "
                "Use an embedding model like ai/nomic-embed-text-v1.5:latest."
            )
        raise RuntimeError(f"Embedding API error {status}: {data}")
    if isinstance(data, dict) and "data" in data:
        return [item.get("embedding") for item in data["data"]]
    if isinstance(data, dict) and "embeddings" in data:
        return data["embeddings"]
    if isinstance(data, dict) and "embedding" in data:
        return [data["embedding"]]
    raise RuntimeError("Embedding response format not recognized.")


def embed_texts_ollama(config, texts):
    endpoint = config["embedding"]["endpoint"]
    model = config["embedding"]["model"]
    timeout = config["embedding"].get("timeout_sec", 90)
    headers = {}
    api_key = config["embedding"].get("api_key") or ""
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    def parse_single(result):
        if isinstance(result, dict) and "embedding" in result:
            return result["embedding"]
        if isinstance(result, dict) and "data" in result:
            data = result["data"]
            if isinstance(data, list) and data:
                return data[0].get("embedding")
        return None

    outputs = []
    if endpoint.lower().endswith("/api/embed"):
        payload = {"model": model, "input": texts if len(texts) > 1 else texts[0]}
        status, data = request_json("POST", endpoint, payload, headers=headers, timeout=timeout)
        if status < 200 or status >= 300:
            raise RuntimeError(f"Embedding API error {status}: {data}")
        if isinstance(data, dict) and "embeddings" in data:
            return data["embeddings"]
        single = parse_single(data)
        if single:
            return [single]
        raise RuntimeError("Embedding response format not recognized.")

    for text in texts:
        payload = {"model": model, "prompt": text}
        status, data = request_json("POST", endpoint, payload, headers=headers, timeout=timeout)
        if status < 200 or status >= 300:
            raise RuntimeError(f"Embedding API error {status}: {data}")
        vector = parse_single(data)
        if vector is None:
            raise RuntimeError("Embedding response format not recognized.")
        outputs.append(vector)
    return outputs


def embed_texts(config, texts):
    if not texts:
        return []
    api = resolve_embedding_api(config)
    if api == "ollama":
        return embed_texts_ollama(config, texts)
    return embed_texts_openai(config, texts)
