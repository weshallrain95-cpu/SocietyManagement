from society.domain_services.payables.account_mapping import (
    resolve_expense_account,
)



def get_expense_account(*, society, subtype):
    """
    Backward-compatibility adapter.

    Translates legacy expense subtype names
    into the canonical Expense Categories
    owned by the Payables Operating Model.

    Business truth lives in:

        payable_categories.py

    Accounting translation lives in:

        account_mapping.py
    """

    return resolve_expense_account(
        society=society,
        expense_category=subtype,
    )