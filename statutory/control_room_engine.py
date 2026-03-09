from society.models import Society, SocietyMember, Flat
from statutory.preregistration.snapshot import preregistration_readiness_snapshot
from statutory.health_engine import SocietyHealthEngine


class ControlRoomEngine:
    """
    Platform-wide operational intelligence layer.
    Aggregates health signals across all societies.
    """

    def build_overview(self):

        societies = Society.objects.all()

        total_societies = societies.count()

        prereg_ready = 0
        prereg_pending = 0
        registered = 0

        alerts = []
        society_health = []

        health_engine = SocietyHealthEngine()

        for society in societies:

            snapshot = preregistration_readiness_snapshot(society)
            health = health_engine.calculate(society)

            # --------------------------------
            # Lifecycle classification
            # --------------------------------

            if society.registration_number:
                registered += 1

            elif snapshot.get("registrar_ready"):
                prereg_ready += 1

            else:
                prereg_pending += 1

            # --------------------------------
            # Governance signal
            # --------------------------------

            members = SocietyMember.objects.filter(society=society)

            if members.count() == 0:
                alerts.append({
                    "society_id": society.id,
                    "society": society.name,
                    "issue": "No members registered"
                })

            # --------------------------------
            # Structure signal
            # --------------------------------

            flats = Flat.objects.filter(society=society)

            if flats.count() == 0:
                alerts.append({
                    "society_id": society.id,
                    "society": society.name,
                    "issue": "Structure not onboarded"
                })

            # --------------------------------
            # Health score alert
            # --------------------------------

            if health["score"] < 60:
                alerts.append({
                    "society_id": society.id,
                    "society": society.name,
                    "issue": "Low health score",
                    "score": health["score"],
                })

            # --------------------------------
            # Track health per society
            # --------------------------------

            society_health.append({
                "society_id": society.id,
                "society": society.name,
                "score": health["score"]
            })

        # --------------------------------
        # Final Control Room Snapshot
        # --------------------------------

        return {
            "total_societies": total_societies,
            "registered_societies": registered,
            "societies_ready_for_registration": prereg_ready,
            "societies_pending_prereg": prereg_pending,
            "society_health": society_health,
            "alerts": alerts,
        }
        