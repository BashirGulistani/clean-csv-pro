from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


CACHE_VERSION = 1


def _stable_text(value: object) -> str:
    if value is None:
        return ""
    return str(value)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()



def _file_digest(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


@dataclass
class CachedFinding:
    rule_id: str
    severity: str
    title: str
    message: str
    file: str
    line: int = 1
    col: int = 1
    help: str = ""

    def to_dict(self) -> Dict[str, object]:
        return {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "title": self.title,
            "message": self.message,
            "file": self.file,
            "line": self.line,
            "col": self.col,
            "help": self.help,
        }


    @classmethod
    def from_dict(cls, raw: Dict[str, object]) -> "CachedFinding":
        return cls(
            rule_id=str(raw.get("rule_id", "")),
            severity=str(raw.get("severity", "low")),
            title=str(raw.get("title", "")),
            message=str(raw.get("message", "")),
            file=str(raw.get("file", "")),
            line=int(raw.get("line", 1) or 1),
            col=int(raw.get("col", 1) or 1),
            help=str(raw.get("help", "")),
        )


@dataclass
class CachedFileEntry:
    relpath: str
    size: int
    mtime_ns: int
    digest: str
    findings: List[CachedFinding] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        return {
            "relpath": self.relpath,
            "size": self.size,
            "mtime_ns": self.mtime_ns,
            "digest": self.digest,
            "findings": [f.to_dict() for f in self.findings],
        }

    @classmethod
    def from_dict(cls, raw: Dict[str, object]) -> "CachedFileEntry":
        findings_raw = raw.get("findings", [])
        findings: List[CachedFinding] = []
        if isinstance(findings_raw, list):
            for item in findings_raw:
                if isinstance(item, dict):
                    findings.append(CachedFinding.from_dict(item))

        return cls(
            relpath=str(raw.get("relpath", "")),
            size=int(raw.get("size", 0) or 0),
            mtime_ns=int(raw.get("mtime_ns", 0) or 0),
            digest=str(raw.get("digest", "")),
            findings=findings,
        )









@dataclass
class ScanCache:
    version: int = CACHE_VERSION
    root_fingerprint: str = ""
    files: Dict[str, CachedFileEntry] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        return {
            "version": self.version,
            "root_fingerprint": self.root_fingerprint,
            "files": {k: v.to_dict() for k, v in self.files.items()},
        }

    @classmethod
    def from_dict(cls, raw: Dict[str, object]) -> "ScanCache":
        files_raw = raw.get("files", {})
        files: Dict[str, CachedFileEntry] = {}

        if isinstance(files_raw, dict):
            for relpath, entry in files_raw.items():
                if isinstance(entry, dict):
                    files[str(relpath)] = CachedFileEntry.from_dict(entry)

        return cls(
            version=int(raw.get("version", CACHE_VERSION) or CACHE_VERSION),
            root_fingerprint=str(raw.get("root_fingerprint", "")),
            files=files,
        )












