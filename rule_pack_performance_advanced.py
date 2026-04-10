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
        if src_l.startswith("http://") or src_l.startswith("https://") or src_l.startswith("//"):
            count += 1
            host = _extract_host(src_l)
            if host:
                third_party_hosts.add(host)

    if count >= 5:
        out.append(
            make_finding(
                "ADV003",
                "high",
                "Heavy third-party script usage",
                f"Found {count} external script tags across {len(third_party_hosts)} host(s).",
                file=file,
                help="Third-party scripts often dominate performance cost. Audit necessity, loading strategy, and duplication.",
            )
        )
    return out


def rule_missing_fetchpriority_hero(file: str, text: str, inv) -> List:
    out = []
    hero_candidates = 0

    for m in IMG_TAG_RE.finditer(text):
        tag = m.group(0)
        attrs = _attrs(tag)
        src = attrs.get("src", "") or attrs.get("data-src", "")
        if not src:
            continue

        cls = attrs.get("class", "").lower()
        alt = attrs.get("alt", "").lower()

        likely_hero = (
            m.start() < 1800 or
            "hero" in cls or
            "banner" in cls or
            "hero" in alt or
            "banner" in alt
        )

        if not likely_hero:
            continue

        hero_candidates += 1
        fetchpriority = attrs.get("fetchpriority", "").lower()
        if fetchpriority != "high":
            line = text[:m.start()].count("\n") + 1
            out.append(
                make_finding(
                    "ADV004",
                    "medium",
                    "Likely hero image missing fetchpriority",
                    "A likely above-the-fold image does not declare fetchpriority=\"high\".",
                    file=file,
                    line=line,
                    help="For the main LCP image, fetchpriority=\"high\" can improve loading priority in supported browsers.",
                )
            )
            break

    return out






def rule_excessive_background_images(file: str, text: str, inv) -> List:
    out = []
    hits = URL_RE.findall(text)
    bg_count = 0
    for raw in hits:
        val = raw.strip().strip('"').strip("'").lower()
        if any(ext in val for ext in (".png", ".jpg", ".jpeg", ".webp", ".gif", ".avif", ".svg")):
            bg_count += 1

    if bg_count >= 8:
        out.append(
            make_finding(
                "ADV005",
                "medium",
                "Many CSS background images detected",
                f"Found approximately {bg_count} image URL references in CSS or inline styles.",
                file=file,
                help="Background images can hide important media from optimization workflows like responsive images and lazy loading.",
            )
        )
    return out




def rule_duplicate_script_sources(file: str, text: str, inv) -> List:
    out = []
    seen = {}
    duplicates = []

    for m in SCRIPT_TAG_RE.finditer(text):
        attrs = _attrs(m.group(0))
        src = attrs.get("src", "").strip()
        if not src:
            continue
        src_key = src.lower()
        seen[src_key] = seen.get(src_key, 0) + 1

    for src, count in seen.items():
        if count > 1:
            duplicates.append((src, count))

    if duplicates:
        dup_text = ", ".join(f"{src} x{count}" for src, count in duplicates[:3])
        out.append(
            make_finding(
                "ADV006",
                "high",
                "Duplicate script includes",
                f"Detected duplicate script sources in the same file: {dup_text}",
                file=file,
                help="Duplicate script loading wastes bandwidth and can cause double execution bugs.",
            )
        )

    return out




def rule_too_many_eager_images(file: str, text: str, inv) -> List:
    out = []
    eager_count = 0

    for m in IMG_TAG_RE.finditer(text):
        attrs = _attrs(m.group(0))
        loading = attrs.get("loading", "").lower()
        if loading == "eager":
            eager_count += 1

    if eager_count >= 4:
        out.append(
            make_finding(
                "ADV007",
                "medium",
                "Too many eager-loaded images",
                f"Found {eager_count} images with loading=\"eager\".",
                file=file,
                help="Only a small number of critical images should be eager-loaded. Excess eager loading can hurt page performance.",
            )
        )
    return out
























