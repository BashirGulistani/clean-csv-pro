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






