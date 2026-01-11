def check_evidence_minimum(token: dict, option: dict, surface: str, tagset: dict, config) -> tuple[str, str] | None:
    evidence = option.get("evidence") or {}
    lexicon_status = evidence.get("lexicon_status")
    attestation = evidence.get("attestation") or []
    if lexicon_status == "unattested" and not attestation:
        if getattr(config, "allow_unattested", False):
            return "downgrade", "unattested without evidence"
        return "rule_out", "unattested without evidence"
    return None
