from society_product.engines.governance_engine import GovernanceEngine

class GovernanceService:
    @staticmethod
    def propose_decision(ctx, payload):
        return GovernanceEngine.propose_decision(ctx, payload)
