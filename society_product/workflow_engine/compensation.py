# Minimal compensation manager - invoked when rollback is required.
class CompensationManager:
    @staticmethod
    def compensate(node, ctx, payload, result):
        # Basic placeholder - record compensation intent; implement domain-specific compensation later.
        return {
            "status": "compensation_recorded",
            "node": node.node_id,
            "society_id": ctx.society_id
        }
