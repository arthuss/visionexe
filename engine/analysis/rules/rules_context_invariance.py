from __future__ import annotations


def _option_key(option: dict) -> str:
    analysis = option.get("analysis") or {}
    affixes = analysis.get("affixes") or {}
    parts = [
        option.get("pos"),
        analysis.get("root"),
        analysis.get("lemma"),
        analysis.get("pattern"),
        ",".join(affixes.get("prefixes") or []),
        ",".join(affixes.get("suffixes") or []),
        ",".join(affixes.get("clitics") or []),
    ]
    return "|".join("" if part is None else str(part) for part in parts)


def build_option_index(payload: dict) -> dict[str, set[str]]:
    index: dict[str, set[str]] = {}
    for token in payload.get("tokens", []):
        token_id = token.get("token_id")
        options = token.get("options", [])
        index[token_id] = {_option_key(option) for option in options}
    return index


def compare_context_windows(window_payloads: list[dict]) -> dict:
    if not window_payloads:
        return {"status": "skipped", "reason": "no windows"}

    indices = [build_option_index(payload) for payload in window_payloads]
    base_index = indices[0]
    report_tokens = []

    for token_id, base_options in base_index.items():
        per_window = [index.get(token_id, set()) for index in indices]
        union_options = set().union(*per_window)
        context_sensitive = []
        for option_key in union_options:
            appearances = [option_key in window_set for window_set in per_window]
            if appearances.count(True) == 1:
                context_sensitive.append({"option_key": option_key, "only_in_window": appearances.index(True)})
        if context_sensitive:
            report_tokens.append(
                {
                    "token_id": token_id,
                    "context_sensitive": context_sensitive,
                }
            )

    return {"status": "completed", "tokens": report_tokens}


def apply_context_penalty(payload: dict, context_report: dict) -> None:
    if context_report.get("status") != "completed":
        return
    sensitive = {item["token_id"]: item["context_sensitive"] for item in context_report.get("tokens", [])}
    if not sensitive:
        return

    for token in payload.get("tokens", []):
        token_id = token.get("token_id")
        if token_id not in sensitive:
            continue
        sensitive_keys = {entry["option_key"] for entry in sensitive[token_id]}
        for option in token.get("options", []):
            option_key = _option_key(option)
            if option_key in sensitive_keys:
                confidence = option.setdefault("confidence", {})
                if confidence.get("type") not in {"ruled_out", "weak"}:
                    confidence["type"] = "weak"
                evidence = option.setdefault("evidence", {})
                constraints = evidence.setdefault("constraints_checked", [])
                if "context_invariance_gate" not in constraints:
                    constraints.append("context_invariance_gate")
