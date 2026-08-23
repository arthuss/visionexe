# exevision

Arbeitsrepo fuer Vector MCP, Story Loader, lokale Modell-Worker und Engram-Integration.

## Komponenten

story_tools/
- `story_tools/story_loader.py`: Laedt Kapitel, Analysen und Subject-Daten in Postgres + Qdrant (Mapping via metadata).
- `story_tools/intercollection_worker.py`: Baut semantische Links via Qdrant Search (auch same-collection per Filter).

model_workers/
- `model_workers/qwen3_vl_service.py`: HTTP Worker fuer Qwen3-VL (embed, rerank, instruct) mit optionaler Engram-Memory-Injection.

Engram/
- `Engram/engram_torch.py`: Referenz-Implementierung fuer Engram Hashing/Lookup (Research).
- `Engram/engram_qwen_surgery.py`: Layer-Injection in Qwen3-VL fuer Engram-Memory.
- `Engram/engram_params.json`: Exportierte Hash-Parameter als gemeinsame Basis fuer Python + C#.

vector_mcp/
- `vector_mcp/VectorMcpServer`: MCP-Server fuer pgvector + Qdrant inkl. Engram-Indexierung.

## Engram Integration (Ultra-Fast Lookup Basis)

Zielbild:
- Engram dient als deterministischer Hash-Index zwischen pgvector (Postgres) und Qdrant.
- Der Hash-Pfad ist als schneller Kandidaten-Layer gedacht, bevor/waehrend ANN- oder SQL-basierte Retrieval-Schritte laufen.

Aktueller Implementierungsstand:
1. In `VectorTools.StoreDocument` wird ein Dokument zuerst normal gespeichert:
   - Postgres (`vector_documents`, pgvector embedding)
   - Qdrant (Point Upsert)
2. Wenn Engram konfiguriert ist, berechnet `IEngramIndexer` aus dem Text Layer-Hashes.
3. Diese Hashes werden pro Layer in `engram_index` persistiert (`document_id`, `collection`, `layer_id`, `hashes`, `token_count`).
4. Bei `DeleteDocumentByTitle` werden die zugehoerigen Engram-Eintraege mit entfernt.

Wichtig:
- Es gibt jetzt ein separates MCP-Tool `EngramLookup` fuer deterministische Hash-Overlap-Abfragen.
- Die Integration bleibt trotzdem zweistufig: Indexaufbau/Synchronisierung plus explizite Retrieval-Wahl im Caller
  (z. B. Qdrant-only, Engram-only oder Hybrid).

### Warum "zwischen Qdrant und pgvector"

- pgvector in Postgres bleibt der kanonische Store fuer Dokument + Embedding.
- Qdrant bleibt der performante ANN-Store fuer Vektor-Suche.
- Engram ergaenzt eine dritte, deterministische Sicht auf denselben Inhalt (Hash-Layer), damit spaetere Recall-Pfade schnell Kandidaten aufloesen koennen.

### Konfiguration

Vector MCP liest folgende optionale Variablen:
- `ENGRAM_PARAMS_PATH`: Pfad zu `engram_params.json`
- `ENGRAM_TOKENIZER_DIR`: Tokenizer-Verzeichnis (z. B. `Models/Qwen3-VL-2B-Instruct`)

Falls nicht explizit gesetzt, nutzt der Loader Default-Kandidaten unter `exevision/Engram` und `exevision/Models`.
Wenn Params oder Tokenizer fehlen, bleibt der Server lauffaehig und schaltet Engram-Indexierung automatisch ab.

### Relevante Codepfade

- `engine/tools/exevision/vector_mcp/VectorMcpServer/Services/Engram/EngramLoader.cs`
- `engine/tools/exevision/vector_mcp/VectorMcpServer/Services/Engram/EngramIndexer.cs`
- `engine/tools/exevision/vector_mcp/VectorMcpServer/Tools/VectorTools.cs`
- `engine/tools/exevision/vector_mcp/VectorMcpServer/Data/SchemaBootstrapper.cs`
- `engine/tools/exevision/vector_mcp/VectorMcpServer/Data/VectorDbContext.cs`
- `engine/tools/exevision/model_workers/qwen3_vl_service.py`
- `engine/tools/exevision/scripts/run_qwen3_vl_instruct.ps1`

## Parallelbetrieb (main + fast Workspace)

Empfehlung: **parallel versionieren statt Daten zusammenmergen**.

Praktisches Setup:
1. Getrennte Datenpfade pro Variante (z. B. `stories/template/...` vs `stories/fast/...` + separates `data_root`/`analysis_segments_root`).
2. Getrennte Vector-Backends pro Variante:
   - eigenes Postgres DB-Schema/DB-Name (z. B. `exegetos` vs `exegetos_fast`)
   - eigenes Qdrant-Target (eigene Instanz/Ports oder klarer Collection-Prefix)
3. Einheitlicher ID-Contract ueber beide Varianten:
   - `document_id` bleibt der Link zwischen pgvector, Qdrant und Engram
   - `chapter_id`/`segment_label` bleiben canonical (`segment_###`)
4. Version-Metadaten mitschreiben (mindestens):
   - `workspace_variant` (`main`|`fast`)
   - `pipeline_version` (z. B. `v1`)
5. Promotion statt Merge:
   - Ergebnisse aus `fast` gezielt exportieren/importieren in `main`
   - kein ungefiltertes Live-Mischen derselben Collections

Schnellstart-Templates:
- `stories/template/config/story_config_fast.template.json`
- `engine/tools/exevision/vector_mcp/.env.fast.example`
- `engine/scripts/switch_fast.ps1` (erstellt `stories/<name>`, schaltet `switch_story` + MCP-Profil in einem Schritt)

## Einstieg

- `QUICKSTART.md`: Enduser Einstieg mit `.bat` Dateien.
- `scripts/README.md`: Script Uebersicht.
- `vector_mcp/README.md`: MCP Server Details.
- `story_tools/README.md`: Loader/Worker Details.
- `env/README.md`: Conda + uv Umgebung fuer lokale Modelle.
