from society_product.engines.auditor_engine import AuditorEngine

class AuditorService:
    @staticmethod
    def request_audit(ctx, payload):
        return AuditorEngine.request_audit(ctx, payload)
