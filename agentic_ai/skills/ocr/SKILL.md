---
name: ocr
description: >-
  Extract text and layout signals from a document. Use when a file needs
  text extraction before search, ingest, or analysis.
---

# OCR

## When to use

- A new document has been uploaded and text is not yet available
- Confidence or coverage of existing text is insufficient

## Inputs

- `document_path`: path to the source file

## Outputs

- `text`, `pages`, optional `blocks`, `confidence`

## Notes

- Low confidence should be surfaced to the agent; do not treat OCR as ground truth
