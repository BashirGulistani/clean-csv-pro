from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Tuple


def _stable_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()







