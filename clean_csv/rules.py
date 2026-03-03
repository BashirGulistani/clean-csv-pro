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





def rule_missing_lazy_loading(file: str, text: str, inv) -> List[Finding]:
    out: List[Finding] = []
    for m in IMG_TAG_RE.finditer(text):
        tag = m.group(0)
        a = _attrs(tag)
        src = a.get("src", "") or a.get("data-src", "")
        if not src:
            continue
        if m.start() < 2000:
            continue
        loading = (a.get("loading", "") or "").lower()
        if loading not in ("lazy", "eager"):
            line = text[: m.start()].count("\n") + 1
            out.append(
                make_finding(
                    "PERF001",
                    "medium",
                    "Image missing loading hint",
                    "Consider adding loading=\"lazy\" for below-the-fold images to reduce initial page load.",
                    file=file,
                    line=line,
                    help="If an image is below the fold, loading=\"lazy\" can improve Core Web Vitals by reducing initial network pressure.",
                )
            )
    return out





def rule_render_blocking_scripts(file: str, text: str, inv) -> List[Finding]:
    out: List[Finding] = []
    for m in SCRIPT_TAG_RE.finditer(text):
        tag = m.group(0)
        a = _attrs(tag)
        src = a.get("src", "")
        if not src:
            continue  
        has_defer = "defer" in tag.lower()
        has_async = "async" in tag.lower()
        if not (has_defer or has_async):
            line = text[: m.start()].count("\n") + 1
            out.append(
                make_finding(
                    "PERF002",
                    "high",
                    "Render-blocking script",
                    f"Script tag loads {src} without defer/async. This can block rendering.",
                    file=file,
                    line=line,
                    help="Prefer <script defer src=...> for most scripts. Use async only if execution order doesn't matter.",
                )
            )
    return out






def rule_inline_script_bloat(file: str, text: str, inv) -> List[Finding]:
    out: List[Finding] = []
    inline_script_re = re.compile(r"<script\b[^>]*>(.*?)</script>", re.IGNORECASE | re.DOTALL)
    for m in inline_script_re.finditer(text):
        body = m.group(1) or ""
        if len(body) > 20_000:
            line = text[: m.start()].count("\n") + 1
            out.append(
                make_finding(
                    "PERF003",
                    "medium",
                    "Large inline script block",
                    f"Inline script block is ~{len(body):,} chars. Consider moving to an asset file for caching and maintainability.",
                    file=file,
                    line=line,
                    help="Large inline JS increases HTML size and prevents long-term caching benefits.",
                )
            )
    return out


def rule_inline_style_bloat(file: str, text: str, inv) -> List[Finding]:
    out: List[Finding] = []
    inline_style_re = re.compile(r"<style\b[^>]*>(.*?)</style>", re.IGNORECASE | re.DOTALL)
    for m in inline_style_re.finditer(text):
        body = m.group(1) or ""
        if len(body) > 15_000:
            line = text[: m.start()].count("\n") + 1
            out.append(
                make_finding(
                    "PERF004",
                    "medium",
                    "Large inline style block",
                    f"Inline style block is ~{len(body):,} chars. Consider moving to CSS assets.",
                    file=file,
                    line=line,
                    help="Large inline CSS can bloat HTML and complicate caching. Keep critical CSS small; move the rest to assets.",
                )
            )
    return out


