from society_product.engines.administration_engine import AdministrationEngine

class AdministrationService:
    @staticmethod
    def configure(ctx, payload):
        return AdministrationEngine.configure(ctx, payload)
