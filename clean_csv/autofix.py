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

def _insert_attr(tag: str, attr: str) -> str:

    if tag.endswith("/>"):
        return tag[:-2] + " " + attr + " />"
    if tag.endswith(">"):
        return tag[:-1] + " " + attr + ">"
    return tag

def _set_attr(tag: str, key: str, value: str) -> str:

    key_l = key.lower()


    def repl(m: re.Match) -> str:
        k = (m.group(1) or "")
        if k.lower() == key_l:

            return f'{k}="{value}"'
        return m.group(0)

    new_tag, n = ATTR_RE.subn(repl, tag)
    if n > 0 and key_l in _attrs(new_tag):
        return new_tag


    return _insert_attr(tag, f'{key}="{value}"')

def _is_decorative_img(attrs: Dict[str, str]) -> bool:

    cls = (attrs.get("class", "") or "").lower()
    src = (attrs.get("src", "") or attrs.get("data-src", "") or "").lower()
    if attrs.get("aria-hidden", "").lower() == "true":
        return True
    if attrs.get("role", "").lower() in ("presentation", "none"):
        return True
    if any(x in cls for x in ("icon", "sprite", "payment", "badge", "svg", "social")):
        return True
    if src.endswith(".svg"):
        return True
    if "/icons/" in src or "icon" in src or "sprite" in src:
        return True
    return False

def _likely_below_fold(tag_start_index: int) -> bool:

    return tag_start_index > 2000



