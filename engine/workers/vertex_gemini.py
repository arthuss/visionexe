import json
import os
import subprocess
import shutil
import urllib.error
import urllib.request


DEFAULT_VERTEX_LOCATION = "us-central1"
DEFAULT_VERTEX_MODEL = "gemini-3-pro-preview"
DEFAULT_MAX_OUTPUT_TOKENS = 8192


def _run_command(cmd):
    if isinstance(cmd, (list, tuple)) and cmd:
        exe = cmd[0]
        resolved = (
            shutil.which(exe)
            or shutil.which(f"{exe}.cmd")
            or shutil.which(f"{exe}.exe")
        )
        if resolved:
            cmd = [resolved, *cmd[1:]]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _env_first(keys):
    for key in keys:
        value = os.environ.get(key)
        if value:
            return value
    return None


def resolve_vertex_project(explicit=None):
    if explicit:
        return explicit
    project = _env_first(("VERTEX_PROJECT", "GOOGLE_CLOUD_PROJECT", "GCLOUD_PROJECT"))
    if project:
        return project
    project = _run_command(["gcloud", "config", "get-value", "project"])
    if project and project != "(unset)":
        return project
    return None


def resolve_vertex_location(explicit=None):
    if explicit:
        return explicit
    location = _env_first((
        "VERTEX_LOCATION",
        "GOOGLE_CLOUD_LOCATION",
        "GOOGLE_CLOUD_REGION",
        "GCLOUD_REGION",
        "GOOGLE_REGION",
    ))
    if location:
        return location
    return DEFAULT_VERTEX_LOCATION


def resolve_vertex_model(explicit=None):
    if explicit:
        return explicit
    return os.environ.get("VERTEX_MODEL") or DEFAULT_VERTEX_MODEL


def resolve_max_output_tokens(explicit=None):
    if explicit:
        return explicit
    env_value = os.environ.get("VERTEX_MAX_OUTPUT_TOKENS")
    if env_value:
        try:
            return int(env_value)
        except ValueError:
            return DEFAULT_MAX_OUTPUT_TOKENS
    return DEFAULT_MAX_OUTPUT_TOKENS


def get_adc_access_token():
    token = _env_first(("GOOGLE_OAUTH_ACCESS_TOKEN", "GOOGLE_ACCESS_TOKEN"))
    if token:
        return token.strip()
    token = _run_command(["gcloud", "auth", "application-default", "print-access-token"])
    if token:
        return token.strip()
    return None


def _extract_text(payload):
    if not isinstance(payload, dict):
        return None
    candidates = payload.get("candidates") or []
    if not candidates:
        return None
    content = candidates[0].get("content") or {}
    parts = content.get("parts") or []
    chunks = []
    for part in parts:
        if isinstance(part, dict) and "text" in part:
            chunks.append(part["text"])
    text = "".join(chunks).strip()
    return text or None


def call_vertex_gemini(
    prompt,
    model=None,
    project=None,
    location=None,
    temperature=0.2,
    max_output_tokens=None,
    log_fn=None,
):
    project = resolve_vertex_project(project)
    location = resolve_vertex_location(location)
    model = resolve_vertex_model(model)
    max_output_tokens = resolve_max_output_tokens(max_output_tokens)
    token = get_adc_access_token()

    if not project:
        if log_fn:
            log_fn("Vertex project not resolved (set VERTEX_PROJECT or gcloud config).")
        return None
    if not token:
        if log_fn:
            log_fn("Vertex ADC token missing (run gcloud auth application-default login).")
        return None

    url = (
        f"https://{location}-aiplatform.googleapis.com/v1/projects/"
        f"{project}/locations/{location}/publishers/google/models/{model}:generateContent"
    )
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_output_tokens,
        },
    }
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    request = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request) as response:
            body = response.read().decode("utf-8")
        return _extract_text(json.loads(body))
    except urllib.error.HTTPError as exc:
        if log_fn:
            try:
                detail = exc.read().decode("utf-8")
            except Exception:
                detail = str(exc)
            log_fn(f"Vertex HTTP {exc.code}: {detail}")
        return None
    except Exception as exc:
        if log_fn:
            log_fn(f"Vertex request failed: {exc}")
        return None
