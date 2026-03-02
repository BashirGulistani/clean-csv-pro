from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Tuple

from .rules import RULES, Finding, make_finding


TEXT_EXTS = {".liquid", ".html", ".htm", ".css", ".js", ".json", ".txt", ".md"}
ASSET_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".avif"}
LIQUID_HTML_EXTS = {".liquid", ".html", ".htm"}




def iter_files(theme_dir: Path) -> Iterable[Path]:
    for p in theme_dir.rglob("*"):
        if p.is_file():
            yield p


def safe_read_text(path: Path, limit_bytes: int) -> str:
    data = path.read_bytes()
    if len(data) > limit_bytes:
        data = data[:limit_bytes]
    try:
        return data.decode("utf-8", errors="replace")
    except Exception:
        return ""

def scan_theme(theme_dir: Path, max_files: int = 5000, max_bytes: int = 15_000_000) -> List[Finding]:
    files = []
    total_bytes = 0

    for i, fp in enumerate(iter_files(theme_dir)):
        if i >= max_files:
            break
        try:
            st = fp.stat()
        except OSError:
            continue
        total_bytes += st.st_size
        if total_bytes > max_bytes:
            break
        files.append(fp)

    findings: List[Finding] = []
    inventory = build_inventory(theme_dir, files)

    for fp in files:
        ext = fp.suffix.lower()
        rel = str(fp.relative_to(theme_dir))

        if ext in TEXT_EXTS:
            txt = safe_read_text(fp, limit_bytes=800_000)
            findings.extend(run_text_rules(rel, txt, inventory))
        elif ext in ASSET_EXTS:
            findings.extend(run_asset_rules(rel, fp, inventory))

    findings.extend(run_cross_rules(inventory))


    findings.sort(key=lambda f: ({"high": 0, "medium": 1, "low": 2}.get(f.severity, 3), f.file, f.rule_id))
    return findings


@dataclass
class Inventory:
    files: List[str]
    text_files: List[str]
    asset_files: List[str]
    assets_by_ext: dict
    inline_script_hits: List[Tuple[str, int]]
    inline_style_hits: List[Tuple[str, int]]
    script_tags: List[Tuple[str, str]] 
    img_tags: List[Tuple[str, str]]  
    asset_sizes: dict 


def build_inventory(theme_dir: Path, files: List[Path]) -> Inventory:
    text_files = []
    asset_files = []
    assets_by_ext = {}
    inline_script_hits = []
    inline_style_hits = []
    script_tags = []
    img_tags = []
    asset_sizes = {}

    script_tag_re = re.compile(r"<script\b[^>]*>", re.IGNORECASE)
    img_tag_re = re.compile(r"<img\b[^>]*>", re.IGNORECASE)

    inline_script_re = re.compile(r"<script\b[^>]*>(.*?)</script>", re.IGNORECASE | re.DOTALL)
    inline_style_re = re.compile(r"<style\b[^>]*>(.*?)</style>", re.IGNORECASE | re.DOTALL)

    for fp in files:
        rel = str(fp.relative_to(theme_dir))
        ext = fp.suffix.lower()

        if ext in TEXT_EXTS:
            text_files.append(rel)
            txt = safe_read_text(fp, limit_bytes=800_000)


            for m in script_tag_re.finditer(txt):
                script_tags.append((rel, m.group(0)))

            for m in img_tag_re.finditer(txt):
                img_tags.append((rel, m.group(0)))

            for m in inline_script_re.finditer(txt):
                inline_script_hits.append((rel, len(m.group(1) or "")))
            for m in inline_style_re.finditer(txt):
                inline_style_hits.append((rel, len(m.group(1) or "")))

        if ext in ASSET_EXTS:
            asset_files.append(rel)
            assets_by_ext.setdefault(ext, 0)
            assets_by_ext[ext] += 1
            try:
                asset_sizes[rel] = fp.stat().st_size
            except OSError:
                asset_sizes[rel] = 0

    return Inventory(
        files=[str(f.relative_to(theme_dir)) for f in files],
        text_files=text_files,
        asset_files=asset_files,
        assets_by_ext=assets_by_ext,
        inline_script_hits=inline_script_hits,
        inline_style_hits=inline_style_hits,
        script_tags=script_tags,
        img_tags=img_tags,
        asset_sizes=asset_sizes,
    )




