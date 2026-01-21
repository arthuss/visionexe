# exevision

Arbeitsrepo fuer Vector MCP, Story Loader und Research Notes.

## Python Dateien

story_tools/
- story_tools/story_loader.py: Laedt Kapiteldateien in Postgres und Qdrant.
- story_tools/intercollection_worker.py: Baut semantische Links ueber Collections.

model_workers/
- model_workers/qwen3_vl_service.py: HTTP Worker fuer Qwen3-VL (embed, rerank, instruct).

knowledge_base/
- knowledge_base/setup_database.py: Setup/Migrationen fuer die alte Knowledge Base.
- knowledge_base/manage_database.py: Management UI fuer die alte Knowledge Base.
- knowledge_base/query_database.py: Altes Query-Tool.
- knowledge_base/query_database_new.py: Neues Query-Tool.
- knowledge_base/ingest_assets.py: Import fuer Asset CSV.

Engram/
- Engram/engram_demo_v1.py: Demo fuer Engram (Research/Upstream).

## Einstieg
- QUICKSTART.md: Enduser Einstieg mit .bat Dateien.
- scripts/README.md: Script Uebersicht.
- vector_mcp/README.md: MCP Server Details.
- story_tools/README.md: Loader/Worker Details.
- env/README.md: Conda + uv Umgebung fuer lokale Modelle.
