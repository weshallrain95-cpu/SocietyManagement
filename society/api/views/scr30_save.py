from rest_framework.decorators import api_view
from rest_framework.response import Response

from society.models import (
    Society,
    MaintenanceCharge,
    BillingRule,
    OperationalRule,
)


@api_view(["POST"])
def save_scr30_receivables(request):

    data = request.data

    society_id = data.get("society_id")

    heads = data.get("heads", [])

    billing = data.get("billing", {})

    operational = data.get("operational", {})

    society = Society.objects.get(
        id=society_id
    )

    # ======================================================
    # MAINTENANCE CHARGES
    # ======================================================

    charges_payload = []

    for head in heads:

        MaintenanceCharge.objects.update_or_create(
            society=society,
            code=head["code"],
            defaults={
                "name": head["name"],
                "basis": head.get("basis"),
                "rate": head.get("rate") or 0,
                "is_active": head.get("enabled", False),
            },
        )

        charges_payload.append({

            # ==================================================
            # CORE
            # ==================================================

            "subtype": head["code"],

            "basis": head.get("basis"),

            "amount": head.get("rate") or 0,

            "mandatory":
                head.get("mandatory", False),

            # ==================================================
            # COMMERCIAL MONETIZATION
            # ==================================================

            "revenue_model":
                head.get("revenueModel"),

            "monthly_value":
                head.get("monthlyValue"),

            "agreement_exists":
                head.get("agreementExists"),

            # ==================================================
            # AMENITIES
            # ==================================================

            "access_type":
                head.get("accessType"),

            "pricing_model":
                head.get("pricingModel"),

            "usage_fee":
                head.get("usageFee"),

            # ==================================================
            # TREASURY
            # ==================================================

            "instrument_type":
                head.get("instrumentType"),

            "institution":
                head.get("institution"),

            "principal_value":
                head.get("principalValue"),

            "current_value":
                head.get("currentValue"),

            "yield_percent":
                head.get("yieldPercent"),

            "principal_linked":
                head.get("principalLinked"),

            "deposit_date":
                head.get("depositDate"),

            "maturity_date":
                head.get("maturityDate"),

            "renewal_mode":
                head.get("renewalMode"),

            "payout_type":
                head.get("payoutType"),

            "premature_withdrawal_allowed":
                head.get(
                    "prematureWithdrawalAllowed"
                ),
        })

    # ======================================================
    # BILLING RULES
    # ======================================================

    BillingRule.objects.update_or_create(
        society=society,
        defaults={

            "billing_cycle":
                billing.get(
                    "billing_cycle",
                    "MONTHLY"
                ),

            "due_day":
                billing.get(
                    "due_day",
                    10
                ),

            "grace_days":
                billing.get(
                    "grace_days",
                    5
                ),

            "billing_start_date":
                billing.get(
                    "billing_start_date"
                ),

            "interest_rules":
                billing.get(
                    "interest_rules",
                    {}
                ),

            "penalty_rules":
                billing.get(
                    "penalty_rules",
                    {}
                ),

            "charges":
                charges_payload,

            "is_active": True,
        },
    )

    # ======================================================
    # OPERATIONAL RULES
    # ======================================================

    OperationalRule.objects.update_or_create(
        society=society,
        defaults={

            "billing_target":
                operational.get(
                    "billing_target",
                    "OWNER"
                ),

            "vacant_type":
                operational.get(
                    "vacant_type",
                    "FULL"
                ),

            "dispute_enabled":
                operational.get(
                    "dispute_enabled",
                    False
                ),

            "dispute_hold_bill":
                operational.get(
                    "dispute_hold_bill",
                    False
                ),

            "dispute_apply_interest":
                operational.get(
                    "dispute_apply_interest",
                    False
                ),

            "financial_controls_configured":
                True,

            "is_active":
                True,
        },
    )

    return Response({
        "success": True,
        "message":
            "SCR30 receivables saved successfully",
    })