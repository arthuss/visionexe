from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

from rag_utils import embed_texts, load_config, request_json, qdrant_headers
from visionexe_paths import load_engine_config, load_story_config, resolve_repo_root, resolve_path


REPO_ROOT = resolve_repo_root()
DEFAULT_PROMPT_PATH = REPO_ROOT / "docs" / "drehbuch_narrativ.md"
DEFAULT_RAG_CONFIG = REPO_ROOT / "engine" / "workers" / "rag_config_small.json"
FALLBACK_RAG_CONFIG = REPO_ROOT / "engine" / "scripts" / "rag_config_small.json"


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def extract_prompt_templates(prompt_path: Path) -> list[str]:
    text = read_text(prompt_path)
    blocks = re.findall(r"```(?:[a-zA-Z]+)?\n(.*?)```", text, flags=re.DOTALL)
    return [block.strip() for block in blocks if block.strip()]


def resolve_llm_profiles() -> tuple[dict, str]:
    engine_config = load_engine_config()
    profiles_path = resolve_path(engine_config.get("llm_profiles_path"), REPO_ROOT)
    if not profiles_path or not profiles_path.exists():
        return {}, engine_config.get("default_llm_profile") or ""
    try:
        profiles = json.loads(profiles_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        profiles = {}
    return profiles, engine_config.get("default_llm_profile") or ""


def openai_compat_chat(profile: dict, prompt: str, temperature: float) -> str:
    base_url = (profile.get("base_url") or "").rstrip("/")
    if base_url.endswith("/v1"):
        endpoint = f"{base_url}/chat/completions"
    else:
        endpoint = f"{base_url}/v1/chat/completions"
    payload = {
        "model": profile.get("model") or "",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
    }
    headers = {}
    api_key = profile.get("api_key") or ""
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    status, data = request_json("POST", endpoint, payload=payload, headers=headers, timeout=180)
    if status < 200 or status >= 300:
        raise RuntimeError(f"LLM error {status}: {data}")
    if isinstance(data, dict):
        choices = data.get("choices") or []
        if choices:
            message = choices[0].get("message") or {}
            content = message.get("content")
            if isinstance(content, str):
                return content.strip()
            text = choices[0].get("text")
            if isinstance(text, str):
                return text.strip()
    raise RuntimeError("LLM response missing content.")


def build_analysis_text(chapter_path: Path, story_root: Path) -> str:
    sections = []
    story_text = read_text(chapter_path / "story.txt")
    if story_text:
        sections.append(f"[RAW_TEXT]\n{story_text}")

    analysis_linguistik = read_text(chapter_path / "analysis_linguistik" / "story.txt")
    if analysis_linguistik:
        sections.append(f"[ANALYSIS_LINGUISTIK]\n{analysis_linguistik}")

    chapter_briefing = read_text(chapter_path / "chapter_briefing.md")
    if chapter_briefing:
        sections.append(f"[CHAPTER_BRIEFING]\n{chapter_briefing}")

    concept_text = read_text(chapter_path / "concept_engine" / "mechanic_concept.txt")
    if concept_text:
        sections.append(f"[CONCEPT_ENGINE]\n{concept_text}")

    writing_guide = read_text(story_root / "briefings" / "writing.md")
    if writing_guide:
        sections.append(f"[WRITING_GUIDE]\n{writing_guide}")

    adobe_format = read_text(story_root / "briefings" / "adobe_drehbuch.md")
    if adobe_format:
        sections.append(f"[ADOBE_FORMAT]\n{adobe_format}")

    format_pdf = story_root / "briefings" / "Formatierungsregeln.pdf"
    if format_pdf.exists():
        sections.append(f"[FORMAT_PDF_PATH]\n{format_pdf}")

    analysis_root_files = [
        "analysis_llm.txt",
        "analysis_llm_graphematic.txt",
        "analysis_llm_morphologic.txt",
        "analysis_llm_synthactic.txt",
        "analysis_llm_semantic_historical.txt",
    ]
    for filename in analysis_root_files:
        content = read_text(chapter_path / filename)
        if content:
            sections.append(f"[{filename.upper()}]\n{content}")

    return "\n\n".join(sections).strip()


def build_rag_context(config_path: Path, chapter_label: str, queries: list[str], limit: int) -> str:
    config = load_config(str(config_path))
    headers = qdrant_headers(config)
    results = []
    for query in queries:
        vector = embed_texts(config, [query])[0]
        payload = {
            "vector": vector,
            "limit": limit,
            "with_payload": True,
            "filter": {"must": [{"key": "chapter", "match": {"value": chapter_label}}]},
        }
        url = f"{config['qdrant_url']}/collections/{config['collection']}/points/search"
        status, data = request_json("POST", url, payload=payload, headers=headers)
        if status < 200 or status >= 300:
            continue
        hits = data.get("result", [])
        for hit in hits:
            payload = hit.get("payload", {})
            text = (payload.get("text") or "").strip()
            if not text:
                continue
            results.append(f"[{query}] {text}")
    if not results:
        return ""
    return "\n\n".join(results)


def normalize_chapter_label(story_config: dict, chapter_num: int) -> str:
    chapter_label = story_config.get("chapter_label", "chapter")
    chapter_padding = int(story_config.get("chapter_index_padding", 3))
    return f"{chapter_label}_{chapter_num:0{chapter_padding}d}"


def resolve_filmsets_root(story_config: dict, repo_root: Path) -> Path:
    filmsets_root = story_config.get("filmsets_root")
    if not filmsets_root:
        raise SystemExit("filmsets_root missing in story_config.json")
    resolved = resolve_path(filmsets_root, repo_root)
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a narrative screenplay (spec script).")
    parser.add_argument("--start", type=int, default=1, help="Start chapter number.")
    parser.add_argument("--end", type=int, default=None, help="End chapter number (inclusive).")
    parser.add_argument("--chapter", type=int, help="Single chapter number override.")
    parser.add_argument("--story-root", help="Story root (defaults to engine_config default_story_root).")
    parser.add_argument("--story-config", help="Path to story_config.json (overrides story-root).")
    parser.add_argument("--prompt-path", default=str(DEFAULT_PROMPT_PATH), help="Path to narration prompt file.")
    parser.add_argument("--genre-profile", default="drama", help="Genre profile label.")
    parser.add_argument("--worldview-profile", default="", help="Worldview profile label.")
    parser.add_argument("--tone-dials", default="pacing=slow;dialogue_density=low;darkness=dark", help="Tone dials.")
    parser.add_argument("--llm-profile", default="", help="LLM profile name (engine/config/llm_profiles.json).")
    parser.add_argument("--model", default="", help="Override model name.")
    parser.add_argument("--temperature", type=float, default=0.4, help="LLM temperature.")
    parser.add_argument("--use-rag", action="store_true", help="Attach RAG context per chapter.")
    parser.add_argument("--rag-config", default="", help="RAG config path.")
    parser.add_argument("--rag-query", action="append", help="Custom RAG query (repeatable).")
    parser.add_argument("--rag-limit", type=int, default=3, help="Max results per query.")
    args = parser.parse_args()

    story_config, story_root, repo_root = load_story_config(
        story_root=args.story_root,
        story_config_path=args.story_config,
    )
    filmsets_root = resolve_filmsets_root(story_config, repo_root)
    timeline_id = story_config.get("timeline_default") or "timeline_01"
    timeline_profile_path = story_config.get("timeline_profiles", {}).get(timeline_id)
    timeline_profile_path = resolve_path(timeline_profile_path, repo_root) if timeline_profile_path else None
    timeline_profile = read_text(timeline_profile_path) if timeline_profile_path else ""

    prompt_templates = extract_prompt_templates(Path(args.prompt_path))
    if len(prompt_templates) < 3:
        raise SystemExit("Prompt file must contain at least 3 fenced code blocks.")
    prompt_blueprint, prompt_draft, prompt_polish = prompt_templates[:3]

    profiles, default_profile = resolve_llm_profiles()
    llm_profile_name = args.llm_profile or ("lmstudio_local" if "lmstudio_local" in profiles else default_profile)
    llm_profile = profiles.get(llm_profile_name)
    if not llm_profile:
        raise SystemExit(f"LLM profile not found: {llm_profile_name}")
    if args.model:
        llm_profile = dict(llm_profile, model=args.model)

    start = args.chapter or args.start
    end = args.chapter or args.end or start

    rag_config_path = args.rag_config
    if not rag_config_path:
        rag_config_path = str(DEFAULT_RAG_CONFIG if DEFAULT_RAG_CONFIG.exists() else FALLBACK_RAG_CONFIG)
    rag_queries = args.rag_query or [
        "chapter summary",
        "key beats",
        "characters and locations",
        "visual motifs",
    ]

    for chapter_num in range(start, end + 1):
        chapter_label = normalize_chapter_label(story_config, chapter_num)
        chapter_path = filmsets_root / chapter_label
        if not chapter_path.exists():
            print(f"Skip missing: {chapter_path}")
            continue

        raw_text = read_text(chapter_path / "story.txt")
        analysis_text = build_analysis_text(chapter_path, story_root)
        if not analysis_text:
            analysis_text = read_text(chapter_path / "analysis_llm.txt")
        if not raw_text:
            raw_text = read_text(chapter_path / "chapter.txt")

        worldview_profile = args.worldview_profile or timeline_id
        if timeline_profile:
            worldview_profile = f"{worldview_profile}\n{timeline_profile}"

        rag_context = ""
        if args.use_rag:
            rag_context = build_rag_context(Path(rag_config_path), chapter_label, rag_queries, args.rag_limit)
            if rag_context:
                analysis_text = "\n\n".join([analysis_text, "[RAG_CONTEXT]\n" + rag_context]).strip()

        prompt1 = prompt_blueprint.format(
            CHAPTER_NUM=str(chapter_num),
            GENRE_PROFILE=args.genre_profile,
            WORLDVIEW_PROFILE=worldview_profile,
            TONE_DIALS=args.tone_dials,
            RAW_TEXT=raw_text,
            ANALYSIS_TEXT=analysis_text,
        )
        blueprint = openai_compat_chat(llm_profile, prompt1, args.temperature)

        prompt2 = prompt_draft.format(
            CHAPTER_NUM=str(chapter_num),
            SCENE_PLAN_FROM_PROMPT_1=blueprint,
            GENRE_PROFILE=args.genre_profile,
            WORLDVIEW_PROFILE=worldview_profile,
            TONE_DIALS=args.tone_dials,
            RAW_TEXT=raw_text,
            ANALYSIS_TEXT=analysis_text,
        )
        draft_script = openai_compat_chat(llm_profile, prompt2, args.temperature)

        prompt3 = prompt_polish.format(
            DRAFT_SCRIPT_TEXT=draft_script,
            GENRE_PROFILE=args.genre_profile,
            WORLDVIEW_PROFILE=worldview_profile,
            TONE_DIALS=args.tone_dials,
            RAW_TEXT=raw_text,
        )
        final_script = openai_compat_chat(llm_profile, prompt3, args.temperature)

        output_path = chapter_path / "DREHBUCH_NARRATIV.md"
        output_path.write_text(final_script.strip() + "\n", encoding="utf-8")
        print(f"Wrote: {output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
