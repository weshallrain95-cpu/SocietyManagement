from decimal import Decimal

class MaintenanceRuleEngine:
    """
    Core rule engine that calculates maintenance charges
    for a flat based on configured MaintenanceCharge rules.
    """

    def __init__(self, flat, charge):
        self.flat = flat
        self.charge = charge

    def calculate(self):

        basis = self.charge.basis
        rate = Decimal(self.charge.rate or 0)

        # ---------------------------------------
        # Equal share across all flats
        # ---------------------------------------
        if basis == "EQUAL":
            return rate

        # ---------------------------------------
        # Area based (carpet area)
        # ---------------------------------------
        elif basis == "AREA":

            area = getattr(self.flat, "carpet_area_sqft", None) or 0

            return Decimal(area) * rate

        # ---------------------------------------
        # Per flat fixed charge
        # ---------------------------------------
        elif basis == "PER_FLAT":
            return rate

        # ---------------------------------------
        # Per parking slot
        # ---------------------------------------
        elif basis == "PER_SLOT":

            slots = getattr(self.flat, "parking_slots", 0) or 0

            return Decimal(slots) * rate

        # ---------------------------------------
        # Per water inlet
        # ---------------------------------------
        elif basis == "PER_INLET":

            inlets = getattr(self.flat, "water_inlets", 1) or 1

            return Decimal(inlets) * rate

        # ---------------------------------------
        # Percentage of maintenance
        # (handled at billing stage)
        # ---------------------------------------
        elif basis == "PERCENT_MAINT":

            # calculated later once base maintenance is known
            return Decimal("0.00")

        # ---------------------------------------
        # Manual override
        # ---------------------------------------
        elif basis == "MANUAL":
            return rate

        # ---------------------------------------
        # Unknown rule safety fallback
        # ---------------------------------------
        return Decimal("0.00")

