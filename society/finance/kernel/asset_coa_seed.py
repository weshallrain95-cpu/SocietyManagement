from django.db import transaction

from society.finance.kernel.account_factory import (
    get_or_create_account,
)

from society.domain_services.assets.asset_categories import (
    ASSET_CATEGORY_REGISTRY,
)

ROOT_ASSET_ACCOUNTS = [

    {
        "code": "FIXED_ASSETS",
        "name": "Fixed Assets",
        "account_type": "ASSET",
        "account_category": "FIXED_ASSET",
        "is_postable": False,
    },

    {
        "code": "CAPITAL_WORK_IN_PROGRESS",
        "name": "Capital Work In Progress",
        "account_type": "ASSET",
        "account_category": "FIXED_ASSET",
    },

    {
        "code": "ACCUMULATED_DEPRECIATION",
        "name": "Accumulated Depreciation",
        "account_type": "ASSET",
        "account_category": "CONTRA_ASSET",
    },

]

@transaction.atomic
def seed_asset_coa(society):

    #
    # Seed accounting root accounts.
    #

    for account in ROOT_ASSET_ACCOUNTS:

        get_or_create_account(
            society=society,
            code=account["code"],
            name=account["name"],
            account_type=account["account_type"],
            account_category=account["account_category"],
            is_postable=account.get(
                "is_postable",
                True,
            ),
            requires_entity=False,
        )

    #
    # Seed one ledger per registered asset category.
    #

    for category in ASSET_CATEGORY_REGISTRY.values():

        definition = category["definition"]

        get_or_create_account(
            society=society,
            code=definition["code"],
            name=definition["name"],
            account_type="ASSET",
            account_category="FIXED_ASSET",
            is_postable=True,
            requires_entity=False,
        )

    return True
