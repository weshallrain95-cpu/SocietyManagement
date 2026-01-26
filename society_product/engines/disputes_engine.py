class DisputesEngine:
    @staticmethod
    def open_dispute(ctx, payload):
        return {
            "status": "dispute_opened",
            "subject": payload.get("subject"),
            "society_id": ctx.society_id
        }
