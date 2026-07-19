"""
==========================================================
SocietyOS
Vendor Bill Factory
==========================================================

Purpose
-------

Creates Vendor Bills from an approved
Expense Authorization and invoice payload.

This factory owns Vendor Bill creation.

It does NOT:

• create Vendor Payables
• recognize accounting
• post journals
• perform workflow transitions
"""

from __future__ import annotations

from society.models import (
    ExpenseAuthorization,
    Vendor,
    VendorBill,
)


class VendorBillFactoryError(Exception):
    """
    Raised when a Vendor Bill cannot
    be created.
    """
    pass


def create_vendor_bill(
    *,
    authorization: ExpenseAuthorization,
    payload: dict,
) -> VendorBill:
    """
    Creates a Vendor Bill linked to the
    originating Expense Authorization.
    """

    required_fields = (
        "vendor_id",
        "bill_number",
        "bill_date",
        "amount",
    )

    missing = [
        field
        for field in required_fields
        if field not in payload
    ]

    if missing:
        raise VendorBillFactoryError(
            "Missing invoice data: "
            + ", ".join(missing)
        )
    
    vendor = Vendor.objects.get(
        pk=payload["vendor_id"],
    )

    return VendorBill.objects.create(
        society=authorization.society,
        expense_authorization=authorization,
        vendor=vendor,
        bill_number=payload["bill_number"],
        bill_date=payload["bill_date"],
        description=payload.get(
            "description",
            "",
        ),
        amount=payload["amount"],
    )