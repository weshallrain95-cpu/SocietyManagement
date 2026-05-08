from rest_framework.decorators import api_view
from rest_framework.response import Response

from society.models import Society, ChartOfAccount
from society.finance.kernel.coa_seed import seed_core_coa


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
    data = {
        "can_setup_bank": True,
        "bank_completed": False,

        "can_setup_income": False,
        "income_completed": False,

        "can_setup_expense": False,
        "expense_completed": False,

        "can_setup_investments": False,
        "investments_completed": False,

        "can_setup_opening": False,
        "opening_completed": False,

        "can_activate": False,
        "is_active": False,
    }

    return Response(data)