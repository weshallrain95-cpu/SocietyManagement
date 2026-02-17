"""
SocietyOS Orchestrator System
Workflow and process orchestration engine (Governed)
"""

from typing import Callable, Dict, List, Any, Optional
from society.core.context import ExecutionContext
from society.core.state import StateEngine
from society.core.events import EventBus, Event
from society.core.governance import GovernanceDecision


class Step:
    """
    Single workflow step
    """

    def __init__(
        self,
        name: str,
        action: Callable[..., Any],
        compensation: Optional[Callable[..., Any]] = None,
    ):
        self.name = name
        self.action = action
        self.compensation = compensation


class Workflow:
    """
    Workflow definition
    """

    def __init__(self, name: str):
        self.name = name
        self.steps: List[Step] = []

    def add_step(self, step: Step):
        self.steps.append(step)


class Orchestrator:
    """
    Core workflow orchestration engine (Governed)
    """

    def __init__(
        self,
        context: ExecutionContext,
        state_engine: StateEngine,
        event_bus: EventBus,
    ):
        self.context = context
        self.state_engine = state_engine
        self.event_bus = event_bus
        self.workflows: Dict[str, Workflow] = {}

    # -------------------------
    # Registration
    # -------------------------

    def register_workflow(self, workflow: Workflow):
        self.workflows[workflow.name] = workflow

        if self.context.debug:
            print(f"[ORCHESTRATOR] Registered workflow: {workflow.name}")

    # -------------------------
    # Execute (Governed)
    # -------------------------

    def execute(self, workflow_name: str, payload: Dict[str, Any]) -> Any:
        workflow = self.workflows.get(workflow_name)

        if not workflow:
            raise ValueError(f"Workflow not found: {workflow_name}")

        # Governance gate (single entry point)
        decision = self.context.system.governance.evaluate(
            self.context,
            f"workflow.execute:{workflow_name}",
            {
                "workflow": workflow_name,
                "steps": [step.name for step in workflow.steps],
                "payload": payload,
            },
        )

        if not decision.allowed:
            raise PermissionError(
                f"Workflow '{workflow_name}' blocked by governance: {decision.reason}"
            )

        execution_id = f"{workflow_name}-{self.context.execution_id}"

        self.event_bus.publish(
            "workflow.started",
            {"workflow": workflow_name, "execution_id": execution_id},
            source="orchestrator",
        )

        results = []
        executed_steps: List[Step] = []

        try:
            for step in workflow.steps:
                if self.context.debug:
                    print(f"[ORCHESTRATOR] Step -> {step.name}")

                result = step.action(**payload)
                results.append(result)
                executed_steps.append(step)

                # Persist step state
                self.state_engine.set(
                    key=f"workflow.{workflow_name}.{step.name}",
                    value=result,
                    scope=execution_id,
                )

                self.event_bus.publish(
                    "workflow.step.completed",
                    {
                        "workflow": workflow_name,
                        "step": step.name,
                        "execution_id": execution_id,
                        "result": result,
                    },
                    source="orchestrator",
                )

            self.event_bus.publish(
                "workflow.completed",
                {"workflow": workflow_name, "execution_id": execution_id},
                source="orchestrator",
            )

            return results

        except Exception as e:
            self.event_bus.publish(
                "workflow.failed",
                {
                    "workflow": workflow_name,
                    "execution_id": execution_id,
                    "error": str(e),
                },
                source="orchestrator",
            )

            # Compensation logic (Saga pattern)
            for step in reversed(executed_steps):
                if step.compensation:
                    try:
                        if self.context.debug:
                            print(f"[ORCHESTRATOR] Compensation -> {step.name}")
                        step.compensation(**payload)
                    except Exception as ce:
                        print(f"[ORCHESTRATOR ERROR] Compensation failed: {ce}")

            raise e

def register_society_onboarding_workflow(orchestrator, context, state_engine):
    from society.core.orchestrator import Workflow, Step

    workflow = Workflow("society.onboard")

    # STEP 1 — initiate society
    def initiate_society():
        state_engine.set("society.exists", True)
        return "society.initiated"

    # STEP 2 — bind chairman
    def bind_chairman():
        state_engine.set("society.chairman_id", "CHAIRMAN_DEMO_ID")
        return "chairman.bound"

    # STEP 3 — lock governance
    def lock_governance():
        context.system.governance.mode = "enforce"
        return "governance.locked"

    # STEP 4 — activate society
    def activate_society():
        state_engine.set("society.status", "ACTIVE")
        return "society.active"

    workflow.add_step(Step("initiate_society", initiate_society))
    workflow.add_step(Step("bind_chairman", bind_chairman))
    workflow.add_step(Step("lock_governance", lock_governance))
    workflow.add_step(Step("activate_society", activate_society))

    orchestrator.register_workflow(workflow)
