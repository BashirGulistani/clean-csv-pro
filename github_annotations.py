from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Iterable, List, Optional

from .rules import Finding

_SEV_TO_CMD = {"low": "notice", "medium": "warning", "high": "error"}




def _escape(s: str) -> str:

    if s is None:
        return ""
    return (
        str(s)
        .replace("%", "%25")
        .replace("\r", "%0D")
        .replace("\n", "%0A")
        .replace(":", "%3A")
        .replace(",", "%2C")
    )



def _normalize_path(path: str) -> str:
    ws = os.getenv("GITHUB_WORKSPACE", "")
    if ws and path.startswith(ws):
        p = path[len(ws):]
        if p.startswith("/") or p.startswith("\\"):
            p = p[1:]
        return p
    return path







@dataclass
class Annotation:
    level: str  
    file: str
    line: int
    col: int
    title: str
    message: str

def findings_to_annotations(findings: Iterable[Finding]) -> List[Annotation]:
    ann: List[Annotation] = []
    for f in findings:
        if f.file == "__inventory__":
            continue
        level = _SEV_TO_CMD.get(f.severity, "warning")
        ann.append(
            Annotation(
                level=level,
                file=_normalize_path(f.file),
                line=max(1, int(f.line)),
                col=max(1, int(f.col)),
                title=f"{f.rule_id} {f.title}",
                message=f.message,
            )
        )
    return ann




