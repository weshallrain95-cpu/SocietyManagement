from communications.engines.compliance_engine import ComplianceEngine
from communications.services.archival_service import ArchivalService
from datetime import datetime


class LifecycleService:
    """
    Data lifecycle governance engine
    """

    def __init__(self):
        self.compliance = ComplianceEngine()
        self.archival = ArchivalService()

    def process(self, message_obj, message_type):
        retention = self.compliance.retention_check(
            message_type=message_type,
            created_at=message_obj.created_at
        )

        now = datetime.utcnow()

        if retention["legal_hold"]:
            return self.archival.legal_hold(message_obj, "policy")

        if now >= retention["expires_at"]:
            if retention["archive"]:
                return self.archival.archive(message_obj, "retention_expired")
            else:
                # Future: secure delete
                return {"status": "deleted", "message_id": str(message_obj.id)}

        return {"status": "active", "message_id": str(message_obj.id)}
