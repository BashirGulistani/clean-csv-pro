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
    def get_rules(self) -> List[Rule]:
        return self.rules

    def filter_rules(
        self,
        enabled_rule_ids: List[str] | None = None,
        disabled_rule_ids: List[str] | None = None,
    ) -> List[Rule]:
        rules = self.rules

        if enabled_rule_ids:
            enabled_set = {r.upper() for r in enabled_rule_ids}
            rules = [r for r in rules if r.id.upper() in enabled_set]

        if disabled_rule_ids:
            disabled_set = {r.upper() for r in disabled_rule_ids}
            rules = [r for r in rules if r.id.upper() not in disabled_set]

        return rules

 



