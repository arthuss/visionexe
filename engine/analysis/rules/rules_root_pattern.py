def check_root_pattern(token: dict, option: dict, surface: str, tagset: dict, config) -> tuple[str, str] | None:
    pos = option.get("pos")
    analysis = option.get("analysis") or {}
    if analysis.get("kind") != "lexical":
        return None
    if pos not in tagset.get("lexical", set()):
        return None

    root = analysis.get("root")
    pattern = analysis.get("pattern")
    if root and not pattern:
        if getattr(config, "strict_root_pattern", False):
            return "rule_out", "root requires pattern"
        return "downgrade", "root missing pattern"
    if not root:
        return "downgrade", "lexical entry missing root"
    return None
