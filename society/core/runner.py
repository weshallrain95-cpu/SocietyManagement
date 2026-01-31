"""
SocietyOS System Runner
Runtime launcher and process controller
"""

import threading
import time
from typing import Optional
from society.core.bootstrap import bootstrap_system

_system = None
_runtime_thread: Optional[threading.Thread] = None


def start_system(background: bool = False):
    """
    Start SocietyOS runtime
    """
    global _system, _runtime_thread

    if _system is not None:
        print("[RUNNER] System already running")
        return

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


def stop_system():
    """
    Stop SocietyOS runtime
    """
    global _system, _runtime_thread

    if _system is None:
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
    if _system is None:
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


def get_governance_mode() -> str:
    global _system
    if not _system:
        _system = bootstrap_system()

    return _system.governance.mode
