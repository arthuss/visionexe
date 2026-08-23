# Vector MCP Server

Ein Model Context Protocol (MCP) Server für die Interaktion mit PostgreSQL (pgvector) und Qdrant Vector Database.

## Features

- **Dokument-Speicherung**: Speichert Dokumente mit Embeddings in PostgreSQL und Qdrant
- **Vektor-Suche**: Semantic Search mit Cosine-Similarity
- **Collection-Management**: Verwaltet Sammlungen in beiden Datenbanken
- **MCP-Integration**: Vollständig kompatibel mit MCP-Clients wie Claude Desktop

## Voraussetzungen

- .NET 10
- PostgreSQL mit pgvector Extension (Container läuft auf Port 5432)
- Qdrant Vector Database (Container läuft auf Port 6333)

## Container Setup

Die Container sind bereits konfiguriert:

**PostgreSQL (pgvector)**:
- Image: `pgvector/pgvector:pg16`
- Port: `${VECTOR_DB_PORT:-5434}:5432`
- Database: `${VECTOR_DB_NAME:-exegetos}`
- User: `${VECTOR_DB_USER:-vector_admin}`
- Password: `${VECTOR_DB_PASSWORD:-change_me}`

**Qdrant**:
- Image: `qdrant/qdrant:v1.8.1`  
- Ports: `${QDRANT_HTTP_PORT:-6335}:6333`, `${QDRANT_GRPC_PORT:-6336}:6334`

## Installation & Start

```bash
# Projekt kompilieren
dotnet build

# Server starten
dotnet run
```

## MCP Tools

Der Server stellt folgende Tools zur Verfügung:

### `StoreDocument`
Speichert ein Dokument mit Embedding in beiden Datenbanken.

**Parameter:**
- `collection` (string): Name der Collection
- `title` (string): Titel des Dokuments
- `content` (string): Inhalt des Dokuments  
- `metadata` (string, optional): Metadaten als JSON

### `SearchDocuments`
Sucht ähnliche Dokumente mit Vektor-Similarity.

**Parameter:**
- `collection` (string): Collection zum Durchsuchen
- `query` (string): Suchtext
- `limit` (int, default: 5): Anzahl Ergebnisse
- `threshold` (float, default: 0.7): Similarity-Schwellenwert
- `source` (string, default: "both"): Suchquelle ("postgres", "qdrant", "both")

### `ListCollections`
Listet alle verfügbaren Collections auf.

### `SearchDocumentsWithFilter`
Qdrant-Suche mit raw Filter-JSON (global collections + payload filtering).

**Parameter:**
- `collection` (string)
- `query` (string)
- `filterJson` (string)
- `limit` (int, default: 5)
- `threshold` (float, default: 0.7)
- `hnswEf` (int, optional)
- `exact` (bool, default: false)

### `EngramLookup`
Deterministischer Engram-Lookup ueber `engram_index` (Hash-Overlap -> `document_id`) mit verlinkter Qdrant-Referenz.

**Parameter:**
- `query` (string): Suchtext fuer Engram-Hashing
- `collections` (string, default: `*`): Komma-separierte Collections oder `*`
- `limit` (int, default: 20)
- `minSharedHashes` (int, default: 1)
- `includeContent` (bool, default: false)

**Antwort (Kurz):**
- aggregierte Treffer aus `engram_index` mit `shared_hash_count`, `matched_layers`, `engram_score`
- verknuepfte Dokumentdaten aus Postgres (Titel/Metadaten, optional Content)
- `qdrant_ref` mit derselben `document_id` als Point-ID

### `ScrollPointsWithFilter`
Filter-only Qdrant scroll (exact match, no ANN) for full payload retrieval.

**Parameter:**
- `collection` (string)
- `filterJson` (string)
- `limit` (int, default: 100)
- `offsetJson` (string, optional)
- `withPayload` (bool, default: true)
- `withVectors` (bool, default: false)

### `DeleteDocument`
Löscht ein Dokument anhand der ID aus beiden Datenbanken.

**Parameter:**
- `documentId` (string): Dokument-ID
- `collection` (string): Collection-Name

### `GetDocument`
Ruft Dokumentdetails anhand der ID ab.

**Parameter:**
- `documentId` (string): Dokument-ID

## Claude Desktop Integration

Füge in `claude_desktop_config.json` hinzu:

```json
{
  "mcpServers": {
    "vector-mcp": {
      "command": "dotnet",
      "args": ["run", "--project", "C:\\Users\\sasch\\visionexe\\engine\\tools\\exevision\\vector_mcp\\VectorMcpServer"]
    }
  }
}
```

## Architektur

- **MCP Server**: ModelContextProtocol SDK für Tool-Integration
- **PostgreSQL**: Persistente Speicherung mit pgvector für Cosine-Similarity
- **Qdrant**: Spezialisierte Vektor-Datenbank für schnelle Similarity-Suche
- **Entity Framework Core**: ORM für PostgreSQL-Zugriff
- **Simple Embedding**: Demo-Embedding-Service (ersetze mit echtem Modell)

## Configuration (env)

Create `vector_mcp/.env` (see `.env.example`) and set the connection values. The server also checks
`VectorMcpServer/.env` and the current working directory for an `.env` file.

Minimal env:
- VECTOR_DB_HOST, VECTOR_DB_PORT, VECTOR_DB_NAME
- VECTOR_DB_USER, VECTOR_DB_PASSWORD
- QDRANT_HOST, QDRANT_HTTP_PORT, QDRANT_GRPC_PORT
- EMBEDDING_ENDPOINT (optional, HTTP embed service)
- EMBEDDING_DIMENSION (default: 1024)
 - QDRANT_PAYLOAD_MODE (default: minimal, values: minimal|full)

Notes:
- QDRANT_GRPC_PORT is used by the MCP server (gRPC client).
- QDRANT_HTTP_PORT is used by loader/worker scripts (REST).
- QDRANT_PAYLOAD_MODE=minimal stores only IDs + metadata in Qdrant; full also stores content.

## Parallel versioning (main + fast)

Wenn ein schneller Parallel-Workspace betrieben wird, Daten **nicht blind mergen**.

Empfohlen:
- getrennte Umgebungen je Variante (`.env.main`, `.env.fast`) mit eigener DB/Qdrant-Zielumgebung
- eigener `VECTOR_DB_NAME` pro Variante (z. B. `exegetos`, `exegetos_fast`)
- getrennte Qdrant-Instanz/Ports oder klarer Collection-Prefix (`fast_*`)
- gleiche Identifier-Norm beibehalten (`chapter_id`, `segment_label=segment_###`, `document_id`)
- Metadaten im Dokument setzen: `workspace_variant`, `pipeline_version`

Template:
- `engine/tools/exevision/vector_mcp/.env.fast.example`
- Umschalten/Bootstrap: `powershell -File engine/scripts/switch_fast.ps1 -StoryName fast`

Damit laufen beide Pipelines parallel, und Promotion in `main` kann kontrolliert per Export/Import erfolgen.

## Docker compose

From `vector_mcp/`:
```
docker compose up -d
```

## Embeddings

If you want Qwen3 embeddings, run a local embedding service and point
`EMBEDDING_ENDPOINT` to its `/embed` endpoint. If not set, the server falls back
to a deterministic hash embedding.

## MCP tools (additions)

- AppendAnalysis (stores analysis in a separate `__analysis` collection)
- SearchAcrossCollections (comma-separated list or `*`)
- CreateRun (canonical run record)
- StoreArtifact (canonical artifact record)
- LinkRunOutput (run -> artifact link)
- StoreTextUnit (canonical input text)
- StoreAnalysisArtifact (analysis output + lineage)
- CreateAssetSet / AddAssetToSet (bundle assets)
- LinkSubjectAssetSet (subject -> set)
- LinkLayer (ui/vfx/grade layer link)
- UpsertSubject / StoreSubjectOccurrence (subject canonical store)
- StoreSubjectOccurrence supports `phase_id` for subject phase queries
- GetAssetsBySegment (Qdrant filter + canonical store lookup for segment assets)
- GetDocumentByTitle / DeleteDocumentByTitle (lookup/delete by collection+title)
- EngramLookup (hash overlap lookup via engram_index -> linked document/qdrant ids)

DeleteDocument is disabled unless VECTOR_DELETE_TOKEN is set and provided.

## Access control

For append-only agents, use a restricted Postgres role (SELECT + INSERT on vector_documents) and point
VECTOR_DB_USER/VECTOR_DB_PASSWORD to that role. Keep DELETE disabled unless you enable
VECTOR_DELETE_TOKEN for an admin session.
