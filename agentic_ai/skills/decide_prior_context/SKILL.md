---
name: decide_prior_context
description: >-
  Decide whether search hits should be used as analysis context. Returns
  use, skip, or ask. Product-specific; may call no tools.
---

# Decide prior context

## When to use

- After `search` returns candidates for the current upload

## Inputs

- Current document summary / OCR text
- Ranked search hits
- Policy thresholds (see `config/policy.yaml`)

## Outputs

- `decision`: `use` | `skip` | `ask`
- `document_ids`: list when `use`
- `reason`: short explanation

## Notes

- Near misses (same form, different year; shared boilerplate) should skew to `ask` or `skip`
- Empty hits → `skip`
