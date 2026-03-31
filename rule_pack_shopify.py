from __future__ import annotations

import re
from typing import List

from .rules import Rule, make_finding


# Shopify-specific patterns
SHOPIFY_CDN_RE = re.compile(r"cdn\.shopify\.com", re.IGNORECASE)
RENDER_JS_RE = re.compile(r"theme\.js", re.IGNORECASE)
LIQUID_RENDER_RE = re.compile(r"{%\s*render\s+", re.IGNORECASE)
SECTION_SCHEMA_RE = re.compile(r"{%\s*schema\s*%}", re.IGNORECASE)






# -------------------------
# Rule: Missing preconnect to Shopify CDN
# -------------------------
def rule_missing_preconnect(file: str, text: str, inv) -> List:
    out = []
    if "cdn.shopify.com" in text.lower():
        if "rel=\"preconnect\"" not in text.lower():
            out.append(
                make_finding(
                    "SHOP001",
                    "medium",
                    "Missing preconnect to Shopify CDN",
                    "Consider adding <link rel=\"preconnect\" href=\"https://cdn.shopify.com\"> for faster asset loading.",
                    file=file,
                    help="Preconnect can reduce latency for Shopify-hosted assets.",
                )
            )
    return out


# -------------------------
# Rule: Large theme.js detected
# -------------------------
def rule_large_theme_js(file: str, text: str, inv) -> List:
    out = []
    if RENDER_JS_RE.search(file):
        size = len(text)
        if size > 150_000:
            out.append(
                make_finding(
                    "SHOP002",
                    "high",
                    "Large theme.js file",
                    f"theme.js appears large (~{size:,} chars). Consider splitting or optimizing.",
                    file=file,
                    help="Large JS bundles hurt load performance and TTI.",
                )
            )
    return out


