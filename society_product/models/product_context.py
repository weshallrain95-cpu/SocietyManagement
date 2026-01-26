from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class ProductContext:
    user_id: str
    society_id: str

    role: str = None
    authority_scope: str = None
    legal_scope: str = None
    compliance_scope: str = None
    governance_scope: str = None

    product_permissions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def has_permission(self, perm: str) -> bool:
        return perm in self.product_permissions

    def require(self, perm: str):
        if not self.has_permission(perm):
            raise PermissionError(f"Missing product permission: {perm}")
