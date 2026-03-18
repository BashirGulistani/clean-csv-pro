from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Tuple


def _stable_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()







def finding_key(finding: object) -> Tuple[str, str, str, int, str, str]:
    """
    Stable comparison key for finding diffs.
    """
    return (
        _stable_text(getattr(finding, "rule_id", "")),
        _stable_text(getattr(finding, "severity", "")),
        _stable_text(getattr(finding, "file", "")).replace("\\", "/"),
        int(getattr(finding, "line", 1) or 1),
        _stable_text(getattr(finding, "title", "")),
        " ".join(_stable_text(getattr(finding, "message", "")).split()),
    )




@dataclass
class DiffItem:
    rule_id: str
    severity: str
    file: str
    line: int
    title: str
    message: str

    @classmethod
    def from_finding(cls, finding: object) -> "DiffItem":
        return cls(
            rule_id=_stable_text(getattr(finding, "rule_id", "")),
            severity=_stable_text(getattr(finding, "severity", "")),
            file=_stable_text(getattr(finding, "file", "")).replace("\\", "/"),
            line=int(getattr(finding, "line", 1) or 1),
            title=_stable_text(getattr(finding, "title", "")),
            message=" ".join(_stable_text(getattr(finding, "message", "")).split()),
        )

    def to_dict(self) -> Dict[str, object]:
        return {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "file": self.file,
            "line": self.line,
            "title": self.title,
            "message": self.message,
        }


@dataclass
class DiffSummary:
    added: List[DiffItem] = field(default_factory=list)
    removed: List[DiffItem] = field(default_factory=list)
    unchanged: List[DiffItem] = field(default_factory=list)

    @property
    def added_count(self) -> int:
        return len(self.added)

    @property
    def removed_count(self) -> int:
        return len(self.removed)

    @property
    def unchanged_count(self) -> int:
        return len(self.unchanged)

    def to_dict(self) -> Dict[str, object]:
        return {
            "added_count": self.added_count,
            "removed_count": self.removed_count,
            "unchanged_count": self.unchanged_count,
            "added": [x.to_dict() for x in self.added],
            "removed": [x.to_dict() for x in self.removed],
            "unchanged": [x.to_dict() for x in self.unchanged],
        }







def diff_findings(old_findings: Iterable[object], new_findings: Iterable[object]) -> DiffSummary:
    old_map: Dict[Tuple[str, str, str, int, str, str], object] = {}
    new_map: Dict[Tuple[str, str, str, int, str, str], object] = {}

    for f in old_findings:
        old_map[finding_key(f)] = f

    for f in new_findings:
        new_map[finding_key(f)] = f

    old_keys = set(old_map.keys())
    new_keys = set(new_map.keys())

    added_keys = sorted(new_keys - old_keys, key=_sort_key)
    removed_keys = sorted(old_keys - new_keys, key=_sort_key)
    unchanged_keys = sorted(old_keys & new_keys, key=_sort_key)

    return DiffSummary(
        added=[DiffItem.from_finding(new_map[k]) for k in added_keys],
        removed=[DiffItem.from_finding(old_map[k]) for k in removed_keys],
        unchanged=[DiffItem.from_finding(new_map[k]) for k in unchanged_keys],
    )


def _sort_key(key: Tuple[str, str, str, int, str, str]) -> Tuple[int, str, int, str, str]:
    rule_id, severity, file, line, title, message = key
    sev_rank = {"high": 0, "medium": 1, "low": 2}.get(severity.lower(), 3)
    return (sev_rank, file, line, rule_id, title)


def render_diff_text(diff: DiffSummary, max_items: int = 20) -> str:
    lines: List[str] = []
    lines.append("[diff] findings comparison")
    lines.append(f"- added: {diff.added_count}")
    lines.append(f"- removed: {diff.removed_count}")
    lines.append(f"- unchanged: {diff.unchanged_count}")

    if diff.added:
        lines.append("- added findings:")
        for item in diff.added[:max_items]:
            lines.append(
                f"  + [{item.severity}] {item.rule_id} {item.file}:{item.line} — {item.title}"
            )
        if diff.added_count > max_items:
            lines.append(f"  ... ({diff.added_count - max_items} more added)")

    if diff.removed:
        lines.append("- removed findings:")
        for item in diff.removed[:max_items]:
            lines.append(
                f"  - [{item.severity}] {item.rule_id} {item.file}:{item.line} — {item.title}"
            )
        if diff.removed_count > max_items:
            lines.append(f"  ... ({diff.removed_count - max_items} more removed)")

    return "\n".join(lines)



def render_diff_markdown(diff: DiffSummary, title: str = "ThemeAudit Diff Report", max_items: int = 200) -> str:
    lines: List[str] = []
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"- Added: **{diff.added_count}**")
    lines.append(f"- Removed: **{diff.removed_count}**")
    lines.append(f"- Unchanged: **{diff.unchanged_count}**")
    lines.append("")

    if diff.added:
        lines.append("## Added findings")
        lines.append("")
        lines.append("| Severity | Rule | Location | Title | Message |")
        lines.append("|---|---|---|---|---|")
        for item in diff.added[:max_items]:
            lines.append(
                f"| **{item.severity}** | `{item.rule_id}` | `{item.file}:{item.line}` | {item.title} | {item.message} |"
            )
        lines.append("")



    if diff.removed:
        lines.append("## Removed findings")
        lines.append("")
        lines.append("| Severity | Rule | Location | Title | Message |")
        lines.append("|---|---|---|---|---|")
        for item in diff.removed[:max_items]:
            lines.append(
                f"| **{item.severity}** | `{item.rule_id}` | `{item.file}:{item.line}` | {item.title} | {item.message} |"
            )
        lines.append("")

    if not diff.added and not diff.removed:
        lines.append("No differences found.")
        lines.append("")

    return "\n".join(lines)


def diff_to_json(diff: DiffSummary) -> str:
    return json.dumps(diff.to_dict(), indent=2)


def severity_delta(diff: DiffSummary) -> Dict[str, int]:
    delta = {"high": 0, "medium": 0, "low": 0}

    for item in diff.added:
        sev = item.severity.lower()
        if sev in delta:
            delta[sev] += 1

    for item in diff.removed:
        sev = item.severity.lower()
        if sev in delta:
            delta[sev] -= 1

    return delta



def summarize_diff_impact(diff: DiffSummary) -> str:
    delta = severity_delta(diff)

    lines: List[str] = []
    lines.append("[diff] impact summary")
    lines.append(
        f"- high delta: {delta['high']:+d}"
    )
    lines.append(
        f"- medium delta: {delta['medium']:+d}"
    )
    lines.append(
        f"- low delta: {delta['low']:+d}"
    )

    weighted = delta["high"] * 5 + delta["medium"] * 3 + delta["low"] * 1
    lines.append(f"- weighted delta: {weighted:+d}")

    if weighted < 0:
        lines.append("- result: overall improvement")
    elif weighted > 0:
        lines.append("- result: overall regression")
    else:
        lines.append("- result: no net change")

    return "\n".join(lines)


