from __future__ import annotations

import re
from typing import List

from .rules import Rule, make_finding


# Shopify-specific patterns
SHOPIFY_CDN_RE = re.compile(r"cdn\.shopify\.com", re.IGNORECASE)
RENDER_JS_RE = re.compile(r"theme\.js", re.IGNORECASE)
LIQUID_RENDER_RE = re.compile(r"{%\s*render\s+", re.IGNORECASE)
SECTION_SCHEMA_RE = re.compile(r"{%\s*schema\s*%}", re.IGNORECASE)






