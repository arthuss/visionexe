from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..io import load_json

from .rules_affix_consistency import check_affix_consistency
from .rules_evidence_minimum import check_evidence_minimum
from .rules_function_words import check_function_word
from .rules_pos_inventory import check_pos_inventory
from .rules_root_pattern import check_root_pattern


@dataclass
class RuleConfig:
    allow_unattested: bool = False
    drop_ruled_out: bool = False
    max_options: int = 8
    strict_root_pattern: bool = False


def load_tagset(tagset_path: Path) -> dict:
    return load_json(tagset_path)


def build_tagset_index(tagset: dict) -> dict:
    return {
        "tags": {entry.get("tag") for entry in tagset.get("tags", []) if entry.get("tag")},
        "lexical": set(tagset.get("lexical_tags", [])),
        "function": set(tagset.get("function_word_tags", [])),
        "function_words": tagset.get("function_words", []),
    }


def ensure_option_fields(option: dict) -> tuple[dict, dict]:
    analysis = option.get("analysis") or {}
    option["analysis"] = analysis
    evidence = option.get("evidence") or {}
    evidence.setdefault("lexicon_status", "unattested")
    evidence.setdefault("attestation", [])
    evidence.setdefault("constraints_checked", [])
    option["evidence"] = evidence
    confidence = option.get("confidence") or {}
    confidence.setdefault("type", "undecided")
    confidence.setdefault("score", None)
    option["confidence"] = confidence
    return evidence, confidence


def apply_rules(
    payload: dict,
    tagset_path: Path | None = None,
    tagset_data: dict | None = None,
    config: RuleConfig | None = None,
) -> tuple[dict, dict]:
    config = config or RuleConfig()
    tagset = tagset_data or load_tagset(tagset_path)
    tagset_index = build_tagset_index(tagset)

    report = {
        "summary": {"ruled_out": 0, "downgraded": 0, "kept": 0},
        "rules": {},
        "tokens": [],
    }

    for token in payload.get("tokens", []):
        surface = token.get("surface", "")
        options = token.get("options", [])

        token_report = {
            "token_id": token.get("token_id"),
            "surface": surface,
            "proposed_options": len(options),
            "ruled_out": [],
            "downgraded": [],
            "kept": [],
        }

        kept_options = []
        for option in options:
            evidence, confidence = ensure_option_fields(option)
            ruled_out = False
            downgraded = False

            for rule_name, rule_fn in (
                ("pos_inventory", check_pos_inventory),
                ("function_word_list", check_function_word),
                ("root_pattern_compatibility", check_root_pattern),
                ("affix_consistency", check_affix_consistency),
                ("evidence_minimum", check_evidence_minimum),
            ):
                outcome = rule_fn(
                    token=token,
                    option=option,
                    surface=surface,
                    tagset=tagset_index,
                    config=config,
                )
                if not outcome:
                    continue

                action, note = outcome
                if rule_name not in evidence["constraints_checked"]:
                    evidence["constraints_checked"].append(rule_name)
                report["rules"].setdefault(rule_name, {"ruled_out": 0, "downgraded": 0})

                if action == "rule_out":
                    confidence["type"] = "ruled_out"
                    confidence["score"] = 0.0
                    token_report["ruled_out"].append({"option_id": option.get("option_id"), "rule": rule_name, "note": note})
                    report["rules"][rule_name]["ruled_out"] += 1
                    ruled_out = True
                    break
                if action == "downgrade":
                    if confidence.get("type") not in {"ruled_out", "weak"}:
                        confidence["type"] = "weak"
                    token_report["downgraded"].append({"option_id": option.get("option_id"), "rule": rule_name, "note": note})
                    report["rules"][rule_name]["downgraded"] += 1
                    downgraded = True

            if not ruled_out:
                kept_options.append(option)
                token_report["kept"].append(option.get("option_id"))
                if downgraded:
                    report["summary"]["downgraded"] += 1
                else:
                    report["summary"]["kept"] += 1
            else:
                report["summary"]["ruled_out"] += 1

        if config.max_options and len(options) > config.max_options:
            for option in kept_options:
                evidence = option.get("evidence") or {}
                if evidence.get("attestation"):
                    continue
                confidence = option.get("confidence") or {}
                if confidence.get("type") == "ruled_out":
                    continue
                if confidence.get("type") != "weak":
                    confidence["type"] = "weak"
                token_report["downgraded"].append(
                    {"option_id": option.get("option_id"), "rule": "overgeneration_penalty", "note": "no attestation"}
                )
                report["rules"].setdefault("overgeneration_penalty", {"ruled_out": 0, "downgraded": 0})
                report["rules"]["overgeneration_penalty"]["downgraded"] += 1
                report["summary"]["downgraded"] += 1

        if config.drop_ruled_out:
            token["options"] = kept_options

        report["tokens"].append(token_report)

    return payload, report
