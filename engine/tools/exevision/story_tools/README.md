# Story tools

Tools for loading chapter text into the vector stores and building inter-collection links.

## story_loader.py
Loads chapter files into Postgres (vector_documents) and Qdrant.

Example:
```
python story_loader.py --data-dir ..\..\..\..\data\Story1-Henoch
```

Options:
- --no-postgres / --no-qdrant to skip a backend
- --embedding-endpoint to use an HTTP embed service
- --embedding-model to use a local sentence-transformers model

## intercollection_worker.py
Builds cross-collection links by searching each point against other collections.

Example:
```
python intercollection_worker.py --collections chapter_01,chapter_02 --limit 3 --threshold 0.75
```

Use --store-db to persist links in Postgres (table intercollection_links).
