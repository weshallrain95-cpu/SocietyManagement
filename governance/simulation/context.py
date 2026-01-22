from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class SimulationContext:
    actor: str
    action: str
    resource: str
    role: str | None = None
    attributes: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self):
        base = {
            "actor": self.actor,
            "action": self.action,
            "resource": self.resource,
            "role": self.role,
        }
        base.update(self.attributes)
        return base
