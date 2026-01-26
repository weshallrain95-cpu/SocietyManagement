from society_product.services.domains.administration_service import AdministrationService

def configure(ctx, payload):
    return AdministrationService.configure(ctx, payload)
