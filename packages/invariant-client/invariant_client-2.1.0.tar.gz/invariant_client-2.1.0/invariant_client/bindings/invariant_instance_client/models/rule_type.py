from enum import Enum


class RuleType(str, Enum):
    EGRESS_CRITICAL_FLOW = "egress-critical-flow"
    EGRESS_DENY = "egress-deny"
    EGRESS_DENY_OTHERS = "egress-deny-others"
    INGRESS_CRITICAL_FLOW = "ingress-critical-flow"
    INGRESS_DENY = "ingress-deny"
    INGRESS_DENY_OTHERS = "ingress-deny-others"

    def __str__(self) -> str:
        return str(self.value)
