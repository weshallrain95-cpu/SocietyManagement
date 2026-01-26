from society_product.api.gateway.router import ProductAPIGateway

class ExecutionDispatcher:
    """
    Responsible for executing action nodes via the ProductAPIGateway.
    """

    @staticmethod
    def execute_node(node, ctx, runtime_payload):
        """
        node: Node instance from process_graph
        ctx: ProductContext
        runtime_payload: current payload dict that can be mutated/extended
        returns: result dict from domain action
        """
        # merge static params and runtime payload (runtime overrides static)
        params = {}
        params.update(node.params or {})
        params.update(runtime_payload or {})

        # call via ProductAPIGateway
        result = ProductAPIGateway.dispatch(
            request=ctx._request_like if hasattr(ctx, "_request_like") else ctx,  # gateway expects request-like for identity
            domain=node.action_domain,
            action=node.action_name,
            payload=params
        )
        return result
