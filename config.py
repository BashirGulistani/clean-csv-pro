from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_CONFIG_FILENAMES = [
    ".themeaudit.json",
    "themeaudit.json",
]







@dataclass
class RuleOverride:
    enabled: Optional[bool] = None
    severity: Optional[str] = None






@dataclass
class ThemeAuditConfig:
    min_severity: str = "low"
    max_files: int = 5000
    max_bytes: int = 15_000_000
    exclude_paths: List[str] = field(default_factory=list)
    include_exts: List[str] = field(default_factory=list)
    rule_overrides: Dict[str, RuleOverride] = field(default_factory=dict)
    report_title: str = "ThemeAudit Report"
    fail_on_severity: str = "medium"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ThemeAuditConfig":
        rule_overrides_raw = data.get("rule_overrides", {}) or {}
        rule_overrides: Dict[str, RuleOverride] = {}

        for rule_id, raw in rule_overrides_raw.items():
            if not isinstance(raw, dict):
                continue
            rule_overrides[rule_id] = RuleOverride(
                enabled=raw.get("enabled"),
                severity=raw.get("severity"),
            )

        return cls(
            min_severity=_coerce_severity(data.get("min_severity", "low")),
            max_files=_coerce_int(data.get("max_files", 5000), default=5000, minimum=1),
            max_bytes=_coerce_int(data.get("max_bytes", 15_000_000), default=15_000_000, minimum=1),
            exclude_paths=_coerce_str_list(data.get("exclude_paths", [])),
            include_exts=_normalize_exts(_coerce_str_list(data.get("include_exts", []))),
            rule_overrides=rule_overrides,
            report_title=str(data.get("report_title", "ThemeAudit Report")),
            fail_on_severity=_coerce_severity(data.get("fail_on_severity", "medium")),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "min_severity": self.min_severity,
            "max_files": self.max_files,
            "max_bytes": self.max_bytes,
            "exclude_paths": list(self.exclude_paths),
            "include_exts": list(self.include_exts),
            "rule_overrides": {
                rule_id: {
                    "enabled": override.enabled,
                    "severity": override.severity,
                }
                for rule_id, override in self.rule_overrides.items()
            },
            "report_title": self.report_title,
            "fail_on_severity": self.fail_on_severity,
        }


def _coerce_int(value: Any, default: int, minimum: int = 0) -> int:
    try:
        n = int(value)
    except Exception:
        return default
    return max(minimum, n)


def _coerce_str_list(value: Any) -> List[str]:
    if not isinstance(value, list):
        return []
    out: List[str] = []
    for item in value:
        if item is None:
            continue
        s = str(item).strip()
        if s:
            out.append(s)
    return out


def _coerce_severity(value: Any) -> str:
    s = str(value or "").strip().lower()
    if s not in {"low", "medium", "high"}:
        return "low"
    return s


def _normalize_exts(exts: List[str]) -> List[str]:
    out: List[str] = []
    for ext in exts:
        e = ext.strip().lower()
        if not e:
            continue
        if not e.startswith("."):
            e = "." + e
        out.append(e)
    return out



    def find_config_file(start_dir: Path) -> Optional[Path]:
    start_dir = start_dir.resolve()

    for candidate in DEFAULT_CONFIG_FILENAMES:
        p = start_dir / candidate
        if p.exists() and p.is_file():
            return p

    for parent in [start_dir, *start_dir.parents]:
        for candidate in DEFAULT_CONFIG_FILENAMES:
            p = parent / candidate
            if p.exists() and p.is_file():
                return p

    return None


def load_config(start_dir: Path, explicit_path: Optional[str] = None) -> ThemeAuditConfig:
    if explicit_path:
        p = Path(explicit_path).expanduser().resolve()
        if not p.exists():
            raise FileNotFoundError(f"Config file not found: {p}")
        return _read_config_file(p)

    found = find_config_file(start_dir)
    if found is None:
        return ThemeAuditConfig()

    return _read_config_file(found)






