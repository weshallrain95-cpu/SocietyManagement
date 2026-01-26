from society_product.engines.operations_engine import OperationsEngine

class OperationsService:
    @staticmethod
    def create_task(ctx, payload):
        return OperationsEngine.create_task(ctx, payload)
