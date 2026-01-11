def _build_function_word_map(function_words: list[dict]) -> dict:
    mapping = {}
    for entry in function_words or []:
        surface = entry.get("surface")
        if not surface:
            continue
        allowed = entry.get("allowed_pos") or []
        mapping[surface] = set(allowed)
    return mapping


def check_function_word(token: dict, option: dict, surface: str, tagset: dict, config) -> tuple[str, str] | None:
    function_words = tagset.get("function_words") or []
    mapping = _build_function_word_map(function_words)
    if surface not in mapping:
        return None
    allowed = mapping.get(surface, set())
    pos = option.get("pos")
    if pos not in allowed:
        return "rule_out", "function word POS mismatch"
    return None
