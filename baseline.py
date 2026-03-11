from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple


BASELINE_VERSION = 1


@dataclass(frozen=True)
class BaselineEntry:
    fingerprint: str
    rule_id: str
    severity: str
    file: str
    line: int
    title: str




def _stable_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def finding_fingerprint(finding: object) -> str:
    """
    Produces a stable-enough fingerprint for a finding.
    Uses:
    - rule_id
    - severity
    - file
    - line
    - title
    - message (normalized)
    """
    rule_id = _stable_text(getattr(finding, "rule_id", ""))
    severity = _stable_text(getattr(finding, "severity", ""))
    file = _stable_text(getattr(finding, "file", ""))
    line = int(getattr(finding, "line", 1) or 1)
    title = _stable_text(getattr(finding, "title", ""))
    message = _stable_text(getattr(finding, "message", ""))

    normalized = "|".join([
        rule_id,
        severity,
        file.replace("\\", "/"),
        str(line),
        title,
        " ".join(message.split()),
    ])

    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()






def finding_to_baseline_entry(finding: object) -> BaselineEntry:
    return BaselineEntry(
        fingerprint=finding_fingerprint(finding),
        rule_id=_stable_text(getattr(finding, "rule_id", "")),
        severity=_stable_text(getattr(finding, "severity", "")),
        file=_stable_text(getattr(finding, "file", "")),
        line=int(getattr(finding, "line", 1) or 1),
        title=_stable_text(getattr(finding, "title", "")),
    )






def save_baseline(findings: Iterable[object], path: str | Path) -> Path:
    p = Path(path).expanduser().resolve()

    entries = [finding_to_baseline_entry(f) for f in findings]
    entries = sorted(entries, key=lambda x: (x.file, x.line, x.rule_id, x.fingerprint))

    payload = {
        "version": BASELINE_VERSION,
        "count": len(entries),
        "entries": [
            {
                "fingerprint": e.fingerprint,
                "rule_id": e.rule_id,
                "severity": e.severity,
                "file": e.file,
                "line": e.line,
                "title": e.title,
            }
            for e in entries
        ],
    }

    p.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return p


def load_baseline(path: str | Path) -> Set[str]:
    p = Path(path).expanduser().resolve()
    if not p.exists():
        raise FileNotFoundError(f"Baseline file not found: {p}")

    raw = p.read_text(encoding="utf-8", errors="replace")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid baseline JSON: {p}: {e}") from e

    if not isinstance(data, dict):
        raise ValueError(f"Baseline must be a JSON object: {p}")

    version = data.get("version")
    if version != BASELINE_VERSION:
        raise ValueError(
            f"Unsupported baseline version: {version}. Expected {BASELINE_VERSION}."
        )

    entries = data.get("entries", [])
    if not isinstance(entries, list):
        raise ValueError("Baseline entries must be a list")

    fingerprints: Set[str] = set()
    for item in entries:
        if not isinstance(item, dict):
            continue
        fp = str(item.get("fingerprint", "")).strip()
        if fp:
            fingerprints.add(fp)

    return fingerprints






def split_by_baseline(findings: Iterable[object], baseline_fingerprints: Set[str]) -> Tuple[List[object], List[object]]:
    """
    Returns:
    - new_findings: not present in baseline
    - known_findings: present in baseline
    """
    new_findings: List[object] = []
    known_findings: List[object] = []

    for f in findings:
        fp = finding_fingerprint(f)
        if fp in baseline_fingerprints:
            known_findings.append(f)
        else:
            new_findings.append(f)

    return new_findings, known_findings





