# model_workers

Qwen3-VL HTTP worker for embeddings, reranking, and generation. One process runs one mode.

## Modes
- embed: exposes /embed
- rerank: exposes /rerank
- instruct: exposes /generate

## Start (PowerShell)
Use the scripts in `scripts/` (see QUICKSTART.md).

## /embed
Request:
```json
{
  "inputs": ["text 1", "text 2"],
  "output_dim": 1024,
  "normalize": true,
  "instruction": "Represent the user's input."
}
```

Response:
```json
{ "embeddings": [[...], [...]] }
```

Inputs can also be objects with `text`, `image`, `video`, `fps`, and optional `instruction`.

## /rerank
Request:
```json
{
  "instruction": "Retrieve images or text relevant to the user's query.",
  "query": { "text": "query text" },
  "documents": [{ "text": "doc 1" }, { "text": "doc 2" }],
  "normalize": false
}
```

Response:
```json
{ "scores": [0.12, -0.34] }
```

## /generate
Request:
```json
{
  "prompt": "Describe the image.",
  "image": "C:\\path\\to\\image.png",
  "max_new_tokens": 256,
  "temperature": 0.2,
  "top_p": 0.9
}
```

Response:
```json
{ "text": "..." }
```

## Notes
- Local files are converted to file:// paths before inference.
- Align EMBEDDING_DIMENSION with output_dim for pgvector.
