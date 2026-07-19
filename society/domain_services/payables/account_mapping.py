"""
==========================================================
SocietyOS
Expense Category Account Resolver
==========================================================

Purpose
-------

Resolves an operational Expense Category into the
corresponding Chart of Account.

This module owns business-to-accounting translation.

No posting.

No journals.

No transactions.

The Finance Kernel consumes this resolver.
"""

from __future__ import annotations

from society.domain_services.payables import payable_categories

from society.finance.kernel.account_factory import (
    get_or_create_account,
)


class ExpenseAccountResolutionError(Exception):
    """
    Raised when an Expense Category cannot be resolved.
    """
    pass

# ---------------------------------------------------------
# Legacy Compatibility
# ---------------------------------------------------------
#
# These aliases exist only to preserve compatibility with
# older Finance Kernel callers.
#
# Every alias MUST resolve to a canonical Expense Head.
#
# Never map to a child category.
# ---------------------------------------------------------

LEGACY_CATEGORY_ALIASES = {

    "COMMON_ELECTRICITY": "COMMON_AREA_ELECTRICITY",

    "WATER": "WATER_CHARGES",

    "CLEANING": "COMMON_AREA_CLEANING",

    "SECURITY": "SECURITY_AGENCY",

    "REPAIRS": "GENERAL_REPAIRS",

    "SALARY": "SALARIES",

    "PLUMBING": "PLUMBING_MAINTENANCE",

    "INSURANCE": "BUILDING_INSURANCE",

    "MISC_EXPENSE": "OFFICE_SUPPLIES",

}

def find_expense_category(
    *,
    expense_category: str,
):
    """
    Returns the complete operating-model
    definition for an Expense Category.
    """

    # ---------------------------------------------------------
    # PASS 1
    # Exact canonical Head
    # ---------------------------------------------------------

    for value in vars(payable_categories).values():

        if not isinstance(value, dict):
            continue

        heads = value.get("heads")

        if not isinstance(heads, dict):
            continue

        if expense_category in heads:
            return heads[expense_category]

    # ---------------------------------------------------------
    # PASS 2
    # Child category
    # ---------------------------------------------------------

    for value in vars(payable_categories).values():

        if not isinstance(value, dict):
            continue

        heads = value.get("heads")

        if not isinstance(heads, dict):
            continue

        for head in heads.values():

            children = head.get(
                "children",
                {},
            )

            if expense_category in children:
                return head

    # ---------------------------------------------------------
    # PASS 3
    # Legacy aliases
    # ---------------------------------------------------------

    canonical = LEGACY_CATEGORY_ALIASES.get(
        expense_category,
    )

    if canonical:

        return find_expense_category(
            expense_category=canonical,
        )

    raise ExpenseAccountResolutionError(
        f"Unknown Expense Category: {expense_category}"
    )


def resolve_expense_account(
    *,
    society,
    expense_category: str,
):
    """
    Resolves an Expense Category into the
    corresponding Expense Chart of Account.

    Returns
    -------
    ChartOfAccount instance.
    """

    from society.models import ChartOfAccount

    category = find_expense_category(
        expense_category=expense_category,
    )

    accounting = category.get(
        "intelligence",
        {},
    ).get(
        "accounting",
        {},
    )

    coa_code = accounting.get(
        "coa_code",
    )

    if not coa_code:

        raise ExpenseAccountResolutionError(
            f"No COA mapping defined for {expense_category}"
        )

    definition = category.get(
        "definition",
        {},
    )

    business = category.get(
        "intelligence",
        {},
    ).get(
        "business",
        {},
    )

    return get_or_create_account(
        society=society,
        code=coa_code,
        name=definition.get(
            "name",
            expense_category,
        ),
        account_type="EXPENSE",
        account_category="EXPENSE",
        subtype=expense_category,
        is_postable=True,
        requires_entity=business.get(
            "requires_entity",
            False,
        ),
    )


def resolve_vendor_payable_account(
    *,
    society,
):
    """
    Resolves the Vendor Payables control account
    for the given society.

    The account is provisioned during financial
    initialization as COA code 2210.
    """

    from society.models import ChartOfAccount

    try:

        return ChartOfAccount.objects.get(
            society=society,
            code="VENDOR_PAYABLES",
        )

    except ChartOfAccount.DoesNotExist as exc:

        raise ExpenseAccountResolutionError(
            "Vendor Payables control account "
            "has not been provisioned "
            "for this society."
        ) from exc