# QUICKSTART.md

Nur die .bat Dateien fuer Enduser. Jede Datei kann per Doppelklick gestartet werden.
Voraussetzung fuer die Qwen3-VL Worker: conda env `exevision-vl` (siehe env/README.md).

1) scripts\start_vector_stack.bat
   Startet pgvector und Qdrant via Docker Compose.

2) scripts\run_mcp_server.bat
   Startet den Vector MCP Server (nutzt EMBEDDING_ENDPOINT falls gesetzt).

3) scripts\run_qwen3_vl_embed.bat
   Startet den Qwen3-VL Embedding Worker (HTTP /embed, default Port 8090).

4) scripts\run_qwen3_vl_rerank.bat
   Startet den Qwen3-VL Reranker Worker (HTTP /rerank, default Port 8091).

5) scripts\run_qwen3_vl_instruct.bat
   Startet den Qwen3-VL Instruct Worker (HTTP /generate, default Port 8092).

6) scripts\load_story.bat --data-dir ..\DATA\Story1-Henoch
   Laedt Kapiteldateien in die Vector Stores. Parameter werden an den Loader durchgereicht.

7) scripts\run_intercollection_worker.bat --collections * --limit 3 --threshold 0.75
   Baut semantische Links zwischen Collections. Parameter werden durchgereicht.

8) scripts\stop_vector_stack.bat
   Stoppt die Docker Services.
