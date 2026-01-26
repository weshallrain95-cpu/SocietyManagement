from society_product.services.domains.complaints_service import ComplaintsService

def report_complaint(ctx, payload):
    return ComplaintsService.report_complaint(ctx, payload)
