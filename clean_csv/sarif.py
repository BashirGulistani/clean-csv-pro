from __future__ import annotations

import json
from typing import List

from .rules import Finding


_SEV_TO_LEVEL = {"low": "note", "medium": "warning", "high": "error"}





def to_sarif_json(findings: List[Finding], repo_root: str = "") -> str:
    rules = {}
    for f in findings:
        if f.rule_id not in rules:
            rules[f.rule_id] = {
                "id": f.rule_id,
                "name": f.title,
                "shortDescription": {"text": f.title},
                "fullDescription": {"text": f.help or f.message or f.title},
                "defaultConfiguration": {"level": _SEV_TO_LEVEL.get(f.severity, "warning")},
            }




