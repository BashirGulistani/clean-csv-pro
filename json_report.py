from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .stats import compute_stats


def _safe_str(value: object) -> str:
    if value is None:
        return ""
    return str(value)




def _safe_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def finding_to_dict(finding: object) -> Dict[str, Any]:
    """
    Convert a finding-like object into a JSON-safe dictionary.
    Supports:
    - dataclass findings
    - normal objects with finding attributes
    - dict-like objects
    """
    if isinstance(finding, dict):
        return {
            "rule_id": _safe_str(finding.get("rule_id", "")),
            "severity": _safe_str(finding.get("severity", "low")),
            "title": _safe_str(finding.get("title", "")),
            "message": _safe_str(finding.get("message", "")),
            "file": _safe_str(finding.get("file", "")),
            "line": _safe_int(finding.get("line", 1), 1),
            "col": _safe_int(finding.get("col", 1), 1),
            "help": _safe_str(finding.get("help", "")),
        }

    if is_dataclass(finding):
        raw = asdict(finding)
        return {









