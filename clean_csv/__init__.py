from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import List, Optional

from rich.console import Console

from .io import read_table_safely, write_csv_utf8
from .headers import clean_headers
from .validation import (
    drop_rows_missing_required,
    trim_all_string_cells,
    normalize_null_like_cells,
)
from .price import normalize_prices_round_up_to_005
from .shopify import apply_shopify_fixes
from .batching import split_into_handle_batches
from .report import Report, save_report_json
from .utils import parse_csv_list, guess_default_out

console = Console()




def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="clean_csv",
        description="CleanCSV Pro: fix messy CSV files (encoding/BOM, headers, validation, Shopify mode, batching).",
    )
    p.add_argument("input", help="Input CSV/TSV file path")
    p.add_argument("--out", default=None, help="Output CSV path (single file mode)")
    p.add_argument("--out-dir", default=None, help="Output directory (batch mode)")
    p.add_argument("--delimiter", default=None, help="Override delimiter: ',', '\\t', ';', '|' (auto by default)")
    p.add_argument("--encoding", default=None, help="Override input encoding (auto by default)")

    p.add_argument("--shopify", action="store_true", help="Apply Shopify-specific fixes")
    p.add_argument("--required", default=None, help="Comma-separated required columns (rows missing are dropped)")
    p.add_argument("--drop-empty-title", action="store_true", help="Drop rows where Title is missing/blank (generic)")


    p.add_argument("--trim", action="store_true", help="Trim whitespace in all string cells")
    p.add_argument("--normalize-nulls", action="store_true", help="Convert common null-like values to empty string")

    p.add_argument("--price-cols", default=None, help="Comma-separated list of price columns to normalize")
    p.add_argument("--round-up-005", action="store_true", help="Round UP prices to nearest 0.05 (ends in 0/5 cents)")

    p.add_argument("--batch-size", type=int, default=0, help="If >0, split into batches of N rows (handle-safe)")
    p.add_argument("--handle-col", default="Handle", help="Grouping key for batching (default: Handle)")

    p.add_argument("--report", default=None, help="Report JSON path (single file) or directory (batch mode)")
    p.add_argument("--dry-run", action="store_true", help="Compute/report changes without writing outputs")

    return p


def main(argv: Optional[List[str]] = None) -> None:
    args = build_parser().parse_args(argv)

    in_path = Path(args.input)
    if not in_path.exists():
        raise SystemExit(f"Input not found: {in_path}")

    batch_mode = bool(args.out_dir) or (args.batch_size and args.batch_size > 0)
    if batch_mode:
        out_dir = Path(args.out_dir or (in_path.parent / (in_path.stem + "_batches")))
        out_dir.mkdir(parents=True, exist_ok=True)
    else:
        out_path = Path(args.out or guess_default_out(in_path))

    report_target = args.report
    if not report_target:
        report_target = str((out_dir if batch_mode else out_path.parent) / "clean_report.json")

    df, read_meta = read_table_safely(
        in_path=str(in_path),
        encoding_override=args.encoding,
        delimiter_override=args.delimiter,
    )

    report = Report(input_path=str(in_path), read_meta=read_meta)
    report.note("rows_in", int(len(df)))
    report.note("cols_in", int(len(df.columns)))

    df, header_changes = clean_headers(df)
    report.add_section("headers", header_changes)

    if args.trim:
        df, changes = trim_all_string_cells(df)
        report.add_section("trim", changes)

    if args.normalize_nulls:
        df, changes = normalize_null_like_cells(df)
        report.add_section("normalize_nulls", changes)






