from society_product.services.domains.auditor_service import AuditorService

def request_audit(ctx, payload):
    ctx.require("AUDIT")
    return AuditorService.request_audit(ctx, payload)
