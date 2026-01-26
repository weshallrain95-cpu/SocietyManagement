from society_product.services.domains.properties_service import PropertiesService

def add_property(ctx, payload):
    return PropertiesService.add_property(ctx, payload)
