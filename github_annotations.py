from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Iterable, List, Optional

from .rules import Finding

_SEV_TO_CMD = {"low": "notice", "medium": "warning", "high": "error"}




def _escape(s: str) -> str:

    if s is None:
        return ""
    return (
        str(s)
        .replace("%", "%25")
        .replace("\r", "%0D")
        .replace("\n", "%0A")
        .replace(":", "%3A")
        .replace(",", "%2C")
    )







