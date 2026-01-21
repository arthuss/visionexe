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
- Database: `exegetos`
- User: `exegetos_user`
- Password: `dev_password`

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
      "args": ["run", "--project", "G:\\QDRANT\\vector_mcp\\VectorMcpServer"]
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

Create `vector_mcp/.env` (see `.env.example`) and set the connection values.

Minimal env:
- VECTOR_DB_HOST, VECTOR_DB_PORT, VECTOR_DB_NAME
- VECTOR_DB_USER, VECTOR_DB_PASSWORD
- QDRANT_HOST, QDRANT_HTTP_PORT, QDRANT_GRPC_PORT
- EMBEDDING_ENDPOINT (optional, HTTP embed service)
- EMBEDDING_DIMENSION (default: 1024)

Notes:
- QDRANT_GRPC_PORT is used by the MCP server (gRPC client).
- QDRANT_HTTP_PORT is used by loader/worker scripts (REST).

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

DeleteDocument is disabled unless VECTOR_DELETE_TOKEN is set and provided.

## Access control

For append-only agents, use a restricted Postgres role (SELECT + INSERT on vector_documents) and point
VECTOR_DB_USER/VECTOR_DB_PASSWORD to that role. Keep DELETE disabled unless you enable
VECTOR_DELETE_TOKEN for an admin session.
