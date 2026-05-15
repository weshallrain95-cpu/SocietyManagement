from rest_framework.decorators import api_view
from rest_framework.response import Response

from society.models import Society, ChartOfAccount
from society.finance.kernel.coa_seed import seed_core_coa
from society.models import BankAccount


@api_view(["GET"])
def financial_onboarding_state(request):

    society_id = request.GET.get("society_id")

    if not society_id:
        return Response(
            {"error": "society_id required"},
            status=400
        )

    try:
        society = Society.objects.get(id=society_id)

    except Society.DoesNotExist:
        return Response(
            {"error": "Society not found"},
            status=404
        )

    # 🔥 COA INITIALIZATION GUARD
    has_coa = ChartOfAccount.objects.filter(
        society=society
    ).exists()

    if not has_coa:
        seed_core_coa(society)

    # 🔹 TEMP ONBOARDING STATE
    # 🔹 STEP 1 — BANK ACCOUNT COMPLETION
    bank_completed = BankAccount.objects.filter(
        society=society,
        is_active=True
    ).exists()

    data = {

        # STEP 1
        "can_setup_bank": True,
        "bank_completed": bank_completed,

        # STEP 2
        "can_setup_income": bank_completed,
        "income_completed": False,

        # STEP 3
        "can_setup_expense": False,
        "expense_completed": False,

        # STEP 4
        "can_setup_investments": False,
        "investments_completed": False,

        # STEP 5
        "can_setup_opening": False,
        "opening_completed": False,

        # STEP 6
        "can_activate": False,
        "is_active": False,
    }

    return Response(data)