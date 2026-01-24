# society/legal/disputes/cases/services/claim_service.py

from society.legal.disputes.cases.models.claim import LegalClaim
from society.legal.disputes.cases.models.case import LegalCase
from society.legal.disputes.cases.models.party import LegalParty


# ============================
# Claim Service
# ============================

class ClaimService:
    """
    Manages legal claims.
    """

    def file_claim(
        self,
        case: LegalCase,
        claimant: LegalParty,
        respondent: LegalParty,
        title: str,
        description: str,
        legal_basis: dict,
        relief_sought: str,
    ) -> LegalClaim:

        claim = LegalClaim.objects.create(
            case=case,
            claimant=claimant,
            respondent=respondent,
            title=title,
            description=description,
            legal_basis=legal_basis,
            relief_sought=relief_sought,
            status="FILED",
        )

        return claim

    def resolve_claim(self, claim: LegalClaim):
        claim.status = "RESOLVED"
        claim.save()
        return claim
