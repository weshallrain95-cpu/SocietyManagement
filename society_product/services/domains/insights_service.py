from society_product.engines.insights_engine import InsightsEngine

class InsightsService:
    @staticmethod
    def get_metrics(ctx, payload):
        return InsightsEngine.get_metrics(ctx, payload)
