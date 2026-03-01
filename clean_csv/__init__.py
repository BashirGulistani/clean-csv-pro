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






