class AuditorEngine:
    @staticmethod
    def request_audit(ctx, payload):
        return {
            "status": "audit_requested",
            "scope": payload.get("scope"),
            "society_id": ctx.society_id
        }
