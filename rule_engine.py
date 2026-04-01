from __future__ import annotations

from typing import List

from .rules import RULES, Rule

# Optional Shopify pack
try:
    from .rule_pack_shopify import SHOPIFY_RULES
except Exception:
    SHOPIFY_RULES = []






class RuleEngine:
    """
    Central rule engine that allows:
    - core rules
    - optional rule packs (Shopify, custom, etc.)
    - dynamic enabling/disabling
    """

    def __init__(
        self,
        include_shopify: bool = True,
        extra_rules: List[Rule] | None = None,
    ):
        self.rules: List[Rule] = list(RULES)

        if include_shopify:
            self.rules.extend(SHOPIFY_RULES)

        if extra_rules:
            self.rules.extend(extra_rules)




