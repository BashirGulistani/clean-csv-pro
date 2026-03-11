from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple


BASELINE_VERSION = 1


@dataclass(frozen=True)
class BaselineEntry:
    fingerprint: str
    rule_id: str
    severity: str
    file: str
    line: int
    title: str







