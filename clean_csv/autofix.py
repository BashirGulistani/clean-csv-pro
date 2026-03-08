from __future__ import annotations

import difflib
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


TEXT_EXTS = {".liquid", ".html", ".htm"}

IMG_TAG_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
SCRIPT_TAG_RE = re.compile(r"<script\b[^>]*>", re.IGNORECASE)

ATTR_RE = re.compile(r'(\w[\w:-]*)\s*=\s*(".*?"|\'.*?\'|[^\s>]+)', re.IGNORECASE)

LIQUID_COMPLEX_RE = re.compile(r"{%|{{", re.IGNORECASE)



def _read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")

def _write_text(p: Path, text: str) -> None:
    p.write_text(text, encoding="utf-8")

def _attrs(tag: str) -> Dict[str, str]:
    attrs = {}
    for m in ATTR_RE.finditer(tag):
        k = (m.group(1) or "").lower()
        v = (m.group(2) or "").strip().strip('"').strip("'")
        attrs[k] = v
    return attrs

def _has_attr(tag: str, name: str) -> bool:
    name_l = name.lower()
    if re.search(rf"\b{name_l}\b", tag.lower()):
        return True
    return False




