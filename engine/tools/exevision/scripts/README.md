# scripts

Quick entry points for common tasks. PowerShell scripts are the primary entry points,
batch files are thin wrappers for end users.

- start_vector_stack.ps1: start pgvector + qdrant (docker compose)
- stop_vector_stack.ps1: stop pgvector + qdrant
- run_mcp_server.ps1: start the MCP server
- load_story.ps1: load chapters into vector stores (passes args to story_loader.py)
- run_intercollection_worker.ps1: build cross-collection links (passes args)
- run_qwen3_vl_embed.ps1: start Qwen3-VL embedding worker
- run_qwen3_vl_rerank.ps1: start Qwen3-VL reranker worker
- run_qwen3_vl_instruct.ps1: start Qwen3-VL instruct worker

Batch wrappers:
- start_vector_stack.bat
- stop_vector_stack.bat
- run_mcp_server.bat
- load_story.bat
- run_intercollection_worker.bat
- run_qwen3_vl_embed.bat
- run_qwen3_vl_rerank.bat
- run_qwen3_vl_instruct.bat

Example:
  scripts\load_story.bat --data-dir ..\..\..\data\Story1-Henoch
