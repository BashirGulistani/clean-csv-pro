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




def build_extensions_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="themeauditx",
        description="Extended CLI utilities for ThemeAudit",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # html
    p_html = sub.add_parser("html", help="Scan a theme and write an HTML report")
    p_html.add_argument("path", type=str, help="Path to theme directory")
    p_html.add_argument("--out", type=str, default="themeaudit-report.html", help="Output HTML file")
    p_html.add_argument("--title", type=str, default="ThemeAudit Report", help="Report title")
    p_html.add_argument("--max-files", type=int, default=5000)
    p_html.add_argument("--max-bytes", type=int, default=15_000_000)









