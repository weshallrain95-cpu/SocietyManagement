# society/legal/constitution/ontology/normative.py

from enum import Enum


# ============================
# Normative Types
# ============================

class NormativeType(str, Enum):
    OBLIGATION = "OBLIGATION"     # Must do
    PROHIBITION = "PROHIBITION"   # Must not do
    PERMISSION = "PERMISSION"     # May do
    EXCEPTION = "EXCEPTION"       # Conditional override
    RIGHT = "RIGHT"               # Entitlement
    DUTY = "DUTY"                 # Responsibility
    LIABILITY = "LIABILITY"       # Legal exposure
    IMMUNITY = "IMMUNITY"         # Protection from liability


# ============================
# Norm Structure (Semantic Model)
# ============================

class Norm:
    """
    Semantic representation of a legal norm.
    This is NOT a Django model.
    This is a reasoning structure.
    """

    def __init__(
        self,
        subject: str,
        action: str,
        obj: str = None,
        condition: dict = None,
        constraint: dict = None,
        consequence: dict = None,
        enforcement: dict = None,
        exception: dict = None,
    ):
        self.subject = subject
        self.action = action
        self.object = obj
        self.condition = condition or {}
        self.constraint = constraint or {}
        self.consequence = consequence or {}
        self.enforcement = enforcement or {}
        self.exception = exception or {}

    def to_dict(self):
        return {
            "subject": self.subject,
            "action": self.action,
            "object": self.object,
            "condition": self.condition,
            "constraint": self.constraint,
            "consequence": self.consequence,
            "enforcement": self.enforcement,
            "exception": self.exception,
        }

    def __repr__(self):
        return f"<Norm {self.subject} {self.action} {self.object}>"
