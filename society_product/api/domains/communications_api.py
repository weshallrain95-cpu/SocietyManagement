from society_product.services.domains.communications_service import CommunicationsService

def send_notice(ctx, payload):
    return CommunicationsService.send_notice(ctx, payload)
