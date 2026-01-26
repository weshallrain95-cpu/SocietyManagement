from society_product.engines.compliance_engine import ComplianceEngine

class ComplianceService:
    @staticmethod
    def check_compliance(ctx, payload):
        return ComplianceEngine.check_compliance(ctx, payload)
