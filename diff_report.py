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




