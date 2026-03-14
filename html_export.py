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






    .card {{
      background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02));
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 20px;
      box-shadow: var(--shadow);
    }}

    .card-label {{
      color: var(--muted);
      font-size: 0.92rem;
      margin-bottom: 10px;
    }}

    .card-value {{
      font-size: 2rem;
      font-weight: 800;
      letter-spacing: -0.03em;
      word-break: break-word;
    }}

    .card-sub {{
      color: var(--muted);
      margin-top: 6px;
      font-size: 0.95rem;
    }}

    .muted {{
      color: var(--muted);
      font-size: 0.95rem;
      font-weight: 600;
    }}

    .section {{
      background: rgba(18, 25, 51, 0.92);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 20px;
      box-shadow: var(--shadow);
      margin-bottom: 18px;
      overflow: hidden;
    }}

    .section h2 {{
      margin: 0 0 14px;
      font-size: 1.2rem;
      letter-spacing: -0.02em;
    }}

    .table-wrap {{
      overflow-x: auto;
      border-radius: 14px;
      border: 1px solid rgba(255,255,255,0.05);
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      min-width: 820px;
    }}

    th, td {{
      text-align: left;
      padding: 12px 14px;
      border-bottom: 1px solid rgba(255,255,255,0.06);
      vertical-align: top;
    }}

    th {{
      color: #d8e0ff;
      font-size: 0.92rem;
      background: rgba(255,255,255,0.04);
      position: sticky;
      top: 0;
      z-index: 1;
    }}

    td {{
      color: #edf2ff;
      font-size: 0.95rem;
      line-height: 1.45;
    }}

    tr:hover td {{
      background: rgba(255,255,255,0.03);
    }}

    .sev {{
      display: inline-flex;
      align-items: center;
      min-height: 28px;
      padding: 4px 10px;
      border-radius: 999px;
      font-size: 0.82rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.03em;
      white-space: nowrap;
    }}

    .sev-high {{ background: rgba(255,93,115,0.16); color: #ffd8de; }}
    .sev-medium {{ background: rgba(255,180,84,0.16); color: #ffe6c0; }}
    .sev-low {{ background: rgba(111,177,255,0.16); color: #dcebff; }}


    code {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      background: rgba(255,255,255,0.06);
      padding: 2px 6px;
      border-radius: 8px;
      font-size: 0.9em;
    }}

    .empty {{
      color: var(--muted);
      padding: 6px 0 2px;
    }}

    .footer {{
      color: var(--muted);
      text-align: center;
      padding: 12px 0 4px;
      font-size: 0.92rem;
    }}

    @media (max-width: 960px) {{
      body {{ padding: 16px; }}
      .cards {{ grid-template-columns: 1fr; }}
      .title {{ font-size: 1.5rem; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <h1 class="title">{html.escape(title)}</h1>
      <div class="meta">
        <div><strong>Theme:</strong> <code>{html.escape(theme_dir or ".")}</code></div>
        <div><strong>Generated:</strong> {html.escape(generated_at)}</div>
      </div>
      {severity_badges}
    </section>

    {summary_cards}

    <section class="section">
      <h2>Top Rules</h2>
      {rules_table}
    </section>

    <section class="section">
      <h2>Hotspot Files</h2>
      {files_table}
    </section>

    <section class="section">
      <h2>All Findings</h2>
      {findings_table}
    </section>

    <div class="footer">
      Generated by ThemeAudit
    </div>
  </div>
</body>
</html>
"""


def _render_rules_table(rules: List[object]) -> str:
    if not rules:
        return '<div class="empty">No rule statistics available.</div>'

    rows = []
    for r in rules:
        sev = str(getattr(r, "severity", "low")).lower()
        rows.append(
            "<tr>"
            f"<td><code>{html.escape(str(getattr(r, 'rule_id', '')))}</code></td>"
            f"<td><span class=\"sev sev-{sev}\">{html.escape(sev)}</span></td>"
            f"<td>{int(getattr(r, 'count', 0))}</td>"
            f"<td>{html.escape(str(getattr(r, 'title', '')))}</td>"
            "</tr>"
        )

    return (
        '<div class="table-wrap"><table>'
        "<thead><tr><th>Rule</th><th>Severity</th><th>Count</th><th>Title</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        "</table></div>"
    )


def _render_files_table(files: List[object]) -> str:
    if not files:
        return '<div class="empty">No hotspot files found.</div>'

    rows = []
    for f in files:
        rows.append(
            "<tr>"
            f"<td><code>{html.escape(str(getattr(f, 'file', '')))}</code></td>"
            f"<td>{int(getattr(f, 'count', 0))}</td>"
            f"<td>{int(getattr(f, 'high', 0))}</td>"
            f"<td>{int(getattr(f, 'medium', 0))}</td>"
            f"<td>{int(getattr(f, 'low', 0))}</td>"
            f"<td>{int(getattr(f, 'weighted_score', 0))}</td>"
            "</tr>"
        )

    return (
        '<div class="table-wrap"><table>'
        "<thead><tr><th>File</th><th>Total</th><th>High</th><th>Medium</th><th>Low</th><th>Weighted</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        "</table></div>"
    )


def _render_findings_table(findings: List[object]) -> str:
    if not findings:
        return '<div class="empty">No findings 🎉</div>'

    sorted_findings = sorted(
        findings,
        key=lambda f: (
            {"high": 0, "medium": 1, "low": 2}.get(str(getattr(f, "severity", "low")).lower(), 3),
            str(getattr(f, "file", "")),
            int(getattr(f, "line", 1) or 1),
            str(getattr(f, "rule_id", "")),
        ),
    )

    rows = []
    for f in sorted_findings:
        sev = str(getattr(f, "severity", "low")).lower()
        file = str(getattr(f, "file", ""))
        line = int(getattr(f, "line", 1) or 1)
        col = int(getattr(f, "col", 1) or 1)
        rule_id = str(getattr(f, "rule_id", ""))
        title = str(getattr(f, "title", ""))
        message = str(getattr(f, "message", ""))
        help_text = str(getattr(f, "help", ""))

        rows.append(
            "<tr>"
            f"<td><span class=\"sev sev-{sev}\">{html.escape(sev)}</span></td>"
            f"<td><code>{html.escape(rule_id)}</code></td>"
            f"<td>{html.escape(title)}</td>"
            f"<td><code>{html.escape(file)}:{line}:{col}</code></td>"
            f"<td>{html.escape(message)}</td>"
            f"<td>{html.escape(help_text)}</td>"
            "</tr>"
        )

    return (
        '<div class="table-wrap"><table>'
        "<thead><tr><th>Severity</th><th>Rule</th><th>Title</th><th>Location</th><th>Message</th><th>Help</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        "</table></div>"
    )







