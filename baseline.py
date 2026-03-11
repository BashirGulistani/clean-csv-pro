from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple


BASELINE_VERSION = 1


@dataclass(frozen=True)
class BaselineEntry:
    fingerprint: str
    rule_id: str
    severity: str
    file: str
    line: int
    title: str




def _stable_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def finding_fingerprint(finding: object) -> str:
    """
    Produces a stable-enough fingerprint for a finding.
    Uses:
    - rule_id
    - severity
    - file
    - line
    - title
    - message (normalized)
    """
    rule_id = _stable_text(getattr(finding, "rule_id", ""))
    severity = _stable_text(getattr(finding, "severity", ""))
    file = _stable_text(getattr(finding, "file", ""))
    line = int(getattr(finding, "line", 1) or 1)
    title = _stable_text(getattr(finding, "title", ""))
    message = _stable_text(getattr(finding, "message", ""))

    normalized = "|".join([
        rule_id,
        severity,
        file.replace("\\", "/"),
        str(line),
        title,
        " ".join(message.split()),
    ])

    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()






