from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional, Union


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str 
    title: str
    message: str
    file: str
    line: int = 1
    col: int = 1
    help: str = ""





