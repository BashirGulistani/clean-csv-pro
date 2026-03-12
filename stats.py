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
