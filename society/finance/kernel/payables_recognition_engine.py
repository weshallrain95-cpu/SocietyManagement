from decimal import Decimal

from society.finance.kernel.posting_engine import post_transaction

from society.domain_services.payables.account_mapping import (
    resolve_expense_account,
)

from society.models import (
    ChartOfAccount,
    Transaction,
    VendorBill,
)


class PayablesRecognitionError(Exception):
    """Raised when a vendor bill cannot be recognized."""


def recognize_vendor_bill(
    *,
    vendor_bill: VendorBill,
    vendor_payable_account: ChartOfAccount,
) -> Transaction:

    """
    Finance Reconstruction FR001

    Recognizes an approved Vendor Bill using accrual accounting.

    Accounting:

        Dr Expense
        Cr Vendor Payable

    This engine deliberately does NOT:
        - create VendorPayment
        - reduce bank
        - update outstanding balances
        - settle liabilities

    It ONLY recognizes the liability.
    """

    # ---------------------------------------------------------
    # Business Validation
    # ---------------------------------------------------------

    if vendor_bill is None:
        raise PayablesRecognitionError("Vendor Bill is required.")

    if vendor_bill.amount <= Decimal("0"):
        raise PayablesRecognitionError(
            "Vendor Bill amount must be greater than zero."
        )

    # A payable must already exist for an approved bill.
    if not hasattr(vendor_bill, "payable"):
        raise PayablesRecognitionError(
            "Vendor Bill has no payable record."
        )

    payable = vendor_bill.payable

    if payable.amount != vendor_bill.amount:
        raise PayablesRecognitionError(
            "Vendor Bill and Vendor Payable amounts do not match."
        )

    # ---------------------------------------------------------
    # FR001 continues in Step 5
    # ---------------------------------------------------------

    authorization = vendor_bill.expense_authorization

    if authorization is None:

        raise PayablesRecognitionError(
            "Vendor Bill is not linked to an Expense Authorization."
        )

    expense_account = resolve_expense_account(
        society=vendor_bill.society,
        expense_category=authorization.expense_category,
    )
    
    transaction = post_transaction(
        society=vendor_bill.society,
        transaction_type="ADJUSTMENT",
        reference_type="VENDOR_INVOICE",
        reference_id=str(vendor_bill.id),
        description=f"Vendor Invoice - {vendor_bill.vendor.name}",
        idempotency_key=f"vendor-invoice-{vendor_bill.id}",
        entries=[
            {
                "account": expense_account,
                "type": "DEBIT",
                "amount": vendor_bill.amount,
            },
            {
                "account": vendor_payable_account,
                "type": "CREDIT",
                "amount": vendor_bill.amount,
            },
        ],
    )

    return transaction

    