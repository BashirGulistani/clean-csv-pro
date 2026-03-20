from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

from .baseline import save_baseline
from .config import make_default_config_json



DEFAULT_WORKFLOW_YAML = """name: themeaudit

on:
  pull_request:
  push:
    branches: [main, master]





