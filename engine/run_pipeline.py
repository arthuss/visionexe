import argparse
import csv
import datetime as dt
import json
import os
import unicodedata
from pathlib import Path

from analysis.io import iter_text_files, read_text, save_json, sha256_text
from analysis.llm import call_gemini, call_ollama
from analysis.prompts import (
    BACK_TRANSLATION_PROMPT_VERSION,
    MORPHOLOGY_PROMPT_VERSION,
    SEMANTIC_PROMPT_VERSION,
    SYNTAX_PROMPT_VERSION,
    TRANSLATION_PROMPT_VERSION,
    build_back_translation_prompt,
    build_morphology_prompt,
    build_semantic_prompt,
    build_syntax_prompt,
    build_translation_prompt,
)
from analysis.rules.rule_engine import RuleConfig, apply_rules
from analysis.rules.rules_context_invariance import apply_context_penalty, compare_context_windows
from analysis.tokenization import tokenize, tokens_to_payload
from analysis.validators import validate_payload


ENGINE_ROOT = Path(__file__).resolve().parent
REPO_ROOT = ENGINE_ROOT.parent
SCHEMA_PATH = REPO_ROOT / "data" / "schemas" / "gez_morphology.schema.json"
TAGSET_PATH = ENGINE_ROOT / "analysis" / "tagsets" / "gez_pos_1.json"


def parse_json_payload(text: str) -> dict | None:
    if not text:
        return None
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    candidate = text[start:end + 1]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        return None


def load_tagset() -> dict:
    return json.loads(TAGSET_PATH.read_text(encoding="utf-8"))


def build_source(text: str, witness_id: str) -> dict:
    punctuation = [ch for ch in text if unicodedata.category(ch).startswith(("P", "S"))]
    removed_artifacts = []
    if any(ch.isdigit() for ch in text):
        removed_artifacts.append("digits")
    if any("a" <= ch.lower() <= "z" for ch in text):
        removed_artifacts.append("latin_text")
    if any(ch in "-–—" for ch in text):
        removed_artifacts.append("dash")
    return {
        "witness_id": witness_id,
        "graphematic_string": text,
        "normalization_policy": "none",
        "punctuation_markers": punctuation,
        "removed_artifacts": removed_artifacts,
        "uncertainties": [],
    }


def call_llm(stage: str, prompt: str, args, expect_json: bool = True) -> tuple[dict | None, dict]:
    gemini_model = args.model or os.environ.get("GEMINI_MODEL")
    model_name = gemini_model if args.use_gemini else (args.model or "gpt-oss:20b")
    model_label = model_name or "default"
    model_call = {
        "stage": stage,
        "provider": "gemini" if args.use_gemini else "ollama",
        "model": model_label,
        "temperature": args.temperature,
        "seed": args.seed if not args.use_gemini else None,
        "prompt_version": args.prompt_versions.get(stage, "unknown"),
        "duration_sec": None,
        "response_sha256": None,
    }
    if args.use_gemini:
        response, duration = call_gemini(prompt, gemini_model)
    else:
        response, duration = call_ollama(
            prompt,
            model_name,
            args.ollama_url,
            temperature=args.temperature,
            seed=args.seed,
        )
    model_call["duration_sec"] = duration
    if response:
        model_call["response_sha256"] = sha256_text(response)
    if expect_json:
        payload = parse_json_payload(response or "")
    else:
        payload = {"text": response} if response else None
    return payload, model_call


def normalize_morphology(tokens: list[dict], morph_payload: dict | None) -> list[dict]:
    options_by_token = {}
    if morph_payload:
        for token in morph_payload.get("tokens", []):
            token_id = token.get("token_id")
            if token_id:
                options_by_token[token_id] = token

    merged_tokens = []
    for token in tokens:
        token_id = token["token_id"]
        entry = options_by_token.get(token_id, {})
        options = entry.get("options") or []
        segmentation = entry.get("segmentation")
        if not options:
            options = [
                {
                    "option_id": "MISSING",
                    "pos": "N",
                    "analysis": {
                        "kind": "lexical",
                        "root": None,
                        "lemma": None,
                        "pattern": None,
                        "affixes": {"prefixes": [], "suffixes": [], "clitics": []},
                        "features": {},
                        "gloss": None,
                    },
                    "confidence": {"type": "ruled_out", "score": 0.0},
                    "evidence": {
                        "lexicon_status": "unattested",
                        "attestation": [],
                        "constraints_checked": [],
                        "notes": "LLM missing token options",
                    },
                }
            ]
        merged = dict(token)
        if segmentation:
            merged["segmentation"] = segmentation
        merged["options"] = _normalize_options(options)
        merged_tokens.append(merged)
    return merged_tokens


def _normalize_options(options: list[dict]) -> list[dict]:
    normalized = []
    for idx, option in enumerate(options):
        option_id = option.get("option_id") or chr(ord("A") + idx)
        analysis = option.get("analysis") or {}
        option["option_id"] = option_id
        option["analysis"] = {
            "kind": analysis.get("kind") or "lexical",
            "root": analysis.get("root"),
            "lemma": analysis.get("lemma"),
            "pattern": analysis.get("pattern"),
            "affixes": analysis.get("affixes") or {"prefixes": [], "suffixes": [], "clitics": []},
            "features": analysis.get("features") or {},
            "gloss": analysis.get("gloss"),
        }
        option.setdefault("confidence", {"type": "undecided", "score": None})
        option.setdefault("evidence", {
            "lexicon_status": "unattested",
            "attestation": [],
            "constraints_checked": [],
            "notes": "",
        })
        normalized.append(option)
    return normalized


def build_key_lemmas(tokens: list[dict]) -> list[str]:
    lemmas = []
    for token in tokens:
        for option in token.get("options", []):
            lemma = option.get("analysis", {}).get("lemma")
            if lemma:
                lemmas.append(lemma)
    return sorted(set(lemmas))


def run_context_invariance(
    args,
    base_text: str,
    function_words: list[dict],
    pos_tags: list[str],
    prev_texts: list[str],
) -> dict:
    if not args.window_tests:
        return {"status": "skipped", "reason": "window tests disabled"}

    base_tokens = tokens_to_payload(tokenize(base_text))
    base_count = len(base_tokens)

    def align_window_payload(payload: dict) -> dict | None:
        tokens = payload.get("tokens", [])
        if base_count == 0 or len(tokens) < base_count:
            return None
        aligned = tokens[-base_count:]
        for token, base_token in zip(aligned, base_tokens):
            token["token_id"] = base_token["token_id"]
        return {"tokens": aligned}

    window_texts = [base_text]
    prev_1 = prev_texts[-1] if len(prev_texts) >= 1 else None
    prev_2 = prev_texts[-2] if len(prev_texts) >= 2 else None
    if prev_1:
        window_texts.append(prev_1 + "\n" + base_text)
    if prev_1 and prev_2:
        window_texts.append(prev_2 + "\n" + prev_1 + "\n" + base_text)

    window_payloads = []
    model_calls = []
    for window_text in window_texts:
        tokens = tokens_to_payload(tokenize(window_text))
        prompt = build_morphology_prompt(tokens, function_words, pos_tags)
        morph_payload, model_call = call_llm("morphology_window", prompt, args)
        model_calls.append(model_call)
        if not morph_payload:
            continue
        merged_tokens = normalize_morphology(tokens, morph_payload)
        filtered_payload, _ = apply_rules(
            {"tokens": merged_tokens},
            tagset_path=TAGSET_PATH,
            config=RuleConfig(
                allow_unattested=args.allow_unattested,
                max_options=args.max_options,
            ),
        )
        aligned_payload = align_window_payload(filtered_payload)
        if aligned_payload:
            window_payloads.append(aligned_payload)

    report = compare_context_windows(window_payloads)
    report["model_calls"] = model_calls
    return report


def run_reproducibility(args, tokens: list[dict], function_words: list[dict], pos_tags: list[str]) -> dict:
    if args.repro_runs < 2:
        return {"status": "skipped", "reason": "repro_runs < 2"}

    hashes = []
    model_calls = []
    for _ in range(args.repro_runs):
        prompt = build_morphology_prompt(tokens, function_words, pos_tags)
        morph_payload, model_call = call_llm("morphology_repro", prompt, args)
        model_calls.append(model_call)
        if not morph_payload:
            hashes.append(None)
            continue
        merged_tokens = normalize_morphology(tokens, morph_payload)
        filtered_payload, _ = apply_rules(
            {"tokens": merged_tokens},
            tagset_path=TAGSET_PATH,
            config=RuleConfig(
                allow_unattested=args.allow_unattested,
                max_options=args.max_options,
            ),
        )
        hashes.append(sha256_text(json.dumps(filtered_payload, ensure_ascii=False)))

    stable = len(set(hashes)) == 1 if hashes and None not in hashes else False
    return {"status": "completed", "hashes": hashes, "stable": stable, "model_calls": model_calls}


def run_back_translation(args, variant_text: str) -> dict:
    if not args.back_translation or not variant_text:
        return {"status": "skipped", "reason": "back_translation disabled"}

    prompt = build_back_translation_prompt(variant_text)
    payload, model_call = call_llm("back_translation", prompt, args, expect_json=False)
    response = payload if payload else {"text": None}
    return {"status": "completed", "result": response, "model_call": model_call}


def token_diff(original_tokens: list[dict], back_text: str) -> dict:
    original = {token["surface"] for token in original_tokens}
    back_tokens = {token.surface for token in tokenize(back_text)}
    return {
        "added": sorted(back_tokens - original),
        "removed": sorted(original - back_tokens),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Ge'ez analysis pipeline.")
    parser.add_argument("--input", required=True, help="Input file or directory with .txt files.")
    parser.add_argument("--outdir", required=True, help="Output directory for artifacts.")
    parser.add_argument("--use-gemini", action="store_true", help="Use Gemini CLI instead of Ollama.")
    parser.add_argument("--model", help="LLM model name (gemini or ollama).")
    parser.add_argument("--ollama-url", help="Override Ollama URL.")
    parser.add_argument("--temperature", type=float, default=0.2, help="LLM temperature.")
    parser.add_argument("--seed", type=int, default=0, help="Ollama seed (ignored for Gemini).")
    parser.add_argument("--translation-space", action="store_true", help="Generate translation variants.")
    parser.add_argument("--back-translation", action="store_true", help="Run back-translation test.")
    parser.add_argument("--window-tests", action="store_true", help="Run context invariance tests.")
    parser.add_argument("--repro-runs", type=int, default=1, help="Number of runs for reproducibility test.")
    parser.add_argument("--allow-unattested", action="store_true", help="Downgrade unattested options instead of ruling out.")
    parser.add_argument("--drop-ruled-out", action="store_true", help="Drop ruled-out options from output.")
    parser.add_argument("--max-options", type=int, default=8, help="Overgeneration threshold before downgrade.")
    parser.add_argument("--validate-only", action="store_true", help="Validate existing JSON artifacts and exit.")
    args = parser.parse_args()

    input_path = Path(args.input)
    outdir = Path(args.outdir)

    if args.validate_only:
        json_files = list(Path(args.input).rglob("*.json")) if Path(args.input).is_dir() else [Path(args.input)]
        failures = 0
        for json_path in json_files:
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            errors = validate_payload(payload, SCHEMA_PATH)
            if errors:
                failures += 1
        return 1 if failures else 0

    tagset = load_tagset()
    function_words = tagset.get("function_words", [])
    pos_tags = [entry.get("tag") for entry in tagset.get("tags", []) if entry.get("tag")]

    args.prompt_versions = {
        "morphology": MORPHOLOGY_PROMPT_VERSION,
        "syntax": SYNTAX_PROMPT_VERSION,
        "semantic": SEMANTIC_PROMPT_VERSION,
        "translation": TRANSLATION_PROMPT_VERSION,
        "back_translation": BACK_TRANSLATION_PROMPT_VERSION,
        "morphology_window": MORPHOLOGY_PROMPT_VERSION,
        "morphology_repro": MORPHOLOGY_PROMPT_VERSION,
    }

    files = iter_text_files(input_path)
    segments_dir = outdir / "segments"
    reports_dir = outdir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    rule_hits = []

    previous_texts: list[str] = []
    for index, file_path in enumerate(files, start=1):
        text = read_text(file_path)
        witness_id = str(file_path.relative_to(input_path)) if input_path.is_dir() else file_path.name
        source = build_source(text, witness_id)
        tokens_payload = tokens_to_payload(tokenize(text))

        prompt = build_morphology_prompt(tokens_payload, function_words, pos_tags)
        morph_payload, morph_call = call_llm("morphology", prompt, args)
        merged_tokens = normalize_morphology(tokens_payload, morph_payload)
        filtered_payload, filter_report = apply_rules(
            {"tokens": merged_tokens},
            tagset_path=TAGSET_PATH,
            config=RuleConfig(
                allow_unattested=args.allow_unattested,
                drop_ruled_out=args.drop_ruled_out,
                max_options=args.max_options,
            ),
        )
        tokens = filtered_payload["tokens"]

        syntax_payload, syntax_call = call_llm("syntax", build_syntax_prompt(tokens), args)
        parses = []
        if syntax_payload:
            parses = syntax_payload.get("syntax", {}).get("parses", [])
        semantic_payload, semantic_call = call_llm(
            "semantic", build_semantic_prompt(parses, build_key_lemmas(tokens)), args
        )
        if semantic_payload:
            semantic_payload = {
                key: value
                for key, value in semantic_payload.items()
                if key in {"evaluation", "final_decision", "decision_log"}
            }

        translation_payload = None
        translation_call = None
        if args.translation_space:
            translation_payload, translation_call = call_llm(
                "translation", build_translation_prompt(parses, tokens), args
            )

        context_report = run_context_invariance(args, text, function_words, pos_tags, previous_texts)
        apply_context_penalty({"tokens": tokens}, context_report)
        repro_report = run_reproducibility(args, tokens_payload, function_words, pos_tags)
        back_translation_report = None
        if args.back_translation and translation_payload:
            variants = translation_payload.get("translation_space", {}).get("variants", [])
            variant_text = variants[0].get("text") if variants else ""
            back_translation_report = run_back_translation(args, variant_text)
        else:
            back_translation_report = {"status": "skipped", "reason": "translation_space disabled"}

        if back_translation_report.get("status") == "completed":
            back_text = back_translation_report.get("result", {}).get("text") or ""
            if back_text:
                back_translation_report["token_diff"] = token_diff(tokens, back_text)

        model_calls = [morph_call, syntax_call, semantic_call]
        if translation_call:
            model_calls.append(translation_call)
        if back_translation_report and back_translation_report.get("model_call"):
            model_calls.append(back_translation_report["model_call"])
        model_calls.extend(context_report.get("model_calls", []))
        model_calls.extend(repro_report.get("model_calls", []))

        decision_log = [
            {
                "step": "graphematic",
                "action": "captured",
                "rationale": "raw text captured without normalization",
                "refs": [witness_id],
            },
            {
                "step": "tokenization",
                "action": "whitespace",
                "rationale": "deterministic token boundaries",
                "refs": [],
            },
            {
                "step": "morphology_filter",
                "action": "rules_applied",
                "rationale": "rules=" + ",".join(sorted(filter_report.get("rules", {}).keys())),
                "refs": [],
            },
        ]

        artifact = {
            "meta": {
                "schema_version": "1.0.0",
                "created_at": dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
                "created_by": "run_pipeline",
                "language": "gez",
                "tagset_id": tagset.get("tagset_id", "GEZ-POS-1"),
                "tokenization_policy": "whitespace",
                "model_calls": model_calls,
            },
            "source": source,
            "tokens": tokens,
            "syntax": syntax_payload.get("syntax") if syntax_payload else {"parses": []},
            "semantic": semantic_payload if semantic_payload else {"evaluation": []},
            "translation_space": translation_payload.get("translation_space") if translation_payload else {"variants": []},
            "tests": {
                "context_invariance": context_report,
                "back_translation": back_translation_report,
                "reproducibility": repro_report,
            },
            "decision_log": decision_log,
        }

        errors = validate_payload(artifact, SCHEMA_PATH)
        if errors:
            artifact.setdefault("decision_log", []).append({
                "step": "validation",
                "action": "failed",
                "rationale": "; ".join(errors),
                "refs": [],
            })

        segment_name = f"seg_{index:04d}.json"
        save_json(segments_dir / segment_name, artifact)
        save_json(reports_dir / f"seg_{index:04d}_filter_report.json", filter_report)
        rule_hits.append({"segment": segment_name, "rules": filter_report.get("rules", {})})
        previous_texts.append(text)

    summary = {"total_segments": len(files), "rule_hits": rule_hits}
    save_json(reports_dir / "summary.json", summary)

    csv_path = reports_dir / "rule_hits.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["segment", "rule", "ruled_out", "downgraded"])
        for item in rule_hits:
            segment = item["segment"]
            for rule_name, stats in item["rules"].items():
                writer.writerow([segment, rule_name, stats.get("ruled_out", 0), stats.get("downgraded", 0)])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
