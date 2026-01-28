"""
SocietyOS State Engine
Central state management system
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from society.core.context import ExecutionContext


class StateRecord:
    """
    Represents a single state record
    """

    def __init__(self, key: str, value: Any, scope: str = "global"):
        self.id = str(uuid.uuid4())
        self.key = key
        self.value = value
        self.scope = scope
        self.timestamp = datetime.utcnow().isoformat()

    def snapshot(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "key": self.key,
            "value": self.value,
            "scope": self.scope,
            "timestamp": self.timestamp,
        }


class StateEngine:
    """
    Global state engine for SocietyOS
    """

    def __init__(self, context: ExecutionContext):
        self.context = context
        self.store: Dict[str, StateRecord] = {}
        self.history: Dict[str, list[StateRecord]] = {}

    def set(self, key: str, value: Any, scope: str = "global"):
        record = StateRecord(key=key, value=value, scope=scope)
        self.store[key] = record

        if key not in self.history:
            self.history[key] = []
        self.history[key].append(record)

        if self.context.debug:
            print(f"[STATE] SET {key} = {value}")

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        record = self.store.get(key)
        if not record:
            return default
        return record.value

    def exists(self, key: str) -> bool:
        return key in self.store

    def delete(self, key: str):
        if key in self.store:
            del self.store[key]
            if self.context.debug:
                print(f"[STATE] DELETE {key}")

    def snapshot(self) -> Dict[str, Any]:
        """
        Full state snapshot
        """
        return {
            "store": {k: v.snapshot() for k, v in self.store.items()},
            "history": {
                k: [r.snapshot() for r in records]
                for k, records in self.history.items()
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

    def reset(self):
        self.store.clear()
        self.history.clear()
        if self.context.debug:
            print("[STATE] RESET")

    # --- Future hooks ---
    # persist()
    # restore()
    # rollback()
    # diff()
    # audit_export()

