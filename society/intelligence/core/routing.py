class AdaptiveRouter:
    def choose_next(self, current_node, graph, intelligence_state):
        # default: normal graph routing
        return graph.get_next_nodes(current_node.node_id)
