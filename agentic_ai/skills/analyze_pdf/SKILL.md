---
name: analyze_pdf
description: >-
  Produce an analysis of the uploaded PDF, optionally using prior documents
  as context when decide_prior_context returned use.
---

# Analyze PDF

## When to use

- After OCR and a prior-context decision (`use`, `skip`, or resolved `ask`)

## Inputs

- Current document text / path
- Optional prior document ids and their text

## Outputs

- Structured analysis result (domain-defined)

## Notes

- If decision was `skip`, analyze the upload alone
- Cite prior docs when they influenced the result
