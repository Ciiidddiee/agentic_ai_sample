---
name: ingest
description: >-
  Normalize a document and index it into a store. Use after a successful
  analysis or when explicitly adding documents to the knowledge base.
---

# Ingest

## When to use

- A document should become searchable for future uploads
- Re-indexing after OCR/config changes

## Inputs

- `document_path`
- `store` (default `knowledge_base`)

## Outputs

- `document_id`, paths for processed artifacts

## Notes

- Prefer ingest as the only write path into the knowledge base
