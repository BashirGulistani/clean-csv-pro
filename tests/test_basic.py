from pathlib import Path

from theme_audit.scanner import scan_theme


def test_scan_smoke(tmp_path: Path):
    (tmp_path / "layout").mkdir()
    (tmp_path / "assets").mkdir()

    html = """
    <html>
      <head>
        <script src="app.js"></script>
        <style>/* big */</style>
      </head>
      <body>
        <img src="hero.jpg">
        <div style="height:2000px"></div>
        <img src="below.jpg">
      </body>
    </html>
    """
    (tmp_path / "layout" / "theme.liquid").write_text(html, encoding="utf-8")
    (tmp_path / "assets" / "hero.jpg").write_bytes(b"x" * 900_000)

    findings = scan_theme(tmp_path)
    assert any(f.rule_id == "A11Y001" for f in findings)
    assert any(f.rule_id == "PERF002" for f in findings)
    assert any(f.rule_id in ("PERF010", "PERF011") for f in findings)
