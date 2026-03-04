from __future__ import annotations

from collections import Counter
from typing import List

from .rules import Finding





def render_text(findings: List[Finding]) -> str:
    if not findings:
        return "[ok] No findings (at selected severity threshold)."

    c = Counter(f.severity for f in findings)
    top = f"[findings] high={c.get('high',0)} medium={c.get('medium',0)} low={c.get('low',0)} total={len(findings)}"
    lines = [top]
