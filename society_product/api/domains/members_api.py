from society_product.services.domains.members_service import MembersService

def add_member(ctx, payload):
    return MembersService.add_member(ctx, payload)
