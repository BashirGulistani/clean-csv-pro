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



