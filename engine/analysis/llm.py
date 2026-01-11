import json
import shutil
import subprocess
import time
import urllib.request


DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434/api/generate"


def _parse_json_output(raw_output: str) -> str | None:
    if not raw_output:
        return None
    json_start = raw_output.find("{")
    if json_start == -1:
        return raw_output.strip()
    json_text = raw_output[json_start:]
    json_end = json_text.rfind("}")
    if json_end != -1:
        json_text = json_text[:json_end + 1]
    try:
        payload = json.loads(json_text)
        response = payload.get("response")
        if isinstance(response, str):
            return response.strip()
    except json.JSONDecodeError:
        return raw_output.strip()
    return None


def call_ollama(prompt: str, model: str, ollama_url: str | None = None, temperature: float = 0.2,
                num_ctx: int = 16384, seed: int | None = None) -> tuple[str | None, float]:
    url = ollama_url or DEFAULT_OLLAMA_URL
    options = {
        "temperature": temperature,
        "num_ctx": num_ctx,
    }
    if seed is not None:
        options["seed"] = seed
    data = {"model": model, "prompt": prompt, "stream": False, "options": options}
    start_time = time.time()
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as response:
            resp_json = json.loads(response.read().decode("utf-8"))
            return resp_json.get("response", ""), time.time() - start_time
    except Exception:
        return None, time.time() - start_time


def _resolve_gemini_command() -> list[str] | None:
    gemini_path = shutil.which("gemini") or shutil.which("gemini.cmd")
    if gemini_path:
        return [gemini_path]

    npx_path = shutil.which("npx") or shutil.which("npx.cmd")
    if npx_path:
        return [npx_path, "-y", "@google/gemini-cli"]

    return None


def call_gemini(prompt: str, model: str | None = None) -> tuple[str | None, float]:
    cmd = _resolve_gemini_command()
    if not cmd:
        return None, 0.0
    cmd = cmd + ["--output-format", "json"]
    if model:
        cmd += ["--model", model]

    start_time = time.time()
    try:
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
        stdout, stderr = process.communicate(input=prompt)
        if process.returncode != 0:
            return None, time.time() - start_time
        return _parse_json_output(stdout), time.time() - start_time
    except OSError:
        return None, time.time() - start_time
