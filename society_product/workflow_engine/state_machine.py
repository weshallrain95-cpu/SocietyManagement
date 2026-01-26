from enum import Enum
from typing import Dict

class NodeState(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"

class WorkflowState:
    def __init__(self, workflow_id: str):
        self.workflow_id = workflow_id
        self.node_states: Dict[str, NodeState] = {}
        self.history = []

    def set_state(self, node_id: str, state: NodeState):
        self.node_states[node_id] = state
        self.history.append((node_id, state))

    def get_state(self, node_id: str):
        return self.node_states.get(node_id, NodeState.PENDING)
