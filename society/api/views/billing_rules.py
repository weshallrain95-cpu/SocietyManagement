from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from society.models import BillingRule, Society


@api_view(["GET"])
def get_billing_rules(request):
    society_id = request.GET.get("society_id")

    if not society_id:
        return Response({"error": "society_id required"}, status=400)

    try:
        rule = BillingRule.objects.get(society_id=society_id)

        return Response({
            "billing_cycle": rule.billing_cycle,
            "billing_start_date": rule.billing_start_date,
            "due_day": rule.due_day,
            "grace_days": rule.grace_days,
            "charges": rule.charges,
            "interest_rules": rule.interest_rules,
            "penalty_rules": rule.penalty_rules,
        })

    except BillingRule.DoesNotExist:
        return Response({
            "message": "No rules found",
            "data": None
        })


@api_view(["POST"])
def save_billing_rules(request):
    data = request.data
    society_id = data.get("society_id")

    if not society_id:
        return Response({"error": "society_id required"}, status=400)

    from django.shortcuts import get_object_or_404
    society = get_object_or_404(Society, id=society_id)

    rule, _ = BillingRule.objects.get_or_create(society=society)

    rule.billing_cycle = data.get("billing_cycle", "MONTHLY")
    rule.billing_start_date = data.get("billing_start_date", "2024-01-01")
    rule.due_day = data.get("due_day", 10)
    rule.grace_days = data.get("grace_days", 5)

    rule.charges = data.get("charges", [])
    rule.interest_rules = data.get("interest_rules", {})
    rule.penalty_rules = data.get("penalty_rules", {})

    rule.save()

    return Response({"message": "Billing rules saved"})