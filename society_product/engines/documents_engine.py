class DocumentsEngine:
    @staticmethod
    def upload_document(ctx, payload):
        return {
            "status": "uploaded",
            "document": payload.get("name"),
            "society_id": ctx.society_id
        }
