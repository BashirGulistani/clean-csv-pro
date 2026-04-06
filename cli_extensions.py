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

    # json
    p_json = sub.add_parser("json", help="Scan a theme and write a JSON report")
    p_json.add_argument("path", type=str, help="Path to theme directory")
    p_json.add_argument("--out", type=str, default="themeaudit-report.json", help="Output JSON file")
    p_json.add_argument("--max-files", type=int, default=5000)
    p_json.add_argument("--max-bytes", type=int, default=15_000_000)

    # baseline
    p_base = sub.add_parser("baseline", help="Create a baseline file from current findings")
    p_base.add_argument("path", type=str, help="Path to theme directory")
    p_base.add_argument("--out", type=str, default=".themeaudit-baseline.json", help="Baseline output path")
    p_base.add_argument("--max-files", type=int, default=5000)
    p_base.add_argument("--max-bytes", type=int, default=15_000_000)





    # compare baseline
    p_compare = sub.add_parser("compare-baseline", help="Compare current scan against baseline")
    p_compare.add_argument("path", type=str, help="Path to theme directory")
    p_compare.add_argument("--baseline", type=str, default=".themeaudit-baseline.json", help="Baseline file")
    p_compare.add_argument("--max-files", type=int, default=5000)
    p_compare.add_argument("--max-bytes", type=int, default=15_000_000)

    # rules docs
    p_rules = sub.add_parser("rules-docs", help="Generate Markdown docs for rules")
    p_rules.add_argument("--out", type=str, default="RULES.md", help="Output Markdown path")
    p_rules.add_argument("--title", type=str, default="ThemeAudit Rules Reference")

    # init
    p_init = sub.add_parser("init", help="Scaffold ThemeAudit files into a repo")
    p_init.add_argument("path", type=str, nargs="?", default=".", help="Target directory")
    p_init.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    p_init.add_argument("--with-baseline", action="store_true", help="Generate baseline from scan")
    p_init.add_argument("--with-readme-snippet", action="store_true", help="Append ThemeAudit snippet to README")
    p_init.add_argument("--max-files", type=int, default=5000)
    p_init.add_argument("--max-bytes", type=int, default=15_000_000)


    # stats
    p_stats = sub.add_parser("stats", help="Print theme statistics summary")
    p_stats.add_argument("path", type=str, help="Path to theme directory")
    p_stats.add_argument("--max-files", type=int, default=5000)
    p_stats.add_argument("--max-bytes", type=int, default=15_000_000)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_extensions_parser()
    args = parser.parse_args(argv)

    if args.command == "html":
        theme_dir = _resolve_dir(args.path)
        findings = _scan(theme_dir, args.max_files, args.max_bytes)
        out = Path(args.out).expanduser().resolve()
        write_html_report(findings, str(out), theme_dir=str(theme_dir), title=args.title)
        print(f"[ok] wrote HTML report: {out}")
        return 0

    if args.command == "json":
        theme_dir = _resolve_dir(args.path)
        findings = _scan(theme_dir, args.max_files, args.max_bytes)
        out = Path(args.out).expanduser().resolve()
        write_json_report(findings, out, theme_dir=str(theme_dir))
        print(f"[ok] wrote JSON report: {out}")
        return 0

    if args.command == "baseline":
        theme_dir = _resolve_dir(args.path)
        findings = _scan(theme_dir, args.max_files, args.max_bytes)
        out = Path(args.out).expanduser().resolve()
        save_baseline(findings, out)
        print(f"[ok] wrote baseline: {out}")
        return 0

    if args.command == "compare-baseline":
        theme_dir = _resolve_dir(args.path)
        findings = _scan(theme_dir, args.max_files, args.max_bytes)
        summary = summarize_baseline_comparison(findings, args.baseline)
        print(summary)
        return 0













