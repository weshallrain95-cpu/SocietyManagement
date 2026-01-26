class GovernanceEngine:
    @staticmethod
    def propose_decision(ctx, payload):
        return {
            "status": "proposed",
            "title": payload.get("title"),
            "society_id": ctx.society_id
        }
