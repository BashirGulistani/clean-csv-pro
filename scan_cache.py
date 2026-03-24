from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


CACHE_VERSION = 1


def _stable_text(value: object) -> str:
    if value is None:
        return ""
    return str(value)








def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _file_digest(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


@dataclass
class CachedFinding:
    rule_id: str
    severity: str
    title: str
    message: str
    file: str
    line: int = 1
    col: int = 1
    help: str = ""






