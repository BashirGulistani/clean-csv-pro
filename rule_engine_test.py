from __future__ import annotations

from typing import List

from .rules import RULES, Rule

# Optional Shopify pack
try:
    from .rule_pack_shopify import SHOPIFY_RULES
except Exception:
    SHOPIFY_RULES = []







