class FinanceEngine:

    @staticmethod
    def collect_due(ctx, payload):
        # placeholder execution
        return {
            "status": "success",
            "action": "collect_due",
            "society_id": ctx.society_id,
            "amount": payload.get("amount")
        }

    @staticmethod
    def approve_payment(ctx, payload):
        return {
            "status": "approved",
            "payment_id": payload.get("payment_id")
        }
