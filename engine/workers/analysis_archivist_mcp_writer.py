import argparse
import json
import re
import subprocess
import time
from pathlib import Path

from visionexe_paths import load_story_config, resolve_path


def log(message: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {message}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Write archivist NDJSON outputs into MCP/Qdrant."
    )
    parser.add_argument("--story-config", default="stories/template/config/story_config.json")
    parser.add_argument("--input-dir", help="Directory containing archivist NDJSON outputs.")
    parser.add_argument("--input-file", help="Single archivist NDJSON file to write.")
    parser.add_argument("--input-glob", default="archivist_*.jsonl", help="Glob for input files.")
    parser.add_argument("--analysis-type", help="Override analysis type.")
    parser.add_argument("--mcp-command")
    parser.add_argument("--mcp-args", nargs="*")
    parser.add_argument("--mcp-cwd")
    parser.add_argument("--mcp-debug-log")
    parser.add_argument(
        "--thinking-from-segments",
        action="store_true",
        help="Attach per-segment thinking sidecar files as separate artifacts.",
    )
    parser.add_argument(
        "--attach-segment-artifacts",
        action="store_true",
        help="Attach segment.txt, segment_meta.json, and raw analysis as artifacts.",
    )
    parser.add_argument(
        "--attach-segment-text",
        action="store_true",
        help="Attach segment.txt as an artifact.",
    )
    parser.add_argument(
        "--attach-segment-meta",
        action="store_true",
        help="Attach segment_meta.json as an artifact.",
    )
    parser.add_argument(
        "--attach-analysis-raw",
        action="store_true",
        help="Attach analysis_llm_<type>.txt as an artifact.",
    )
    parser.add_argument(
        "--analysis-source",
        choices=["auto", "local", "adk"],
        default="auto",
        help="Tag analysis source (auto|local|adk).",
    )
    parser.add_argument(
        "--dedupe-priority",
        choices=["local", "adk"],
        default="local",
        help="When a segment exists, keep this source and skip/replace the other.",
    )
    parser.add_argument(
        "--no-dedupe",
        action="store_true",
        help="Disable duplicate checks before writing.",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def load_json(path: Path) -> dict:
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
                "clientInfo": {"name": "visionexe-archivist-writer", "version": "0.1.0"},
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


def parse_ndjson(path: Path) -> tuple[dict, list[dict], dict | None]:
    header: dict = {}
    records: list[dict] = []
    footer: dict | None = None
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        entry_type = payload.get("type")
        if entry_type == "header":
            header = payload
        elif entry_type == "footer":
            footer = payload
        elif entry_type == "record":
            records.append(payload)
    return header, records, footer


def derive_segment_label(payload: dict) -> str | None:
    if "segment_label" in payload:
        value = str(payload.get("segment_label")).strip()
        return value or None
    source = payload.get("source") if isinstance(payload.get("source"), dict) else None
    witness_id = None
    if source and source.get("witness_id"):
        witness_id = str(source.get("witness_id"))
    if not witness_id and payload.get("witness_id"):
        witness_id = str(payload.get("witness_id"))
    if witness_id:
        match = re.search(r"(segment_[^/]+)", witness_id)
        if match:
            return match.group(1)
    return None


def derive_chapter_id(payload: dict, header: dict) -> str | None:
    if header.get("chapter_id"):
        return str(header.get("chapter_id"))
    if payload.get("chapter_id"):
        return str(payload.get("chapter_id"))
    source = payload.get("source") if isinstance(payload.get("source"), dict) else None
    witness_id = None
    if source and source.get("witness_id"):
        witness_id = str(source.get("witness_id"))
    if witness_id:
        match = re.search(r"chapter[_-]?(\d+)", witness_id)
        if match:
            return match.group(1)
    return None


def infer_analysis_source(header: dict, input_path: Path, override: str) -> str:
    if override and override != "auto":
        return override
    existing = header.get("analysis_source")
    if isinstance(existing, str) and existing.strip():
        return existing.strip()
    source_path = header.get("source_path") or str(input_path)
    source_name = Path(str(source_path)).name
    if source_name.startswith("wal_"):
        return "adk"
    return "local"


def resolve_existing_source(payload: dict) -> str:
    metadata = payload.get("metadata")
    if isinstance(metadata, dict):
        source = metadata.get("analysis_source")
        if isinstance(source, str) and source.strip():
            return source.strip()
    return "unknown"


def get_existing_document(
    mcp: SimpleMcpClient,
    *,
    collection: str,
    title: str,
) -> dict | None:
    result = mcp.call_tool(
        "get_document_by_title",
        {"collection": collection, "title": title},
    )
    payload = tool_text_to_json(result)
    if payload.get("found"):
        return payload
    return None


def delete_existing_document(
    mcp: SimpleMcpClient,
    *,
    collection: str,
    title: str,
    dry_run: bool,
) -> bool:
    if dry_run:
        log(f"[dry-run] delete_document_by_title -> {collection} :: {title}")
        return True
    result = mcp.call_tool(
        "delete_document_by_title",
        {"collection": collection, "title": title},
    )
    payload = tool_text_to_json(result)
    return bool(payload.get("success"))


def collection_for_analysis(analysis_type: str) -> str:
    if analysis_type.startswith("analysis_"):
        return analysis_type
    return f"analysis_{analysis_type}"


def thinking_filename_for_analysis(analysis_type: str) -> str:
    normalized = analysis_type.replace("-", "_")
    return f"analysis_llm_{normalized}.thinking.txt"


def analysis_filename_for_type(analysis_type: str) -> str:
    normalized = analysis_type.replace("-", "_")
    return f"analysis_llm_{normalized}.txt"


def resolve_segment_dir(
    *,
    segments_root: Path | None,
    chapter_label: str,
    chapter_id: str | None,
    segment_label: str | None,
) -> Path | None:
    if segments_root is None or not chapter_id:
        return None
    chapter_dir = segments_root / f"{chapter_label}_{chapter_id}"
    target_dir = chapter_dir / segment_label if segment_label else chapter_dir
    return target_dir if target_dir.exists() else None


def resolve_thinking_path(
    *,
    segments_root: Path | None,
    chapter_label: str,
    chapter_id: str | None,
    segment_label: str | None,
    analysis_type: str,
) -> Path | None:
    if segments_root is None or not chapter_id:
        return None
    chapter_dir = segments_root / f"{chapter_label}_{chapter_id}"
    target_dir = chapter_dir / segment_label if segment_label else chapter_dir
    candidate = target_dir / thinking_filename_for_analysis(analysis_type)
    return candidate if candidate.exists() else None


def resolve_segment_text_path(
    *,
    segments_root: Path | None,
    chapter_label: str,
    chapter_id: str | None,
    segment_label: str | None,
) -> Path | None:
    target_dir = resolve_segment_dir(
        segments_root=segments_root,
        chapter_label=chapter_label,
        chapter_id=chapter_id,
        segment_label=segment_label,
    )
    if not target_dir:
        return None
    candidate = target_dir / "segment.txt"
    return candidate if candidate.exists() else None


def resolve_segment_meta_path(
    *,
    segments_root: Path | None,
    chapter_label: str,
    chapter_id: str | None,
    segment_label: str | None,
    meta_name: str = "segment_meta.json",
) -> Path | None:
    target_dir = resolve_segment_dir(
        segments_root=segments_root,
        chapter_label=chapter_label,
        chapter_id=chapter_id,
        segment_label=segment_label,
    )
    if not target_dir:
        return None
    candidate = target_dir / meta_name
    return candidate if candidate.exists() else None


def resolve_analysis_raw_path(
    *,
    segments_root: Path | None,
    chapter_label: str,
    chapter_id: str | None,
    segment_label: str | None,
    analysis_type: str,
) -> Path | None:
    target_dir = resolve_segment_dir(
        segments_root=segments_root,
        chapter_label=chapter_label,
        chapter_id=chapter_id,
        segment_label=segment_label,
    )
    if not target_dir:
        return None
    candidate = target_dir / analysis_filename_for_type(analysis_type)
    return candidate if candidate.exists() else None


def store_thinking_artifact(
    mcp: SimpleMcpClient,
    *,
    story_id: str,
    run_id: str | None,
    analysis_type: str,
    unit_ref: str,
    metadata: dict,
    thinking_text: str,
    dry_run: bool,
) -> None:
    if not thinking_text:
        return
    thinking_unit_ref = f"{unit_ref}:thinking"
    thinking_role = f"{collection_for_analysis(analysis_type)}_thinking"
    if dry_run:
        log(f"[dry-run] store_artifact(thinking) -> {thinking_unit_ref}")
        return
    artifact_result = mcp.call_tool(
        "store_artifact",
        {
            "kind": "analysis_thinking",
            "content": thinking_text,
            "mime": "text/plain",
            "runId": run_id,
            "storyId": story_id,
            "unitRef": thinking_unit_ref,
            "metadata": json.dumps(metadata, ensure_ascii=False),
        },
    )
    artifact_payload = tool_text_to_json(artifact_result)
    artifact_id = artifact_payload.get("artifact_id")
    if not artifact_id:
        raise RuntimeError(f"StoreArtifact(thinking) did not return artifact_id: {artifact_payload}")
    if run_id:
        mcp.call_tool(
            "link_run_output",
            {
                "runId": run_id,
                "artifactId": artifact_id,
                "role": thinking_role,
                "metadata": json.dumps({"analysis_type": analysis_type, "kind": "thinking"}, ensure_ascii=False),
            },
        )
    mcp.call_tool(
        "store_document",
        {
            "collection": thinking_role,
            "title": f"{story_id}/{thinking_unit_ref}",
            "content": thinking_text,
            "metadata": json.dumps(
                {**metadata, "analysis_kind": "thinking", "analysis_type": analysis_type},
                ensure_ascii=False,
            ),
        },
    )


def store_segment_artifact(
    mcp: SimpleMcpClient,
    *,
    story_id: str,
    run_id: str | None,
    analysis_type: str,
    unit_ref: str,
    kind: str,
    content: str,
    metadata: dict,
    dry_run: bool,
) -> None:
    if not content:
        return
    segment_unit_ref = f"{unit_ref}:{kind}"
    segment_role = f"{collection_for_analysis(analysis_type)}_{kind}"
    if dry_run:
        log(f"[dry-run] store_artifact({kind}) -> {segment_unit_ref}")
        return
    artifact_result = mcp.call_tool(
        "store_artifact",
        {
            "kind": kind,
            "content": content,
            "mime": "text/plain",
            "runId": run_id,
            "storyId": story_id,
            "unitRef": segment_unit_ref,
            "metadata": json.dumps(metadata, ensure_ascii=False),
        },
    )
    artifact_payload = tool_text_to_json(artifact_result)
    artifact_id = artifact_payload.get("artifact_id")
    if not artifact_id:
        raise RuntimeError(f"StoreArtifact({kind}) did not return artifact_id: {artifact_payload}")
    if run_id:
        mcp.call_tool(
            "link_run_output",
            {
                "runId": run_id,
                "artifactId": artifact_id,
                "role": segment_role,
                "metadata": json.dumps({"analysis_type": analysis_type, "kind": kind}, ensure_ascii=False),
            },
        )


def write_record(
    mcp: SimpleMcpClient,
    *,
    story_id: str,
    run_id: str | None,
    analysis_type: str,
    chapter_id: str | None,
    segment_label: str | None,
    batch_index: int | None,
    payload: dict,
    analysis_source: str,
    dedupe_priority: str,
    dedupe_enabled: bool,
    segments_root: Path | None,
    chapter_label: str,
    attach_thinking: bool,
    attach_segment_text: bool,
    attach_segment_meta: bool,
    attach_analysis_raw: bool,
    dry_run: bool,
) -> None:
    analysis_collection = collection_for_analysis(analysis_type)
    collection = analysis_collection
    unit_ref_label = segment_label or (f"batch_{batch_index:03d}" if batch_index is not None else "batch_000")
    unit_ref = f"{story_id}:chapter_{chapter_id or 'unknown'}:{unit_ref_label}"

    metadata = {
        "story_id": story_id,
        "analysis_type": analysis_type,
        "chapter_id": chapter_id,
        "segment_label": segment_label,
        "unit_ref": unit_ref,
        "batch_index": batch_index,
        "source": "analysis_archivist_mcp_writer",
        "analysis_source": analysis_source,
    }
    if segment_label is None:
        metadata["archivist_batch"] = True
    content = json.dumps(payload, ensure_ascii=False, indent=2)
    document_title = f"{story_id}/chapter_{chapter_id or 'unknown'}/{unit_ref_label}"

    if dedupe_enabled and not dry_run:
        existing = get_existing_document(
            mcp,
            collection=analysis_collection,
            title=document_title,
        )
        if existing:
            existing_source = resolve_existing_source(existing)
            if existing_source == analysis_source:
                log(f"Skipping existing {analysis_collection} {unit_ref_label} (source={analysis_source}).")
                return
            if dedupe_priority == analysis_source:
                deleted = delete_existing_document(
                    mcp,
                    collection=analysis_collection,
                    title=document_title,
                    dry_run=dry_run,
                )
                if not deleted:
                    log(
                        f"Failed to delete {analysis_collection} {unit_ref_label}; skipping to avoid duplicates."
                    )
                    return
            else:
                log(
                    f"Skipping {analysis_collection} {unit_ref_label}; "
                    f"priority={dedupe_priority}, existing={existing_source}, incoming={analysis_source}."
                )
                return

    if dry_run:
        log(f"[dry-run] store_artifact -> {unit_ref}")
        return

    artifact_result = mcp.call_tool(
        "store_artifact",
        {
            "kind": "analysis",
            "content": content,
            "mime": "application/json",
            "runId": run_id,
            "storyId": story_id,
            "unitRef": unit_ref,
            "metadata": json.dumps(metadata, ensure_ascii=False),
        },
    )
    artifact_payload = tool_text_to_json(artifact_result)
    artifact_id = artifact_payload.get("artifact_id")
    if not artifact_id:
        raise RuntimeError(f"StoreArtifact did not return artifact_id: {artifact_payload}")

    if segment_label:
        mcp.call_tool(
            "store_analysis_artifact",
            {
                "analysisType": analysis_type,
                "unitRef": unit_ref,
                "artifactId": artifact_id,
                "runId": run_id,
                "metadata": json.dumps(metadata, ensure_ascii=False),
            },
        )

    if run_id:
        mcp.call_tool(
            "link_run_output",
            {
                "runId": run_id,
                "artifactId": artifact_id,
                "role": collection,
                "metadata": json.dumps({"analysis_type": analysis_type}, ensure_ascii=False),
            },
        )

    document_metadata = {
        **metadata,
        "analysis_id": artifact_id,
    }
    mcp.call_tool(
        "store_document",
        {
            "collection": collection,
            "title": document_title,
            "content": content,
            "metadata": json.dumps(document_metadata, ensure_ascii=False),
        },
    )

    if attach_thinking:
        thinking_path = resolve_thinking_path(
            segments_root=segments_root,
            chapter_label=chapter_label,
            chapter_id=chapter_id,
            segment_label=segment_label,
            analysis_type=analysis_type,
        )
        if thinking_path:
            try:
                thinking_text = thinking_path.read_text(encoding="utf-8", errors="replace")
            except OSError as exc:
                log(f"Failed to read thinking sidecar {thinking_path}: {exc}")
            else:
                thinking_metadata = {
                    **metadata,
                    "analysis_id": artifact_id,
                    "thinking_path": str(thinking_path),
                }
                store_thinking_artifact(
                    mcp,
                    story_id=story_id,
                    run_id=run_id,
                    analysis_type=analysis_type,
                    unit_ref=unit_ref,
                    metadata=thinking_metadata,
                    thinking_text=thinking_text,
                    dry_run=dry_run,
                )

    if segments_root and (attach_segment_text or attach_segment_meta or attach_analysis_raw):
        segment_metadata = {
            **metadata,
            "analysis_id": artifact_id,
        }
        if attach_segment_text:
            segment_path = resolve_segment_text_path(
                segments_root=segments_root,
                chapter_label=chapter_label,
                chapter_id=chapter_id,
                segment_label=segment_label,
            )
            if segment_path:
                try:
                    segment_text = segment_path.read_text(encoding="utf-8", errors="replace")
                except OSError as exc:
                    log(f"Failed to read segment.txt {segment_path}: {exc}")
                else:
                    store_segment_artifact(
                        mcp,
                        story_id=story_id,
                        run_id=run_id,
                        analysis_type=analysis_type,
                        unit_ref=unit_ref,
                        kind="segment_text",
                        content=segment_text,
                        metadata={**segment_metadata, "segment_path": str(segment_path)},
                        dry_run=dry_run,
                    )
        if attach_segment_meta:
            meta_path = resolve_segment_meta_path(
                segments_root=segments_root,
                chapter_label=chapter_label,
                chapter_id=chapter_id,
                segment_label=segment_label,
            )
            if meta_path:
                try:
                    meta_text = meta_path.read_text(encoding="utf-8", errors="replace")
                except OSError as exc:
                    log(f"Failed to read segment_meta.json {meta_path}: {exc}")
                else:
                    store_segment_artifact(
                        mcp,
                        story_id=story_id,
                        run_id=run_id,
                        analysis_type=analysis_type,
                        unit_ref=unit_ref,
                        kind="segment_meta",
                        content=meta_text,
                        metadata={**segment_metadata, "segment_meta_path": str(meta_path)},
                        dry_run=dry_run,
                    )
        if attach_analysis_raw:
            analysis_raw_path = resolve_analysis_raw_path(
                segments_root=segments_root,
                chapter_label=chapter_label,
                chapter_id=chapter_id,
                segment_label=segment_label,
                analysis_type=analysis_type,
            )
            if analysis_raw_path:
                try:
                    analysis_raw = analysis_raw_path.read_text(encoding="utf-8", errors="replace")
                except OSError as exc:
                    log(f"Failed to read analysis raw {analysis_raw_path}: {exc}")
                else:
                    store_segment_artifact(
                        mcp,
                        story_id=story_id,
                        run_id=run_id,
                        analysis_type=analysis_type,
                        unit_ref=unit_ref,
                        kind="analysis_raw",
                        content=analysis_raw,
                        metadata={**segment_metadata, "analysis_raw_path": str(analysis_raw_path)},
                        dry_run=dry_run,
                    )


def main() -> None:
    args = parse_args()
    story_config, _, repo_root = load_story_config(story_config_path=args.story_config)
    story_id = story_config.get("story_id") or "story"
    chapter_label = story_config.get("chapter_label", "chapter")
    segments_root = None
    attach_segment_text = args.attach_segment_text or args.attach_segment_artifacts
    attach_segment_meta = args.attach_segment_meta or args.attach_segment_artifacts
    attach_analysis_raw = args.attach_analysis_raw or args.attach_segment_artifacts
    if args.thinking_from_segments or attach_segment_text or attach_segment_meta or attach_analysis_raw:
        segments_root = resolve_path(story_config.get("analysis_segments_root"), repo_root)
        if not segments_root:
            log("analysis_segments_root missing; disabling segment/thinking attachments.")
            segments_root = None
            attach_segment_text = False
            attach_segment_meta = False
            attach_analysis_raw = False

    input_paths: list[Path] = []
    if args.input_file:
        input_paths.append(resolve_path(args.input_file, repo_root))
    if args.input_dir:
        input_dir = resolve_path(args.input_dir, repo_root)
        input_paths.extend(sorted(input_dir.glob(args.input_glob)))
    if not input_paths:
        log("No input files provided.")
        return

    vector_mcp_dir = repo_root / "engine" / "tools" / "exevision" / "vector_mcp" / "VectorMcpServer"
    default_exe = vector_mcp_dir / "bin" / "Debug" / "net10.0" / "VectorMcpServer.exe"
    mcp_command = args.mcp_command or (str(default_exe) if default_exe.exists() else "dotnet")
    if args.mcp_args is not None:
        mcp_args = args.mcp_args
    else:
        mcp_args = [] if default_exe.exists() else ["run", "--project", str(vector_mcp_dir)]
    mcp_cwd = args.mcp_cwd or str(vector_mcp_dir)
    debug_log = Path(args.mcp_debug_log) if args.mcp_debug_log else None

    mcp_client = None
    if not args.dry_run:
        mcp_client = SimpleMcpClient(
            command=mcp_command,
            args=mcp_args,
            cwd=mcp_cwd,
            debug_log=debug_log,
        )

    try:
        for ndjson_path in input_paths:
            header, records, _ = parse_ndjson(ndjson_path)
            analysis_type = args.analysis_type or header.get("analysis_type")
            if not analysis_type:
                log(f"Missing analysis_type in {ndjson_path.name}. Skipping.")
                continue
            analysis_source = infer_analysis_source(header, ndjson_path, args.analysis_source)
            chapter_id = header.get("chapter_id")
            run_id = header.get("run_id")
            batch_index = header.get("batch_index")
            if not records:
                log(f"No records found in {ndjson_path.name}.")
                continue
            for record in records:
                payload = record.get("payload") if isinstance(record, dict) else None
                if not isinstance(payload, dict):
                    log(f"Skipping record without payload in {ndjson_path.name}.")
                    continue
                segment_label = derive_segment_label(payload)
                resolved_chapter = derive_chapter_id(payload, header) or chapter_id
                write_record(
                    mcp_client,
                    story_id=story_id,
                    run_id=run_id,
                    analysis_type=analysis_type,
                    chapter_id=resolved_chapter,
                    segment_label=segment_label,
                    batch_index=batch_index,
                    payload=payload,
                    analysis_source=analysis_source,
                    dedupe_priority=args.dedupe_priority,
                    dedupe_enabled=not args.no_dedupe,
                    segments_root=segments_root,
                    chapter_label=chapter_label,
                    attach_thinking=args.thinking_from_segments,
                    attach_segment_text=attach_segment_text,
                    attach_segment_meta=attach_segment_meta,
                    attach_analysis_raw=attach_analysis_raw,
                    dry_run=args.dry_run,
                )
            log(f"Wrote {len(records)} records from {ndjson_path.name}.")
    finally:
        if mcp_client is not None:
            mcp_client.close()


if __name__ == "__main__":
    main()
