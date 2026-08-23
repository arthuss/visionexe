import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

from visionexe_paths import ensure_dir, load_story_config, resolve_path


JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*([\[{].*?[\]}])\s*```", re.DOTALL | re.IGNORECASE)
CHAPTER_RE = re.compile(r"chapter_(\d+)", re.IGNORECASE)
VERSE_RE = re.compile(r"verse_(\d+)", re.IGNORECASE)
SEGMENT_RE = re.compile(r"segment_(\d+)", re.IGNORECASE)
SCENE_RE = re.compile(r"scene_(\d+)", re.IGNORECASE)
PART_RE = re.compile(r"part_(\d+)", re.IGNORECASE)

ANALYSIS_LAYER_FILES = {
    "graphematic": "analysis_llm_graphematic.txt",
    "morphologic": "analysis_llm_morphologic.txt",
    "synthactic": "analysis_llm_synthactic.txt",
    "semantic_historical": "analysis_llm_semantic_historical.txt",
}

SCENE_ANALYSIS_TYPE = "scene"


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
                "clientInfo": {"name": "visionexe-analysis-master", "version": "0.1.0"},
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
        tools = result.get("tools") if isinstance(result, dict) else result
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
        return name

    @staticmethod
    def _to_snake_case(value: str) -> str:
        if not value:
            return value
        step1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", value)
        step2 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", step1)
        return step2.replace("-", "_").lower()


def warn(message: str) -> None:
    print(f"WARNING: {message}", file=sys.stderr)


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


def collection_for_analysis(analysis_type: str) -> str:
    if analysis_type.startswith("analysis_"):
        return analysis_type
    return f"analysis_{analysis_type}"


def build_filter(story_id: str, chapter_id: str, analysis_type: str) -> str:
    must = [
        {"key": "story_id", "match": {"value": story_id}},
        {"key": "chapter_id", "match": {"value": chapter_id}},
        {"key": "analysis_type", "match": {"value": analysis_type}},
    ]
    return json.dumps({"must": must}, ensure_ascii=False)


def fetch_analysis_points(
    client: SimpleMcpClient,
    story_id: str,
    chapter_id: str,
    analysis_type: str,
) -> list[dict]:
    collection = collection_for_analysis(analysis_type)
    filter_json = build_filter(story_id, chapter_id, analysis_type)
    points: list[dict] = []
    offset = None
    while True:
        args: dict[str, object] = {
            "collection": collection,
            "filterJson": filter_json,
            "limit": 500,
            "withPayload": True,
        }
        if offset:
            args["offsetJson"] = json.dumps(offset, ensure_ascii=False)
        result = client.call_tool("scroll_points_with_filter", args)
        payload = tool_text_to_json(result)
        batch = payload.get("points", []) if isinstance(payload, dict) else []
        if batch:
            points.extend(batch)
        offset = payload.get("next_page_offset") if isinstance(payload, dict) else None
        if not offset or not batch:
            break
    return points


def normalize_chapter_id(value, chapter_padding: int) -> str:
    if value is None:
        return ""
    raw = str(value).strip()
    if not raw:
        return ""
    if raw.isdigit():
        return f"{int(raw):0{chapter_padding}d}"
    match = CHAPTER_RE.search(raw)
    if match:
        return f"{int(match.group(1)):0{chapter_padding}d}"
    digits = re.sub(r"[^0-9]", "", raw)
    if digits:
        return f"{int(digits):0{chapter_padding}d}"
    return raw


def merge_point_payload(existing_payload: dict, incoming_payload: dict) -> dict:
    merged = dict(existing_payload or {})
    for key, value in (incoming_payload or {}).items():
        if key not in merged or merged[key] in ("", None, [], {}):
            merged[key] = value
    return merged


def merge_points(existing: dict, incoming: dict) -> dict:
    existing_payload = existing.get("payload", {}) if isinstance(existing, dict) else {}
    incoming_payload = incoming.get("payload", {}) if isinstance(incoming, dict) else {}
    merged = dict(existing or {})
    merged["id"] = merged.get("id") or incoming.get("id")
    merged["payload"] = merge_point_payload(existing_payload, incoming_payload)
    return merged


def fetch_analysis_points_engram(
    client: SimpleMcpClient,
    story_id: str,
    chapter_id: str,
    chapter_padding: int,
    analysis_type: str,
    queries: list[str],
    limit_per_query: int,
    min_shared_hashes: int,
) -> list[dict]:
    if not queries:
        return []

    collection = collection_for_analysis(analysis_type)
    result_map: dict[str, dict] = {}
    seen_empty = False

    for raw_query in queries:
        query = str(raw_query or "").strip()
        if not query:
            continue
        query_text = f"{query} {analysis_type}".strip()
        try:
            tool_result = client.call_tool(
                "engram_lookup",
                {
                    "query": query_text,
                    "collections": collection,
                    "limit": max(1, int(limit_per_query)),
                    "minSharedHashes": max(1, int(min_shared_hashes)),
                    "includeContent": True,
                },
            )
        except RuntimeError as exc:
            warn(f"Engram lookup unavailable/failed for {analysis_type}: {exc}")
            break
        payload = tool_text_to_json(tool_result)
        rows = payload.get("results", []) if isinstance(payload, dict) else []
        if not rows:
            seen_empty = True
            continue

        for row in rows:
            if not isinstance(row, dict):
                continue

            metadata = row.get("metadata")
            if not isinstance(metadata, dict):
                metadata = {}

            meta_story_id = str(metadata.get("story_id") or "").strip()
            if story_id and meta_story_id and meta_story_id != story_id:
                continue

            meta_chapter = normalize_chapter_id(metadata.get("chapter_id"), chapter_padding)
            if chapter_id and meta_chapter and meta_chapter != chapter_id:
                continue

            meta_analysis_type = str(metadata.get("analysis_type") or "").strip()
            if meta_analysis_type and meta_analysis_type != analysis_type:
                continue

            content = row.get("content")
            if not isinstance(content, str):
                content = ""
            if not content:
                raw_content = metadata.get("content")
                content = raw_content if isinstance(raw_content, str) else ""

            merged_payload = dict(metadata)
            merged_payload.setdefault("story_id", story_id)
            merged_payload.setdefault("chapter_id", chapter_id)
            merged_payload.setdefault("analysis_type", analysis_type)
            if content:
                merged_payload["content"] = content

            point_id = str(row.get("document_id") or "").strip()
            if not point_id:
                qdrant_ref = row.get("qdrant_ref")
                if isinstance(qdrant_ref, dict):
                    point_id = str(qdrant_ref.get("point_id") or "").strip()

            key = point_id or (
                f"{merged_payload.get('chapter_id')}"
                f"::{merged_payload.get('segment_label')}"
                f"::{merged_payload.get('analysis_type')}"
            )

            candidate = {"id": point_id, "payload": merged_payload}
            if key in result_map:
                result_map[key] = merge_points(result_map[key], candidate)
            else:
                result_map[key] = candidate

    if seen_empty and not result_map:
        warn(
            f"No Engram hits for chapter {chapter_id} / {analysis_type}. "
            "Try broader --mcp-engram-query values or lower --mcp-engram-min-shared-hashes."
        )

    return list(result_map.values())


def parse_xml_attr(node, attr_name: str) -> str:
    return str(node.get(attr_name, "")).strip()


def parse_scene_segment_xml(segment_xml: str) -> dict:
    block: dict[str, object] = {
        "actors": [],
        "characters": [],
        "props": [],
        "places": [],
        "locations": [],
        "environments": [],
        "geo_environments": [],
        "scenes": [],
        "phases": [],
        "blocking": {},
    }
    try:
        root = ET.fromstring(segment_xml)
    except ET.ParseError:
        return block

    def collect_list(tag: str, item_tag: str) -> list[dict]:
        parent = root.find(tag)
        if parent is None:
            return []
        items = []
        for item in parent.findall(item_tag):
            name = parse_xml_attr(item, "name")
            entry = {"name": name} if name else {}
            role = item.get("role")
            if role:
                entry["role"] = role
            if entry:
                items.append(entry)
        return items

    block["actors"] = collect_list("actors", "actor")
    block["characters"] = collect_list("characters", "character")
    block["props"] = collect_list("props", "prop")
    block["places"] = collect_list("places", "place")
    block["locations"] = collect_list("locations", "location")
    block["environments"] = collect_list("environments", "environment")
    block["geo_environments"] = collect_list("geo_environments", "geo_environment")

    scenes = []
    scenes_node = root.find("scenes")
    if scenes_node is not None:
        for scene in scenes_node.findall("scene"):
            scene_entry = {}
            scene_id = parse_xml_attr(scene, "id")
            if scene_id:
                scene_entry["scene_id"] = scene_id
            label = parse_xml_attr(scene, "label")
            if label:
                scene_entry["title"] = label
            location = parse_xml_attr(scene, "location")
            if location:
                scene_entry["location"] = location
            if scene_entry:
                scenes.append(scene_entry)
    if scenes:
        actor_names = [item.get("name") for item in block.get("actors", []) if item.get("name")]
        for scene_entry in scenes:
            if actor_names:
                scene_entry["actorsInvolved"] = actor_names
    block["scenes"] = scenes

    phases_node = root.find("phases")
    if phases_node is not None:
        phases = []
        for phase in phases_node.findall("phase"):
            phase_entry = {
                "index": parse_xml_attr(phase, "index"),
                "label": parse_xml_attr(phase, "label"),
                "changes": [],
            }
            for change in phase.findall("change"):
                change_entry = {
                    "target": parse_xml_attr(change, "target"),
                    "name": parse_xml_attr(change, "name"),
                    "description": parse_xml_attr(change, "description"),
                }
                phase_entry["changes"].append(change_entry)
            phases.append(phase_entry)
        block["phases"] = phases

    blocking_node = root.find("blocking")
    if blocking_node is not None:
        anchors = []
        anchors_node = blocking_node.find("anchors")
        if anchors_node is not None:
            for anchor in anchors_node.findall("anchor"):
                anchors.append(
                    {
                        "id": parse_xml_attr(anchor, "id"),
                        "location": parse_xml_attr(anchor, "location"),
                        "note": parse_xml_attr(anchor, "note"),
                    }
                )
        paths = []
        paths_node = blocking_node.find("paths")
        if paths_node is not None:
            for path in paths_node.findall("path"):
                paths.append(
                    {
                        "from": parse_xml_attr(path, "from"),
                        "to": parse_xml_attr(path, "to"),
                        "motion": parse_xml_attr(path, "motion"),
                        "duration_sec": parse_xml_attr(path, "duration_sec"),
                    }
                )
        block["blocking"] = {"anchors": anchors, "paths": paths}

    return block


def parse_segment_identifiers(segment_xml: str) -> tuple[str | None, str | None, str | None]:
    try:
        root = ET.fromstring(segment_xml)
    except ET.ParseError:
        return None, None, None
    return (
        parse_xml_attr(root, "chapter_id") or None,
        parse_xml_attr(root, "segment_label") or None,
        parse_xml_attr(root, "verse_id") or None,
    )


def _attach_phase_changes(block: dict) -> None:
    phases = block.get("phases") or []
    if not phases:
        return
    change_by_target: dict[str, list[str]] = {}
    for phase in phases:
        for change in phase.get("changes", []) if isinstance(phase, dict) else []:
            if not isinstance(change, dict):
                continue
            target = str(change.get("target") or "").strip()
            if not target:
                continue
            name = str(change.get("name") or "").strip()
            description = str(change.get("description") or "").strip()
            if name and description:
                value = f"{name}: {description}"
            else:
                value = description or name
            if not value:
                continue
            change_by_target.setdefault(target.lower(), []).append(value)

    if not change_by_target:
        return

    for key in (
        "actors",
        "characters",
        "props",
        "places",
        "locations",
        "environments",
        "geo_environments",
    ):
        items = block.get(key) or []
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name") or "").strip()
            if not name:
                continue
            changes = change_by_target.get(name.lower())
            if not changes:
                continue
            existing = item.get("changes") or []
            if not isinstance(existing, list):
                existing = []
            for change in changes:
                if change not in existing:
                    existing.append(change)
            item["changes"] = existing


def load_analysis_from_mcp(
    *,
    client: SimpleMcpClient,
    story_id: str,
    chapters: list[int],
    chapter_padding: int,
    segment_label: str,
    segment_padding: int,
    segment_type_default: str,
    analysis_types: list[str],
    include_raw: bool,
    lookup_mode: str = "qdrant",
    engram_queries: list[str] | None = None,
    engram_limit_per_query: int = 20,
    engram_min_shared_hashes: int = 1,
) -> list[dict]:
    segment_map: dict[tuple[str, str], dict] = {}
    mode = (lookup_mode or "qdrant").strip().lower()
    if mode not in {"qdrant", "engram", "hybrid"}:
        warn(f"Unknown lookup_mode '{lookup_mode}', fallback to 'qdrant'.")
        mode = "qdrant"

    query_list = [str(q).strip() for q in (engram_queries or []) if str(q).strip()]
    if mode in {"engram", "hybrid"} and not query_list:
        warn("lookup_mode uses Engram, but no engram_queries provided.")

    for chapter in chapters:
        chapter_id = f"{chapter:0{chapter_padding}d}"
        for analysis_type in analysis_types:
            point_map: dict[str, dict] = {}

            if mode in {"qdrant", "hybrid"}:
                qdrant_points = fetch_analysis_points(client, story_id, chapter_id, analysis_type)
                for point in qdrant_points:
                    if not isinstance(point, dict):
                        continue
                    point_id = str(point.get("id") or "").strip()
                    payload = point.get("payload", {}) if isinstance(point.get("payload"), dict) else {}
                    key = point_id or (
                        f"{payload.get('chapter_id')}"
                        f"::{payload.get('segment_label')}"
                        f"::{payload.get('analysis_type', analysis_type)}"
                    )
                    if key in point_map:
                        point_map[key] = merge_points(point_map[key], point)
                    else:
                        point_map[key] = point

            if mode in {"engram", "hybrid"} and query_list:
                engram_points = fetch_analysis_points_engram(
                    client=client,
                    story_id=story_id,
                    chapter_id=chapter_id,
                    chapter_padding=chapter_padding,
                    analysis_type=analysis_type,
                    queries=query_list,
                    limit_per_query=engram_limit_per_query,
                    min_shared_hashes=engram_min_shared_hashes,
                )
                for point in engram_points:
                    if not isinstance(point, dict):
                        continue
                    point_id = str(point.get("id") or "").strip()
                    payload = point.get("payload", {}) if isinstance(point.get("payload"), dict) else {}
                    key = point_id or (
                        f"{payload.get('chapter_id')}"
                        f"::{payload.get('segment_label')}"
                        f"::{payload.get('analysis_type', analysis_type)}"
                    )
                    if key in point_map:
                        point_map[key] = merge_points(point_map[key], point)
                    else:
                        point_map[key] = point

            points = list(point_map.values())
            for point in points:
                payload = point.get("payload", {}) if isinstance(point, dict) else {}
                content = payload.get("content") or payload.get("Content") or ""
                if not isinstance(content, str):
                    content = ""

                seg_chapter, seg_label, seg_verse = parse_segment_identifiers(content)
                seg_chapter = seg_chapter or payload.get("chapter_id") or chapter_id
                seg_label = seg_label or payload.get("segment_label") or ""
                if not seg_label:
                    continue

                label_value, label_index, label_type = parse_segment_label_value(seg_label)
                resolved_label = label_value or seg_label
                segment_index = label_index if label_index is not None else parse_int(seg_label)
                resolved_type = label_type or segment_type_default

                key = (str(seg_chapter), str(resolved_label))
                entry = segment_map.setdefault(
                    key,
                    {
                        "source_id": payload.get("analysis_id") or payload.get("unit_ref") or "",
                        "source_path": "",
                        "chapter": parse_int(seg_chapter),
                        "segment_index": segment_index,
                        "segment_label": resolved_label,
                        "segment_type": resolved_type,
                        "segment_summary": "",
                        "scene_label": "",
                        "analysis_blocks": [],
                        "analysis_layers": {},
                        "raw_content": "",
                        "lineage": payload.get("lineage") or None,
                        "verse_id": seg_verse or payload.get("verse_id") or None,
                    },
                )

                if analysis_type == SCENE_ANALYSIS_TYPE:
                    block = parse_scene_segment_xml(content)
                    _attach_phase_changes(block)
                    if block:
                        entry["analysis_blocks"].append(block)
                else:
                    entry["analysis_layers"][analysis_type] = {"raw": content}
                    if analysis_type == "analysis_llm" and content:
                        blocks = extract_json_blocks(content)
                        if not blocks:
                            payload = load_json_text(content)
                            if payload is not None:
                                if isinstance(payload, list):
                                    blocks = payload
                                else:
                                    blocks = [payload]
                        for block in blocks:
                            if isinstance(block, dict):
                                entry["analysis_blocks"].append(block)

                if include_raw and content:
                    entry["raw_content"] += content + "\n"

    return list(segment_map.values())




def parse_int(value):
    if value is None:
        return None
    try:
        return int(str(value).strip())
    except (ValueError, TypeError):
        return None


def parse_segment_label_value(raw_label):
    if raw_label is None:
        return None, None, None
    label = str(raw_label).strip()
    if not label:
        return None, None, None
    if label.isdigit():
        return None, parse_int(label), None
    lowered = label.lower()
    for seg_type, regex in (
        ("segment", SEGMENT_RE),
        ("verse", VERSE_RE),
        ("scene", SCENE_RE),
        ("part", PART_RE),
    ):
        if lowered.startswith(seg_type):
            match = regex.search(lowered)
            idx = parse_int(match.group(1)) if match else None
            return label, idx, seg_type
    match = re.search(r"(\d+)", lowered)
    idx = parse_int(match.group(1)) if match else None
    return label, idx, None


def extract_json_blocks(text):
    blocks = []
    if not text:
        return blocks
    for match in JSON_BLOCK_RE.finditer(text):
        raw = match.group(1)
        try:
            blocks.append(json.loads(raw))
        except json.JSONDecodeError:
            continue
    if blocks:
        return blocks
    stripped = text.strip()
    if not stripped:
        return blocks
    try:
        blocks.append(json.loads(stripped))
        return blocks
    except json.JSONDecodeError:
        pass
    decoder = json.JSONDecoder()
    for idx, ch in enumerate(stripped):
        if ch not in "{[":
            continue
        try:
            payload, _ = decoder.raw_decode(stripped[idx:])
            blocks.append(payload)
            return blocks
        except json.JSONDecodeError:
            continue
    return blocks


def load_json_text(text):
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def resolve_segment_dir(
    source_path,
    filmsets_root,
    chapter_label,
    chapter_padding,
    chapter_value,
    segment_label,
):
    if source_path:
        try:
            source_path = Path(source_path)
        except TypeError:
            source_path = None
        if source_path and source_path.exists():
            parent = source_path.parent
            if segment_label and parent.name == segment_label:
                return parent
            if segment_label:
                candidate = parent / segment_label
                if candidate.exists():
                    return candidate
            return parent

    if not filmsets_root or not chapter_value or not segment_label:
        return None
    try:
        chapter_int = int(chapter_value)
    except (ValueError, TypeError):
        return None
    chapter_folder = f"{chapter_label}_{chapter_int:0{chapter_padding}d}"
    candidate = Path(filmsets_root) / chapter_folder / segment_label
    if candidate.exists():
        return candidate
    return None


def load_analysis_layers(segment_dir):
    if not segment_dir:
        return {}
    layers = {}
    for key, filename in ANALYSIS_LAYER_FILES.items():
        path = segment_dir / filename
        if not path.exists():
            continue
        try:
            raw = path.read_text(encoding="utf-8").strip()
        except OSError:
            continue
        payload = load_json_text(raw)
        if payload is None:
            blocks = extract_json_blocks(raw)
            payload = blocks[0] if len(blocks) == 1 else (blocks or None)
        if payload is None:
            layers[key] = {"path": str(path), "raw": raw}
        else:
            layers[key] = {"path": str(path), "payload": payload}
    return layers


def extract_from_path(source_path):
    if not source_path:
        return None, None, None, None
    chapter = None
    segment_index = None
    segment_type = None
    scene_index = None
    match = CHAPTER_RE.search(source_path)
    if match:
        chapter = parse_int(match.group(1))
    match = VERSE_RE.search(source_path)
    if match:
        segment_index = parse_int(match.group(1))
        segment_type = "verse"
    match = SEGMENT_RE.search(source_path)
    if match and segment_index is None:
        segment_index = parse_int(match.group(1))
        segment_type = "segment"
    match = SCENE_RE.search(source_path)
    if match:
        scene_index = parse_int(match.group(1))
        if segment_index is None:
            segment_index = scene_index
            segment_type = "scene"
    match = PART_RE.search(source_path)
    if match and segment_index is None:
        segment_index = parse_int(match.group(1))
        segment_type = "part"
    return chapter, segment_index, segment_type, scene_index


def build_source_id(source_path, row_index, mode):
    if mode == "hash":
        base = source_path or f"row_{row_index}"
        return hashlib.sha1(base.encode("utf-8")).hexdigest()[:12]
    if source_path:
        return source_path.replace("\\", "/")
    return f"row_{row_index}"


def scan_analysis_files(root: Path):
    index = {}
    if not root or not root.exists():
        return index
    for path in root.rglob("analysis_llm.*"):
        chapter, segment_index, segment_type, _scene_index = extract_from_path(str(path))
        if chapter is None:
            continue
        key = (chapter, segment_index, segment_type)
        index.setdefault(key, []).append(str(path))
    return index


def find_field(row, names):
    for name in names:
        if name in row and row[name]:
            return row[name]
    return None


def main():
    parser = argparse.ArgumentParser(description="Build analysis_master.jsonl from CSV + analysis outputs.")
    parser.add_argument("--story-root", help="Story root path (defaults to engine_config default_story_root).")
    parser.add_argument("--story-config", help="Path to story_config.json (overrides story-root).")
    parser.add_argument("--csv", help="CSV input path (defaults to story_config analysis_progress_csv_path).")
    parser.add_argument("--analysis-dir", help="Optional analysis directory to scan for analysis_llm files.")
    parser.add_argument("--output", help="Output JSONL path (defaults to story_config analysis_master_path).")
    parser.add_argument("--from-mcp", action="store_true", help="Build analysis_master.jsonl from MCP/Qdrant.")
    parser.add_argument("--chapters", type=int, nargs="*", help="Chapter numbers to load (required for --from-mcp).")
    parser.add_argument(
        "--analysis-types",
        nargs="*",
        default=[
            "graphematic",
            "morphologic",
            "synthactic",
            "semantic_historical",
            SCENE_ANALYSIS_TYPE,
        ],
        help="Analysis types to load when using --from-mcp.",
    )
    parser.add_argument("--mcp-command", default="dotnet")
    parser.add_argument(
        "--mcp-args",
        nargs="*",
        default=[
            "run",
            "--project",
            str(
                Path(__file__).resolve().parents[2]
                / "tools"
                / "exevision"
                / "vector_mcp"
                / "VectorMcpServer"
            ),
        ],
    )
    parser.add_argument(
        "--mcp-cwd",
        default=str(
            Path(__file__).resolve().parents[2]
            / "tools"
            / "exevision"
            / "vector_mcp"
            / "VectorMcpServer"
        ),
    )
    parser.add_argument("--mcp-debug-log", default=None)
    parser.add_argument(
        "--mcp-lookup-mode",
        choices=("qdrant", "engram", "hybrid"),
        default="qdrant",
        help="MCP retrieval mode for --from-mcp.",
    )
    parser.add_argument(
        "--mcp-engram-query",
        action="append",
        default=[],
        help="Query seed for Engram lookup (repeatable).",
    )
    parser.add_argument(
        "--mcp-engram-limit-per-query",
        type=int,
        default=20,
        help="Max Engram results per query.",
    )
    parser.add_argument(
        "--mcp-engram-min-shared-hashes",
        type=int,
        default=1,
        help="Minimum shared hash count for Engram matches.",
    )
    parser.add_argument("--include-raw", action="store_true", help="Include raw LLM content in output.")
    parser.add_argument("--max-raw-chars", type=int, default=0, help="Trim raw content to N chars (0 = no trim).")
    parser.add_argument("--id-mode", choices=("path", "hash"), default="path", help="Source ID strategy.")
    parser.add_argument("--no-extract-json", action="store_true", help="Disable JSON block extraction.")
    args = parser.parse_args()

    story_config, story_root, repo_root = load_story_config(
        story_root=args.story_root,
        story_config_path=args.story_config,
    )

    if args.from_mcp:
        if not args.chapters:
            raise SystemExit("--chapters is required when using --from-mcp.")
        output_path = args.output or story_config.get("analysis_master_path")
        if not output_path:
            raise SystemExit("No output path configured (analysis_master_path).")
        output_path = resolve_path(output_path, repo_root)
        ensure_dir(output_path.parent)

        chapter_padding = int(story_config.get("chapter_index_padding", 3))
        segment_label = story_config.get("segment_label", "segment")
        segment_padding = int(story_config.get("segment_index_padding", 3))
        segment_type_default = story_config.get("segment_type", "segment")
        story_id = story_config.get("story_id") or ""
        engram_queries = [str(q).strip() for q in (args.mcp_engram_query or []) if str(q).strip()]
        if args.mcp_lookup_mode in {"engram", "hybrid"} and not engram_queries:
            engram_queries = [
                f"story {story_id} chapter {chapter:0{chapter_padding}d}"
                for chapter in args.chapters
            ]

        debug_log = Path(args.mcp_debug_log) if args.mcp_debug_log else None
        client = SimpleMcpClient(
            command=args.mcp_command,
            args=args.mcp_args,
            cwd=args.mcp_cwd,
            debug_log=debug_log,
        )
        try:
            records = load_analysis_from_mcp(
                client=client,
                story_id=story_id,
                chapters=args.chapters,
                chapter_padding=chapter_padding,
                segment_label=segment_label,
                segment_padding=segment_padding,
                segment_type_default=segment_type_default,
                analysis_types=args.analysis_types,
                include_raw=args.include_raw,
                lookup_mode=args.mcp_lookup_mode,
                engram_queries=engram_queries,
                engram_limit_per_query=args.mcp_engram_limit_per_query,
                engram_min_shared_hashes=args.mcp_engram_min_shared_hashes,
            )
        finally:
            client.close()

        with output_path.open("w", encoding="utf-8") as out:
            for record in records:
                out.write(json.dumps(record, ensure_ascii=False) + "\n")
        print(f"Wrote analysis master: {output_path}")
        return

    csv_path = args.csv or story_config.get("analysis_progress_csv_path")
    if not csv_path:
        csv_path = str(Path(story_config["data_root"]) / "raw" / "first_analysis_progress_python.csv")
    csv_path = resolve_path(csv_path, repo_root)
    if not csv_path.exists():
        raise SystemExit(f"CSV not found: {csv_path}")

    output_path = args.output or story_config.get("analysis_master_path")
    if not output_path:
        raise SystemExit("No output path configured (analysis_master_path).")
    output_path = resolve_path(output_path, repo_root)
    ensure_dir(output_path.parent)

    segment_label = story_config.get("segment_label", "segment")
    segment_type_default = story_config.get("segment_type", "segment")
    segment_padding = int(story_config.get("segment_index_padding", 3))
    scene_label = story_config.get("scene_label", "scene")
    scene_padding = int(story_config.get("scene_index_padding", 3))
    chapter_label = story_config.get("chapter_label", "chapter")
    chapter_padding = int(story_config.get("chapter_index_padding", 3))
    filmsets_root = resolve_path(story_config.get("filmsets_root"), repo_root)

    analysis_dir = args.analysis_dir
    analysis_index = {}
    if analysis_dir:
        analysis_dir_path = resolve_path(analysis_dir, repo_root)
        analysis_index = scan_analysis_files(analysis_dir_path)

    with csv_path.open("r", encoding="utf-8") as f, output_path.open("w", encoding="utf-8") as out:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=1):
            source_path = find_field(row, ["SourcePath", "source_path", "Path", "path", "Source", "source", "File", "file"])
            chapter = parse_int(find_field(row, ["ChapterID", "chapter", "Chapter", "chapter_id"]))
            segment_index = parse_int(find_field(row, ["Verse", "verse", "Segment", "segment", "Scene", "scene", "Part", "part"]))
            segment_type = find_field(row, ["segment_type", "SegmentType", "SegmentType"]) or None
            segment_label_raw = find_field(row, ["SegmentLabel", "segment_label", "segmentLabel"])
            scene_index = parse_int(find_field(row, ["SceneIndex", "scene_index"]))

            segment_label_value = None
            label_value, label_index, label_type = parse_segment_label_value(segment_label_raw)
            if label_value:
                segment_label_value = label_value
            if segment_index is None and label_index is not None:
                segment_index = label_index
            if not segment_type and label_type:
                segment_type = label_type

            if source_path:
                parsed_chapter, parsed_segment, parsed_type, parsed_scene = extract_from_path(source_path)
                chapter = chapter if chapter is not None else parsed_chapter
                segment_index = segment_index if segment_index is not None else parsed_segment
                segment_type = segment_type or parsed_type
                scene_index = scene_index if scene_index is not None else parsed_scene

            segment_type = segment_type or segment_type_default
            if segment_index is None:
                segment_index = 0
            if not segment_label_value:
                segment_label_value = f"{segment_label}_{segment_index:0{segment_padding}d}"
            scene_label_value = ""
            if scene_index is not None:
                scene_label_value = f"{scene_label}_{scene_index:0{scene_padding}d}"

            summary = find_field(row, ["Summary", "summary", "ShortSummary", "short_summary"]) or ""
            raw_content = find_field(row, ["RawContent", "raw_content", "Content", "content", "Text", "text"]) or ""

            if args.max_raw_chars and raw_content:
                raw_content = raw_content[: args.max_raw_chars]

            record = {
                "source_id": build_source_id(source_path, idx, args.id_mode),
                "source_path": source_path or "",
                "chapter": chapter if chapter is not None else "",
                "segment_index": segment_index,
                "segment_label": segment_label_value,
                "segment_type": segment_type,
                "source_index": idx,
                "summary": summary,
                "scene_index": scene_index,
                "scene_label": scene_label_value,
            }

            if not args.no_extract_json and raw_content:
                record["analysis_blocks"] = extract_json_blocks(raw_content)

            if args.include_raw:
                record["raw_content"] = raw_content

            if analysis_index:
                key = (chapter, segment_index, segment_type)
                if key in analysis_index:
                    record["analysis_paths"] = analysis_index[key]

            segment_dir = resolve_segment_dir(
                source_path,
                filmsets_root,
                chapter_label,
                chapter_padding,
                chapter,
                segment_label_value,
            )
            analysis_layers = load_analysis_layers(segment_dir)
            if analysis_layers:
                record["analysis_layers"] = analysis_layers

            out.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Wrote analysis master: {output_path}")


if __name__ == "__main__":
    main()
