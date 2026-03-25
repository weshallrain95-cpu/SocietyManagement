from decimal import Decimal
from django.utils import timezone

from society.models import (
    MemberReceivable,
    PaymentTransaction,
    PaymentReceipt,
)


def record_member_payment(
    receivable_id,
    amount,
    payment_method,
    reference_number=None
):

    receivable = MemberReceivable.objects.get(id=receivable_id)

    amount = Decimal(amount)

    if amount <= 0:
        raise ValueError("Payment amount must be greater than zero")

    if amount > receivable.outstanding_amount:
        raise ValueError("Payment exceeds outstanding amount")

    # Create payment transaction
    payment = PaymentTransaction.objects.create(
        society=receivable.society,
        flat=receivable.flat,
        receivable=receivable,
        amount=amount,
        payment_method=payment_method,
        reference_number=reference_number or "",
        payment_date=timezone.now(),
    )

    # Update receivable
    receivable.outstanding_amount -= amount

    if receivable.outstanding_amount == 0:
        receivable.status = "PAID"
    else:
        receivable.status = "PARTIAL"

    receivable.save()

    # Generate receipt
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
    