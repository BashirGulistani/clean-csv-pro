from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Tuple


SEVERITY_ORDER = {"high": 3, "medium": 2, "low": 1}


@dataclass
class SeverityBreakdown:
    high: int = 0
    medium: int = 0
    low: int = 0

    @property
    def total(self) -> int:
        return self.high + self.medium + self.low

    def to_dict(self) -> Dict[str, int]:
        return {
            "high": self.high,
            "medium": self.medium,
            "low": self.low,
            "total": self.total,
        }



@dataclass
class RuleStat:
    rule_id: str
    count: int = 0
    severity: str = "low"
    title: str = ""


@dataclass
class FileStat:
    file: str
    count: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0

    @property
    def weighted_score(self) -> int:
        return self.high * 5 + self.medium * 3 + self.low * 1

    def to_dict(self) -> Dict[str, int | str]:
        return {
            "file": self.file,
            "count": self.count,
            "high": self.high,
            "medium": self.medium,
            "low": self.low,
            "weighted_score": self.weighted_score,
        }






@dataclass
class ThemeStats:
    breakdown: SeverityBreakdown = field(default_factory=SeverityBreakdown)
    rules: List[RuleStat] = field(default_factory=list)
    files: List[FileStat] = field(default_factory=list)
    health_score: int = 100
    risk_level: str = "excellent"
    total_findings: int = 0

    def to_dict(self) -> Dict[str, object]:
        return {
            "breakdown": self.breakdown.to_dict(),
            "rules": [
                {
                    "rule_id": r.rule_id,
                    "count": r.count,
                    "severity": r.severity,
                    "title": r.title,
                }
                for r in self.rules
            ],
            "files": [f.to_dict() for f in self.files],
            "health_score": self.health_score,
            "risk_level": self.risk_level,
            "total_findings": self.total_findings,
        }




def compute_stats(findings: Iterable[object], top_rules: int = 15, top_files: int = 15) -> ThemeStats:
    findings_list = list(findings)

    breakdown = SeverityBreakdown()
    rules_map: Dict[str, RuleStat] = {}
    files_map: Dict[str, FileStat] = {}

    for f in findings_list:
        severity = str(getattr(f, "severity", "low")).lower()
        rule_id = str(getattr(f, "rule_id", "UNKNOWN"))
        title = str(getattr(f, "title", ""))
        file = str(getattr(f, "file", "__inventory__"))

        if severity == "high":
            breakdown.high += 1
        elif severity == "medium":
            breakdown.medium += 1
        else:
            breakdown.low += 1

        if rule_id not in rules_map:
            rules_map[rule_id] = RuleStat(
                rule_id=rule_id,
                count=0,
                severity=severity,
                title=title,
            )
        rules_map[rule_id].count += 1

        if file not in files_map:
            files_map[file] = FileStat(file=file)
        files_map[file].count += 1
        if severity == "high":
            files_map[file].high += 1
        elif severity == "medium":
            files_map[file].medium += 1
        else:
            files_map[file].low += 1

    rules_sorted = sorted(
        rules_map.values(),
        key=lambda r: (-r.count, -SEVERITY_ORDER.get(r.severity, 1), r.rule_id),
    )[:top_rules]

    files_sorted = sorted(
        files_map.values(),
        key=lambda x: (-x.weighted_score, -x.count, x.file),
    )[:top_files]

    score = calculate_health_score(
        high=breakdown.high,
        medium=breakdown.medium,
        low=breakdown.low,
        total_files=max(1, len(files_map)),
    )

    risk = classify_risk(score)

    return ThemeStats(
        breakdown=breakdown,
        rules=rules_sorted,
        files=files_sorted,
        health_score=score,
        risk_level=risk,
        total_findings=breakdown.total,
    )


def calculate_health_score(high: int, medium: int, low: int, total_files: int = 1) -> int:
    """
    Produces a 0-100 score.
    Heavier penalty for high severity findings.
    Slight normalization by file count to avoid punishing larger themes too harshly.
    """
    weighted = high * 10 + medium * 4 + low * 1

    # normalize pressure a bit by number of touched files
    normalized = weighted / max(1.0, min(float(total_files), 100.0) ** 0.5)

    # convert to score
    score = int(round(100 - normalized * 3.2))

    if high >= 10:
        score -= 10
    if medium >= 25:
        score -= 5

    return max(0, min(100, score))


def classify_risk(score: int) -> str:
    if score >= 92:
        return "excellent"
    if score >= 80:
        return "good"
    if score >= 65:
        return "fair"
    if score >= 45:
        return "poor"
    return "critical"


def summarize_stats(stats: ThemeStats) -> str:
    lines: List[str] = []
    lines.append("[stats] theme health")

    lines.append(f"- score: {stats.health_score}/100")
    lines.append(f"- risk: {stats.risk_level}")
    lines.append(f"- findings: {stats.total_findings}")
    lines.append(
        f"- severity breakdown: high={stats.breakdown.high}, medium={stats.breakdown.medium}, low={stats.breakdown.low}"
    )

    if stats.rules:
        lines.append("- top rules:")
        for r in stats.rules[:8]:
            lines.append(
                f"  - {r.rule_id} ({r.severity}) x{r.count} — {r.title}"
            )

    if stats.files:
        lines.append("- hotspot files:")
        for f in stats.files[:8]:
            lines.append(
                f"  - {f.file}: total={f.count}, weighted={f.weighted_score}, high={f.high}, medium={f.medium}, low={f.low}"
            )

    return "\n".join(lines)


def findings_trend_summary(current_findings: Iterable[object], previous_findings: Iterable[object]) -> str:
    current = list(current_findings)
    previous = list(previous_findings)

    cur_stats = compute_stats(current)
    prev_stats = compute_stats(previous)

    delta_total = cur_stats.total_findings - prev_stats.total_findings
    delta_high = cur_stats.breakdown.high - prev_stats.breakdown.high
    delta_medium = cur_stats.breakdown.medium - prev_stats.breakdown.medium
    delta_low = cur_stats.breakdown.low - prev_stats.breakdown.low
    delta_score = cur_stats.health_score - prev_stats.health_score

    lines: List[str] = []
    lines.append("[stats] comparison")
    lines.append(
        f"- findings: {prev_stats.total_findings} -> {cur_stats.total_findings} ({_fmt_delta(delta_total, inverse=True)})"
    )
    lines.append(
        f"- high: {prev_stats.breakdown.high} -> {cur_stats.breakdown.high} ({_fmt_delta(delta_high, inverse=True)})"
    )
    lines.append(
        f"- medium: {prev_stats.breakdown.medium} -> {cur_stats.breakdown.medium} ({_fmt_delta(delta_medium, inverse=True)})"
    )
    lines.append(
        f"- low: {prev_stats.breakdown.low} -> {cur_stats.breakdown.low} ({_fmt_delta(delta_low, inverse=True)})"
    )
    lines.append(
        f"- score: {prev_stats.health_score} -> {cur_stats.health_score} ({_fmt_delta(delta_score, inverse=False)})"
    )


    if delta_score > 0:
        lines.append("- result: theme quality improved")
    elif delta_score < 0:
        lines.append("- result: theme quality regressed")
    else:
        lines.append("- result: no significant score change")

    return "\n".join(lines)



def group_findings_by_rule(findings: Iterable[object]) -> Dict[str, List[object]]:
    out: Dict[str, List[object]] = {}
    for f in findings:
        rule_id = str(getattr(f, "rule_id", "UNKNOWN"))
        out.setdefault(rule_id, []).append(f)
    return out


def group_findings_by_file(findings: Iterable[object]) -> Dict[str, List[object]]:
    out: Dict[str, List[object]] = {}
    for f in findings:
        file = str(getattr(f, "file", "__inventory__"))
        out.setdefault(file, []).append(f)
    return out



