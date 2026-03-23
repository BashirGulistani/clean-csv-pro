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






