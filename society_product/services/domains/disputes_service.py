from society_product.engines.disputes_engine import DisputesEngine

class DisputesService:
    @staticmethod
    def open_dispute(ctx, payload):
        return DisputesEngine.open_dispute(ctx, payload)
