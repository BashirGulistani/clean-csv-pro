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


    



