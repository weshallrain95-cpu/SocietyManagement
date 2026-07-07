from society.models import (
    Society,
    BankAccount,
)

from society.finance.scr30_context import (
    build_scr30_financial_context,
)
from django.http import JsonResponse

from django.views.decorators.http import (
    require_GET,
)

# =====================================================
# SCR34 Maintenance Billing Activation Context
#
# Aggregates all existing platform engines into a
# single orchestration payload for the activation UI.
#
# This function MUST NOT perform business logic.
# It only hydrates previously established engines.
# =====================================================

def build_scr34_context(
    society_id,
):

    society = Society.objects.get(
        id=society_id,
    )

    financial_context = (
        build_scr30_financial_context(
            society_id=society_id,
        )
    )

    bank_accounts = list(

        BankAccount.objects.filter(
            society=society,
            is_active=True,
        )
        .order_by(
            "treasury_role",
            "name",
        )
        .values(

            "id",

            "name",

            "bank_name",

            "account_number",

            "ifsc",

            "upi_id",

            "is_active",
        )

    )

    if len(bank_accounts) == 1:

        selected_account = {

            "selection_required": False,

            "account": bank_accounts[0],
        }

    else:

        selected_account = {

            "selection_required": True,

            "account": None,
        }

    context = {

        "society": {

            "id": society.id,

            "name": society.name,

            "registration_number": getattr(
                society,
                "registration_number",
                "",
            ),
        },

        "communications": {

            "official_email":
                society.official_email,

            "enabled":
                society.communications_enabled,

        },
        
        "billing_policy": {

            "billing_cycle":
                financial_context.get(
                    "billing_cycle",
                ),

            "billing_start_date":
                financial_context.get(
                    "billing_start_date",
                ),

            "due_day":
                financial_context.get(
                    "due_day",
                ),

            "grace_days":
                financial_context.get(
                    "grace_days",
                ),

            "interest_rules":
                financial_context.get(
                    "interest_rules",
                    {},
                ),

            "penalty_rules":
                financial_context.get(
                    "penalty_rules",
                    {},
                ),
        },

        "bank_accounts":
            bank_accounts,

        "selected_account":
            selected_account,

        "preview": {

            "available": False,

            "pdf_url": None,

            "flat_number": None,

            "member_name": None,

            "net_payable": None,

            "billing_month": None,
        },

        "distribution": {

            "email": True,

            "whatsapp": True,

            "sms": False,

            "retry_failed":
                True,
        },

        "readiness": {

            "billing_policy": True,

            "bank_account": len(bank_accounts) > 0,

            "upi": any(
                account.get("upi_id")
                for account in bank_accounts
            ),

            "preview": False,

            "communications": True,

            "scheduler": True,

            "overall_ready": False,
        },

        "automation": {

            "enabled": False,

            "activated_on": None,

            "activated_by": None,
        },
    }

    return context

@require_GET
def scr34_context(request):

    society_id = request.GET.get(
        "society_id",
    )

    context = build_scr34_context(
        society_id=society_id,
    )

    return JsonResponse(
        context,
        safe=False,
    )