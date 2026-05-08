from collections import defaultdict

from rest_framework.decorators import api_view
from rest_framework.response import Response

from society.models import LedgerEntryV2
from society.models import BankAccount


@api_view(["GET"])
def transfer_ledger_view(request):
    
    from society.models import Society

    society = Society.objects.first()

    entries = LedgerEntryV2.objects.filter(
        transaction__society=society,
        transaction__reference_type="INTERNAL_TRANSFER"
    ).select_related("transaction", "account").order_by("-transaction__created_at")

    # 🔥 BANK FILTER (OPTIONAL)
    bank_account_id = request.GET.get("bank_account_id")

    limit = request.GET.get("limit")
    offset = request.GET.get("offset")

    if bank_account_id:
        try:
            bank = BankAccount.objects.get(id=bank_account_id, society=society)
        except BankAccount.DoesNotExist:
            return Response({"error": "Invalid bank_account_id"}, status=400)

        # 🔥 Step 1: find transactions involving this bank
        tx_ids = entries.filter(
            account=bank.chart_account
        ).values_list("transaction_id", flat=True)

        # 🔥 Step 2: fetch ALL entries for those transactions
        entries = entries.filter(transaction_id__in=tx_ids)

    grouped = defaultdict(list)

    for e in entries:
        grouped[e.transaction.reference_id].append({
            "account": e.account.code,
            "type": e.entry_type,
            "amount": float(e.amount),
        })
    
    # 🔥 Running balance (only if bank filter applied)
    running_balance = 0
    
    result = []


    for ref, rows in grouped.items():
        tx = entries.filter(transaction__reference_id=ref).first().transaction

        debit_entry = next((r for r in rows if r["type"] == "DEBIT"), None)
        credit_entry = next((r for r in rows if r["type"] == "CREDIT"), None)

        from_account = credit_entry["account"] if credit_entry else None
        to_account = debit_entry["account"] if debit_entry else None
        amount = debit_entry["amount"] if debit_entry else 0

        # 🔥 Balance logic (only if bank filter active)
        if bank_account_id:
            if from_account == bank.chart_account.code:
                running_balance -= amount
            elif to_account == bank.chart_account.code:
                running_balance += amount

        from datetime import datetime

        from_date = request.GET.get("from_date")
        to_date = request.GET.get("to_date")

        try:
            if from_date:
                from_date_parsed = datetime.strptime(from_date, "%Y-%m-%d").date()
                entries = entries.filter(transaction__created_at__date__gte=from_date_parsed)

            if to_date:
                to_date_parsed = datetime.strptime(to_date, "%Y-%m-%d").date()
                entries = entries.filter(transaction__created_at__date__lte=to_date_parsed)

        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=400)

        result.append({
            "reference_id": ref,
            "transaction_type": tx.transaction_type,
            "created_at": tx.created_at,
            "from_account": from_account,
            "to_account": to_account,
            "amount": amount,
            "balance": running_balance if bank_account_id else None,
        })

        # 🔥 FINAL SORT (guaranteed order)
        result = sorted(
            result,
            key=lambda x: x["created_at"],
            reverse=True  # latest first
        )
        
        # 🔥 Pagination (applied after full result is built)
        if offset:
            offset = int(offset)
        else:
            offset = 0

        if limit:
            limit = int(limit)
            result = result[offset: offset + limit]
        else:
            result = result[offset:]

    return Response(result)