# ==========================================================
# 🧠 SCR30 FINANCIAL CONTEXT API
# ==========================================================
# Date: 2026-05-12
#
# Purpose:
# Exposes unified financial governance context for SCR30.
#
# This endpoint consolidates:
# - governance rules
# - billing rules
# - maintenance heads
# - inferred receivable logic
# - operational financial intelligence
#
# Frontend MUST hydrate from this endpoint instead of
# relying on hardcoded assumptions.
#
# ==========================================================

from rest_framework.decorators import api_view
from rest_framework.response import Response

from society.finance.scr30_context import (
    build_scr30_financial_context
)


@api_view(["GET"])
def scr30_financial_context(request):

    society_id = request.GET.get("society_id")

    if not society_id:
        return Response(
            {
                "error": "society_id is required"
            },
            status=400,
        )

    try:

        context = build_scr30_financial_context(
            society_id=society_id
        )

        return Response(context)

    except Exception as e:

        return Response(
            {
                "error": str(e)
            },
            status=500,
        )