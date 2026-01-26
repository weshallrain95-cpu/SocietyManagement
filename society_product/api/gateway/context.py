from society_product.api.gateway.identity import IdentityResolver
from society_product.api.gateway.authorization import PermissionResolver

class ProductContextBuilder:

    @staticmethod
    def build(request):
        ctx = IdentityResolver.resolve(request)
        ctx = PermissionResolver.bind_permissions(ctx)
        return ctx
