import argparse
from pathlib import Path

from visionexe_paths import ensure_dir, load_story_config, resolve_path


TYPE_PREFIXES = {
    "character": "CHAR",
    "prop": "PROP",
    "requisite": "REQ",
    "environment": "ENV",
    "set_environment": "SETENV",
    "geo_environment": "GEOENV",
    "scene": "SCENE",
    "location": "LOC",
    "place": "PLACE",
}


def build_prompt(corpus_text: str) -> str:
    prefix_lines = "\n".join(f"- {key}: {value}_" for key, value in TYPE_PREFIXES.items())
    return f"""ROLE: Subject Extractor / Canonicalizer.
TASK: Read the raw corpus and create canonical subjects using MCP tools only.

HARD RULES:
- Use ONLY the corpus. Do NOT invent new subjects.
- Canonicalize spelling variants into one subject_id.
- Prefer meaningful canonical names (no fragments).
- If unsure, keep the subject but add a note (add_subject_note).
- Type rule: use `prop` only for subject-bound items; scene dressing goes to `requisite`.

SUBJECT TYPES + ID PREFIXES:
{prefix_lines}

TOOL USAGE (MCP):
- For each canonical subject: upsert_subject {{subject_id, name, subject_type, status, meta}}
- For spelling variants: add_aliases {{subject_id, aliases, source}}
- For uncertainties/risks: add_subject_note {{subject_id, note}}
- If you discover duplicates in this run: merge_subjects {{canonical_id, merge_ids, reason}}

OUTPUT:
- Use ONLY tool calls. If you must reply, reply with: done

CORPUS (RAW JSON OR JSONL):
{corpus_text}
""".strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a raw prompt for MCP-driven subject extraction.")
    parser.add_argument("--story-root", help="Story root path (defaults to engine_config default_story_root).")
    parser.add_argument("--story-config", help="Path to story_config.json (overrides story-root).")
    parser.add_argument("--corpus", help="Path to the corpus JSON/JSONL file.")
    parser.add_argument("--output", help="Output prompt file path.")
    args = parser.parse_args()

    story_config, _story_root, repo_root = load_story_config(
        story_root=args.story_root,
        story_config_path=args.story_config,
    )

    corpus_path = resolve_path(
        args.corpus or "stories/template/subjects/subject_corpus.json",
        repo_root,
    )
    if not corpus_path.exists():
        raise SystemExit(f"Corpus not found: {corpus_path}")

    output_path = resolve_path(
        args.output or "stories/template/subjects/subject_registry_prompt.txt",
        repo_root,
    )

    corpus_text = corpus_path.read_text(encoding="utf-8", errors="replace")
    prompt = build_prompt(corpus_text)

    ensure_dir(output_path.parent)
    output_path.write_text(prompt, encoding="utf-8")
    print(f"Wrote subject registry prompt: {output_path}")


if __name__ == "__main__":
    main()
