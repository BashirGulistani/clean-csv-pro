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









