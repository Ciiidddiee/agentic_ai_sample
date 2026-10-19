---
name: search
description: >-
  Query a document store for similar or relevant items. Use when prior
  documents may provide useful context. Scores are candidates, not proof.
---

# Search

## When to use

- After OCR (or when query text is already available)
- Before deciding whether to attach prior context

## Inputs

- `query`: text or embedding source text
- `store`: store id (default `knowledge_base`)
- `top_k`: number of hits

## Outputs

- Ranked list of `{id, score, snippet, metadata}`

## Notes

- High score ≠ correct context; pass hits to decision logic
- Empty results are valid; analysis may proceed without prior docs
