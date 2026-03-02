from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Tuple

from .rules import RULES, Finding, make_finding


TEXT_EXTS = {".liquid", ".html", ".htm", ".css", ".js", ".json", ".txt", ".md"}
ASSET_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".avif"}
LIQUID_HTML_EXTS = {".liquid", ".html", ".htm"}





