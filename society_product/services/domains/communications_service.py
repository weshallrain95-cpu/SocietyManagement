from society_product.engines.communications_engine import CommunicationsEngine

class CommunicationsService:
    @staticmethod
    def send_notice(ctx, payload):
        return CommunicationsEngine.send_notice(ctx, payload)
