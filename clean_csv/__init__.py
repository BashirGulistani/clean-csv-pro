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



    required_cols = parse_csv_list(args.required) if args.required else []
    if args.drop_empty_title and "Title" not in required_cols:
        required_cols.append("Title")

    if required_cols:
        df, changes = drop_rows_missing_required(df, required_cols)
        report.add_section("required", changes)

    if args.shopify:
        df, changes = apply_shopify_fixes(df)
        report.add_section("shopify", changes)

    price_cols = parse_csv_list(args.price_cols) if args.price_cols else []
    if args.round_up_005 and price_cols:
        df, changes = normalize_prices_round_up_to_005(df, price_cols)
        report.add_section("prices", changes)
    elif args.round_up_005 and not price_cols:
        report.warn("round_up_005 enabled but --price-cols not provided; skipping price normalization.")

    report.note("rows_out", int(len(df)))
    report.note("cols_out", int(len(df.columns)))

    if args.dry_run:
        console.print("[yellow]Dry-run enabled: not writing output files.[/yellow]")
        save_report_json(report, report_target)
        console.print(f"[green]Report written:[/green] {report_target}")
        return

    if batch_mode:
        batches = split_into_handle_batches(df, handle_col=args.handle_col, batch_size=args.batch_size or 5000)
        batch_reports = []
        for i, bdf in enumerate(batches, start=1):
            out_file = out_dir / f"{in_path.stem}_clean_batch_{i:03d}.csv"
            write_csv_utf8(bdf, str(out_file))
            b_rep = report.clone_for_batch(batch_index=i, output_path=str(out_file), rows=int(len(bdf)))
            batch_reports.append(b_rep)

        rep_dir = Path(report_target) if report_target.endswith(os.sep) else Path(report_target)
        if rep_dir.suffix.lower() == ".json":
            rep_dir = rep_dir.parent
        rep_dir.mkdir(parents=True, exist_ok=True)


        combined_path = rep_dir / "clean_report.json"
        save_report_json(report, str(combined_path))

        for br in batch_reports:
            save_report_json(br, str(rep_dir / f"clean_report_batch_{br.batch_index:03d}.json"))

        console.print(f"[green]Wrote[/green] {len(batches)} batch file(s) to: {out_dir}")
        console.print(f"[green]Reports[/green] written to: {rep_dir}")
    else:
        write_csv_utf8(df, str(out_path))
        save_report_json(report, report_target)
        console.print(f"[green]Wrote cleaned file:[/green] {out_path}")
        console.print(f"[green]Report written:[/green] {report_target}")

