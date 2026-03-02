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



