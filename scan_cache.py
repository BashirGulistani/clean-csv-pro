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


def make_root_fingerprint(theme_dir: Path, config_signature: str = "") -> str:
    """
    Root fingerprint should change when:
    - cache format changes
    - config changes
    - Python version logic changes (approx)
    """
    parts = [
        f"cache_version={CACHE_VERSION}",
        f"theme_dir={theme_dir.resolve()}",
        f"config_signature={config_signature}",
    ]
    return _sha256_bytes("\n".join(parts).encode("utf-8"))


def default_cache_path(theme_dir: Path) -> Path:
    return theme_dir / ".themeaudit.cache.json"


def load_cache(path: str | Path) -> ScanCache:
    p = Path(path).expanduser().resolve()
    if not p.exists():
        return ScanCache()

    raw = p.read_text(encoding="utf-8", errors="replace")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return ScanCache()

    if not isinstance(data, dict):
        return ScanCache()

    try:
        cache = ScanCache.from_dict(data)
    except Exception:
        return ScanCache()

    if cache.version != CACHE_VERSION:
        return ScanCache()

    return cache


def save_cache(cache: ScanCache, path: str | Path) -> Path:
    p = Path(path).expanduser().resolve()
    p.write_text(json.dumps(cache.to_dict(), indent=2), encoding="utf-8")
    return p


def get_file_state(path: Path) -> Tuple[int, int]:
    st = path.stat()
    return int(st.st_size), int(st.st_mtime_ns)


def file_changed(path: Path, entry: Optional[CachedFileEntry]) -> bool:
    if entry is None:
        return True

    try:
        size, mtime_ns = get_file_state(path)
    except OSError:
        return True

    if size != entry.size or mtime_ns != entry.mtime_ns:
        return True

    return False







def build_cache_entry(path: Path, relpath: str, findings: Iterable[object]) -> CachedFileEntry:
    size, mtime_ns = get_file_state(path)
    digest = _file_digest(path)

    cached_findings: List[CachedFinding] = []
    for f in findings:
        cached_findings.append(
            CachedFinding(
                rule_id=str(getattr(f, "rule_id", "")),
                severity=str(getattr(f, "severity", "low")),
                title=str(getattr(f, "title", "")),
                message=str(getattr(f, "message", "")),
                file=str(getattr(f, "file", relpath)),
                line=int(getattr(f, "line", 1) or 1),
                col=int(getattr(f, "col", 1) or 1),
                help=str(getattr(f, "help", "")),
            )
        )

    return CachedFileEntry(
        relpath=relpath,
        size=size,
        mtime_ns=mtime_ns,
        digest=digest,
        findings=cached_findings,
    )




def cached_entry_valid(path: Path, entry: Optional[CachedFileEntry]) -> bool:
    if entry is None:
        return False

    try:
        size, mtime_ns = get_file_state(path)
    except OSError:
        return False

    if size != entry.size or mtime_ns != entry.mtime_ns:
        return False

    try:
        digest = _file_digest(path)
    except OSError:
        return False

    return digest == entry.digest


def extract_cached_findings(entry: CachedFileEntry) -> List[CachedFinding]:
    return list(entry.findings)


def invalidate_missing_files(cache: ScanCache, existing_relpaths: Iterable[str]) -> None:
    existing = set(existing_relpaths)
    stale = [rel for rel in cache.files.keys() if rel not in existing]
    for rel in stale:
        del cache.files[rel]


def summarize_cache_usage(
    total_files: int,
    cache_hits: int,
    rescanned: int,
    reused_findings: int,
) -> str:
    miss = max(0, total_files - cache_hits)
    lines: List[str] = []
    lines.append("[cache] scan cache summary")
    lines.append(f"- files considered: {total_files}")
    lines.append(f"- cache hits: {cache_hits}")
    lines.append(f"- rescanned files: {rescanned}")
    lines.append(f"- reused findings: {reused_findings}")
    lines.append(f"- cache misses: {miss}")
    if total_files > 0:
        hit_rate = (cache_hits / total_files) * 100.0
        lines.append(f"- hit rate: {hit_rate:.1f}%")
    return "\n".join(lines)






























