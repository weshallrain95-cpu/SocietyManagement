# society/legal/disputes/cases/services/party_service.py

from society.legal.disputes.cases.models.party import LegalParty


# ============================
# Party Service
# ============================

class PartyService:
    """
    Manages legal parties.
    """

    def register_party(
        self,
        name: str,
        party_type: str,
        entity_ref: str = None,
        contact_info: dict = None,
        legal_capacity: str = "FULL",
        authority_role: str = None,
    ) -> LegalParty:

        party = LegalParty.objects.create(
            name=name,
            party_type=party_type,
            entity_ref=entity_ref,
            contact_info=contact_info or {},
            legal_capacity=legal_capacity,
            authority_role=authority_role,
        )

        return party
