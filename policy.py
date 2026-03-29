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

        if self.triggered_rules:
            lines.append("- triggered rules:")
            for rule in self.triggered_rules:
                lines.append(f"  - {rule}")

        return "\n".join(lines)



@dataclass
class ScanPolicy:
    fail_on_severity: str = "medium"
    budget: PolicyBudget = field(default_factory=PolicyBudget)
    fail_on_rules: List[str] = field(default_factory=list)
    warn_on_rules: List[str] = field(default_factory=list)
    max_hotspot_findings: Optional[int] = None

    def to_dict(self) -> Dict[str, object]:
        return {
            "fail_on_severity": self.fail_on_severity,
            "budget": self.budget.to_dict(),
            "fail_on_rules": list(self.fail_on_rules),
            "warn_on_rules": list(self.warn_on_rules),
            "max_hotspot_findings": self.max_hotspot_findings,
        }


def evaluate_policy(findings: Iterable[object], policy: ScanPolicy) -> PolicyResult:
    items = list(findings)
    counts = count_by_severity(items)

    reasons: List[str] = []
    triggered_rules: List[str] = []

    fail_rank = SEVERITY_RANK.get(policy.fail_on_severity.lower(), 2)
    matched_fail_severity = [
        f for f in items if SEVERITY_RANK.get(str(getattr(f, "severity", "low")).lower(), 1) >= fail_rank
    ]
    if matched_fail_severity:
        reasons.append(
            f"Found {len(matched_fail_severity)} finding(s) at or above severity '{policy.fail_on_severity}'."
        )















