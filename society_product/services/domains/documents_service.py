from society_product.engines.documents_engine import DocumentsEngine

class DocumentsService:
    @staticmethod
    def upload_document(ctx, payload):
        return DocumentsEngine.upload_document(ctx, payload)
