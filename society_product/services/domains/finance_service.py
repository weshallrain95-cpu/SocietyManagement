from society_product.engines.finance_engine import FinanceEngine

class FinanceService:

    @staticmethod
    def collect_due(ctx, payload):
        return FinanceEngine.collect_due(ctx, payload)

    @staticmethod
    def approve_payment(ctx, payload):
        return FinanceEngine.approve_payment(ctx, payload)
