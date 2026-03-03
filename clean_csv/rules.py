from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional, Union


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str 
    title: str
    message: str
    file: str
    line: int = 1
    col: int = 1
    help: str = ""




def make_finding(
    rule_id: str,
    severity: str,
    title: str,
    message: str,
    file: str,
    line: int = 1,
    col: int = 1,
    help: str = "",
) -> Finding:
    return Finding(
        rule_id=rule_id,
        severity=severity,
        title=title,
        message=message,
        file=file,
        line=max(1, int(line)),
        col=max(1, int(col)),
        help=help,
    )


CheckFn = Callable[[str, Union[str, Path], object], List[Finding]]



