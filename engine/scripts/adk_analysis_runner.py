import argparse
import json
import re
import sys
import time
import subprocess
from dataclasses import dataclass
import urllib.error
import urllib.request
import uuid
import random
from pathlib import Path
from xml.sax.saxutils import escape
from xml.etree import ElementTree as ET

ENGINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE_ROOT))

from workers.visionexe_paths import load_story_config, resolve_path  # noqa: E402


LINE_RE = re.compile(r"^\s*(\d+)\s*:\s*(\d+)\s+(.*)$")


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_pos_tags(engine_root: Path) -> list[dict]:
    tagset_path = engine_root / "config" / "gez_pos_tagset.json"
    if not tagset_path.exists():
        return []
    data = load_json(tagset_path)
    return data.get("tags", [])


def load_function_words(engine_root: Path) -> list[dict]:
    words_path = engine_root / "config" / "gez_function_words.json"
    if not words_path.exists():
        return []
    data = load_json(words_path)
    return data.get("function_words", [])


def load_geo_env_catalog(story_config: dict, repo_root: Path) -> dict:
    env_root = story_config.get("environments_root")
    if not env_root:
        return {}
    env_root = resolve_path(env_root, repo_root)
    for name in ("geo_env_catalog.json", "geo_environments.json"):
        candidate = env_root / name
        if candidate.exists():
            return load_json(candidate)
    return {}


def load_analysis_schemas(schema_path: Path) -> dict:
    if not schema_path.exists():
        warn(f"Analysis schema config not found: {schema_path}")
        return {}
    try:
        data = load_json(schema_path)
    except (OSError, json.JSONDecodeError) as exc:
        warn(f"Failed to load analysis schema config: {exc}")
        return {}
    return data.get("analysis_types", {})


def write_wal_entry(
    wal_dir: Path,
    *,
    story_id: str,
    run_id: str | None,
    analysis_type: str,
    chapter_id: str,
    batch_index: int,
    attempt: int,
    input_types: list[str] | None,
    chunks: list[str],
) -> Path:
    wal_dir.mkdir(parents=True, exist_ok=True)
    wal_id = uuid.uuid4().hex[:8]
    wal_path = wal_dir / (
        f"wal_{analysis_type}_chapter_{chapter_id}_batch_{batch_index:03d}_"
        f"attempt_{attempt:02d}_{wal_id}.jsonl"
    )
    raw_text = "\n---\n".join(chunks)
    header = {
        "type": "header",
        "schema_version": "1.0.0",
        "story_id": story_id,
        "run_id": run_id,
        "analysis_type": analysis_type,
        "chapter_id": chapter_id,
        "batch_index": batch_index,
        "attempt": attempt,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "input_types": input_types or [],
        "chunk_count": len(chunks),
        "chunk_separator": "\\n---\\n",
    }
    record = {
        "type": "raw",
        "content_type": "text/plain",
        "content_raw": raw_text,
    }
    footer = {
        "type": "footer",
        "records": 1,
        "bytes": len(raw_text.encode("utf-8")),
        "done": bool(raw_text),
    }
    wal_path.write_text(
        "\n".join(
            json.dumps(entry, ensure_ascii=False)
            for entry in (header, record, footer)
        ),
        encoding="utf-8",
    )
    return wal_path


def iter_chapter_files(chapters_root: Path, chapters: list[int] | None) -> list[Path]:
    if chapters:
        files = []
        for chapter in chapters:
            for width in (2, 3):
                candidate = chapters_root / f"chapter_{chapter:0{width}d}.txt"
                if candidate.exists():
                    files.append(candidate)
                    break
        return files
    return sorted(chapters_root.glob("chapter_*.txt"))


def parse_story_lines(
    chapters_root: Path,
    chapters: list[int] | None,
    chapter_pad: int,
    segment_pad: int,
) -> list[dict]:
    lines = []
    for chapter_file in iter_chapter_files(chapters_root, chapters):
        for raw_line in chapter_file.read_text(encoding="utf-8").splitlines():
            if not raw_line.strip():
                continue
            match = LINE_RE.match(raw_line)
            if not match:
                continue
            chapter_num = int(match.group(1))
            verse_num = int(match.group(2))
            text = match.group(3).strip()
            chapter_id = f"{chapter_num:0{chapter_pad}d}"
            segment_label = f"segment_{verse_num:0{segment_pad}d}"
            verse_id = f"{chapter_num}:{verse_num}"
            lines.append(
                {
                    "chapter_id": chapter_id,
                    "segment_label": segment_label,
                    "verse_id": verse_id,
                    "text": text,
                }
            )
    return lines


def build_analysis_context(
    *,
    story_id: str,
    run_id: str | None,
    unit_ref_template: str,
    lineage_template: str,
    phase_limit: int,
    pos_tags: list[dict],
    function_words: list[dict],
    geo_env_catalog: dict,
) -> str:
    run_attr = f' run_id="{escape(run_id)}"' if run_id else ""
    parts = [f'<analysis_context story_id="{escape(story_id)}"{run_attr}>']
    parts.append(f"  <unit_ref_template>{escape(unit_ref_template)}</unit_ref_template>")
    parts.append(f"  <lineage_template>{escape(lineage_template)}</lineage_template>")
    parts.append(f"  <phase_limit>{phase_limit}</phase_limit>")

    if pos_tags:
        parts.append("  <pos_tags>")
        for tag in pos_tags:
            parts.append(
                "    <tag value=\"{value}\" category=\"{category}\" description=\"{description}\" />".format(
                    value=escape(str(tag.get("tag", ""))),
                    category=escape(str(tag.get("category", ""))),
                    description=escape(str(tag.get("description", ""))),
                )
            )
        parts.append("  </pos_tags>")

    if function_words:
        parts.append("  <function_words>")
        for word in function_words:
            parts.append(
                "    <word surface=\"{surface}\">".format(
                    surface=escape(str(word.get("surface", ""))),
                )
            )
            for pos in word.get("allowed_pos", []) or []:
                parts.append(f"      <allowed_pos>{escape(str(pos))}</allowed_pos>")
            note = word.get("note")
            if note:
                parts.append(f"      <note>{escape(str(note))}</note>")
            parts.append("    </word>")
        parts.append("  </function_words>")

    if geo_env_catalog:
        parts.append("  <geo_env_catalog>")
        for canonical in geo_env_catalog.get("geo_environments", []) or []:
            parts.append(f"    <canonical name=\"{escape(str(canonical))}\">")
            for alias, mapped in (geo_env_catalog.get("aliases", {}) or {}).items():
                if mapped == canonical:
                    parts.append(f"      <alias>{escape(str(alias))}</alias>")
            parts.append("    </canonical>")
        parts.append("  </geo_env_catalog>")

    parts.append("</analysis_context>")
    return "\n".join(parts)


def build_story_batch(story_id: str, lines: list[dict]) -> str:
    parts = [f'<story_batch story_id="{escape(story_id)}">']
    for item in lines:
        parts.append(
            "  <line chapter_id=\"{chapter_id}\" verse_id=\"{verse_id}\" segment_label=\"{segment_label}\">{text}</line>".format(
                chapter_id=escape(item["chapter_id"]),
                verse_id=escape(item["verse_id"]),
                segment_label=escape(item["segment_label"]),
                text=escape(item["text"]),
            )
        )
    parts.append("</story_batch>")
    return "\n".join(parts)


@dataclass
class SegmentPayload:
    chapter_id: str
    segment_label: str
    verse_id: str
    segment_xml: str
    witness_id: str | None = None


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
            errors="replace",
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
                "clientInfo": {"name": "visionexe-adk-runner", "version": "0.1.0"},
            },
        )
        if "error" in response:
            raise RuntimeError(f"MCP initialize failed: {response['error']}")
        self._notify("notifications/initialized", {})
        self._load_tools()

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
        tool_name = self._resolve_tool_name(name)
        if self._tools and tool_name == name and name not in self._tools:
            raise RuntimeError(
                f"MCP tool {name} not found. Available tools: {', '.join(self._tools)}"
            )
        response = self._request("tools/call", {"name": tool_name, "arguments": arguments})
        if "error" in response:
            raise RuntimeError(f"MCP tool {tool_name} failed: {response['error']}")
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

    def _load_tools(self) -> None:
        try:
            response = self._request("tools/list", {})
        except Exception:
            return
        result = response.get("result")
        if isinstance(result, dict):
            tools = result.get("tools")
        else:
            tools = result
        if not isinstance(tools, list):
            return
        names: list[str] = []
        for item in tools:
            if isinstance(item, dict) and "name" in item:
                names.append(str(item["name"]))
            elif isinstance(item, str):
                names.append(item)
        self._tools = names

    def _resolve_tool_name(self, name: str) -> str:
        if not self._tools:
            return name
        if name in self._tools:
            return name
        lowered = name.lower()
        for candidate in self._tools:
            if candidate.lower() == lowered:
                return candidate
        snake = self._to_snake_case(name)
        for candidate in self._tools:
            if candidate.lower() == snake:
                return candidate
        compact = lowered.replace("_", "")
        for candidate in self._tools:
            if candidate.lower().replace("_", "") == compact:
                return candidate
        for candidate in self._tools:
            if candidate.lower().endswith(lowered):
                return candidate
        return name

    @staticmethod
    def _to_snake_case(value: str) -> str:
        if not value:
            return value
        step1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", value)
        step2 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", step1)
        return step2.replace("-", "_").lower()


def extract_analysis_batch(chunks: list[str]) -> str | None:
    text = "".join(chunks)
    end = text.rfind("</analysis_batch>")
    if end < 0:
        return None
    start = text.rfind("<analysis_batch", 0, end)
    if start < 0:
        return None
    end += len("</analysis_batch>")
    return text[start:end]


def _scan_json_object(text: str) -> dict | list | None:
    decoder = json.JSONDecoder()
    preferred: dict | list | None = None
    for idx, ch in enumerate(text):
        if ch not in "{[":
            continue
        try:
            obj, _end = decoder.raw_decode(text[idx:])
        except json.JSONDecodeError:
            continue
        if isinstance(obj, (dict, list)):
            if isinstance(obj, dict) and (
                "analysis_batch" in obj
                or "segments" in obj
                or "source" in obj
                or "evaluation" in obj
                or "syntax" in obj
            ):
                return obj
            if preferred is None:
                preferred = obj
    return preferred


def extract_analysis_json(chunks: list[str]) -> dict | list | None:
    for chunk in chunks:
        candidate = chunk.strip()
        if candidate.startswith("```"):
            candidate = re.sub(r"^```(?:json)?", "", candidate, flags=re.IGNORECASE).strip()
            if candidate.endswith("```"):
                candidate = candidate[:-3].strip()
        if candidate.startswith("{") and candidate.endswith("}"):
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass
        obj = _scan_json_object(candidate)
        if obj is not None:
            return obj
    text = "".join(chunks).strip()
    return _scan_json_object(text)


def wrap_single_segment_batch(
    batch_json: dict | list,
    analysis_type: str,
    batch_lines: list[dict],
) -> dict:
    line = batch_lines[0]
    segment = {
        "chapter_id": line["chapter_id"],
        "segment_label": line["segment_label"],
        "verse_id": line.get("verse_id") or "",
    }
    if isinstance(batch_json, dict):
        segment.update(batch_json)
    else:
        segment["items"] = batch_json
    segment["chapter_id"] = line["chapter_id"]
    segment["segment_label"] = line["segment_label"]
    segment["verse_id"] = line.get("verse_id") or ""
    return {
        "analysis_batch": {
            "type": analysis_type,
            "segments": [segment],
        }
    }


def repair_graphematic_xml(batch_xml: str) -> str:
    cleaned = re.sub(r"<(/?)gatic_string>", r"<\1graphematic_string>", batch_xml)
    cleaned = re.sub(r"<(/?)ghematic_string>", r"<\1graphematic_string>", cleaned)
    return cleaned


def repair_analysis_xml(analysis_type: str, batch_xml: str) -> str:
    cleaned = batch_xml
    if analysis_type == "graphematic":
        cleaned = repair_graphematic_xml(cleaned)
        cleaned = re.sub(r"(?m)^([ \t]*)source>", r"\1</source>", cleaned)
    if analysis_type == "synthactic":
        dep_pattern = re.compile(r"(<dep[^>]*?)\s*\([^<>]*\)")
        while True:
            updated = dep_pattern.sub(r"\1", cleaned)
            if updated == cleaned:
                break
            cleaned = updated
        cleaned = re.sub(r"\]\]\s*</bracket_notation>", "]]></bracket_notation>", cleaned)
    cleaned = re.sub(r"<(/?)paralleals>", r"<\1parallels>", cleaned)
    cleaned = re.sub(r'translation_id_([A-Za-z0-9_-]+)"', r'translation_id="\1"', cleaned)
    cleaned = re.sub(r"(<bracket_notation>[^<]*)</parse>", r"\1</bracket_notation>", cleaned)
    return cleaned


def parse_segments(batch_xml: str) -> list[SegmentPayload]:
    root = ET.fromstring(batch_xml)
    segments: list[SegmentPayload] = []
    for segment in root.findall("segment"):
        chapter_id = segment.get("chapter_id") or ""
        segment_label = segment.get("segment_label") or ""
        verse_id = segment.get("verse_id") or ""
        witness_id = segment.get("witness_id")
        segment_xml = ET.tostring(segment, encoding="unicode")
        if chapter_id and segment_label and verse_id:
            segments.append(
                SegmentPayload(
                    chapter_id=chapter_id,
                    segment_label=segment_label,
                    verse_id=verse_id,
                    witness_id=witness_id,
                    segment_xml=segment_xml,
                )
            )
    return segments


def parse_segments_json(batch_obj: dict) -> list[SegmentPayload]:
    batch = batch_obj.get("analysis_batch", batch_obj)
    items = batch.get("segments", []) or []
    segments: list[SegmentPayload] = []
    for item in items:
        chapter_id = str(item.get("chapter_id") or "")
        segment_label = str(item.get("segment_label") or "")
        verse_id = str(item.get("verse_id") or "")
        segment_json = json.dumps(item, ensure_ascii=False)
        if not (chapter_id and segment_label):
            continue
        segments.append(
            SegmentPayload(
                chapter_id=chapter_id,
                segment_label=segment_label,
                verse_id=verse_id,
                segment_xml=segment_json,
            )
        )
    return segments


def analysis_output_filename(analysis_type: str) -> str | None:
    mapping = {
        "graphematic": "analysis_llm_graphematic.txt",
        "morphologic": "analysis_llm_morphologic.txt",
        "synthactic": "analysis_llm_synthactic.txt",
        "semantic_historical": "analysis_llm_semantic_historical.txt",
        "analysis_llm": "analysis_llm.txt",
        "scene": "analysis_llm_scene.txt",
    }
    return mapping.get(analysis_type)


def write_analysis_files(
    analysis_segments_root: Path | None,
    chapter_label: str,
    analysis_type: str,
    segments: list[SegmentPayload],
) -> None:
    if not analysis_segments_root:
        warn("analysis_segments_root not set; cannot write analysis files.")
        return
    filename = analysis_output_filename(analysis_type)
    if not filename:
        warn(f"No analysis filename mapping for {analysis_type}; skipping file write.")
        return
    analysis_segments_root.mkdir(parents=True, exist_ok=True)
    for segment in segments:
        if not segment.chapter_id or not segment.segment_label:
            continue
        chapter_dir = analysis_segments_root / f"{chapter_label}_{segment.chapter_id}"
        segment_dir = chapter_dir / segment.segment_label
        segment_dir.mkdir(parents=True, exist_ok=True)
        target_path = segment_dir / filename
        target_path.write_text(segment.segment_xml, encoding="utf-8")


def collection_for_analysis(analysis_type: str) -> str:
    if analysis_type.startswith("analysis_"):
        return analysis_type
    return f"analysis_{analysis_type}"


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


def store_segment_via_mcp(
    mcp: SimpleMcpClient,
    *,
    story_id: str,
    run_id: str,
    unit_ref_template: str,
    lineage_template: str,
    analysis_type: str,
    segment: SegmentPayload,
) -> None:
    unit_ref = unit_ref_template.replace("[chapter_id]", segment.chapter_id).replace(
        "[segment_label]", segment.segment_label
    )
    lineage = (
        lineage_template.replace("[story_id]", story_id)
        .replace("[chapter_id]", segment.chapter_id)
        .replace("[segment_label]", segment.segment_label)
        .replace("[verse_id]", segment.verse_id)
    )
    collection = collection_for_analysis(analysis_type)
    role = collection
    roles = ["analysis", collection]

    metadata = {
        "roles": roles,
        "lineage": lineage,
        "chapter_id": segment.chapter_id,
        "segment_label": segment.segment_label,
        "verse_id": segment.verse_id,
        "story_id": story_id,
        "analysis_type": analysis_type,
    }
    if segment.witness_id:
        metadata["witness_id"] = segment.witness_id

    artifact_result = mcp.call_tool(
        "store_artifact",
        {
            "kind": "analysis",
            "content": segment.segment_xml,
            "mime": "text/xml",
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

    mcp.call_tool(
        "link_run_output",
        {
            "runId": run_id,
            "artifactId": artifact_id,
            "role": role,
            "metadata": json.dumps({"analysis_type": analysis_type}, ensure_ascii=False),
        },
    )

    document_metadata = {
        **metadata,
        "analysis_id": artifact_id,
        "unit_ref": unit_ref,
    }
    mcp.call_tool(
        "store_document",
        {
            "collection": collection,
            "title": f"{story_id}/chapter_{segment.chapter_id}/{segment.segment_label}",
            "content": segment.segment_xml,
            "metadata": json.dumps(document_metadata, ensure_ascii=False),
        },
    )


def create_session(server_url: str, app_name: str, user_id: str) -> str:
    payload = json.dumps({"state": {}}).encode("utf-8")
    req = urllib.request.Request(
        f"{server_url}/apps/{app_name}/users/{user_id}/sessions",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["id"]


def _collect_chunks_from_events(
    events: list[dict],
    meta: dict | None = None,
) -> list[str]:
    chunks: list[str] = []
    if meta is not None:
        meta.setdefault("authors", set())
        meta.setdefault("function_calls", set())
    for event in events:
        if not isinstance(event, dict):
            continue
        if meta is not None:
            author = event.get("author")
            if isinstance(author, str) and author:
                meta["authors"].add(author)
        text_parts: list[str] = []
        content = event.get("content")
        parts = None
        if isinstance(content, dict):
            parts = content.get("parts")
        elif isinstance(content, list):
            parts = content
        if parts:
            for part in parts:
                if isinstance(part, dict) and "text" in part:
                    text_parts.append(part["text"])
                if meta is not None and isinstance(part, dict) and "functionCall" in part:
                    call_name = part.get("functionCall", {}).get("name")
                    if isinstance(call_name, str) and call_name:
                        meta["function_calls"].add(call_name)
                if isinstance(part, dict) and "functionResponse" in part:
                    response = part.get("functionResponse", {}).get("response")
                    if isinstance(response, dict):
                        response_content = response.get("content")
                        items = None
                        if isinstance(response_content, dict):
                            items = response_content.get("parts")
                        elif isinstance(response_content, list):
                            items = response_content
                        if items:
                            for item in items:
                                if isinstance(item, dict) and "text" in item:
                                    text_parts.append(item["text"])
                        if "text" in response and isinstance(response["text"], str):
                            text_parts.append(response["text"])
                        if "result" in response:
                            result = response.get("result")
                            if isinstance(result, (dict, list)):
                                text_parts.append(json.dumps(result, ensure_ascii=False))
                            elif result is not None:
                                text_parts.append(str(result))
                    elif response is not None:
                        text_parts.append(str(response))
        candidates = event.get("candidates")
        if isinstance(candidates, list):
            for candidate in candidates:
                if not isinstance(candidate, dict):
                    continue
                cand_content = candidate.get("content")
                if isinstance(cand_content, dict):
                    for part in cand_content.get("parts") or []:
                        if isinstance(part, dict) and "text" in part:
                            text_parts.append(part["text"])
        if text_parts:
            chunks.append("".join(text_parts))
    return chunks


def run_agent_sse(
    server_url: str,
    payload: dict,
    event_sink: list[dict] | None = None,
    meta: dict | None = None,
) -> tuple[str | None, list[str]]:
    req = urllib.request.Request(
        f"{server_url}/run_sse",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    run_id = None
    chunks: list[str] = []
    if meta is not None:
        meta.setdefault("authors", set())
        meta.setdefault("function_calls", set())
    with urllib.request.urlopen(req) as resp:
        while True:
            line = resp.readline()
            if not line:
                break
            if not line.startswith(b"data:"):
                continue
            data = line[len(b"data:") :].strip()
            if not data:
                continue
            try:
                event = json.loads(data.decode("utf-8"))
            except json.JSONDecodeError:
                continue
            if event_sink is not None:
                event_sink.append(event)
            if is_rate_limit_event(event):
                raise RateLimitError("Resource exhausted (429) from SSE event.")
            new_chunks = _collect_chunks_from_events([event], meta)
            if new_chunks:
                text = "".join(new_chunks)
                chunks.append(text)
                match = re.search(r'run_id="([^"]+)"', text)
                if match:
                    run_id = match.group(1)
    return run_id, chunks


class RateLimitError(RuntimeError):
    pass


def is_rate_limit_event(event: dict) -> bool:
    error_message = str(event.get("errorMessage", "")).lower()
    error_code = str(event.get("errorCode", "")).lower()
    if "resource_exhausted" in error_code or "resource exhausted" in error_message:
        return True
    if "too many requests" in error_message or "429" in error_message:
        return True
    return False


def run_agent_with_retries(
    server_url: str,
    payload: dict,
    *,
    max_retries: int,
    base_sleep: float,
    max_sleep: float,
    event_sink: list[dict] | None = None,
    meta: dict | None = None,
) -> tuple[str | None, list[str]]:
    attempt = 0
    while True:
        try:
            return run_agent_sse(server_url, payload, event_sink, meta)
        except RateLimitError:
            if attempt >= max_retries:
                raise
        except urllib.error.HTTPError as err:
            if err.code != 429:
                raise
            if attempt >= max_retries:
                raise
        sleep_for = min(max_sleep, base_sleep * (2 ** attempt)) + random.uniform(0, 0.5)
        time.sleep(sleep_for)
        attempt += 1


def build_task_message(analysis_type: str, input_types: list[str] | None = None) -> str:
    if analysis_type == "bootstrap":
        return '<task type="bootstrap">Store text units only.</task>'
    if analysis_type == "analysis_llm":
        return "<task type=\"analysis_llm\">Run Level E analysis for all lines.</task>"
    if input_types:
        inputs = ",".join(input_types)
        return f'<task type="{analysis_type}" inputs="{inputs}">Run {analysis_type} analysis for all lines.</task>'
    return f'<task type="{analysis_type}">Run {analysis_type} analysis for all lines.</task>'


TOOL_FOR_ANALYSIS = {
    "graphematic": "graphematic_analysis_subagent",
    "morphologic": "morphological_analysis_subagent",
    "synthactic": "syntactic_analysis_subagent",
    "semantic_historical": "semantic_historical_evaluation_subagent",
    "scene": "scene_analysis_subagent",
    "analysis_llm": None,
}
ANALYSIS_TOOL_NAMES = {name for name in TOOL_FOR_ANALYSIS.values() if name}
ANALYSIS_TYPE_ALIASES = {
    "graphematic": {"graphematic"},
    "morphologic": {"morphologic", "morphological"},
    "synthactic": {"synthactic", "syntactic"},
    "semantic_historical": {"semantic_historical", "semantic-historical", "semanticHistorical"},
    "analysis_llm": {"analysis_llm", "analysis-llm", "analysis"},
    "scene": {"scene"},
}
STRICT_ANALYSIS_TYPES = {"analysis_llm", "graphematic"}


def _analysis_type_matches_declared(analysis_type: str, declared: str | None) -> bool:
    if not declared:
        return True
    aliases = ANALYSIS_TYPE_ALIASES.get(analysis_type, {analysis_type})
    return declared in aliases


def build_tool_directive(analysis_type: str) -> str:
    tool = TOOL_FOR_ANALYSIS.get(analysis_type)
    if tool:
        return (
            "TOOL_CHOICE: {tool}\n"
            "You MUST delegate to the subagent named above for the current task and return its JSON output verbatim.\n"
            "Do NOT call any tools. If you used the wrong subagent, retry with the correct one.\n"
            "Output must be JSON only (no XML).\n"
        ).format(tool=tool)
    return (
        "TOOL_CHOICE: none\n"
        "Do NOT delegate and do NOT call any tools for this task. Output must be JSON only (no XML).\n"
    )


def build_tool_retry_note(analysis_type: str) -> str:
    tool = TOOL_FOR_ANALYSIS.get(analysis_type)
    if tool:
        return (
            f"RETRY: You MUST delegate ONLY to {tool} and return its JSON output verbatim. "
            "No tools. No XML."
        )
    return "RETRY: Do NOT delegate and do NOT call any tools. Output JSON only (no XML)."


def _analysis_type_matches_xml(batch_xml: str, analysis_type: str) -> bool:
    match = re.search(r'<analysis_batch[^>]*type="([^"]+)"', batch_xml)
    if not match:
        return True
    return _analysis_type_matches_declared(analysis_type, match.group(1))


def _analysis_type_matches_json(batch_json: dict | list | None, analysis_type: str) -> bool:
    if not isinstance(batch_json, dict):
        return True
    batch_obj = batch_json.get("analysis_batch", batch_json)
    if not isinstance(batch_obj, dict):
        return True
    declared = batch_obj.get("type")
    return _analysis_type_matches_declared(analysis_type, declared)


def build_schema_message(analysis_type: str, schema_entry: dict) -> str:
    contract = schema_entry.get("contract")
    if not contract:
        return ""
    lines = [f"Schema contract for {analysis_type} (JSON):"]
    schema_ref = schema_entry.get("schema_ref")
    if schema_ref:
        lines.append(f"Schema ref: {schema_ref}")
    lines.append(json.dumps(contract, ensure_ascii=False, indent=2))
    notes = schema_entry.get("notes") or []
    if notes:
        lines.append("Notes:")
        for note in notes:
            lines.append(f"- {note}")
    return "\n".join(lines)


def warn(message: str) -> None:
    print(f"WARNING: {message}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run ADK analysis sessions over Ge'ez chapters.")
    parser.add_argument("--story-config", default="stories/template/config/story_config.json")
    parser.add_argument("--chapters-root", default="data/Story1-Henoch")
    parser.add_argument("--chapters", nargs="*", type=int)
    parser.add_argument("--server-url", default="http://127.0.0.1:8000")
    parser.add_argument("--app-name", default="app")
    parser.add_argument("--user-id", default="user")
    parser.add_argument("--run-id")
    parser.add_argument("--per-analysis-session", action="store_true")
    parser.add_argument("--skip-bootstrap", action="store_true")
    parser.add_argument(
        "--write-analysis-files",
        action="store_true",
        help="Write per-segment analysis files into analysis_segments_root.",
    )
    parser.add_argument(
        "--analysis-segments-root",
        default="",
        help="Override analysis_segments_root (defaults to story_config).",
    )
    parser.add_argument(
        "--store-via-mcp",
        action="store_true",
        help="DEPRECATED: disabled. Use --wal-dir and the Archivist pipeline.",
    )
    parser.add_argument("--no-streaming", action="store_true", help="Disable SSE streaming in ADK requests.")
    parser.add_argument("--mcp-command")
    parser.add_argument("--mcp-args", nargs="*")
    parser.add_argument("--mcp-cwd")
    parser.add_argument("--mcp-debug-log")
    parser.add_argument("--retry-429", type=int, default=0)
    parser.add_argument("--retry-base-sleep", type=float, default=2.0)
    parser.add_argument("--retry-max-sleep", type=float, default=60.0)
    parser.add_argument("--analysis-sleep", type=float, default=0.2)
    parser.add_argument(
        "--analysis-schema-config",
        default="engine/config/analysis_schemas.json",
        help="Path to analysis schema definitions injected into prompts.",
    )
    parser.add_argument(
        "--wal-dir",
        help="Write raw LLM responses to append-only JSONL WAL files (one file per request).",
    )
    parser.add_argument(
        "--chapter-sleep",
        type=float,
        default=0.0,
        help="Seconds to wait after finishing a chapter.",
    )
    parser.add_argument(
        "--segment-batch-size",
        type=int,
        default=0,
        help="Segments per analysis batch (0 = whole chapter).",
    )
    parser.add_argument("--retry-empty", type=int, default=0)
    parser.add_argument("--retry-empty-sleep", type=float, default=3.0)
    parser.add_argument("--analysis-types", nargs="*", default=[
        "graphematic",
        "morphologic",
        "synthactic",
        "semantic_historical",
        "scene",
        "analysis_llm",
    ])
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    if args.store_via_mcp:
        raise SystemExit(
            "ADK-MCP wurde deaktiviert. Nutze WAL via --wal-dir und den Archivist-Workflow."
        )

    story_config, _, repo_root = load_story_config(story_config_path=args.story_config)
    chapter_label = story_config.get("chapter_label") or "story"
    analysis_segments_root = None
    if args.analysis_segments_root:
        analysis_segments_root = resolve_path(args.analysis_segments_root, repo_root)
    elif story_config.get("analysis_segments_root"):
        analysis_segments_root = resolve_path(story_config.get("analysis_segments_root"), repo_root)
    engine_root = repo_root / "engine"
    chapters_root = resolve_path(args.chapters_root, repo_root)
    schema_path = resolve_path(args.analysis_schema_config, repo_root)
    analysis_schemas = load_analysis_schemas(schema_path)
    wal_dir = resolve_path(args.wal_dir, repo_root) if args.wal_dir else None

    story_id = story_config.get("story_id", "story")
    chapter_pad = int(story_config.get("chapter_index_padding", 3))
    segment_pad = int(story_config.get("segment_index_padding", 3))
    phase_limit = int(story_config.get("dynamic_phase_max", 3))

    lines = parse_story_lines(chapters_root, args.chapters, chapter_pad, segment_pad)
    if not lines:
        raise SystemExit("No lines found to analyze.")
    chapter_groups: dict[str, list[dict]] = {}
    chapter_order: list[str] = []
    for item in lines:
        chapter_id = item["chapter_id"]
        if chapter_id not in chapter_groups:
            chapter_groups[chapter_id] = []
            chapter_order.append(chapter_id)
        chapter_groups[chapter_id].append(item)

    pos_tags = load_pos_tags(engine_root)
    function_words = load_function_words(engine_root)
    geo_env_catalog = load_geo_env_catalog(story_config, repo_root)

    unit_ref_template = f"{story_id}:chapter_[chapter_id]:[segment_label]"
    lineage_template = "story_id=[story_id]|chapter_id=[chapter_id]|segment_label=[segment_label]|verse_id=[verse_id]"

    run_id = args.run_id
    story_batch = build_story_batch(story_id, lines)
    mcp_client: SimpleMcpClient | None = None

    if args.store_via_mcp:
        vector_mcp_dir = repo_root / "engine" / "tools" / "exevision" / "vector_mcp" / "VectorMcpServer"
        default_exe = vector_mcp_dir / "bin" / "Debug" / "net10.0" / "VectorMcpServer.exe"
        mcp_command = args.mcp_command or (str(default_exe) if default_exe.exists() else "dotnet")
        if args.mcp_args is not None:
            mcp_args = args.mcp_args
        else:
            mcp_args = [] if default_exe.exists() else ["run", "--project", str(vector_mcp_dir)]
        mcp_cwd = args.mcp_cwd or str(vector_mcp_dir)
        debug_log = Path(args.mcp_debug_log) if args.mcp_debug_log else None
        mcp_client = SimpleMcpClient(
            command=mcp_command,
            args=mcp_args,
            cwd=mcp_cwd,
            debug_log=debug_log,
        )
        if not run_id:
            create_run_result = mcp_client.call_tool(
                "create_run",
                {
                    "runType": "analysis",
                    "storyId": story_id,
                    "metadata": json.dumps({"source": "adk_analysis_runner"}, ensure_ascii=False),
                },
            )
            create_run_payload = tool_text_to_json(create_run_result)
            run_id = create_run_payload.get("run_id")
            if not run_id:
                raise SystemExit(f"CreateRun failed: {create_run_payload}")
        if not args.skip_bootstrap:
            for item in lines:
                unit_ref = unit_ref_template.replace("[chapter_id]", item["chapter_id"]).replace(
                    "[segment_label]", item["segment_label"]
                )
                mcp_client.call_tool(
                    "store_text_unit",
                    {
                        "unitRef": unit_ref,
                        "content": item["text"],
                        "storyId": story_id,
                        "chapterId": item["chapter_id"],
                        "segmentLabel": item["segment_label"],
                        "verseId": item["verse_id"],
                        "metadata": json.dumps({"source": "adk_analysis_runner"}, ensure_ascii=False),
                    },
                )
            print(f"Bootstrap run_id: {run_id}")
    else:
        analysis_context = build_analysis_context(
            story_id=story_id,
            run_id=run_id,
            unit_ref_template=unit_ref_template,
            lineage_template=lineage_template,
            phase_limit=phase_limit,
            pos_tags=pos_tags,
            function_words=function_words,
            geo_env_catalog=geo_env_catalog,
        )
        session_id = create_session(args.server_url, args.app_name, args.user_id)
        if not args.skip_bootstrap:
            bootstrap_payload = {
                "app_name": args.app_name,
                "user_id": args.user_id,
                "session_id": session_id,
                "streaming": (not args.no_streaming),
                "new_message": {
                    "role": "user",
                    "parts": [{"text": f"{analysis_context}\n{story_batch}\n{build_task_message('bootstrap')}"}],
                },
            }
            bootstrap_events: list[dict] | None = [] if args.debug else None
            if args.retry_429:
                run_id, chunks = run_agent_with_retries(
                    args.server_url,
                    bootstrap_payload,
                    max_retries=args.retry_429,
                    base_sleep=args.retry_base_sleep,
                    max_sleep=args.retry_max_sleep,
                    event_sink=bootstrap_events,
                )
            else:
                run_id, chunks = run_agent_sse(args.server_url, bootstrap_payload, bootstrap_events)
            if args.debug:
                debug_path = repo_root / "tmp" / "adk_bootstrap_debug.txt"
                raw_path = repo_root / "tmp" / "adk_bootstrap_events.jsonl"
                debug_path.parent.mkdir(parents=True, exist_ok=True)
                debug_path.write_text("\n---\n".join(chunks), encoding="utf-8")
                if bootstrap_events is not None:
                    raw_path.write_text(
                        "\n".join(json.dumps(event, ensure_ascii=False) for event in bootstrap_events),
                        encoding="utf-8",
                    )
                if not run_id:
                    print(f"Bootstrap response did not include run_id. Debug saved to {debug_path}")
            if not run_id:
                if args.run_id:
                    run_id = args.run_id
                else:
                    run_id = f"adk_local_{time.strftime('%Y%m%d_%H%M%S', time.gmtime())}"
                warn(f"Bootstrap did not return run_id. Using fallback run_id={run_id}.")
            print(f"Bootstrap run_id: {run_id}")

    analysis_context = build_analysis_context(
        story_id=story_id,
        run_id=run_id,
        unit_ref_template=unit_ref_template,
        lineage_template=lineage_template,
        phase_limit=phase_limit,
        pos_tags=pos_tags,
        function_words=function_words,
        geo_env_catalog=geo_env_catalog,
    )

    session_id = create_session(args.server_url, args.app_name, args.user_id)
    chain_inputs: dict[str, list[str]] = {
        "graphematic": ["story_batch"],
        "morphologic": ["graphematic"],
        "synthactic": ["morphologic"],
        "semantic_historical": ["morphologic", "synthactic"],
        "scene": ["morphologic", "synthactic", "semantic_historical"],
        "analysis_llm": ["morphologic", "synthactic", "semantic_historical"],
    }

    try:
        for chapter_id in chapter_order:
            print(f"Chapter {chapter_id}: starting")
            chapter_lines = chapter_groups[chapter_id]
            batch_size = args.segment_batch_size or 0
            if batch_size > 0:
                batches = [
                    chapter_lines[i : i + batch_size]
                    for i in range(0, len(chapter_lines), batch_size)
                ]
            else:
                batches = [chapter_lines]

            for batch_index, batch_lines in enumerate(batches, start=1):
                chapter_batch = build_story_batch(story_id, batch_lines)
                analysis_batches: dict[str, str] = {}

                for analysis_type in args.analysis_types:
                    if args.per_analysis_session:
                        session_id = create_session(args.server_url, args.app_name, args.user_id)

                    input_types = chain_inputs.get(analysis_type, ["story_batch"])
                    missing = [
                        req for req in input_types if req != "story_batch" and req not in analysis_batches
                    ]
                    if missing:
                        warn(
                            f"Skipping {analysis_type} for chapter {chapter_id}: missing inputs {', '.join(missing)}"
                        )
                        continue

                    prompt_parts = [analysis_context]
                    if "story_batch" in input_types:
                        prompt_parts.append(chapter_batch)
                    for req in input_types:
                        if req == "story_batch":
                            continue
                        prompt_parts.append(f'<analysis_input type="{req}">{analysis_batches[req]}</analysis_input>')
                    schema_entry = analysis_schemas.get(analysis_type)
                    if schema_entry:
                        schema_message = build_schema_message(analysis_type, schema_entry)
                        if schema_message:
                            prompt_parts.append(schema_message)
                    prompt_parts.append(build_tool_directive(analysis_type))
                    prompt_parts.append(build_task_message(analysis_type, input_types))

                    payload = {
                        "app_name": args.app_name,
                        "user_id": args.user_id,
                        "session_id": session_id,
                        "streaming": (not args.no_streaming),
                        "new_message": {
                            "role": "user",
                            "parts": [{"text": "\n".join(prompt_parts)}],
                        },
                    }
                    base_prompt_text = payload["new_message"]["parts"][0]["text"]

                    batch_xml = None
                    batch_json: dict | None = None
                    fallback_xml = None
                    fallback_json: dict | None = None
                    fallback_reason = ""
                    chunks: list[str] = []
                    capture_events = args.debug or (analysis_type not in STRICT_ANALYSIS_TYPES)
                    analysis_events: list[dict] | None = [] if capture_events else None
                    max_attempts = max(1, args.retry_empty + 1)
                    if TOOL_FOR_ANALYSIS.get(analysis_type) and max_attempts < 2:
                        max_attempts = 2
                    last_meta: dict | None = None
                    for attempt in range(max_attempts):
                        if attempt > 0:
                            payload["new_message"]["parts"][0]["text"] = (
                                base_prompt_text + "\n" + build_tool_retry_note(analysis_type)
                            )
                        else:
                            payload["new_message"]["parts"][0]["text"] = base_prompt_text
                        meta: dict = {}
                        if args.retry_429:
                            _, chunks = run_agent_with_retries(
                                args.server_url,
                                payload,
                                max_retries=args.retry_429,
                                base_sleep=args.retry_base_sleep,
                                max_sleep=args.retry_max_sleep,
                                event_sink=analysis_events,
                                meta=meta,
                            )
                        else:
                            _, chunks = run_agent_sse(args.server_url, payload, analysis_events, meta)

                        batch_xml = extract_analysis_batch(chunks)
                        if not batch_xml:
                            batch_json = extract_analysis_json(chunks)
                        if not batch_xml and not batch_json and analysis_events:
                            extra_chunks = _collect_chunks_from_events(analysis_events)
                            if extra_chunks:
                                batch_xml = extract_analysis_batch(extra_chunks)
                                if not batch_xml:
                                    batch_json = extract_analysis_json(extra_chunks)
                                if batch_xml or batch_json:
                                    chunks = extra_chunks
                        expected_tool = TOOL_FOR_ANALYSIS.get(analysis_type)
                        authors = set()
                        tool_calls: set[str] = set()
                        if isinstance(meta.get("authors"), set):
                            authors = meta["authors"]
                        if isinstance(meta.get("function_calls"), set):
                            tool_calls = meta["function_calls"]
                        if batch_xml and not _analysis_type_matches_xml(batch_xml, analysis_type):
                            warn(
                                f"{analysis_type} analysis_batch type mismatch (XML). Retrying."
                            )
                            if analysis_type in STRICT_ANALYSIS_TYPES:
                                batch_xml = None
                        if batch_json and not _analysis_type_matches_json(batch_json, analysis_type):
                            warn(
                                f"{analysis_type} analysis_batch type mismatch (JSON). Retrying."
                            )
                            if analysis_type in STRICT_ANALYSIS_TYPES:
                                batch_json = None
                        tool_mismatch = False
                        if expected_tool:
                            # Require the expected tool call OR matching author for tool-routed analyses.
                            if expected_tool not in tool_calls and expected_tool not in authors:
                                tool_mismatch = True
                        else:
                            # For non-tool analyses, any tool call is a mismatch.
                            if tool_calls:
                                tool_mismatch = True
                        if not tool_mismatch and authors:
                            if expected_tool:
                                if expected_tool not in authors and (authors & ANALYSIS_TOOL_NAMES):
                                    tool_mismatch = True
                            else:
                                if authors & ANALYSIS_TOOL_NAMES:
                                    tool_mismatch = True
                        # Accept valid batches even if tool metadata is missing/mismatched,
                        # as long as the declared analysis type matches.
                        if tool_mismatch and (batch_xml or batch_json):
                            type_ok = False
                            if batch_xml and _analysis_type_matches_xml(batch_xml, analysis_type):
                                type_ok = True
                            if batch_json and _analysis_type_matches_json(batch_json, analysis_type):
                                type_ok = True
                            if type_ok:
                                warn(
                                    f"{analysis_type} accepted output despite tool_mismatch:{','.join(sorted(authors)) or 'unknown'}."
                                )
                                tool_mismatch = False
                        if tool_mismatch:
                            expected_text = expected_tool or "no tools"
                            warn(
                                f"{analysis_type} tool mismatch: expected {expected_text}, got {', '.join(sorted(authors))}. Retrying."
                            )
                            if batch_xml or batch_json:
                                if batch_xml and not fallback_xml:
                                    fallback_xml = batch_xml
                                    fallback_reason = f"tool_mismatch:{','.join(sorted(authors))}"
                                if batch_json and not fallback_json:
                                    fallback_json = batch_json
                                    fallback_reason = f"tool_mismatch:{','.join(sorted(authors))}"
                            if analysis_type in STRICT_ANALYSIS_TYPES:
                                batch_xml = None
                                batch_json = None
                        if batch_xml or batch_json:
                            break
                        if attempt < max_attempts - 1:
                            warn(
                                f"No analysis_batch found for {analysis_type} (chapter {chapter_id}); retrying..."
                            )
                            time.sleep(args.retry_empty_sleep)
                        last_meta = meta

                    if wal_dir is not None:
                        write_wal_entry(
                            wal_dir,
                            story_id=story_id,
                            run_id=run_id,
                            analysis_type=analysis_type,
                            chapter_id=chapter_id,
                            batch_index=batch_index,
                            attempt=attempt + 1,
                            input_types=input_types,
                            chunks=chunks,
                        )
                    if args.debug:
                        batch_suffix = f"chapter_{chapter_id}"
                        if len(batches) > 1:
                            batch_suffix = f"chapter_{chapter_id}_batch_{batch_index:03d}"
                        attempt_suffix = ""
                        if args.retry_empty:
                            attempt_suffix = f"_attempt_{attempt + 1:02d}"
                        debug_path = repo_root / "tmp" / f"adk_{analysis_type}_{batch_suffix}{attempt_suffix}_debug.txt"
                        raw_path = repo_root / "tmp" / f"adk_{analysis_type}_{batch_suffix}{attempt_suffix}_events.jsonl"
                        debug_path.parent.mkdir(parents=True, exist_ok=True)
                        debug_path.write_text("\n---\n".join(chunks), encoding="utf-8")
                        if analysis_events is not None:
                            raw_path.write_text(
                                "\n".join(json.dumps(event, ensure_ascii=False) for event in analysis_events),
                                encoding="utf-8",
                            )

                    if not batch_xml and not batch_json and (fallback_xml or fallback_json):
                        batch_xml = fallback_xml
                        batch_json = fallback_json
                        warn(
                            f"{analysis_type} accepted output despite {fallback_reason} (no valid tool-routed batch after retries)."
                        )
                    if not batch_xml and not batch_json:
                        authors = []
                        calls = []
                        if last_meta:
                            if isinstance(last_meta.get("authors"), set):
                                authors = sorted(last_meta["authors"])
                            if isinstance(last_meta.get("function_calls"), set):
                                calls = sorted(last_meta["function_calls"])
                        details = []
                        if authors:
                            details.append(f"authors={','.join(authors)}")
                        if calls:
                            details.append(f"calls={','.join(calls)}")
                        suffix = f" ({' '.join(details)})" if details else ""
                        warn(f"No analysis_batch found for {analysis_type} (chapter {chapter_id}).{suffix}")
                        time.sleep(args.analysis_sleep)
                        continue
                    if batch_xml:
                        batch_xml = repair_analysis_xml(analysis_type, batch_xml)
                        try:
                            segments = parse_segments(batch_xml)
                        except ET.ParseError as exc:
                            warn(
                                f"Skipping {analysis_type} for chapter {chapter_id}: XML parse failed ({exc})."
                            )
                            time.sleep(args.analysis_sleep)
                            continue
                        analysis_batches[analysis_type] = batch_xml
                    else:
                        if batch_json and isinstance(batch_json, (dict, list)) and "analysis_batch" not in batch_json:
                            if analysis_type in STRICT_ANALYSIS_TYPES:
                                warn(
                                    f"{analysis_type} JSON missing analysis_batch with {len(batch_lines)} segments; cannot map."
                                )
                            elif len(batch_lines) == 1:
                                batch_json = wrap_single_segment_batch(
                                    batch_json,
                                    analysis_type,
                                    batch_lines,
                                )
                            else:
                                warn(
                                    f"{analysis_type} JSON missing analysis_batch with {len(batch_lines)} segments; cannot map."
                                )
                        try:
                            segments = parse_segments_json(batch_json or {})
                        except Exception as exc:
                            warn(
                                f"Skipping {analysis_type} for chapter {chapter_id}: JSON parse failed ({exc})."
                            )
                            time.sleep(args.analysis_sleep)
                            continue
                        analysis_batches[analysis_type] = json.dumps(batch_json, ensure_ascii=False)
                    if not segments:
                        warn(f"No segments parsed for {analysis_type} (chapter {chapter_id}).")
                        time.sleep(args.analysis_sleep)
                        continue

                    if args.write_analysis_files:
                        write_analysis_files(
                            analysis_segments_root=analysis_segments_root,
                            chapter_label=chapter_label,
                            analysis_type=analysis_type,
                            segments=segments,
                        )

                    if mcp_client is not None:
                        for segment in segments:
                            store_segment_via_mcp(
                                mcp_client,
                                story_id=story_id,
                                run_id=run_id,
                                unit_ref_template=unit_ref_template,
                                lineage_template=lineage_template,
                                analysis_type=analysis_type,
                                segment=segment,
                            )
                    time.sleep(args.analysis_sleep)
            if args.chapter_sleep:
                time.sleep(args.chapter_sleep)
    finally:
        if mcp_client is not None:
            mcp_client.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
