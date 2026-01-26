class CommunicationsEngine:
    @staticmethod
    def send_notice(ctx, payload):
        return {
            "status": "sent",
            "message": payload.get("message"),
            "society_id": ctx.society_id
        }
