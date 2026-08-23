import argparse
import json
import os
import subprocess
import time
from pathlib import Path

from visionexe_paths import load_story_config, resolve_path


ROOT_PATH = Path(__file__).resolve().parent
DEFAULT_REGISTRY = ROOT_PATH / "asset_registry.json"
DEFAULT_ENV_BRIDGE = ROOT_PATH / "environment_bridge.json"

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
SUBJECT_PREFIXES = ("CHAR_", "PROP_", "REQ_", "ENV_", "SETENV_", "GEOENV_")


def log(message: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {message}")


def load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


class SimpleMcpClient:
    def __init__(
        self,
        *,
        command: str,
        args: list[str],
        cwd: str | None,
        debug_log: Path | None = None,
    ) -> None:
        stderr_target = subprocess.DEVNULL
        if debug_log is not None:
            debug_log.parent.mkdir(parents=True, exist_ok=True)
            stderr_target = debug_log.open("a", encoding="utf-8")
        self._stderr_handle = stderr_target if hasattr(stderr_target, "write") else None
        self._proc = subprocess.Popen(
            [command, *args],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=stderr_target,
            cwd=cwd,
            text=True,
            encoding="utf-8",
            bufsize=1,
        )
        self._next_id = 0
        self._tools: list[str] = []
        self._initialize()

    def _initialize(self) -> None:
        response = self._request(
            "initialize",
            {
                "protocolVersion": "2025-11-25",
                "capabilities": {},
                "clientInfo": {"name": "visionexe-asset-registry-sync", "version": "0.1.0"},
            },
        )
        if "error" in response:
            raise RuntimeError(f"MCP initialize failed: {response['error']}")
        self._notify("notifications/initialized", {})
        self._load_tools()

    def _load_tools(self) -> None:
        response = self._request("tools/list", {})
        if "error" in response:
            return
        tools = response.get("result", {}).get("tools", [])
        self._tools = [tool.get("name") for tool in tools if tool.get("name")]

    def close(self) -> None:
        if self._proc.stdin:
            try:
                self._proc.stdin.close()
            except OSError:
                pass
        try:
            self._proc.terminate()
            self._proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            try:
                self._proc.kill()
                self._proc.wait(timeout=5)
            except OSError:
                pass
        except OSError:
            pass
        if self._stderr_handle is not None:
            try:
                self._stderr_handle.close()
            except OSError:
                pass

    def call_tool(self, name: str, arguments: dict) -> dict:
        response = self._request("tools/call", {"name": name, "arguments": arguments})
        if "error" in response:
            raise RuntimeError(f"MCP tool {name} failed: {response['error']}")
        return response.get("result", {})

    def _notify(self, method: str, params: dict) -> None:
        self._send({"jsonrpc": "2.0", "method": method, "params": params})

    def _request(self, method: str, params: dict) -> dict:
        self._next_id += 1
        request_id = self._next_id
        self._send({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params})
        while True:
            line = self._read_line()
            if line is None:
                raise RuntimeError("MCP server closed stdout unexpectedly.")
            if not line.strip().startswith("{"):
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if payload.get("id") == request_id:
                return payload

    def _send(self, payload: dict) -> None:
        if not self._proc.stdin:
            raise RuntimeError("MCP server stdin unavailable.")
        self._proc.stdin.write(json.dumps(payload, ensure_ascii=False) + "\n")
        self._proc.stdin.flush()

    def _read_line(self) -> str | None:
        if not self._proc.stdout:
            return None
        return self._proc.stdout.readline()


def tool_text_to_json(result: dict) -> dict:
    content = result.get("content") or []
    text = ""
    for part in content:
        if isinstance(part, dict) and "text" in part:
            text += part["text"]
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"raw": text}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync asset_registry.json into MCP.")
    parser.add_argument("--story-root", help="Story root path (defaults to engine_config default_story_root).")
    parser.add_argument("--story-config", help="Path to story_config.json (overrides story-root).")
    parser.add_argument("--asset-registry", help="Path to asset_registry.json.")
    parser.add_argument("--env-bridge", help="Path to environment_bridge.json.")
    parser.add_argument("--asset-root", help="Base path for relative asset files.")
    parser.add_argument("--collection", help="Qdrant collection override.")
    parser.add_argument("--max-assets", type=int, default=0)
    parser.add_argument("--replace-documents", action="store_true", help="Delete existing documents by title.")
    parser.add_argument("--skip-asset-sets", action="store_true", help="Skip creating asset sets.")
    parser.add_argument("--skip-documents", action="store_true", help="Skip writing asset registry documents.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--mcp-command", default="dotnet")
    parser.add_argument(
        "--mcp-args",
        nargs="*",
        default=[
            "run",
            "--project",
            str(ROOT_PATH.parents[1] / "tools" / "exevision" / "vector_mcp" / "VectorMcpServer"),
        ],
    )
    parser.add_argument(
        "--mcp-cwd",
        default=str(ROOT_PATH.parents[1] / "tools" / "exevision" / "vector_mcp" / "VectorMcpServer"),
    )
    parser.add_argument("--mcp-debug-log", default=None)
    return parser.parse_args()


def normalize_collection(value: str | None) -> str:
    if value:
        return value
    return os.environ.get("QDRANT_TEXT_COLLECTION") or os.environ.get("QDRANT_COLLECTION") or "vx_text_qwen3e2b_v1"


def is_subject_asset(asset_id: str) -> bool:
    return asset_id.startswith(SUBJECT_PREFIXES)


def infer_mime(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in IMAGE_EXTS:
        return f"image/{suffix.lstrip('.')}"
    if suffix == ".safetensors":
        return "application/octet-stream"
    if suffix == ".json":
        return "application/json"
    return "application/octet-stream"


def resolve_asset_path(base_path: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return base_path / path


def maybe_delete_document(
    client: SimpleMcpClient,
    *,
    collection: str,
    title: str,
    dry_run: bool,
) -> None:
    if dry_run:
        log(f"[dry-run] delete_document_by_title -> {collection} :: {title}")
        return
    result = client.call_tool("delete_document_by_title", {"collection": collection, "title": title})
    payload = tool_text_to_json(result)
    if not payload.get("success"):
        log(f"DeleteDocumentByTitle failed: {payload}")


def store_document(
    client: SimpleMcpClient,
    *,
    collection: str,
    title: str,
    content: dict,
    metadata: dict,
    dry_run: bool,
) -> None:
    if dry_run:
        log(f"[dry-run] store_document -> {collection} :: {title}")
        return
    client.call_tool(
        "store_document",
        {
            "collection": collection,
            "title": title,
            "content": json.dumps(content, ensure_ascii=False, indent=2),
            "metadata": json.dumps(metadata, ensure_ascii=False),
        },
    )


def store_artifact(
    client: SimpleMcpClient,
    *,
    story_id: str,
    timeline_id: str | None,
    unit_ref: str,
    kind: str,
    storage_path: str,
    size_bytes: int | None,
    mime: str,
    metadata: dict,
    dry_run: bool,
) -> str | None:
    if dry_run:
        log(f"[dry-run] store_artifact -> {storage_path}")
        return None
    result = client.call_tool(
        "store_artifact",
        {
            "kind": kind,
            "storagePath": storage_path,
            "mime": mime,
            "sizeBytes": size_bytes,
            "storyId": story_id,
            "timelineId": timeline_id,
            "unitRef": unit_ref,
            "metadata": json.dumps(metadata, ensure_ascii=False),
        },
    )
    payload = tool_text_to_json(result)
    return payload.get("artifact_id")


def create_asset_set(
    client: SimpleMcpClient,
    *,
    story_id: str,
    timeline_id: str | None,
    subject_id: str | None,
    label: str,
    set_type: str,
    variant: str | None,
    metadata: dict,
    dry_run: bool,
) -> str | None:
    if dry_run:
        log(f"[dry-run] create_asset_set -> {subject_id} {set_type}")
        return None
    result = client.call_tool(
        "create_asset_set",
        {
            "storyId": story_id,
            "timelineId": timeline_id,
            "subjectId": subject_id,
            "label": label,
            "setType": set_type,
            "variant": variant,
            "metadata": json.dumps(metadata, ensure_ascii=False),
        },
    )
    payload = tool_text_to_json(result)
    return payload.get("set_id")


def add_asset_to_set(
    client: SimpleMcpClient,
    *,
    set_id: str,
    artifact_id: str,
    role: str,
    ordinal: int,
    metadata: dict,
    dry_run: bool,
) -> None:
    if dry_run:
        log(f"[dry-run] add_asset_to_set -> {set_id} :: {artifact_id}")
        return
    client.call_tool(
        "add_asset_to_set",
        {
            "setId": set_id,
            "artifactId": artifact_id,
            "role": role,
            "ordinal": ordinal,
            "metadata": json.dumps(metadata, ensure_ascii=False),
        },
    )


def link_subject_asset_set(
    client: SimpleMcpClient,
    *,
    subject_id: str,
    set_id: str,
    variant: str | None,
    metadata: dict,
    dry_run: bool,
) -> None:
    if dry_run:
        log(f"[dry-run] link_subject_asset_set -> {subject_id} :: {set_id}")
        return
    try:
        client.call_tool(
            "link_subject_asset_set",
            {
                "subjectId": subject_id,
                "setId": set_id,
                "variant": variant,
                "metadata": json.dumps(metadata, ensure_ascii=False),
            },
        )
    except RuntimeError as exc:
        log(f"LinkSubjectAssetSet failed for {subject_id}: {exc}")


def main() -> None:
    args = parse_args()
    story_config, _, repo_root = load_story_config(
        story_root=args.story_root,
        story_config_path=args.story_config,
    )

    story_id = story_config.get("story_id") or "story"
    timeline_id = story_config.get("timeline_default") or story_config.get("timeline_id")
    collection = normalize_collection(args.collection)

    registry_path = resolve_path(args.asset_registry or str(DEFAULT_REGISTRY), repo_root)
    env_bridge_path = resolve_path(args.env_bridge or str(DEFAULT_ENV_BRIDGE), repo_root)
    asset_root = resolve_path(args.asset_root or str(ROOT_PATH), repo_root)

    registry_payload = load_json(registry_path)
    if not registry_payload:
        raise SystemExit(f"asset_registry.json not found at {registry_path}")

    env_bridge_payload = load_json(env_bridge_path)
    env_bridge_entries = []
    if env_bridge_payload and isinstance(env_bridge_payload.get("bridge"), list):
        env_bridge_entries = env_bridge_payload.get("bridge", [])

    assets = registry_payload.get("assets") or []
    if args.max_assets:
        assets = assets[: args.max_assets]

    debug_log = Path(args.mcp_debug_log) if args.mcp_debug_log else None
    client = SimpleMcpClient(
        command=args.mcp_command,
        args=args.mcp_args,
        cwd=args.mcp_cwd,
        debug_log=debug_log,
    )

    try:
        for asset in assets:
            asset_id = asset.get("id")
            if not asset_id:
                continue
            title = f"asset registry {asset_id}"
            metadata = {
                "doc_kind": "asset_registry",
                "story_id": story_id,
                "timeline_id": timeline_id,
                "owner_kind": "subject",
                "owner_id": asset_id,
                "asset_id": asset_id,
                "asset_category": asset.get("category"),
                "asset_category_slug": asset.get("category_slug"),
                "asset_bible_dir": asset.get("asset_bible_dir"),
                "has_outputs": bool(asset.get("asset_bible_outputs")),
                "has_lora": bool(asset.get("lora_files")),
                "has_training": bool(asset.get("training")),
            }

            if not args.skip_documents:
                if args.replace_documents:
                    maybe_delete_document(client, collection=collection, title=title, dry_run=args.dry_run)
                store_document(
                    client,
                    collection=collection,
                    title=title,
                    content=asset,
                    metadata=metadata,
                    dry_run=args.dry_run,
                )

            if args.skip_asset_sets:
                continue

            unit_ref = f"{story_id}:asset:{asset_id}"
            outputs = asset.get("asset_bible_outputs") or []
            if outputs:
                set_id = create_asset_set(
                    client,
                    story_id=story_id,
                    timeline_id=timeline_id,
                    subject_id=asset_id if is_subject_asset(asset_id) else None,
                    label=f"{asset_id} asset_bible_outputs",
                    set_type="asset_bible_outputs",
                    variant="generated",
                    metadata={"asset_id": asset_id, "source": "asset_registry_sync"},
                    dry_run=args.dry_run,
                )
                if set_id:
                    for idx, raw_path in enumerate(outputs):
                        path_obj = resolve_asset_path(asset_root, raw_path)
                        size_bytes = None
                        if path_obj.exists():
                            try:
                                size_bytes = path_obj.stat().st_size
                            except OSError:
                                size_bytes = None
                        mime = infer_mime(path_obj)
                        artifact_id = store_artifact(
                            client,
                            story_id=story_id,
                            timeline_id=timeline_id,
                            unit_ref=unit_ref,
                            kind="image" if path_obj.suffix.lower() in IMAGE_EXTS else "file",
                            storage_path=str(raw_path),
                            size_bytes=size_bytes,
                            mime=mime,
                            metadata={"asset_id": asset_id, "asset_role": "asset_bible_output"},
                            dry_run=args.dry_run,
                        )
                        if artifact_id:
                            add_asset_to_set(
                                client,
                                set_id=set_id,
                                artifact_id=artifact_id,
                                role="image",
                                ordinal=idx,
                                metadata={"asset_id": asset_id},
                                dry_run=args.dry_run,
                            )
                    if is_subject_asset(asset_id):
                        link_subject_asset_set(
                            client,
                            subject_id=asset_id,
                            set_id=set_id,
                            variant="generated",
                            metadata={"asset_id": asset_id},
                            dry_run=args.dry_run,
                        )

            loras = asset.get("lora_files") or []
            if loras:
                set_id = create_asset_set(
                    client,
                    story_id=story_id,
                    timeline_id=timeline_id,
                    subject_id=asset_id if is_subject_asset(asset_id) else None,
                    label=f"{asset_id} lora_files",
                    set_type="lora_files",
                    variant="training",
                    metadata={"asset_id": asset_id, "source": "asset_registry_sync"},
                    dry_run=args.dry_run,
                )
                if set_id:
                    for idx, raw_path in enumerate(loras):
                        path_obj = resolve_asset_path(asset_root, raw_path)
                        size_bytes = None
                        if path_obj.exists():
                            try:
                                size_bytes = path_obj.stat().st_size
                            except OSError:
                                size_bytes = None
                        artifact_id = store_artifact(
                            client,
                            story_id=story_id,
                            timeline_id=timeline_id,
                            unit_ref=unit_ref,
                            kind="lora",
                            storage_path=str(raw_path),
                            size_bytes=size_bytes,
                            mime="application/octet-stream",
                            metadata={"asset_id": asset_id, "asset_role": "lora"},
                            dry_run=args.dry_run,
                        )
                        if artifact_id:
                            add_asset_to_set(
                                client,
                                set_id=set_id,
                                artifact_id=artifact_id,
                                role="lora",
                                ordinal=idx,
                                metadata={"asset_id": asset_id},
                                dry_run=args.dry_run,
                            )
                    if is_subject_asset(asset_id):
                        link_subject_asset_set(
                            client,
                            subject_id=asset_id,
                            set_id=set_id,
                            variant="training",
                            metadata={"asset_id": asset_id},
                            dry_run=args.dry_run,
                        )

        for entry in env_bridge_entries:
            asset_id = entry.get("asset_id")
            if not asset_id:
                continue
            title = f"environment bridge {asset_id}"
            metadata = {
                "doc_kind": "environment_bridge",
                "story_id": story_id,
                "timeline_id": timeline_id,
                "owner_kind": "subject",
                "owner_id": asset_id,
                "asset_id": asset_id,
                "geo_key": entry.get("geo_key"),
                "geo_tag": entry.get("geo_tag"),
            }
            if not args.skip_documents:
                if args.replace_documents:
                    maybe_delete_document(client, collection=collection, title=title, dry_run=args.dry_run)
                store_document(
                    client,
                    collection=collection,
                    title=title,
                    content=entry,
                    metadata=metadata,
                    dry_run=args.dry_run,
                )

        log(f"Synced {len(assets)} asset entries. Env bridge: {len(env_bridge_entries)}.")
    finally:
        client.close()


if __name__ == "__main__":
    main()
