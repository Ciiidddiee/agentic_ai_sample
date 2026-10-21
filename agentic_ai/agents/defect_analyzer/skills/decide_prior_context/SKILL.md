---
name: decide_prior_context
description: >-
  Decide use (analyze with priors) or ask (human chooses continue / ingest /
  drop / use). No automatic skip-to-analyze.
---

# Decide prior context

Agent outputs **use** or **ask** only. Under **ask**, resume with
`DefectAnalyzer.run(..., user_action=...)`.
