from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional


SEVERITY_RANK = {"low": 1, "medium": 2, "high": 3}







@dataclass
class PolicyBudget:
    high: Optional[int] = None
    medium: Optional[int] = None
    low: Optional[int] = None
    total: Optional[int] = None

    def to_dict(self) -> Dict[str, Optional[int]]:
        return {
            "high": self.high,
            "medium": self.medium,
            "low": self.low,
            "total": self.total,
        }






@dataclass
class PolicyResult:
    passed: bool
    reasons: List[str] = field(default_factory=list)
    counts: Dict[str, int] = field(default_factory=dict)
    triggered_rules: List[str] = field(default_factory=list)

    def render_text(self) -> str:
        lines: List[str] = []
        lines.append("[policy] evaluation")
        lines.append(f"- passed: {'yes' if self.passed else 'no'}")

        if self.counts:
            lines.append(
                "- counts: "
                f"high={self.counts.get('high', 0)}, "
                f"medium={self.counts.get('medium', 0)}, "
                f"low={self.counts.get('low', 0)}, "
                f"total={self.counts.get('total', 0)}"
            )

        if self.reasons:
            lines.append("- reasons:")
            for reason in self.reasons:
                lines.append(f"  - {reason}")







