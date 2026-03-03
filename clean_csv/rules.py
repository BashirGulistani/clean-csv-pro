from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional, Union


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str 
    title: str
    message: str
    file: str
    line: int = 1
    col: int = 1
    help: str = ""




def make_finding(
    rule_id: str,
    severity: str,
    title: str,
    message: str,
    file: str,
    line: int = 1,
    col: int = 1,
    help: str = "",
) -> Finding:
    return Finding(
        rule_id=rule_id,
        severity=severity,
        title=title,
        message=message,
        file=file,
        line=max(1, int(line)),
        col=max(1, int(col)),
        help=help,
    )


CheckFn = Callable[[str, Union[str, Path], object], List[Finding]]




@dataclass(frozen=True)
class Rule:
    id: str
    title: str
    applies_to: str  
    severity: str
    description: str
    check: Callable



IMG_TAG_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
ATTR_RE = re.compile(r'(\w[\w:-]*)\s*=\s*(".*?"|\'.*?\'|[^\s>]+)', re.IGNORECASE)

SCRIPT_TAG_RE = re.compile(r"<script\b[^>]*>", re.IGNORECASE)


def _attrs(tag: str) -> dict:
    attrs = {}
    for m in ATTR_RE.finditer(tag):
        k = (m.group(1) or "").lower()
        v = (m.group(2) or "").strip().strip('"').strip("'")
        attrs[k] = v
    return attrs


def rule_missing_img_alt(file: str, text: str, inv) -> List[Finding]:
    out: List[Finding] = []
    for m in IMG_TAG_RE.finditer(text):
        tag = m.group(0)
        a = _attrs(tag)
        aria_hidden = (a.get("aria-hidden", "").lower() == "true")
        role = (a.get("role", "").lower())
        if aria_hidden or role == "presentation":
            continue

        if "alt" not in a:
            line = text[: m.start()].count("\n") + 1
            out.append(
                make_finding(
                    "A11Y001",
                    "high",
                    "Image missing alt text",
                    "Found <img> without alt attribute. Add meaningful alt text, or alt=\"\" for decorative images.",
                    file=file,
                    line=line,
                    help="Missing alt hurts accessibility and SEO. If decorative, use alt=\"\" and optionally aria-hidden=\"true\".",
                )
            )
    return out




