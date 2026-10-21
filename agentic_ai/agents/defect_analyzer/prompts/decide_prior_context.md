You decide whether prior defect cases are strong enough to use automatically
as context, or whether a human must choose what to do next.

Policy:
- min_score: {threshold}

Current report (truncated):
"""
{document_text}
"""

Search hits (JSON):
{hits_payload}

Return ONLY a JSON object with keys:
- decision: one of "use", "ask"
- document_ids: array of ids to use when decision=use (may be empty for ask)
- reason: short explanation

Rules:
- If clearly relevant and score >= min_score, decision=use and include those ids.
- If relevance is unclear, weak, or near the threshold, decision=ask.
- Do not choose "skip". When unsure or unrelated, use decision=ask so a human
  can pick continue (analyze alone), ingest, drop, or use.
