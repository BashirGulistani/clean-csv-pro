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



jobs:
  scan:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write

    steps:
      - name: Checkout
        uses: actions/checkout@v4


      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install ThemeAudit
        run: |
          python -m pip install --upgrade pip
          python -m pip install themeaudit

      - name: Run ThemeAudit
        run: |
          themeaudit scan . --out themeaudit-report.md --sarif themeaudit.sarif.json || true


      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: themeaudit.sarif.json






