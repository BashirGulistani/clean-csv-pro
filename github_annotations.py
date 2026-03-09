from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Iterable, List, Optional

from .rules import Finding

_SEV_TO_CMD = {"low": "notice", "medium": "warning", "high": "error"}






