from __future__ import annotations

from pathlib import Path

from jsonschema import Draft202012Validator

from .io import load_json


def load_schema(schema_path: Path) -> dict:
    return load_json(schema_path)


def validate_payload(payload: dict, schema_path: Path) -> list[str]:
    schema = load_schema(schema_path)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda err: err.path)
    return [f"{'/'.join([str(item) for item in error.path])}: {error.message}" for error in errors]
