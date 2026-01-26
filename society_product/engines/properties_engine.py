class PropertiesEngine:
    @staticmethod
    def add_property(ctx, payload):
        return {
            "status": "property_added",
            "property": payload.get("property"),
            "society_id": ctx.society_id
        }
