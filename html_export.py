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

    rules_table = _render_rules_table(stats.rules)
    files_table = _render_files_table(stats.files)
    findings_table = _render_findings_table(findings_list)



    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{
      --bg: #0b1020;
      --panel: #121933;
      --panel-2: #0f1530;
      --text: #edf2ff;
      --muted: #a6b0d4;
      --border: #263159;
      --high: #ff5d73;
      --medium: #ffb454;
      --low: #6fb1ff;
      --good: #3ddc97;
      --shadow: 0 10px 30px rgba(0,0,0,0.22);
      --radius: 18px;
    }}

    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; padding: 0; background: linear-gradient(180deg, #0a0f1f 0%, #0f1833 100%); color: var(--text); font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; }}
    body {{ padding: 28px; }}

    .wrap {{
      max-width: 1320px;
      margin: 0 auto;
    }}

    .hero {{
      background: linear-gradient(135deg, rgba(111,177,255,0.15), rgba(61,220,151,0.12));
      border: 1px solid var(--border);
      border-radius: 24px;
      padding: 28px;
      box-shadow: var(--shadow);
      margin-bottom: 22px;
    }}

    .title {{
      margin: 0 0 8px;
      font-size: 2rem;
      font-weight: 800;
      letter-spacing: -0.03em;
    }}

    .meta {{
      color: var(--muted);
      font-size: 0.98rem;
      line-height: 1.5;
    }}

    .badges {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 16px;
    }}

    .badge {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 36px;
      padding: 8px 14px;
      border-radius: 999px;
      font-weight: 700;
      font-size: 0.92rem;
      border: 1px solid rgba(255,255,255,0.08);
      background: rgba(255,255,255,0.05);
    }}

    .badge-high {{ color: white; background: rgba(255,93,115,0.18); border-color: rgba(255,93,115,0.4); }}
    .badge-medium {{ color: white; background: rgba(255,180,84,0.18); border-color: rgba(255,180,84,0.4); }}
    .badge-low {{ color: white; background: rgba(111,177,255,0.18); border-color: rgba(111,177,255,0.4); }}

    .cards {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 16px;
      margin-bottom: 22px;
    }}



