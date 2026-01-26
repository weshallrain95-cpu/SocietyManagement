class ComplianceEngine:
    @staticmethod
    def check_compliance(ctx, payload):
        return {
            "status": "compliant",
            "rule": payload.get("rule"),
            "society_id": ctx.society_id
        }
