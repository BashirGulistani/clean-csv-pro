import argparse
import sys
from pathlib import Path

from .scanner import scan_theme
from .reporters import render_markdown, render_text
from .sarif import to_sarif_json


SEV_ORDER = {"low": 1, "medium": 2, "high": 3}





