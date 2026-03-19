from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Tuple


def _stable_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()








def finding_key(finding: object) -> Tuple[str, str, str, int, str, str]:
    """
    Stable comparison key for finding diffs.
    """
    return (
        _stable_text(getattr(finding, "rule_id", "")),
        _stable_text(getattr(finding, "severity", "")),
        _stable_text(getattr(finding, "file", "")).replace("\\", "/"),
        int(getattr(finding, "line", 1) or 1),
        _stable_text(getattr(finding, "title", "")),
        " ".join(_stable_text(getattr(finding, "message", "")).split()),
    )



@dataclass
class DiffItem:
    rule_id: str
    severity: str
    file: str
    line: int
    title: str
    message: str

    @classmethod
    def from_finding(cls, finding: object) -> "DiffItem":
        return cls(
            rule_id=_stable_text(getattr(finding, "rule_id", "")),
            severity=_stable_text(getattr(finding, "severity", "")),
            file=_stable_text(getattr(finding, "file", "")).replace("\\", "/"),
            line=int(getattr(finding, "line", 1) or 1),
            title=_stable_text(getattr(finding, "title", "")),
            message=" ".join(_stable_text(getattr(finding, "message", "")).split()),
        )

    def to_dict(self) -> Dict[str, object]:
        return {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "file": self.file,
            "line": self.line,
            "title": self.title,
            "message": self.message,
        }


@dataclass
class DiffSummary:
    added: List[DiffItem] = field(default_factory=list)
    removed: List[DiffItem] = field(default_factory=list)
    unchanged: List[DiffItem] = field(default_factory=list)

    @property
    def added_count(self) -> int:
        return len(self.added)

    @property
    def removed_count(self) -> int:
        return len(self.removed)

    @property
    def unchanged_count(self) -> int:
        return len(self.unchanged)

    def to_dict(self) -> Dict[str, object]:
        return {
            "added_count": self.added_count,
            "removed_count": self.removed_count,
            "unchanged_count": self.unchanged_count,
            "added": [x.to_dict() for x in self.added],
            "removed": [x.to_dict() for x in self.removed],
            "unchanged": [x.to_dict() for x in self.unchanged],
        }











