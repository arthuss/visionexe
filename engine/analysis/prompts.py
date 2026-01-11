import json


MORPHOLOGY_PROMPT_VERSION = "v1.0.0"
SYNTAX_PROMPT_VERSION = "v1.0.0"
SEMANTIC_PROMPT_VERSION = "v1.0.0"
TRANSLATION_PROMPT_VERSION = "v1.0.0"
BACK_TRANSLATION_PROMPT_VERSION = "v1.0.0"


def build_morphology_prompt(tokens: list[dict], function_words: list[dict], pos_tags: list[str]) -> str:
    payload = {"tokens": tokens, "function_words": function_words, "pos_tags": pos_tags}
    return (
        "Instruction: Perform a rigorous Morphological Analysis (Level B) on Ge'ez tokens.\n"
        "Goal: Enumerate all morphologically valid options per token without choosing.\n\n"
        "Rules:\n"
        "1. Use only POS tags from pos_tags.\n"
        "2. Do NOT merge POS tags; emit separate options.\n"
        "3. Function words must use allowed POS (see function_words).\n"
        "4. root != surface. root is consonantal root only; particles use null.\n"
        "5. Include evidence.lexicon_status and evidence.attestation for every option.\n"
        "6. No semantic or syntactic decisions.\n\n"
        f"Input JSON:\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n\n"
        "Output strictly valid JSON:\n"
        "{\n"
        '  "tokens": [\n'
        '    {\n'
        '      "token_id": "t1",\n'
        '      "options": [\n'
        '        {\n'
        '          "option_id": "A",\n'
        '          "pos": "N",\n'
        '          "analysis": {\n'
        '            "kind": "lexical",\n'
        '            "root": "root",\n'
        '            "lemma": "lemma",\n'
        '            "pattern": "pattern",\n'
        '            "affixes": {"prefixes": [], "suffixes": [], "clitics": []},\n'
        '            "features": {"state": "construct"},\n'
        '            "gloss": "gloss"\n'
        "          },\n"
        '          "confidence": {"type": "undecided", "score": null},\n'
        '          "evidence": {\n'
        '            "lexicon_status": "attested_in_lexicon",\n'
        '            "attestation": [{"type": "lexicon", "ref": "REF"}],\n'
        '            "constraints_checked": [],\n'
        '            "notes": ""\n'
        "          }\n"
        "        }\n"
        "      ]\n"
        "    }\n"
        "  ]\n"
        "}"
    )


def build_syntax_prompt(tokens: list[dict]) -> str:
    payload = {"tokens": tokens}
    return (
        "Instruction: Perform a scientific Syntactic Analysis (Level C) of the Ge'ez tokens.\n"
        "Goal: Enumerate the full structure space without choosing a single parse.\n\n"
        "Rules:\n"
        "1. Use only provided tokens/options.\n"
        "2. No semantic preferences.\n"
        "3. Use bracket notation and explicit dependencies.\n\n"
        f"Input JSON:\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n\n"
        "Output strictly valid JSON:\n"
        "{\n"
        '  "syntax": {\n'
        '    "parses": [\n'
        '      {\n'
        '        "id": "S1",\n'
        '        "structure_type": "Nominal Chain",\n'
        '        "bracket_notation": "[NP [N t1] [Gen t2]]",\n'
        '        "dependencies": ["t1->t2 (genitive)"],\n'
        '        "notes": ""\n'
        "      }\n"
        "    ]\n"
        "  }\n"
        "}"
    )


def build_semantic_prompt(parses: list[dict], key_lemmas: list[str]) -> str:
    payload = {"parses": parses, "key_lemmas": key_lemmas}
    return (
        "Instruction: Perform a semantic & historical evaluation (Level D).\n"
        "Goal: Rank parses using attestation and document uncertainty.\n\n"
        "Rules:\n"
        "1. Cite parallels only if attested.\n"
        "2. If no evidence, mark missing.\n"
        "3. No fabrication.\n\n"
        f"Input JSON:\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n\n"
        "Output strictly valid JSON:\n"
        "{\n"
        '  "evaluation": [\n'
        '    {\n'
        '      "hypothesis_ref": "S1",\n'
        '      "plausibility": "high",\n'
        '      "reasoning": "...",\n'
        '      "parallels": [{"ref": "SOURCE:REF", "note": ""}],\n'
        '      "context_invariance": "stable",\n'
        '      "back_translation": "pass"\n'
        "    }\n"
        "  ],\n"
        '  "decision_log": "..." \n'
        "}"
    )


def build_translation_prompt(parses: list[dict], tokens: list[dict]) -> str:
    payload = {"parses": parses, "tokens": tokens}
    return (
        "Instruction: Generate a constrained translation space.\n"
        "Goal: Provide literal variants mapped to parse + token option IDs.\n\n"
        "Rules:\n"
        "1. No free paraphrase.\n"
        "2. Map each variant to parse_ref and token_map.\n\n"
        f"Input JSON:\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n\n"
        "Output strictly valid JSON:\n"
        "{\n"
        '  "translation_space": {\n'
        '    "variants": [\n'
        '      {\n'
        '        "id": "T1",\n'
        '        "text": "...",\n'
        '        "parse_ref": "S1",\n'
        '        "token_map": [{"token_id": "t1", "option_id": "A"}],\n'
        '        "notes": ""\n'
        "      }\n"
        "    ]\n"
        "  }\n"
        "}"
    )


def build_back_translation_prompt(translation: str) -> str:
    return (
        "Instruction: Back-translate the following text into Ge'ez as literally as possible.\n"
        "Return only the Ge'ez text, no commentary.\n\n"
        f"Text:\n{translation}\n"
    )
