from __future__ import annotations

import html
from datetime import datetime, timezone
from typing import Iterable, List, Optional

from .stats import compute_stats







def render_html_report(
    findings: Iterable[object],
    theme_dir: str = "",
    title: str = "ThemeAudit Report",
    generated_at: Optional[str] = None,
) -> str:
    findings_list = list(findings)
    stats = compute_stats(findings_list)

    if generated_at is None:
        generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    severity_badges = f"""
      <div class="badges">
        <span class="badge badge-high">High {stats.breakdown.high}</span>
        <span class="badge badge-medium">Medium {stats.breakdown.medium}</span>
        <span class="badge badge-low">Low {stats.breakdown.low}</span>
      </div>
    """




