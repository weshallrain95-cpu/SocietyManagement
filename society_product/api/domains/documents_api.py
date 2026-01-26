from society_product.services.domains.documents_service import DocumentsService

def upload_document(ctx, payload):
    return DocumentsService.upload_document(ctx, payload)
