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


    summary_cards = f"""
      <div class="cards">
        <div class="card">
          <div class="card-label">Health Score</div>
          <div class="card-value">{stats.health_score}<span class="muted">/100</span></div>
          <div class="card-sub">{html.escape(stats.risk_level.title())}</div>
        </div>
        <div class="card">
          <div class="card-label">Total Findings</div>
          <div class="card-value">{stats.total_findings}</div>
          <div class="card-sub">Across all severities</div>
        </div>
        <div class="card">
          <div class="card-label">Top Hotspot</div>
          <div class="card-value">{html.escape(stats.files[0].file) if stats.files else "None"}</div>
          <div class="card-sub">{stats.files[0].count if stats.files else 0} findings</div>
        </div>
      </div>
    """



