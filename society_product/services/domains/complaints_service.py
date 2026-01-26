from society_product.engines.complaints_engine import ComplaintsEngine

class ComplaintsService:
    @staticmethod
    def report_complaint(ctx, payload):
        return ComplaintsEngine.report_complaint(ctx, payload)
