from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .stats import compute_stats


def _safe_str(value: object) -> str:
    if value is None:
        return ""
    return str(value)









