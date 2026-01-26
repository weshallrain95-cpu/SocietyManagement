from society_product.engines.members_engine import MembersEngine

class MembersService:
    @staticmethod
    def add_member(ctx, payload):
        return MembersEngine.add_member(ctx, payload)
