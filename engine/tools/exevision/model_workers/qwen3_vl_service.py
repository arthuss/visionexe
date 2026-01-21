import argparse
import logging
import os
from typing import Any, Dict, List, Optional, Tuple

import torch
from fastapi import FastAPI, HTTPException
from transformers import AutoModelForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info

LOG = logging.getLogger("qwen3_vl_service")

DEFAULT_EMBED_INSTRUCTION = "Represent the user's input."
DEFAULT_RERANK_INSTRUCTION = "Retrieve images or text relevant to the user's query."
DEFAULT_INSTRUCT_SYSTEM = "You are a helpful assistant."
EMBED_INSTRUCTION = DEFAULT_EMBED_INSTRUCTION
RERANK_INSTRUCTION = DEFAULT_RERANK_INSTRUCTION
INSTRUCT_SYSTEM = DEFAULT_INSTRUCT_SYSTEM
EMBED_OUTPUT_DIM = None

app = FastAPI()
SERVICE = None
MODE = None


def _resolve_media(value: Optional[Any]) -> Optional[Any]:
    if value is None:
        return None
    if not isinstance(value, str):
        return value
    lower = value.lower()
    if lower.startswith(("http://", "https://", "oss")):
        return value
    if lower.startswith("file://"):
        return value
    abs_path = os.path.abspath(value).replace("\\", "/")
    return f"file://{abs_path}"


def _normalize_inputs(raw: Any) -> List[Dict[str, Any]]:
    if raw is None:
        return []
    if isinstance(raw, str):
        return [{"text": raw}]
    if isinstance(raw, dict):
        return [raw]
    if isinstance(raw, list):
        normalized: List[Dict[str, Any]] = []
        for item in raw:
            if isinstance(item, str):
                normalized.append({"text": item})
            elif isinstance(item, dict):
                normalized.append(item)
            else:
                raise ValueError(f"Unsupported input type: {type(item)}")
        return normalized
    raise ValueError(f"Unsupported input payload: {type(raw)}")


def _build_messages(item: Dict[str, Any], instruction: str) -> List[Dict[str, Any]]:
    content: List[Dict[str, Any]] = []
    image = _resolve_media(item.get("image"))
    video = _resolve_media(item.get("video"))
    text = item.get("text")
    fps = item.get("fps")

    if image:
        content.append({"type": "image", "image": image})
    if video:
        video_payload = {"type": "video", "video": video}
        if fps:
            video_payload["fps"] = fps
        content.append(video_payload)
    if text:
        content.append({"type": "text", "text": text})

    if not content:
        content.append({"type": "text", "text": ""})

    return [
        {"role": "system", "content": [{"type": "text", "text": instruction}]},
        {"role": "user", "content": content},
    ]


def _build_rerank_messages(
    query: Dict[str, Any], document: Dict[str, Any], instruction: str
) -> List[Dict[str, Any]]:
    content: List[Dict[str, Any]] = [{"type": "text", "text": "Query:"}]
    content.extend(_build_messages(query, instruction="")[-1]["content"])
    content.append({"type": "text", "text": "Document:"})
    content.extend(_build_messages(document, instruction="")[-1]["content"])

    return [
        {"role": "system", "content": [{"type": "text", "text": instruction}]},
        {"role": "user", "content": content},
    ]


def _pick_dtype(value: str) -> torch.dtype:
    if value == "auto":
        return torch.bfloat16 if torch.cuda.is_available() else torch.float32
    if value == "float16":
        return torch.float16
    if value == "bfloat16":
        return torch.bfloat16
    if value == "float32":
        return torch.float32
    raise ValueError(f"Unsupported dtype: {value}")


def _pick_device(value: str) -> str:
    if value == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    return value


class Qwen3VLBase:
    def __init__(
        self,
        model_path: str,
        device: str,
        dtype: torch.dtype,
        attn_implementation: Optional[str] = None,
    ) -> None:
        self.device = device
        self.dtype = dtype
        self.processor = AutoProcessor.from_pretrained(model_path)
        self.use_device_map = device == "cuda"
        model_kwargs: Dict[str, Any] = {"torch_dtype": dtype}
        if self.use_device_map:
            model_kwargs["device_map"] = "auto"
        if attn_implementation:
            model_kwargs["attn_implementation"] = attn_implementation
        self.model = AutoModelForConditionalGeneration.from_pretrained(model_path, **model_kwargs)
        if not self.use_device_map:
            self.model.to(device)
        self.model.eval()

    def _prepare_inputs(self, messages: List[Dict[str, Any]], add_generation_prompt: bool) -> Dict[str, Any]:
        text = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=add_generation_prompt
        )
        image_inputs, video_inputs = process_vision_info(messages)
        inputs = self.processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        )
        if not self.use_device_map:
            return {key: value.to(self.device) for key, value in inputs.items()}
        return inputs


class Qwen3VLEmbedder(Qwen3VLBase):
    def embed(
        self,
        inputs: List[Dict[str, Any]],
        instruction: str,
        output_dim: Optional[int],
        normalize: bool,
    ) -> List[List[float]]:
        embeddings: List[List[float]] = []
        for item in inputs:
            item_instruction = item.get("instruction") or instruction
            messages = _build_messages(item, item_instruction)
            batch = self._prepare_inputs(messages, add_generation_prompt=False)
            with torch.no_grad():
                outputs = self.model(**batch, output_hidden_states=True, return_dict=True)
            hidden = outputs.hidden_states[-1]
            mask = batch.get("attention_mask")
            if mask is None:
                pooled = hidden.mean(dim=1)
            else:
                mask = mask.unsqueeze(-1).to(hidden)
                pooled = (hidden * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1)
            vector = pooled[0]
            if normalize:
                vector = torch.nn.functional.normalize(vector, p=2, dim=0)
            if output_dim and output_dim < vector.shape[0]:
                vector = vector[:output_dim]
            embeddings.append(vector.float().cpu().tolist())
        return embeddings


class Qwen3VLReranker(Qwen3VLBase):
    def __init__(
        self,
        model_path: str,
        device: str,
        dtype: torch.dtype,
        attn_implementation: Optional[str] = None,
    ) -> None:
        super().__init__(model_path, device, dtype, attn_implementation)
        self.yes_token_id = self._token_id(" yes")
        self.no_token_id = self._token_id(" no")

    def _token_id(self, text: str) -> int:
        token_ids = self.processor.tokenizer.encode(text, add_special_tokens=False)
        if not token_ids:
            raise ValueError(f"Token not found for: {text}")
        if len(token_ids) > 1:
            LOG.warning("Token '%s' maps to multiple ids, using first id.", text)
        return token_ids[0]

    def score(
        self,
        query: Dict[str, Any],
        documents: List[Dict[str, Any]],
        instruction: str,
        normalize: bool,
    ) -> List[float]:
        scores: List[float] = []
        for doc in documents:
            messages = _build_rerank_messages(query, doc, instruction)
            batch = self._prepare_inputs(messages, add_generation_prompt=True)
            with torch.no_grad():
                outputs = self.model(**batch, return_dict=True)
            logits = outputs.logits[0, -1]
            yes = logits[self.yes_token_id]
            no = logits[self.no_token_id]
            score = yes - no
            if normalize:
                score = torch.sigmoid(score)
            scores.append(float(score.detach().cpu().item()))
        return scores


class Qwen3VLInstruct(Qwen3VLBase):
    def generate(
        self,
        messages: List[Dict[str, Any]],
        max_new_tokens: int,
        temperature: float,
        top_p: float,
    ) -> str:
        batch = self._prepare_inputs(messages, add_generation_prompt=True)
        do_sample = temperature > 0
        with torch.no_grad():
            generated = self.model.generate(
                **batch,
                max_new_tokens=max_new_tokens,
                do_sample=do_sample,
                temperature=temperature if do_sample else None,
                top_p=top_p if do_sample else None,
            )
        input_len = batch["input_ids"].shape[1]
        output_tokens = generated[0][input_len:]
        return self.processor.tokenizer.decode(output_tokens, skip_special_tokens=True).strip()


def _require_service() -> Any:
    if SERVICE is None:
        raise HTTPException(status_code=503, detail="Service not initialized.")
    return SERVICE


@app.post("/embed")
def embed(payload: Dict[str, Any]) -> Dict[str, Any]:
    if MODE != "embed":
        raise HTTPException(status_code=404, detail="Embed mode is not active.")
    service: Qwen3VLEmbedder = _require_service()
    raw_inputs = payload.get("inputs") or payload.get("input") or payload.get("text")
    inputs = _normalize_inputs(raw_inputs)
    if not inputs:
        raise HTTPException(status_code=400, detail="No inputs provided.")
    instruction = payload.get("instruction") or EMBED_INSTRUCTION
    output_dim = payload.get("output_dim", EMBED_OUTPUT_DIM)
    normalize = bool(payload.get("normalize", True))
    embeddings = service.embed(inputs, instruction=instruction, output_dim=output_dim, normalize=normalize)
    return {"embeddings": embeddings}


@app.post("/rerank")
def rerank(payload: Dict[str, Any]) -> Dict[str, Any]:
    if MODE != "rerank":
        raise HTTPException(status_code=404, detail="Rerank mode is not active.")
    service: Qwen3VLReranker = _require_service()
    query = payload.get("query")
    documents = payload.get("documents")
    if not isinstance(query, dict):
        raise HTTPException(status_code=400, detail="Query must be an object.")
    if not isinstance(documents, list):
        raise HTTPException(status_code=400, detail="Documents must be a list.")
    fps = payload.get("fps")
    if fps is not None:
        query = {**query, "fps": query.get("fps", fps)}
        documents = [{**doc, "fps": doc.get("fps", fps)} for doc in documents]
    instruction = payload.get("instruction") or RERANK_INSTRUCTION
    normalize = bool(payload.get("normalize", False))
    scores = service.score(query=query, documents=documents, instruction=instruction, normalize=normalize)
    return {"scores": scores}


@app.post("/generate")
def generate(payload: Dict[str, Any]) -> Dict[str, Any]:
    if MODE != "instruct":
        raise HTTPException(status_code=404, detail="Instruct mode is not active.")
    service: Qwen3VLInstruct = _require_service()
    messages = payload.get("messages")
    if not isinstance(messages, list):
        prompt = payload.get("prompt")
        if not prompt:
            raise HTTPException(status_code=400, detail="Missing messages or prompt.")
        system_text = payload.get("system") or INSTRUCT_SYSTEM
        item = {"text": prompt, "image": payload.get("image"), "video": payload.get("video"), "fps": payload.get("fps")}
        messages = _build_messages(item, system_text)
    max_new_tokens = int(payload.get("max_new_tokens", 256))
    temperature = float(payload.get("temperature", 0.2))
    top_p = float(payload.get("top_p", 0.9))
    text = service.generate(messages=messages, max_new_tokens=max_new_tokens, temperature=temperature, top_p=top_p)
    return {"text": text}


def build_service(args: argparse.Namespace) -> Tuple[Any, str]:
    device = _pick_device(args.device)
    dtype = _pick_dtype(args.dtype)
    if args.mode == "embed":
        return Qwen3VLEmbedder(args.model_path, device, dtype, args.attn_impl), "embed"
    if args.mode == "rerank":
        return Qwen3VLReranker(args.model_path, device, dtype, args.attn_impl), "rerank"
    if args.mode == "instruct":
        return Qwen3VLInstruct(args.model_path, device, dtype, args.attn_impl), "instruct"
    raise ValueError(f"Unsupported mode: {args.mode}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Qwen3-VL HTTP worker")
    parser.add_argument("--mode", choices=["embed", "rerank", "instruct"], required=True)
    parser.add_argument("--model-path", required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8090)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--dtype", default="auto")
    parser.add_argument("--attn-impl", default=None)
    parser.add_argument("--embed-instruction", default=DEFAULT_EMBED_INSTRUCTION)
    parser.add_argument("--rerank-instruction", default=DEFAULT_RERANK_INSTRUCTION)
    parser.add_argument("--system-prompt", default=DEFAULT_INSTRUCT_SYSTEM)
    parser.add_argument("--default-output-dim", type=int, default=None)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    global SERVICE, MODE, EMBED_INSTRUCTION, RERANK_INSTRUCTION, INSTRUCT_SYSTEM, EMBED_OUTPUT_DIM
    SERVICE, MODE = build_service(args)
    EMBED_INSTRUCTION = args.embed_instruction
    RERANK_INSTRUCTION = args.rerank_instruction
    INSTRUCT_SYSTEM = args.system_prompt
    EMBED_OUTPUT_DIM = args.default_output_dim

    import uvicorn

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
