# ==========================================================
# 🧠 SCR30 FINANCIAL GOVERNANCE CONTEXT ENGINE
# ==========================================================
# Date: 2026-05-12
#
# Purpose:
# Builds unified financial governance context for SCR30.
#
# SCR30 is NOT a fresh onboarding screen.
# It is a consolidation + operationalization layer that:
#
# - Reads previously captured onboarding decisions
# - Detects operational financial truth
# - Hydrates receivable heads intelligently
# - Infers operational billing behavior
# - Detects missing mandatory financial configuration
#
# This engine acts as the single intelligence layer for:
# - auto-selection
# - auto-hydration
# - operational recommendations
# - mandatory configuration detection
#
# IMPORTANT:
# SCR30 must NEVER depend on isolated hardcoded assumptions.
# All intelligence should flow through this context builder.
#
# ==========================================================
from society.models import OperationalRule
from society.models import (
    Society,
    MaintenanceCharge,
    FlatOccupancy,
    ParkingSlot,
    Amenity,
    BillingRule,
)

# ==========================================================
# 🧠 MAIN CONTEXT BUILDER
# ==========================================================

def build_scr30_financial_context(*, society_id):

    society = Society.objects.get(id=society_id)

    # ======================================================
    # OPERATIONAL RULES
    # ======================================================

    operational_rules = OperationalRule.objects.filter(
        society_id=society_id
    ).first()

    billing_rules = BillingRule.objects.filter(
        society_id=society_id,
        is_active=True,
    ).first()

    charges = []

    # ======================================================
    # BASE CONTEXT
    # ======================================================

    context = {
        "society_id": society.id,
        "society_name": society.name,

        # ==================================================
        # DISCOVERED OPERATIONAL TRUTH
        # ==================================================
        "maintenance_detected": False,
        "parking_detected": False,
        "amenities_detected": False,
        "rental_occupancy_detected": False,

        # ==================================================
        # GOVERNANCE / BILLING INTELLIGENCE
        # ==================================================
        "billing_target": None,
        "vacant_policy": None,

        "dispute_enabled": False,
        "dispute_hold_bill": False,
        "dispute_apply_interest": False,

        "approval_mode": None,
        "waiver_authority": None,
        "manager_enabled": False,

        # ==================================================
        # BILLING ENGINE
        # ==================================================
        "billing_cycle": None,
        "billing_start_date": None,
        "due_day": None,
        "grace_days": None,

        "interest_rules": {},
        "penalty_rules": {},

        # ==================================================
        # HYDRATED REVENUE HEADS
        # ==================================================
        "hydrated_heads": [],

        # ==================================================
        # USER ACTION REQUIRED
        # ==================================================
        "missing_mandatory_heads": [],
        "recommended_heads": [],

        # ==================================================
        # DEBUG / TRACEABILITY
        # ==================================================
        "debug": {},
    }

    # ======================================================
    # GOVERNANCE + OPERATIONAL RULE HYDRATION
    # ======================================================

    if operational_rules:

        context["billing_target"] = getattr(
            operational_rules,
            "billing_target",
            None,
        )

        context["vacant_policy"] = getattr(
            operational_rules,
            "vacant_type",
            None,
        )

        # --------------------------------------------------
        # DISPUTE GOVERNANCE
        # --------------------------------------------------

        context["dispute_enabled"] = getattr(
            operational_rules,
            "dispute_enabled",
            False,
        )

        context["dispute_hold_bill"] = getattr(
            operational_rules,
            "dispute_hold_bill",
            False,
        )

        context["dispute_apply_interest"] = getattr(
            operational_rules,
            "dispute_apply_interest",
            False,
        )

        if context["dispute_apply_interest"]:

            context["recommended_heads"].append({
                "code": "INTEREST_ON_DUES",
                "reason":
                    "Interest applicable on disputed dues",
            })

        # --------------------------------------------------
        # VACANT POLICY
        # --------------------------------------------------

        if context["vacant_policy"] == "FULL":

            context["recommended_heads"].append({
                "code": "VACANT_FLAT_CHARGES",
                "reason":
                    "Full vacant recovery policy configured",
            })

    # ======================================================
    # BILLING RULE HYDRATION
    # ======================================================

    if billing_rules:

        context["billing_cycle"] = getattr(
            billing_rules,
            "billing_cycle",
            None,
        )

        context["billing_start_date"] = getattr(
            billing_rules,
            "billing_start_date",
            None,
        )

        context["due_day"] = getattr(
            billing_rules,
            "due_day",
            None,
        )

        context["grace_days"] = getattr(
            billing_rules,
            "grace_days",
            None,
        )

        context["interest_rules"] = getattr(
            billing_rules,
            "interest_rules",
            {},
        ) or {}

        context["penalty_rules"] = getattr(
            billing_rules,
            "penalty_rules",
            {},
        ) or {}

        # --------------------------------------------------
        # INTEREST DETECTION
        # --------------------------------------------------

        if context["interest_rules"].get("enabled"):

            context["recommended_heads"].append({
                "code": "INTEREST_ON_DUES",
                "reason":
                    "Interest recovery configured in billing rules",
            })

        # --------------------------------------------------
        # PENALTY DETECTION
        # --------------------------------------------------

        if context["penalty_rules"].get("enabled"):

            context["recommended_heads"].append({
                "code": "LATE_PAYMENT_PENALTY",
                "reason":
                    "Late payment penalty configured",
            })

        # --------------------------------------------------
        # CHARGE DETECTION
        # --------------------------------------------------

        charges = getattr(
            billing_rules,
            "charges",
            [],
        ) or []

        for charge in charges:

            subtype = charge.get("subtype")

            if subtype:

                context["recommended_heads"].append({
                    "code": subtype,
                    "reason":
                        "Detected from billing rule charges",
                })

    # ======================================================
    # MAINTENANCE DETECTION
    # ======================================================

    maintenance_charges = MaintenanceCharge.objects.filter(
        society_id=society_id,
        is_active=True,
    )

    if maintenance_charges.exists():

        context["maintenance_detected"] = True

        for charge in maintenance_charges.exclude(
            code__in=[
                "INTEREST_ON_DUES",
                "LATE_PAYMENT",
                "CHEQUE_BOUNCE",
                "TRANSFER_FEES",
                "TRANSFER_PREMIUM",
                "FESTIVAL_CONTRIBUTIONS",
            ]
        ):

            matching_charge = next(
                (
                    item
                    for item in charges
                    if item.get("subtype") == charge.code
                ),
                {},
            )

            context["hydrated_heads"].append({

                # ==================================================
                # CORE
                # ==================================================

                "code": charge.code,

                "name": charge.name,

                "basis":
                    matching_charge.get(
                        "basis",
                        charge.basis,
                    ),

                "rate":
                    str(
                        matching_charge.get(
                            "amount",
                            charge.rate,
                        )
                    ),

                "mandatory":
                    matching_charge.get(
                        "mandatory",
                        True,
                    ),

                "source": "MaintenanceCharge",

                "auto_enabled": True,

                "editable": True,

                # ==================================================
                # COMMERCIAL MONETIZATION
                # ==================================================

                "revenueModel":
                    matching_charge.get(
                        "revenue_model",
                        "",
                    ),

                "monthlyValue":
                    matching_charge.get(
                        "monthly_value",
                        "",
                    ),

                "agreementExists":
                    matching_charge.get(
                        "agreement_exists",
                        False,
                    ),

                # ==================================================
                # AMENITIES
                # ==================================================

                "accessType":
                    matching_charge.get(
                        "access_type",
                        "",
                    ),

                "pricingModel":
                    matching_charge.get(
                        "pricing_model",
                        "",
                    ),

                "usageFee":
                    matching_charge.get(
                        "usage_fee",
                        "",
                    ),

                # ==================================================
                # TREASURY
                # ==================================================

                "instrumentType":
                    matching_charge.get(
                        "instrument_type",
                        "",
                    ),

                "institution":
                    matching_charge.get(
                        "institution",
                        "",
                    ),

                "principalValue":
                    matching_charge.get(
                        "principal_value",
                        "",
                    ),

                "currentValue":
                    matching_charge.get(
                        "current_value",
                        "",
                    ),

                "yieldPercent":
                    matching_charge.get(
                        "yield_percent",
                        "",
                    ),

                "principalLinked":
                    matching_charge.get(
                        "principal_linked",
                        False,
                    ),

                "depositDate":
                    matching_charge.get(
                        "deposit_date",
                        "",
                    ),

                "maturityDate":
                    matching_charge.get(
                        "maturity_date",
                        "",
                    ),

                "renewalMode":
                    matching_charge.get(
                        "renewal_mode",
                        "",
                    ),

                "payoutType":
                    matching_charge.get(
                        "payout_type",
                        "",
                    ),

                "prematureWithdrawalAllowed":
                    matching_charge.get(
                        "premature_withdrawal_allowed",
                        False,
                    ),
            })

    
    # ======================================================
    # FLEXIBLE BILLING RULE HYDRATION
    # ======================================================

    hydrated_codes = {
        item["code"]
        for item in context["hydrated_heads"]
    }

    for charge in charges:

        subtype = charge.get("subtype")

        if not subtype:
            continue

        # --------------------------------------------------
        # ALREADY HYDRATED
        # --------------------------------------------------

        if subtype in hydrated_codes:
            continue

        context["hydrated_heads"].append({

            # ==================================================
            # CORE
            # ==================================================

            "code": subtype,
            "name": subtype.replace(
            "_",
                " "
            ).title(),

            "basis":
                charge.get("basis", ""),

            "rate":
                str(
                    charge.get(
                        "amount",
                        ""
                    )
                ),

            "mandatory":
                charge.get(
                    "mandatory",
                    False,
                ),

            "source":
                "BillingRule",

            "auto_enabled":
                True,

            "editable":
                True,

            # ==================================================
            # COMMERCIAL MONETIZATION
            # ==================================================

            "revenueModel":
                charge.get(
                    "revenue_model",
                    "",
                ),

            "monthlyValue":
                charge.get(
                    "monthly_value",
                    "",
                ),

            "agreementExists":
                charge.get(
                    "agreement_exists",
                    False,
                ),

            # ==================================================
            # AMENITIES
            # ==================================================

            "accessType":
                charge.get(
                    "access_type",
                    "",
                ),

            "pricingModel":
                charge.get(
                    "pricing_model",
                    "",
                ),

            "usageFee":
                charge.get(
                    "usage_fee",
                    "",
                ),

            # ==================================================
            # TREASURY
            # ==================================================

            "instrumentType":
                charge.get(
                    "instrument_type",
                    "",
                ),

            "institution":
                charge.get(
                    "institution",
                    "",
                ),

            "principalValue":
                charge.get(
                    "principal_value",
                    "",
                ),

            "currentValue":
                charge.get(
                    "current_value",
                    "",
                ),

            "yieldPercent":
                charge.get(
                    "yield_percent",
                    "",
                ),
        })

    context["debug"]["maintenance_charge_count"] = (
        maintenance_charges.count()
    )

    # ======================================================
    # RENTAL / NON OCCUPANCY DETECTION
    # ======================================================

    rented_exists = FlatOccupancy.objects.filter(
        flat__society_id=society_id,
        occupancy_type="RENTED",
    ).exists()

    if rented_exists:

        context["rental_occupancy_detected"] = True

        context["recommended_heads"].append({
            "code": "NON_OCCUPANCY",
            "reason":
                "Rented flats detected in occupancy declarations",
        })

    # ======================================================
    # PARKING DETECTION
    # ======================================================

    parking_exists = ParkingSlot.objects.filter(
        society_id=society_id
    ).exists()

    if parking_exists:

        context["parking_detected"] = True

        context["recommended_heads"].append({
            "code": "PARKING_CHARGES",
            "reason":
                "Parking infrastructure detected",
        })

    context["debug"]["parking_detected"] = parking_exists

    # ======================================================
    # AMENITY DETECTION
    # ======================================================

    amenities = Amenity.objects.filter(
        society_id=society_id
    )

    if amenities.exists():

        context["amenities_detected"] = True

        for amenity in amenities:

            context["recommended_heads"].append({
                "code": amenity.name.upper().replace(" ", "_"),
                "reason":
                    f"{amenity.name} amenity detected",
            })

    context["debug"]["amenity_count"] = amenities.count()

    # ======================================================
    # MANDATORY HEAD DETECTION
    # ======================================================

    mandatory_codes = [
        "SERVICE_CHARGES",
        "REPAIR_FUND",
    ]

    hydrated_codes = {
        h["code"]
        for h in context["hydrated_heads"]
    }

    for code in mandatory_codes:

        if code not in hydrated_codes:

            context["missing_mandatory_heads"].append({
                "code": code,
                "reason":
                    "Required for operational billing engine",
            })

    # ======================================================
    # FINAL DEBUG
    # ======================================================

    context["debug"]["hydrated_head_count"] = len(
        context["hydrated_heads"]
    )

    context["debug"]["recommended_head_count"] = len(
        context["recommended_heads"]
    )
    
    context["debug"]["billing_rules_detected"] = (
        billing_rules is not None
    )
    
    context["debug"]["missing_mandatory_count"] = len(
        context["missing_mandatory_heads"]
    )

    return context