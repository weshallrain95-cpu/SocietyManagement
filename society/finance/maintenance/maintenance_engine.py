from decimal import Decimal

from society.models import Flat, MaintenanceCharge


def calculate_flat_maintenance(flat):

    charges = MaintenanceCharge.objects.filter(
        society=flat.society,
        is_active=True,
    )

    total = Decimal("0.00")

    rows = []

    for charge in charges:

        amount = Decimal("0.00")

        if charge.basis == "EQUAL":

            amount = charge.rate

        elif charge.basis == "AREA":

            amount = flat.area * charge.rate

        rows.append({
            "charge": charge.name,
            "amount": amount,
        })

        total += amount

    return rows, total

from decimal import Decimal

from society.models import Flat, MaintenanceCharge
from society.finance.maintenance.rule_engine import MaintenanceRuleEngine


def calculate_flat_maintenance(flat):

    charges = MaintenanceCharge.objects.filter(
        society=flat.society,
        is_active=True,
    )

    rows = []
    total = Decimal("0.00")

    for charge in charges:

        engine = MaintenanceRuleEngine(flat, charge)

        amount = engine.calculate()

        rows.append({
            "charge_code": charge.code,
            "charge_name": charge.name,
            "amount": str(amount),
        })

        total += amount

    return rows, total

