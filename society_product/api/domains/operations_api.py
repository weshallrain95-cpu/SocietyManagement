from society_product.services.domains.operations_service import OperationsService

def create_task(ctx, payload):
    return OperationsService.create_task(ctx, payload)
