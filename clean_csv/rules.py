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





def rule_large_raster_assets(file: str, fp: Path, inv) -> List[Finding]:
    out: List[Finding] = []
    ext = fp.suffix.lower()
    if ext not in (".png", ".jpg", ".jpeg", ".gif"):
        return out
    try:
        size = fp.stat().st_size
    except OSError:
        return out
    if size >= 800_000:
        out.append(
            make_finding(
                "PERF010",
                "medium",
                "Large raster asset",
                f"Asset is {size/1024:.0f} KB. Consider WebP/AVIF and proper sizing.",
                file=file,
                help="Large images are a top cause of slow LCP. Prefer AVIF/WebP, compress, and avoid uploading oversized originals.",
            )
        )
    if size >= 2_500_000:
        out.append(
            make_finding(
                "PERF011",
                "high",
                "Very large raster asset",
                f"Asset is {size/1024/1024:.2f} MB. Likely oversized/unoptimized.",
                file=file,
                help="Resize to actual display size, compress aggressively, and serve modern formats when possible.",
            )
        )
    return out


def rule_asset_count_budget(file: str, _: str, inv) -> List[Finding]:
    out: List[Finding] = []
    total_assets = len(inv.asset_files)
    if total_assets > 600:
        out.append(
            make_finding(
                "BUDGET001",
                "medium",
                "High asset count",
                f"Theme contains {total_assets} image assets. Consider deduping, removing unused, or moving rarely used assets out of the theme.",
                file="__inventory__",
                help="Huge asset directories often indicate duplicates and unused images, increasing maintenance burden and sometimes deploy size.",
            )
        )
    if total_assets > 1500:
        out.append(
            make_finding(
                "BUDGET002",
                "high",
                "Very high asset count",
                f"Theme contains {total_assets} image assets. This is unusually high and likely includes many unused files.",
                file="__inventory__",
                help="Audit assets/ for duplicates and unused files. Large themes slow down developer workflows and increase risk of mistakes.",
            )
        )
    return out





def rule_excessive_inline_blocks(file: str, _: str, inv) -> List[Finding]:
    out: List[Finding] = []
    big_inline_js = sum(1 for _, n in inv.inline_script_hits if n > 20_000)
    big_inline_css = sum(1 for _, n in inv.inline_style_hits if n > 15_000)

    if big_inline_js >= 3:
        out.append(
            make_finding(
                "PERF020",
                "medium",
                "Multiple large inline scripts",
                f"Found {big_inline_js} large inline <script> blocks across the theme.",
                file="__inventory__",
                help="Move JS to assets for caching and reduce HTML payload size. Keep only truly critical code inline.",
            )
        )
    if big_inline_css >= 3:
        out.append(
            make_finding(
                "PERF021",
                "medium",
                "Multiple large inline styles",
                f"Found {big_inline_css} large inline <style> blocks across the theme.",
                file="__inventory__",
                help="Move most CSS to assets. If using critical CSS, keep it small and measured.",
            )
        )
    return out



RULES: List[Rule] = [
    Rule(
        id="A11Y001",
        title="Image missing alt text",
        applies_to="text",
        severity="high",
        description="Flags <img> tags without alt text.",
        check=rule_missing_img_alt,
    ),
    Rule(
        id="PERF001",
        title="Image missing loading hint",
        applies_to="text",
        severity="medium",
        description="Flags below-the-fold <img> tags missing loading attribute.",
        check=rule_missing_lazy_loading,
    ),
    Rule(
        id="PERF002",
        title="Render-blocking script",
        applies_to="text",
        severity="high",
        description="Flags <script src> without defer/async.",
        check=rule_render_blocking_scripts,
    ),
    Rule(
        id="PERF003",
        title="Large inline script block",
        applies_to="text",
        severity="medium",
        description="Flags large inline script blocks that bloat HTML.",
        check=rule_inline_script_bloat,
    ),

