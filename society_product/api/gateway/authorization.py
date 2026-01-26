class PermissionResolver:

    @staticmethod
    def bind_permissions(ctx):
        # Placeholder logic (will bind to governance/compliance later)
        role_map = {
            "admin": ["ALL"],
            "member": ["READ", "PAY", "VOTE"],
            "auditor": ["READ", "AUDIT"]
        }

        role = ctx.role or "member"
        ctx.product_permissions = role_map.get(role, [])
        return ctx
