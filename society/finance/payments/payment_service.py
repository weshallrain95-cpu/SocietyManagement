from decimal import Decimal
from django.utils import timezone
from django.db import transaction

from society.models import (
    MemberReceivable,
    PaymentTransaction,
    PaymentReceipt,
    ChartOfAccount,
    BankAccount,
)

from society.finance.kernel.posting_engine import post_transaction


@transaction.atomic
def record_member_payment(
    receivable_id,
    amount,
    payment_method,
    bank_account_id=None,
    receivable_account_code="MEMBER_RECEIVABLE",  # NEW
    reference_number=None
):
    """
    🧠 Member Payment Flow (V2 - Fully Integrated)

    Steps:
    1. Validate input
    2. Create PaymentTransaction (business record)
    3. Update MemberReceivable
    4. Post accounting entry (double-entry)
    5. Generate receipt

    Accounting:
    DEBIT  → BankAccount (asset increases)
    CREDIT → Member Receivable (asset reduces)
    """

    # ==============================
    # 🔍 Fetch receivable
    # ==============================
    try:
        receivable = MemberReceivable.objects.get(id=receivable_id)
    except MemberReceivable.DoesNotExist:
        raise Exception("❌ Invalid receivable_id")

    amount = Decimal(amount)

    if amount <= 0:
        raise ValueError("Payment amount must be greater than zero")

    if amount > receivable.outstanding_amount:
        raise ValueError("Payment exceeds outstanding amount")

    # ==============================
    # 💳 Create payment transaction
    # ==============================
    payment = PaymentTransaction.objects.create(
        society=receivable.society,
        flat=receivable.flat,
        receivable=receivable,
        amount=amount,
        payment_method=payment_method,
        reference_number=reference_number or "",
        payment_date=timezone.now(),
    )

    # ==============================
    # 📉 Update receivable
    # ==============================
    receivable.outstanding_amount -= amount

    if receivable.outstanding_amount == 0:
        receivable.status = "PAID"
    else:
        receivable.status = "PARTIAL"

    receivable.save()

    # ==============================
    # 🧾 ACCOUNTING ENTRY (V2 ENGINE)
    # ==============================

    if not bank_account_id:
        raise Exception("❌ bank_account_id is required")

    try:
        bank_account = BankAccount.objects.get(
            id=bank_account_id,
            society=receivable.society
        )
    except BankAccount.DoesNotExist:
        raise Exception("❌ Invalid bank_account_id for this society")

    try:
        receivable_account = ChartOfAccount.objects.get(
            society=receivable.society,
            code=receivable_account_code
        )
    except ChartOfAccount.DoesNotExist:
        raise Exception(f"❌ Invalid receivable account: {receivable_account_code}")

    post_transaction(
        society=receivable.society,
        transaction_type="PAYMENT",
        reference_type="MEMBER_PAYMENT",
        reference_id=f"PAY-{payment.id}",
        description=f"Member payment ({payment_method})",
        entries=[
            {
                "account": bank_account.chart_account,
                "type": "DEBIT",
                "amount": amount,
                "flat": receivable.flat
            },
            {
                "account": receivable_account,
                "type": "CREDIT",
                "amount": amount,
                "flat": receivable.flat
            },
        ],
    )

    # ==============================
    # 🧾 Generate receipt
    # ==============================
    receipt_number = f"RCPT-{payment.id:06d}"

    receipt = PaymentReceipt.objects.create(
        society=receivable.society,
        payment=payment,
        receipt_number=receipt_number,
        amount=amount,
    )
    
    return {
        "payment": payment,
        "receipt": receipt,
        "remaining_balance": receivable.outstanding_amount,
    }
