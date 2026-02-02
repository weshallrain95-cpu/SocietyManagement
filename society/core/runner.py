"""
SocietyOS System Runner
Runtime launcher and process controller
"""

import threading
from typing import Optional
from society.core.bootstrap import bootstrap_system

_system = None
_runtime_thread: Optional[threading.Thread] = None


def start_system(background: bool = False):
    """
    Start SocietyOS runtime
    """
    global _system, _runtime_thread

    if _system:
        print("[RUNNER] System already running")
        return _system

    print("[RUNNER] Bootstrapping system...")
    _system = bootstrap_system()

    def run():
        try:
            _system.start()
        except KeyboardInterrupt:
            pass

    if background:
        print("[RUNNER] Starting in background mode")
        _runtime_thread = threading.Thread(target=run, daemon=True)
        _runtime_thread.start()
    else:
        print("[RUNNER] Starting in foreground mode")
        run()

    return _system


def stop_system():
    """
    Stop SocietyOS runtime
    """
    global _system, _runtime_thread

    if not _system:
        print("[RUNNER] System not running")
        return

    print("[RUNNER] Stopping system...")
    _system.shutdown()
    _system = None
    _runtime_thread = None
    print("[RUNNER] System stopped")


def system_status():
    """
    Get system status
    """
    if not _system:
        return {"running": False}

    return {
        "running": True,
        "status": _system.status(),
    }


# -------------------------
# Governance mode control
# -------------------------

def set_governance_mode(mode: str):
    global _system
    if not _system:
        _system = bootstrap_system()

    _system.governance.set_mode(mode)


def get_governance_mode():
    global _system
    if not _system:
        _system = bootstrap_system()

    return _system.governance.mode


# -------------------------
# Demo mode
# -------------------------

def demo_system(command: str | None = None):
    """
    Run SocietyOS demo mode
    """
    print("\n=== SocietyOS DEMO MODE ===")

    system = start_system(background=False)

    lifecycle = system.lifecycle
    router = system.router
    orchestrator = system.orchestrator
    governance = system.governance

    print("\n[DEMO] Governance Mode:", governance.mode)

    # --------------------------------------------------
    # Governance rule
    def block_shutdown(context, action, payload):
        if action == "system.shutdown":
            return False, "Shutdown not allowed in demo"
        return True, "ok"

    governance.register_rule(block_shutdown)

    # --------------------------------------------------
    # Demo route
    def read_status():
        return "system.read.ok"

    router.register("demo.read", read_status, domain="demo")

    # --------------------------------------------------
    # Demo workflow
    from society.core.orchestrator import Workflow, Step

    wf = Workflow("demo.workflow")
    wf.add_step(Step("step1", lambda: "step1"))
    wf.add_step(Step("step2", lambda: "step2"))
    orchestrator.register_workflow(wf)

    lifecycle.boot()

    # --------------------------------------------------
    if command == "onboard":
        print("\n[DEMO] Running society onboarding workflow")

        try:
            result = orchestrator.execute("society.onboard", {})
            print("RESULT:", result)
        except Exception as e:
            print("ERROR:", e)

        print("\n[DEMO] Attempting second onboarding (should fail)")
        try:
            orchestrator.execute("society.onboard", {})
        except Exception as e:
            print("BLOCKED:", e)

        print("\n=== DEMO COMPLETE ===\n")
        return

    # --------------------------------------------------
    print("\n[DEMO] Route result:", router.route("demo.read", {}))
    print("\n[DEMO] Workflow result:", orchestrator.execute("demo.workflow", {}))

    decision = governance.evaluate(system.context, "system.shutdown")
    print("\n[DEMO] Shutdown decision:", decision.snapshot())

    print("\n=== DEMO COMPLETE ===\n")

