import argparse
import sys
from pathlib import Path

from .scanner import scan_theme
from .reporters import render_markdown, render_text
from .sarif import to_sarif_json


SEV_ORDER = {"low": 1, "medium": 2, "high": 3}




def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    p = argparse.ArgumentParser(prog="themeaudit", description="Shopify theme performance + a11y auditor")
    sub = p.add_subparsers(dest="cmd", required=True)

    scan = sub.add_parser("scan", help="Scan a theme directory")
    scan.add_argument("path", type=str, help="Path to Shopify theme folder")
    scan.add_argument("--out", type=str, default="", help="Write Markdown report to file")
    scan.add_argument("--sarif", type=str, default="", help="Write SARIF JSON to file")
    scan.add_argument("--min-severity", choices=["low", "medium", "high"], default="low")
    scan.add_argument("--max-files", type=int, default=5000, help="Safety limit on file count")
    scan.add_argument("--max-bytes", type=int, default=15_000_000, help="Safety limit on total bytes read")


