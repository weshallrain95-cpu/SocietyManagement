# society/legal/disputes/evidence/services/integrity_service.py

import hashlib
from society.legal.disputes.evidence.models.evidence import Evidence


# ============================
# Integrity Service
# ============================

class IntegrityService:
    """
    Validates cryptographic integrity of evidence.
    """

    def compute_hashes(self, raw_bytes: bytes) -> dict:
        return {
            "sha256": hashlib.sha256(raw_bytes).hexdigest(),
            "sha512": hashlib.sha512(raw_bytes).hexdigest(),
        }

    def verify_integrity(self, evidence: Evidence, raw_bytes: bytes) -> bool:
        hashes = self.compute_hashes(raw_bytes)

        return (
            hashes["sha256"] == evidence.hash_sha256 and
            (not evidence.hash_sha512 or hashes["sha512"] == evidence.hash_sha512)
        )
