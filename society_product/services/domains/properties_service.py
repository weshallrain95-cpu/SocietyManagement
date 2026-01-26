from society_product.engines.properties_engine import PropertiesEngine

class PropertiesService:
    @staticmethod
    def add_property(ctx, payload):
        return PropertiesEngine.add_property(ctx, payload)
