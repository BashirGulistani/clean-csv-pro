from __future__ import annotations

import re
from typing import List

from .rules import Rule, make_finding


LINK_TAG_RE = re.compile(r"<link\b[^>]*>", re.IGNORECASE)
SCRIPT_TAG_RE = re.compile(r"<script\b[^>]*>", re.IGNORECASE)
IMG_TAG_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
ATTR_RE = re.compile(r'(\w[\w:-]*)\s*=\s*(".*?"|\'.*?\'|[^\s>]+)', re.IGNORECASE)
URL_RE = re.compile(r'url\((.*?)\)', re.IGNORECASE)


def _attrs(tag: str) -> dict:
    attrs = {}
    for m in ATTR_RE.finditer(tag):
        k = (m.group(1) or "").lower()
        v = (m.group(2) or "").strip().strip('"').strip("'")
        attrs[k] = v
    return attrs










