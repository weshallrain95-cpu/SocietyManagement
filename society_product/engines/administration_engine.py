class AdministrationEngine:
    @staticmethod
    def configure(ctx, payload):
        return {
            "status": "configured",
            "config": payload,
            "society_id": ctx.society_id
        }
