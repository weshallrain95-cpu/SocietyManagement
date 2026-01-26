from .process_graph import ProcessGraph, Node
from .state_machine import WorkflowState, NodeState
from .transitions import should_execute
from .conditions import CONDITIONS
from .execution_dispatcher import ExecutionDispatcher
from .rollback import RollbackManager
from .escalation import EscalationManager
from .audit_binding import emit_workflow_event

# Intelligence layer
from society.intelligence.bootstrap import build_intelligence


class WorkflowEngine:
    """
    Core Workflow Execution Engine
    Now integrated with Intelligence Layer (Phase 12.5)
    """

    def __init__(self):
        # Build intelligence engine once per workflow engine instance
        self.intelligence = build_intelligence()

    def run(self, process_graph: ProcessGraph, ctx, initial_payload: dict):
        """
        Executes a process graph sequentially (default).
        Records states, runs compensations on failure.
        Intelligence layer influences execution decisions, scoring, and routing.
        """

        wf_state = WorkflowState(process_graph.graph_id)
        results_by_node = {}
        completed_nodes = []

        # --- Initialize workflow states ---
        for node_id, node in process_graph.nodes.items():
            wf_state.set_state(node_id, NodeState.PENDING)

        emit_workflow_event(ctx, "workflow_started", {
            "graph": process_graph.graph_id
        })

        try:
            for node_id, node in process_graph.nodes.items():

                # -----------------------------
                # Intelligence pre-evaluation
                # -----------------------------
                intelligence_signal = self.intelligence.evaluate_node(
                    node=node,
                    context=ctx,
                    payload=initial_payload,
                    workflow_state=wf_state,
                )

                # intelligence can veto execution
                if intelligence_signal.get("block") is True:
                    wf_state.set_state(node_id, NodeState.SKIPPED)
                    emit_workflow_event(ctx, "node_blocked_by_intelligence", {
                        "node": node_id,
                        "reason": intelligence_signal.get("reason")
                    })
                    continue

                # -----------------------------
                # Condition evaluation
                # -----------------------------
                if not should_execute(node, ctx, initial_payload, CONDITIONS):
                    wf_state.set_state(node_id, NodeState.SKIPPED)
                    emit_workflow_event(ctx, "node_skipped", {"node": node_id})
                    continue

                # -----------------------------
                # Node execution
                # -----------------------------
                wf_state.set_state(node_id, NodeState.RUNNING)
                emit_workflow_event(ctx, "node_started", {
                    "node": node_id,
                    "intelligence": intelligence_signal
                })

                try:
                    result = ExecutionDispatcher.execute_node(node, ctx, initial_payload)

                    wf_state.set_state(node_id, NodeState.COMPLETED)
                    results_by_node[node_id] = result
                    completed_nodes.append(node)

                    # Intelligence post-processing
                    self.intelligence.observe_execution(
                        node=node,
                        result=result,
                        context=ctx,
                        payload=initial_payload,
                        workflow_state=wf_state,
                    )

                    emit_workflow_event(ctx, "node_completed", {
                        "node": node_id,
                        "result": result
                    })

                except Exception as exc:
                    wf_state.set_state(node_id, NodeState.FAILED)

                    emit_workflow_event(ctx, "node_failed", {
                        "node": node_id,
                        "error": str(exc)
                    })

                    # Intelligence failure observation
                    self.intelligence.observe_failure(
                        node=node,
                        error=exc,
                        context=ctx,
                        payload=initial_payload,
                        workflow_state=wf_state,
                    )

                    # escalate
                    EscalationManager.escalate(node, ctx, initial_payload, exc)

                    # rollback
                    rollback_result = RollbackManager.rollback(
                        completed_nodes,
                        ctx,
                        initial_payload,
                        results_by_node
                    )

                    return {
                        "status": "failed",
                        "failed_node": node_id,
                        "error": str(exc),
                        "rollback": rollback_result,
                        "workflow_state": wf_state,
                        "intelligence": self.intelligence.snapshot(),
                    }

            # -----------------------------
            # Success path
            # -----------------------------
            emit_workflow_event(ctx, "workflow_completed", {
                "graph": process_graph.graph_id
            })

            return {
                "status": "completed",
                "results": results_by_node,
                "workflow_state": wf_state,
                "intelligence": self.intelligence.snapshot(),
            }

        finally:
            # Final lifecycle hook
            emit_workflow_event(ctx, "workflow_finished", {
                "graph": process_graph.graph_id
            })
