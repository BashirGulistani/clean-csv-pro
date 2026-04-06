from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, List, Optional

from .baseline import save_baseline, summarize_baseline_comparison
from .html_export import write_html_report
from .init_project import scaffold_project
from .json_report import write_json_report
from .rule_docs import write_rules_markdown
from .scanner import scan_theme
from .stats import summarize_stats, compute_stats








