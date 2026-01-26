class InsightsEngine:
    @staticmethod
    def get_metrics(ctx, payload):
        return {
            "status": "metrics_ready",
            "society_id": ctx.society_id,
            "metrics": {
                "members": 120,
                "complaints": 4,
                "disputes": 1
            }
        }
