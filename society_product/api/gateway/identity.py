from society_product.models.product_context import ProductContext

class IdentityResolver:

    @staticmethod
    def resolve(request) -> ProductContext:
        # placeholder for auth integration
        user_id = request.headers.get("X-User-ID")
        society_id = request.headers.get("X-Society-ID")

        if not user_id or not society_id:
            raise Exception("Invalid identity context")

        return ProductContext(
            user_id=user_id,
            society_id=society_id
        )
