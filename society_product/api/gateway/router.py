from society_product.api.gateway.context import ProductContextBuilder
from society_product.api.gateway.governance_hooks import GovernanceHooks
from society_product.api.gateway.compliance_hooks import ComplianceHooks
from society_product.api.gateway.audit_hooks import AuditHooks
from society_product.api.domains import (
    governance_api,
    operations_api,
    members_api,
    finance_api,
    auditor_api,
    communications_api,
    compliance_api,
)

from society_product.api.domains import (
    governance_api,
    operations_api,
    members_api,
    finance_api,
)

DOMAIN_MAP = {
    "governance": governance_api,
    "operations": operations_api,
    "members": members_api,
    "finance": finance_api,
    "auditor": auditor_api,
    "communications": communications_api,
    "compliance": compliance_api,
}


class ProductAPIGateway:

    @staticmethod
    def dispatch(request, domain: str, action: str, payload: dict):
        ctx = ProductContextBuilder.build(request)

        # Pre-hooks
        GovernanceHooks.before(ctx, action)
        ComplianceHooks.before(ctx, action)

        # Domain routing
        if domain not in DOMAIN_MAP:
            raise Exception(f"Unknown product domain: {domain}")

        domain_api = DOMAIN_MAP[domain]

        if not hasattr(domain_api, action):
            raise Exception(f"Unknown action '{action}' in domain '{domain}'")

        handler = getattr(domain_api, action)

        result = handler(ctx, payload)

        # Post-hooks
        AuditHooks.after(ctx, action, result)

        return result
