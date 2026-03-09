from society.models import Flat, SocietyMember, Payment
from statutory.preregistration.snapshot import preregistration_readiness_snapshot


class SocietyHealthEngine:
    """
    Computes a simple operational health score for a society.
    Score range: 0 — 100
    """

    def calculate(self, society):

        score = 100
        signals = []

        # --------------------------------
        # 1. Structure
        # --------------------------------

        flats = Flat.objects.filter(society=society)

        if flats.count() == 0:
            score -= 30
            signals.append("Structure not onboarded")

        # --------------------------------
        # 2. Governance
        # --------------------------------

        members = SocietyMember.objects.filter(society=society)

        if members.count() == 0:
            score -= 20
            signals.append("No members registered")

        # --------------------------------
        # 3. Finance
        # --------------------------------

        payments = Payment.objects.filter(society=society)

        if payments.count() == 0:
            score -= 15
            signals.append("No financial activity")

        # --------------------------------
        # 4. Legal readiness
        # --------------------------------

        snapshot = preregistration_readiness_snapshot(society)

        if not snapshot.get("registrar_ready"):
            score -= 15
            signals.append("Pre-registration incomplete")

        # --------------------------------
        # Normalize
        # --------------------------------

        if score < 0:
            score = 0

        return {
            "score": score,
            "signals": signals,
        }


# ------------------------------------------------------
# MODULE LEVEL WRAPPER (used by cockpit)
# ------------------------------------------------------

def calculate_society_health_score(society):

    engine = SocietyHealthEngine()

    result = engine.calculate(society)

    return result["score"]
    