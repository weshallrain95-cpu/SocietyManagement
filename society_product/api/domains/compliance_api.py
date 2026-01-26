from society_product.services.domains.compliance_service import ComplianceService

def check_compliance(ctx, payload):
    return ComplianceService.check_compliance(ctx, payload)
