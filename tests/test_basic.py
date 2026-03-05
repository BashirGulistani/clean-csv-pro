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
