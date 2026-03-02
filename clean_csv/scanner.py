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




