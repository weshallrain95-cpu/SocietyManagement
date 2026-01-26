# Manual override handling - stub
class OverridesManager:
    @staticmethod
    def request_override(node, ctx, payload, reason):
        return {
            "status": "override_requested",
            "node": node.node_id,
            "reason": reason
        }
