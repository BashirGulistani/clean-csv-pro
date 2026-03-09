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




def print_github_annotations(findings: List[Finding], max_annotations: int = 200) -> str:

    anns = findings_to_annotations(findings)[:max_annotations]
    for a in anns:
        msg = f"{a.title}: {a.message}".strip()
        cmd = (
            f"::{a.level} "
            f"file={_escape(a.file)},line={a.line},col={a.col}::{_escape(msg)}"
        )
        print(cmd)

    skipped = max(0, len(findings_to_annotations(findings)) - len(anns))
    return f"[github] emitted {len(anns)} annotations" + (f" (skipped {skipped})" if skipped else "")







def findings_to_check_run_json(findings: List[Finding], title: str = "ThemeAudit", max_items: int = 500) -> str:

    items = []
    for f in findings:
        if len(items) >= max_items:
            break
        items.append(
            {
                "rule_id": f.rule_id,
                "severity": f.severity,
                "title": f.title,
                "message": f.message,
                "file": f.file,
                "line": f.line,
                "col": f.col,
                "help": f.help,
            }
        )

    payload = {
        "tool": title,
        "count": len(items),
        "items": items,
    }
    return json.dumps(payload, indent=2)

def summarize_annotations(findings: List[Finding]) -> str:
    anns = findings_to_annotations(findings)
    c = {"error": 0, "warning": 0, "notice": 0}
    for a in anns:
        c[a.level] = c.get(a.level, 0) + 1
    return f"[github] annotations ready: error={c['error']} warning={c['warning']} notice={c['notice']} total={len(anns)}"



