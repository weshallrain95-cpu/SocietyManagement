"""
SocietyOS Governance Authority Layer
System-level governance enforcement (Profiled)
"""

from typing import Dict, Any, Callable, List


class GovernanceDecision:
    """
    Result of governance evaluation
    """

    def __init__(
        self,
        allowed: bool,
        reason: str = "",
        metadata: Dict[str, Any] = None,
        severity: str = "info",
    ):
        self.allowed = allowed
        self.reason = reason
        self.metadata = metadata or {}
        self.severity = severity  # info | warning | critical

    def snapshot(self):
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "severity": self.severity,
            "metadata": self.metadata,
        }


class GovernanceAuthority:
    """
    Central governance control layer
    Modes:
      - observe : allow + log
      - enforce : block
      - strict  : block + critical audit
    """

    VALID_MODES = {"observe", "enforce", "strict"}

    def __init__(self, mode: str = "observe"):
        if mode not in self.VALID_MODES:
            raise ValueError(f"Invalid governance mode: {mode}")

        self.mode = mode
        self.rules: List[Callable] = []
        self.audit_log = []

    # -------------------------
    # Configuration
    # -------------------------

    def set_mode(self, mode: str):
        if mode not in self.VALID_MODES:
            raise ValueError(f"Invalid governance mode: {mode}")
        self.mode = mode

    # -------------------------
    # Rules
    # -------------------------

    def register_rule(self, rule_callable):
        """
        rule_callable(context, action, payload) -> (allowed: bool, reason: str)
        """
        self.rules.append(rule_callable)

    # -------------------------
    # Evaluation
    # -------------------------

    def evaluate(
        self,
        context,
        action: str,
        payload: Dict[str, Any] = None,
    ) -> GovernanceDecision:
        payload = payload or {}

        for rule in self.rules:
            allowed, reason = rule(context, action, payload)

            if not allowed:
                severity = (
                    "critical" if self.mode == "strict"
                    else "warning"
                )

                decision = GovernanceDecision(
                    allowed=False,
                    reason=reason,
                    severity=severity,
                    metadata={
                        "mode": self.mode,
                        "action": action,
                    },
                )

                self.audit_log.append(decision.snapshot())

                if self.mode in {"enforce", "strict"}:
                    return decision

                # observe mode → allow but visible
                return GovernanceDecision(
                    allowed=True,
                    reason=f"Observed violation: {reason}",
                    severity="info",
                    metadata={
                        "mode": self.mode,
                        "action": action,
                    },
                )

        decision = GovernanceDecision(
            allowed=True,
            reason="Allowed",
            severity="info",
            metadata={
                "mode": self.mode,
                "action": action,
            },
        )

        self.audit_log.append(decision.snapshot())
        return decision

    # -------------------------
    # Introspection
    # -------------------------

    def snapshot(self):
        return {
            "mode": self.mode,
            "rules": len(self.rules),
            "audit_events": len(self.audit_log),
        }
