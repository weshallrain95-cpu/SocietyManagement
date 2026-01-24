# society/legal/disputes/evidence/services/verification_service.py

from django.utils import timezone
from society.legal.disputes.evidence.models.evidence import Evidence
from society.legal.disputes.evidence.models.chain_of_custody import ChainOfCustody
from .integrity_service import IntegrityService


# ============================
# Verification Service
# ============================

class VerificationService:
    """
    Performs legal-grade verification of evidence.
    """

    def __init__(self):
        self.integrity_service = IntegrityService()

    def verify_evidence(self, evidence: Evidence, raw_bytes: bytes, verifier: str) -> bool:
        valid = self.integrity_service.verify_integrity(evidence, raw_bytes)

        if valid:
            evidence.status = "VERIFIED"
            evidence.save()

            ChainOfCustody.objects.create(
                evidence=evidence,
                handler=verifier,
                action="VERIFIED",
                hash_snapshot=evidence.hash_sha256,
                timestamp=timezone.now(),
                purpose="Integrity verification",
            )
        else:
            evidence.status = "DISPUTED"
            evidence.save()

            ChainOfCustody.objects.create(
                evidence=evidence,
                handler=verifier,
                action="INTEGRITY_FAILED",
                hash_snapshot=evidence.hash_sha256,
                timestamp=timezone.now(),
                purpose="Integrity verification failed",
            )

        return valid
