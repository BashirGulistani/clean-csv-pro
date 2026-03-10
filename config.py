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






def _read_config_file(path: Path) -> ThemeAuditConfig:
    raw = path.read_text(encoding="utf-8", errors="replace")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in config file {path}: {e}") from e

    if not isinstance(data, dict):
        raise ValueError(f"Config file must contain a JSON object: {path}")

    return ThemeAuditConfig.from_dict(data)


def should_exclude_path(relpath: str, config: ThemeAuditConfig) -> bool:
    rel = relpath.replace("\\", "/").strip()

    for prefix in config.exclude_paths:
        p = prefix.replace("\\", "/").strip().rstrip("/")
        if not p:
            continue
        if rel == p or rel.startswith(p + "/"):
            return True

    return False


def should_include_ext(ext: str, config: ThemeAuditConfig) -> bool:
    if not config.include_exts:
        return True
    return ext.lower() in set(config.include_exts)


def apply_rule_overrides(findings: List[Any], config: ThemeAuditConfig) -> List[Any]:
    """
    Applies enable/disable and severity override logic to finding-like objects.
    Assumes each finding has at least `.rule_id` and `.severity`.
    Returns a new list.
    """
    out: List[Any] = []

    for f in findings:
        override = config.rule_overrides.get(getattr(f, "rule_id", ""), None)
        if override is None:
            out.append(f)
            continue

        if override.enabled is False:
            continue

        if override.severity:
            try:
                new_f = type(f)(
                    rule_id=f.rule_id,
                    severity=override.severity,
                    title=f.title,
                    message=f.message,
                    file=f.file,
                    line=f.line,
                    col=f.col,
                    help=f.help,
                )
                out.append(new_f)
            except Exception:
                out.append(f)
            continue

        out.append(f)

    return out


def make_default_config_json() -> str:
    example = ThemeAuditConfig(
        min_severity="low",
        max_files=5000,
        max_bytes=15_000_000,
        exclude_paths=[
            "node_modules",
            ".git",
            "dist",
            "build",
            "templates/customers",
        ],
        include_exts=[
            ".liquid",
            ".html",
            ".htm",
            ".css",
            ".js",
            ".json",
            ".png",
            ".jpg",
            ".jpeg",
            ".webp",
            ".gif",
            ".svg",
            ".avif",
        ],
        rule_overrides={
            "PERF001": RuleOverride(enabled=True, severity="low"),
            "PERF002": RuleOverride(enabled=True, severity="high"),
            "A11Y001": RuleOverride(enabled=True, severity="high"),
        },
        report_title="ThemeAudit Report",
        fail_on_severity="medium",
    )
    return json.dumps(example.to_dict(), indent=2)





