class MembersEngine:
    @staticmethod
    def add_member(ctx, payload):
        return {
            "status": "member_added",
            "name": payload.get("name"),
            "society_id": ctx.society_id
        }
