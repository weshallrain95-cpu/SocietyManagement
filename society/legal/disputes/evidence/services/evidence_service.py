# society/legal/disputes/evidence/services/evidence_service.py

import uuid
import hashlib
from django.utils import timezone
from society.legal.disputes.evidence.models.evidence import Evidence
from society.legal.disputes.evidence.models.chain_of_custody import ChainOfCustody


# ============================
# Evidence Service
# ============================

class EvidenceService:
    """
    Manages legal evidence lifecycle.
    """

    def create_evidence(
        self,
        case_id: str,
        evidence_type: str,
        storage_uri: str,
        mime_type: str,
        raw_bytes: bytes,
        source: str,
        collected_by: str,
        context: dict = None,
    ) -> Evidence:

        sha256 = hashlib.sha256(raw_bytes).hexdigest()
        sha512 = hashlib.sha512(raw_bytes).hexdigest()

        ref_id = f"EVD-{uuid.uuid4().hex[:12].upper()}"

        evidence = Evidence.objects.create(
            reference_id=ref_id,
            case_id=case_id,
            evidence_type=evidence_type,
            storage_uri=storage_uri,
            mime_type=mime_type,
            hash_sha256=sha256,
            hash_sha512=sha512,
            signed=False,
            source=source,
            collected_by=collected_by,
            collected_at=timezone.now(),
            context=context or {},
            status="COLLECTED",
        )

        # Chain of custody entry
        ChainOfCustody.objects.create(
            evidence=evidence,
            handler=collected_by,
            action="COLLECTED",
            hash_snapshot=sha256,
            timestamp=timezone.now(),
            purpose="Initial collection",
        )

        return evidence

    def archive_evidence(self, evidence: Evidence, handler: str):
        evidence.status = "ARCHIVED"
        evidence.save()

        ChainOfCustody.objects.create(
            evidence=evidence,
            handler=handler,
            action="ARCHIVED",
            hash_snapshot=evidence.hash_sha256,
            timestamp=timezone.now(),
            purpose="Archived evidence",
        )

        return evidence
