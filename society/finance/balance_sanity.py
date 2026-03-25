from decimal import Decimal

from society.models import ChartOfAccount


def validate_opening_balances(society, opening_data):
    """
    Validates that opening balances follow accounting equation.

    Assets = Liabilities + Funds

    opening_data example:
    {
        "BANK": 100000,
        "FD": 500000,
        "SINK": -200000
    }
    """

    asset_total = Decimal("0.00")
    liability_total = Decimal("0.00")

    for account_code, amount in opening_data.items():

        account = ChartOfAccount.objects.get(
            society=society,
            code=account_code
        )

        amount = Decimal(amount)

        if account.account_type == "ASSET":

            asset_total += amount

        else:

            liability_total += abs(amount)

    if asset_total != liability_total:

        raise Exception(
            f"Opening balance mismatch.\n"
            f"Assets = {asset_total}\n"
            f"Liabilities/Funds = {liability_total}"
        )

    return True
    