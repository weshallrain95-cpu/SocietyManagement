from society_product.services.domains.insights_service import InsightsService

def get_metrics(ctx, payload):
    return InsightsService.get_metrics(ctx, payload)
