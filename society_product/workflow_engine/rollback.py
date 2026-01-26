# Minimal rollback manager - orchestrates compensation for previously completed nodes.
from .compensation import CompensationManager

class RollbackManager:
    @staticmethod
    def rollback(completed_nodes, ctx, payload, results_by_node):
        compensations = []
        # iterate in reverse order
        for node in reversed(completed_nodes):
            res = CompensationManager.compensate(node, ctx, payload, results_by_node.get(node.node_id))
            compensations.append(res)
        return {
            "status": "rolled_back",
            "compensations": compensations
        }
