from rest_framework.decorators import api_view
from rest_framework.response import Response
from society.models import ChartOfAccount, Society


@api_view(["GET"])
def get_coa_list(request):

    # 🔥 TEMP: using first society (same pattern as before)
    society = Society.objects.first()

    accounts = ChartOfAccount.objects.filter(
        society=society,
        is_active=True
    ).order_by("account_type", "code")

    result = []

    for a in accounts:
        result.append({
            "id": a.id,
            "code": a.code,
            "name": a.name,
            "account_type": a.account_type,
            "account_category": a.account_category,
            "subtype": a.subtype,
            "is_postable": a.is_postable,
            "requires_entity": a.requires_entity,
            "is_system": a.is_system,
        })

    return Response(result)