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


def rule_too_many_stylesheets(file: str, text: str, inv) -> List:
    out = []
    stylesheet_links = 0
    for m in LINK_TAG_RE.finditer(text):
        attrs = _attrs(m.group(0))
        if attrs.get("rel", "").lower() == "stylesheet":
            stylesheet_links += 1

    if stylesheet_links > 6:
        out.append(
            make_finding(
                "ADV001",
                "medium",
                "Too many stylesheet requests",
                f"Found {stylesheet_links} stylesheet link tags in one file.",
                file=file,
                help="Too many CSS requests can delay rendering. Consider bundling or reducing non-critical stylesheets.",
            )
        )
    return out


def rule_preload_stylesheet_hack(file: str, text: str, inv) -> List:
    out = []
    lower = text.lower()
    if 'rel="preload"' in lower and 'as="style"' in lower and "onload=" in lower:
        out.append(
            make_finding(
                "ADV002",
                "low",
                "Preload stylesheet onload hack detected",
                "Found preload+onload stylesheet pattern. Verify fallback and browser behavior carefully.",
                file=file,
                help="This pattern can be effective, but should be tested for browser compatibility and noscript fallback.",
            )
        )
    return out


def rule_too_many_third_party_scripts(file: str, text: str, inv) -> List:
    out = []
    count = 0
    third_party_hosts = set()

    for m in SCRIPT_TAG_RE.finditer(text):
        attrs = _attrs(m.group(0))
        src = attrs.get("src", "")
        if not src:
            continue
        src_l = src.lower()







