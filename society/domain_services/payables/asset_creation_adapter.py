"""
==========================================================
SocietyOS
Purchase Asset Creation Adapter
==========================================================

Purpose
-------

Bridges the Payables domain to the Asset domain.

Determines whether a completed purchase should
result in an Asset being created.

Asset creation is delegated exclusively to the
Asset Acquisition Engine.
"""

from __future__ import annotations

from society.domain_services.spend.spend_resolver import (
    resolve_spend,
)

from society.domain_services.assets.asset_acquisition import (
    acquire_asset,
)

from society.domain_services.spend.spend_catalog import (
    get_spend_item,
)


def create_asset_from_purchase(
    *,
    authorization,
    vendor_bill,
    asset_details=None,
):
    """
    Creates an Asset from a completed purchase
    when the Spend Item represents an Asset.

    Asset creation is delegated to the
    Asset Acquisition Engine.
    """

    if asset_details is None:
        asset_details = {}

    resolution = resolve_spend(
        operational_domain_code=(
            authorization.operational_domain_code
        ),
        spend_item_code=(
            authorization.spend_item_code
        ),
    )

    spend_item = get_spend_item(
        resolution.spend_item_code
    )

    is_asset_purchase = (
        spend_item.acquisition_type
        == "ASSET"
    )

    if not is_asset_purchase:
        
        return None

    return acquire_asset(
        acquisition_mode="PURCHASED",
        acquisition_data={
            "vendor": vendor_bill.vendor,
            "purchase_date": vendor_bill.bill_date,
            "valuation_amount": vendor_bill.amount,
        },
        society=authorization.society,
        asset_type=spend_item.asset_type,
        name=spend_item.display_name,
        manufacturer=asset_details.get(
            "manufacturer",
        ),
        serial_number=asset_details.get(
            "serial_number",
        ),
        installed_on=asset_details.get(
            "installed_on",
        ),
    )