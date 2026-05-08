from society.models import ChartOfAccount


def get_or_create_account(
    *,
    society,
    code,
    name,
    account_type,
    account_category="GENERAL",
    subtype=None,
    is_postable=True,
    requires_entity=False,
):
    """
    Central factory for creating/fetching COA accounts.
    Ensures consistency and prevents duplication.
    """

    obj, created = ChartOfAccount.objects.get_or_create(
        society=society,
        code=code,
        defaults={
            "name": name,
            "account_type": account_type,
            "account_category": account_category,
            "subtype": subtype,
            "is_postable": is_postable,
            "requires_entity": requires_entity,
            "is_system": True,
            "is_active": True,
        },
    )

    return obj