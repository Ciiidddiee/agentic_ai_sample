Analyze this defect / quality report. Focus on defect type, affected part or
area, likely cause signals, and severity. Use prior cases only if provided.

Uploaded report:
"""
{document_text}
"""

Prior defect cases:
{prior_block}

Return ONLY a JSON object with keys:
- summary: string (short defect summary)
- findings: array of short strings
- severity: one of "low", "medium", "high", "unknown"
- citations: array of prior document ids actually used (empty if none)
