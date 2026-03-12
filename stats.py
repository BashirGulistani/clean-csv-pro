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






