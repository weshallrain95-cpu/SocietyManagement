from society_product.services.domains.disputes_service import DisputesService

def open_dispute(ctx, payload):
    return DisputesService.open_dispute(ctx, payload)
