from society_product.services.domains.governance_service import GovernanceService

def propose_decision(ctx, payload):
    ctx.require("VOTE")
    return GovernanceService.propose_decision(ctx, payload)
