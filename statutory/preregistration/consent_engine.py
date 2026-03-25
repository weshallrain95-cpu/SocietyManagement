import uuid

from statutory.models import SocietyConsent
from society.models import Flat, FlatOwnership, FlatOwner


class ConsentEngine:

    @staticmethod
    def initialize_requests(society):

        flats = Flat.objects.filter(society=society)

        created = 0

        for flat in flats:

            ownership = FlatOwnership.objects.filter(
                flat=flat,
                is_active=True
            ).first()

            if not ownership:
                continue

            owner_link = FlatOwner.objects.filter(
                ownership=ownership
            ).select_related("person").first()

            if not owner_link:
                continue

            owner = owner_link.person

            obj, was_created = SocietyConsent.objects.get_or_create(
                society=society,
                flat=flat,
                defaults={
                    "owner": owner,
                    "token": uuid.uuid4().hex
                }
            )

            if was_created:
                created += 1

        return created


    @staticmethod
    def consent_percentage(society):

        total_flats = Flat.objects.filter(society=society).count()

        approved = SocietyConsent.objects.filter(
            society=society,
            status="APPROVED"
        ).count()

        if total_flats == 0:
            return 0

        return (approved / total_flats) * 100
        