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

    if policy.budget.high is not None and counts["high"] > policy.budget.high:
        reasons.append(
            f"High severity budget exceeded: {counts['high']} > {policy.budget.high}."
        )

    if policy.budget.medium is not None and counts["medium"] > policy.budget.medium:
        reasons.append(
            f"Medium severity budget exceeded: {counts['medium']} > {policy.budget.medium}."
        )

    if policy.budget.low is not None and counts["low"] > policy.budget.low:
        reasons.append(
            f"Low severity budget exceeded: {counts['low']} > {policy.budget.low}."
        )

    if policy.budget.total is not None and counts["total"] > policy.budget.total:
        reasons.append(
            f"Total findings budget exceeded: {counts['total']} > {policy.budget.total}."
        )

    fail_on_rules_set = {x.strip().upper() for x in policy.fail_on_rules if str(x).strip()}
    if fail_on_rules_set:
        matched_rules = sorted({
            str(getattr(f, "rule_id", "")).upper()
            for f in items
            if str(getattr(f, "rule_id", "")).upper() in fail_on_rules_set
        })
        if matched_rules:
            triggered_rules.extend(matched_rules)
            reasons.append(
                f"Blocked rule(s) present: {', '.join(matched_rules)}."
            )

    if policy.max_hotspot_findings is not None:
        worst_file, worst_count = worst_hotspot(items)
        if worst_count > policy.max_hotspot_findings:
            reasons.append(
                f"Hotspot limit exceeded: file '{worst_file}' has {worst_count} findings "
                f"(limit {policy.max_hotspot_findings})."
            )

    passed = len(reasons) == 0

    return PolicyResult(
        passed=passed,
        reasons=reasons,
        counts=counts,
        triggered_rules=sorted(set(triggered_rules)),
    )


def count_by_severity(findings: Iterable[object]) -> Dict[str, int]:
    counts = {"high": 0, "medium": 0, "low": 0, "total": 0}
    for f in findings:
        sev = str(getattr(f, "severity", "low")).lower()
        if sev not in counts:
            sev = "low"
        counts[sev] += 1
        counts["total"] += 1
    return counts


def findings_by_rule(findings: Iterable[object]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for f in findings:
        rule_id = str(getattr(f, "rule_id", "UNKNOWN")).upper()
        out[rule_id] = out.get(rule_id, 0) + 1
    return out


def findings_by_file(findings: Iterable[object]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for f in findings:
        file = str(getattr(f, "file", "__inventory__"))
        out[file] = out.get(file, 0) + 1
    return out


def worst_hotspot(findings: Iterable[object]) -> tuple[str, int]:
    by_file = findings_by_file(findings)
    if not by_file:
        return ("", 0)
    file, count = sorted(by_file.items(), key=lambda x: (-x[1], x[0]))[0]
    return file, count


def render_policy_markdown(result: PolicyResult, title: str = "ThemeAudit Policy Result") -> str:
    lines: List[str] = []
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"- Passed: **{'Yes' if result.passed else 'No'}**")
    lines.append(
        f"- Counts: high={result.counts.get('high', 0)}, "
        f"medium={result.counts.get('medium', 0)}, "
        f"low={result.counts.get('low', 0)}, "
        f"total={result.counts.get('total', 0)}"
    )
    lines.append("")

    if result.reasons:
        lines.append("## Reasons")
        lines.append("")
        for reason in result.reasons:
            lines.append(f"- {reason}")
        lines.append("")

    if result.triggered_rules:
        lines.append("## Triggered Rules")
        lines.append("")
        for rule in result.triggered_rules:
            lines.append(f"- `{rule}`")
        lines.append("")

    if not result.reasons:
        lines.append("No policy violations found.")
        lines.append("")

    return "\n".join(lines)


def make_default_policy() -> ScanPolicy:
    return ScanPolicy(
        fail_on_severity="medium",
        budget=PolicyBudget(
            high=0,
            medium=20,
            low=100,
            total=120,
        ),
        fail_on_rules=["A11Y001", "PERF002"],
        warn_on_rules=["PERF001", "PERF010"],
        max_hotspot_findings=25,
    )


def parse_policy_dict(data: Dict[str, object]) -> ScanPolicy:
    budget_raw = data.get("budget", {})
    if not isinstance(budget_raw, dict):
        budget_raw = {}

    budget = PolicyBudget(
        high=_maybe_int(budget_raw.get("high")),
        medium=_maybe_int(budget_raw.get("medium")),
        low=_maybe_int(budget_raw.get("low")),
        total=_maybe_int(budget_raw.get("total")),
    )

    fail_on_rules = _normalize_str_list(data.get("fail_on_rules", []))
    warn_on_rules = _normalize_str_list(data.get("warn_on_rules", []))

    fail_on_severity = str(data.get("fail_on_severity", "medium")).strip().lower()
    if fail_on_severity not in {"low", "medium", "high"}:
        fail_on_severity = "medium"

    return ScanPolicy(
        fail_on_severity=fail_on_severity,
        budget=budget,
        fail_on_rules=fail_on_rules,
        warn_on_rules=warn_on_rules,
        max_hotspot_findings=_maybe_int(data.get("max_hotspot_findings")),
    )


def render_policy_json(policy: ScanPolicy) -> str:
    import json
    return json.dumps(policy.to_dict(), indent=2)


def _maybe_int(value: object) -> Optional[int]:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except Exception:
        return None


def _normalize_str_list(value: object) -> List[str]:
    if not isinstance(value, list):
        return []
    out: List[str] = []
    for item in value:
        s = str(item).strip()
        if s:
            out.append(s.upper())
    return out
