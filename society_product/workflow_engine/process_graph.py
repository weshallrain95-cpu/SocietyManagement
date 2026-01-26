# A lightweight process graph representation (sequential by default)
from typing import List, Dict, Any

class Node:
    def __init__(self, node_id: str, action_domain: str, action_name: str, params: Dict[str, Any]=None, condition: str=None):
        """
        action_domain: e.g. "members"
        action_name: e.g. "add_member"
        params: static params for action; merged with current payload when executed
        condition: optional condition key name evaluated by conditions module
        """
        self.node_id = node_id
        self.action_domain = action_domain
        self.action_name = action_name
        self.params = params or {}
        self.condition = condition  # string key resolved in conditions module

class ProcessGraph:
    def __init__(self, graph_id: str, nodes: List[Node], edges: List[tuple]=None):
        """
        nodes: ordered list for sequential execution by default
        edges: optional list of (from_node_id, to_node_id) tuples for graph traversal
        """
        self.graph_id = graph_id
        self.nodes = {n.node_id: n for n in nodes}
        # default linear edges if not provided: order of nodes
        if edges is None:
            self.edges = []
            for i in range(len(nodes)-1):
                self.edges.append((nodes[i].node_id, nodes[i+1].node_id))
        else:
            self.edges = edges

    def get_start_nodes(self):
        if len(self.nodes) == 0:
            return []
        # nodes without incoming edges
        incoming = {t for (_, t) in self.edges}
        return [nid for nid in self.nodes.keys() if nid not in incoming]

    def get_next(self, node_id):
        return [t for (f, t) in self.edges if f == node_id]
