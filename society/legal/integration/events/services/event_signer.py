# society/legal/integration/events/services/event_signer.py

import hashlib
import json


# ============================
# Event Signer
# ============================

class EventSigner:
    """
    Signs legal events for integrity.
    """

    def sign(self, event_data: dict) -> dict:
        serialized = json.dumps(event_data, sort_keys=True).encode()
        sha = hashlib.sha256(serialized).hexdigest()
        event_data["hash"] = sha
        return event_data
