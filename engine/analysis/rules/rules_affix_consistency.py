def _collect_morphemes(token: dict) -> dict:
    morphemes = token.get("segmentation", {}).get("morphemes", [])
    groups = {"prefix": set(), "suffix": set(), "clitic": set()}
    for morph in morphemes:
        morph_type = morph.get("type")
        if morph_type in groups:
            groups[morph_type].add(morph.get("surface"))
    return groups


def check_affix_consistency(token: dict, option: dict, surface: str, tagset: dict, config) -> tuple[str, str] | None:
    morphemes = token.get("segmentation", {}).get("morphemes")
    if not morphemes:
        return None
    analysis = option.get("analysis") or {}
    affixes = analysis.get("affixes")
    if not affixes:
        return "rule_out", "segmentation present without affixes"

    grouped = _collect_morphemes(token)
    prefixes = set(affixes.get("prefixes") or [])
    suffixes = set(affixes.get("suffixes") or [])
    clitics = set(affixes.get("clitics") or [])

    if grouped["prefix"] and not grouped["prefix"].issubset(prefixes):
        return "rule_out", "prefix mismatch"
    if grouped["suffix"] and not grouped["suffix"].issubset(suffixes):
        return "rule_out", "suffix mismatch"
    if grouped["clitic"] and not grouped["clitic"].issubset(clitics):
        return "rule_out", "clitic mismatch"

    return None
