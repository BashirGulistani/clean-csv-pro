from __future__ import annotations

import difflib
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


TEXT_EXTS = {".liquid", ".html", ".htm"}

IMG_TAG_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
SCRIPT_TAG_RE = re.compile(r"<script\b[^>]*>", re.IGNORECASE)

ATTR_RE = re.compile(r'(\w[\w:-]*)\s*=\s*(".*?"|\'.*?\'|[^\s>]+)', re.IGNORECASE)

LIQUID_COMPLEX_RE = re.compile(r"{%|{{", re.IGNORECASE)



def _read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")

def _write_text(p: Path, text: str) -> None:
    p.write_text(text, encoding="utf-8")

def _attrs(tag: str) -> Dict[str, str]:
    attrs = {}
    for m in ATTR_RE.finditer(tag):
        k = (m.group(1) or "").lower()
        v = (m.group(2) or "").strip().strip('"').strip("'")
        attrs[k] = v
    return attrs

def _has_attr(tag: str, name: str) -> bool:
    name_l = name.lower()
    if re.search(rf"\b{name_l}\b", tag.lower()):
        return True
    return False




def _insert_attr(tag: str, attr: str) -> str:

    if tag.endswith("/>"):
        return tag[:-2] + " " + attr + " />"
    if tag.endswith(">"):
        return tag[:-1] + " " + attr + ">"
    return tag

def _set_attr(tag: str, key: str, value: str) -> str:

    key_l = key.lower()


    def repl(m: re.Match) -> str:
        k = (m.group(1) or "")
        if k.lower() == key_l:

            return f'{k}="{value}"'
        return m.group(0)

    new_tag, n = ATTR_RE.subn(repl, tag)
    if n > 0 and key_l in _attrs(new_tag):
        return new_tag


    return _insert_attr(tag, f'{key}="{value}"')




def _is_decorative_img(attrs: Dict[str, str]) -> bool:

    cls = (attrs.get("class", "") or "").lower()
    src = (attrs.get("src", "") or attrs.get("data-src", "") or "").lower()
    if attrs.get("aria-hidden", "").lower() == "true":
        return True
    if attrs.get("role", "").lower() in ("presentation", "none"):
        return True
    if any(x in cls for x in ("icon", "sprite", "payment", "badge", "svg", "social")):
        return True
    if src.endswith(".svg"):
        return True
    if "/icons/" in src or "icon" in src or "sprite" in src:
        return True
    return False

def _likely_below_fold(tag_start_index: int) -> bool:

    return tag_start_index > 2000






@dataclass
class Fix:
    file: str
    rule_id: str
    title: str
    before: str
    after: str
    start: int
    end: int
    note: str = ""

@dataclass
class FixResult:
    file: str
    applied: int
    diff: str

class AutoFixer:

    def __init__(
        self,
        theme_dir: Path,
        backup: bool = True,
        max_fixes_per_file: int = 200,
        dry_run: bool = True,
    ):
        self.theme_dir = theme_dir
        self.backup = backup
        self.max_fixes_per_file = max_fixes_per_file
        self.dry_run = dry_run



    def iter_theme_files(self) -> Iterable[Path]:
        for p in self.theme_dir.rglob("*"):
            if p.is_file() and p.suffix.lower() in TEXT_EXTS:
                yield p

    def plan(self) -> List[Fix]:
        fixes: List[Fix] = []
        for fp in self.iter_theme_files():
            rel = str(fp.relative_to(self.theme_dir))
            text = _read_text(fp)
            fixes.extend(self._plan_file(rel, text))
        return fixes





    def apply(self, fixes: List[Fix]) -> List[FixResult]:

        by_file: Dict[str, List[Fix]] = {}
        for f in fixes:
            by_file.setdefault(f.file, []).append(f)

        results: List[FixResult] = []
        for rel, file_fixes in by_file.items():
            fp = (self.theme_dir / rel)
            if not fp.exists():
                continue
            original = _read_text(fp)
            updated = original

            file_fixes_sorted = sorted(file_fixes, key=lambda x: x.start, reverse=True)
            file_fixes_sorted = file_fixes_sorted[: self.max_fixes_per_file]

            applied = 0
            for fx in file_fixes_sorted:
                if updated[fx.start:fx.end] != fx.before:
                    continue
                updated = updated[:fx.start] + fx.after + updated[fx.end:]
                applied += 1

            if applied == 0 or updated == original:
                continue


            diff = _unified_diff(rel, original, updated)

            if not self.dry_run:
                if self.backup:
                    self._backup_file(fp)
                _write_text(fp, updated)

            results.append(FixResult(file=rel, applied=applied, diff=diff))

        return results


    def _plan_file(self, rel: str, text: str) -> List[Fix]:
        fixes: List[Fix] = []
        fixes.extend(self._plan_defer_scripts(rel, text))
        fixes.extend(self._plan_missing_alt(rel, text))
        fixes.extend(self._plan_lazy_loading(rel, text))
        return fixes

    def _plan_defer_scripts(self, rel: str, text: str) -> List[Fix]:
        out: List[Fix] = []
        for m in SCRIPT_TAG_RE.finditer(text):
            tag = m.group(0)
            attrs = _attrs(tag)
            if "src" not in attrs:
                continue
            tl = tag.lower()
            if "defer" in tl or "async" in tl:
                continue

            if LIQUID_COMPLEX_RE.search(tag):
                continue

            new_tag = _insert_attr(tag, "defer")

            out.append(
                Fix(
                    file=rel,
                    rule_id="PERF002",
                    title="Add defer to render-blocking script",
                    before=tag,
                    after=new_tag,
                    start=m.start(),
                    end=m.end(),
                    note="Added defer (safe for most scripts; if order matters with inline scripts, review).",
                )
            )
        return out




    def _plan_missing_alt(self, rel: str, text: str) -> List[Fix]:
        out: List[Fix] = []
        for m in IMG_TAG_RE.finditer(text):
            tag = m.group(0)
            attrs = _attrs(tag)

            if "alt" in attrs:
                continue

            if LIQUID_COMPLEX_RE.search(tag):
                continue

            if not _is_decorative_img(attrs):
                continue

            new_tag = _insert_attr(tag, 'alt=""')
            out.append(
                Fix(
                    file=rel,
                    rule_id="A11Y001",
                    title='Add alt="" to decorative image',
                    before=tag,
                    after=new_tag,
                    start=m.start(),
                    end=m.end(),
                    note='Added alt="" to decorative image. For meaningful images, write descriptive alt.',
                )
            )
        return out






    def _plan_lazy_loading(self, rel: str, text: str) -> List[Fix]:
        out: List[Fix] = []
        for m in IMG_TAG_RE.finditer(text):
            tag = m.group(0)
            attrs = _attrs(tag)

            src = attrs.get("src") or attrs.get("data-src") or ""
            if not src:
                continue

            if "loading" in attrs:
                continue

            if not _likely_below_fold(m.start()):
                continue

            if LIQUID_COMPLEX_RE.search(tag):
                continue

            new_tag = _insert_attr(tag, 'loading="lazy"')
            out.append(
                Fix(
                    file=rel,
                    rule_id="PERF001",
                    title='Add loading="lazy" to likely below-the-fold image',
                    before=tag,
                    after=new_tag,
                    start=m.start(),
                    end=m.end(),
                    note='Added loading="lazy" (heuristic: appears later in document). Review if above-the-fold.',
                )
            )
        return out

    def _backup_file(self, fp: Path) -> None:
        ts = time.strftime("%Y%m%d-%H%M%S")
        bak = fp.with_suffix(fp.suffix + f".bak.{ts}")
        bak.write_bytes(fp.read_bytes())




