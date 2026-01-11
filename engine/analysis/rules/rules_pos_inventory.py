def check_pos_inventory(token: dict, option: dict, surface: str, tagset: dict, config) -> tuple[str, str] | None:
    pos = option.get("pos")
    if not pos or pos not in tagset.get("tags", set()):
        return "rule_out", "pos not in tagset"
    return None
