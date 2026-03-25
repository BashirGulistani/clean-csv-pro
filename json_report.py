from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .stats import compute_stats





def _safe_str(value: object) -> str:
    if value is None:
        return ""
    return str(value)


def _safe_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def finding_to_dict(finding: object) -> Dict[str, Any]:
    """
    Convert a finding-like object into a JSON-safe dictionary.
    Supports:
    - dataclass findings
    - normal objects with finding attributes
    - dict-like objects
    """
    if isinstance(finding, dict):
        return {
            "rule_id": _safe_str(finding.get("rule_id", "")),
            "severity": _safe_str(finding.get("severity", "low")),
            "title": _safe_str(finding.get("title", "")),
            "message": _safe_str(finding.get("message", "")),
            "file": _safe_str(finding.get("file", "")),
            "line": _safe_int(finding.get("line", 1), 1),
            "col": _safe_int(finding.get("col", 1), 1),
            "help": _safe_str(finding.get("help", "")),
        }



    if is_dataclass(finding):
        raw = asdict(finding)
        return {
            "rule_id": _safe_str(raw.get("rule_id", "")),
            "severity": _safe_str(raw.get("severity", "low")),
            "title": _safe_str(raw.get("title", "")),
            "message": _safe_str(raw.get("message", "")),
            "file": _safe_str(raw.get("file", "")),
            "line": _safe_int(raw.get("line", 1), 1),
            "col": _safe_int(raw.get("col", 1), 1),
            "help": _safe_str(raw.get("help", "")),
        }

    return {
        "rule_id": _safe_str(getattr(finding, "rule_id", "")),
        "severity": _safe_str(getattr(finding, "severity", "low")),
        "title": _safe_str(getattr(finding, "title", "")),
        "message": _safe_str(getattr(finding, "message", "")),
        "file": _safe_str(getattr(finding, "file", "")),
        "line": _safe_int(getattr(finding, "line", 1), 1),
        "col": _safe_int(getattr(finding, "col", 1), 1),
        "help": _safe_str(getattr(finding, "help", "")),
    }


def findings_to_list(findings: Iterable[object]) -> List[Dict[str, Any]]:
    return [finding_to_dict(f) for f in findings]


def summarize_findings(findings: Iterable[object]) -> Dict[str, Any]:
    items = findings_to_list(findings)

    counts = {"high": 0, "medium": 0, "low": 0}
    by_rule: Dict[str, int] = {}
    by_file: Dict[str, int] = {}

    for item in items:
        sev = str(item.get("severity", "low")).lower()
        counts[sev] = counts.get(sev, 0) + 1

        rule_id = str(item.get("rule_id", "UNKNOWN"))
        by_rule[rule_id] = by_rule.get(rule_id, 0) + 1

        file = str(item.get("file", "__inventory__"))
        by_file[file] = by_file.get(file, 0) + 1

    top_rules = sorted(by_rule.items(), key=lambda x: (-x[1], x[0]))[:15]
    top_files = sorted(by_file.items(), key=lambda x: (-x[1], x[0]))[:15]

    return {
        "counts": {
            "high": counts.get("high", 0),
            "medium": counts.get("medium", 0),
            "low": counts.get("low", 0),
            "total": len(items),
        },
        "top_rules": [{"rule_id": k, "count": v} for k, v in top_rules],
        "top_files": [{"file": k, "count": v} for k, v in top_files],
    }






def build_json_report(
    findings: Iterable[object],
    theme_dir: str = "",
    tool_version: str = "0.1.0",
    include_stats: bool = True,
    include_summary: bool = True,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    findings_list = list(findings)
    findings_json = findings_to_list(findings_list)

    report: Dict[str, Any] = {
        "tool": {
            "name": "ThemeAudit",
            "version": tool_version,
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "theme_dir": theme_dir,
        "finding_count": len(findings_json),
        "findings": findings_json,
    }

    if include_summary:
        report["summary"] = summarize_findings(findings_json)

    if include_stats:
        stats = compute_stats(findings_list)
        report["stats"] = stats.to_dict()

    if metadata:
        report["metadata"] = dict(metadata)

    return report


def render_json_report(
    findings: Iterable[object],
    theme_dir: str = "",
    tool_version: str = "0.1.0",
    include_stats: bool = True,
    include_summary: bool = True,
    metadata: Optional[Dict[str, Any]] = None,
    indent: int = 2,
) -> str:
    report = build_json_report(
        findings=findings,
        theme_dir=theme_dir,
        tool_version=tool_version,
        include_stats=include_stats,
        include_summary=include_summary,
        metadata=metadata,
    )
    return json.dumps(report, indent=indent, sort_keys=False)


def write_json_report(
    findings: Iterable[object],
    output_path: str | Path,
    theme_dir: str = "",
    tool_version: str = "0.1.0",
    include_stats: bool = True,
    include_summary: bool = True,
    metadata: Optional[Dict[str, Any]] = None,
    indent: int = 2,
) -> Path:
    p = Path(output_path).expanduser().resolve()
    p.write_text(
        render_json_report(
            findings=findings,
            theme_dir=theme_dir,
            tool_version=tool_version,
            include_stats=include_stats,
            include_summary=include_summary,
            metadata=metadata,
            indent=indent,
        ),
        encoding="utf-8",
    )
    return p






def load_json_report(path: str | Path) -> Dict[str, Any]:
    p = Path(path).expanduser().resolve()
    raw = p.read_text(encoding="utf-8", errors="replace")
    data = json.loads(raw)

    if not isinstance(data, dict):
        raise ValueError(f"Invalid report format in {p}: root must be an object")

    return data


def extract_findings_from_report(report: Dict[str, Any]) -> List[Dict[str, Any]]:
    findings = report.get("findings", [])
    if not isinstance(findings, list):
        raise ValueError("Report has invalid findings field; expected a list")
    out: List[Dict[str, Any]] = []
    for item in findings:
        if isinstance(item, dict):
            out.append(finding_to_dict(item))
    return out


def render_compact_json_summary(report: Dict[str, Any]) -> str:
    tool = report.get("tool", {}) if isinstance(report.get("tool"), dict) else {}
    name = _safe_str(tool.get("name", "ThemeAudit"))
    version = _safe_str(tool.get("version", ""))
    theme_dir = _safe_str(report.get("theme_dir", ""))
    count = _safe_int(report.get("finding_count", 0), 0)

    lines: List[str] = []
    lines.append("[json] report summary")
    lines.append(f"- tool: {name} {version}".strip())
    lines.append(f"- theme: {theme_dir or '.'}")
    lines.append(f"- findings: {count}")







