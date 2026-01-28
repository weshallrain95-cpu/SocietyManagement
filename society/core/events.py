"""
SocietyOS Event Bus System
Central event communication layer
"""

import uuid
from datetime import datetime
from typing import Callable, Dict, List, Any
from society.core.context import ExecutionContext


class Event:
    """
    Base event model
    """

    def __init__(self, name: str, payload: Dict[str, Any], source: str = "system"):
        self.event_id = str(uuid.uuid4())
        self.name = name
        self.payload = payload
        self.source = source
        self.timestamp = datetime.utcnow().isoformat()

    def snapshot(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "name": self.name,
            "source": self.source,
            "timestamp": self.timestamp,
            "payload": self.payload,
        }


class EventBus:
    """
    Publish / Subscribe Event Bus
    """

    def __init__(self, context: ExecutionContext):
        self.context = context
        self.subscribers: Dict[str, List[Callable[[Event], None]]] = {}
        self.history: List[Event] = []

    def subscribe(self, event_name: str, handler: Callable[[Event], None]):
        if event_name not in self.subscribers:
            self.subscribers[event_name] = []
        self.subscribers[event_name].append(handler)

    def publish(self, event_name: str, payload: Dict[str, Any], source: str = "system"):
        event = Event(name=event_name, payload=payload, source=source)
        self.history.append(event)

        if self.context.debug:
            print(f"[EVENT] {event_name} from {source}")

        # Dispatch to subscribers
        handlers = self.subscribers.get(event_name, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"[EVENT ERROR] Handler failure for {event_name}: {e}")

    def get_history(self) -> List[Dict[str, Any]]:
        return [e.snapshot() for e in self.history]

    def clear_history(self):
        self.history.clear()

