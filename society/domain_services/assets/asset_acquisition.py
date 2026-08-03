"""
==========================================================
SocietyOS Asset Acquisition Engine

Purpose
-------
Determines whether an Asset is eligible to enter the
Society Asset Register based on its acquisition mode.

The Acquisition Engine DOES NOT create Assets.

Creation is delegated exclusively to Asset Factory.

Flow

acquire_asset()

        │

        ▼

_validate_acquisition_mode()

        │

        ▼

_validate_required_fields()

        │

        ▼

create_asset()

        │

        ▼

return Asset
==========================================================
"""

from __future__ import annotations

from typing import Any

from decimal import Decimal
from datetime import date

from django.db import transaction

from society.domain_services.assets.asset_factory import (
    create_asset,
)

from society.domain_services.assets.asset_valuation import (
    ORIGINAL_COST,
    OPENING_BALANCE,
    FAIR_VALUE,
    create_asset_valuation,
)

# ==========================================================
# Acquisition Modes
# ==========================================================

PURCHASED = "PURCHASED"

BUILDER_HANDOVER = "BUILDER_HANDOVER"

CONSTRUCTED = "CONSTRUCTED"

DONATION = "DONATION"

LEGACY = "LEGACY"

ACQUISITION_MODES = {
    PURCHASED: {
        "required": [
            "vendor",
            "purchase_date",
            "valuation_amount",
        ],
    },
    BUILDER_HANDOVER: {
        "required": [
            "builder",
            "handover_date",
            "valuation_amount",
        ],
    },
    CONSTRUCTED: {
        "required": [
            "completion_date",
            "valuation_amount",
        ],
    },
    DONATION: {
        "required": [
            "donor",
            "donation_date",
            "valuation_amount",
        ],
    },
    LEGACY: {
        "required": [
            "migration_date",
            "valuation_amount",
        ],
    },
}

# ==========================================================
# Exceptions
# ==========================================================


class AssetAcquisitionError(Exception):
    """Base Acquisition exception."""
    pass


class InvalidAcquisitionModeError(AssetAcquisitionError):
    """Unsupported acquisition mode."""
    pass


class AcquisitionValidationError(AssetAcquisitionError):
    """Missing mandatory acquisition information."""
    pass


# ==========================================================
# Validation
# ==========================================================


def _validate_acquisition_mode(
    acquisition_mode: str,
) -> None:
    """
    Ensures acquisition mode is supported.
    """

    if acquisition_mode not in ACQUISITION_MODES:

        raise InvalidAcquisitionModeError(
            f"Unsupported acquisition mode '{acquisition_mode}'."
        )


def _validate_required_fields(
    *,
    acquisition_mode: str,
    acquisition_data: dict[str, Any],
) -> None:
    """
    Validates mandatory information for
    the selected acquisition mode.
    """

    required = ACQUISITION_MODES[
        acquisition_mode
    ]["required"]

    for field in required:

        value = acquisition_data.get(field)

        if value in (
            None,
            "",
        ):

            raise AcquisitionValidationError(
                f"'{field}' is required for "
                f"{acquisition_mode} assets."
            )


def _validate_acquisition(
    *,
    acquisition_mode: str,
    acquisition_data: dict[str, Any],
) -> None:
    """
    Performs complete acquisition validation.
    """

    _validate_acquisition_mode(
        acquisition_mode,
    )

    _validate_required_fields(
        acquisition_mode=acquisition_mode,
        acquisition_data=acquisition_data,
    )


# ==========================================================
# Valuation Mapping
# ==========================================================


def _valuation_type_for_acquisition(
    acquisition_mode: str,
) -> str:
    """
    Determines the initial valuation type
    based on acquisition mode.
    """

    mapping = {
        PURCHASED: ORIGINAL_COST,
        CONSTRUCTED: ORIGINAL_COST,
        BUILDER_HANDOVER: OPENING_BALANCE,
        LEGACY: OPENING_BALANCE,
        DONATION: FAIR_VALUE,
    }

    return mapping[acquisition_mode]


# ==========================================================
# Public API
# ==========================================================


def acquire_asset(
    *,
    acquisition_mode: str,
    acquisition_data: dict[str, Any],
    society,
    asset_type: str,
    name: str,
    manufacturer=None,
    serial_number=None,
    installed_on=None,
    wing=None,
    floor=None,
    flat=None,
):
    """
    Validates Asset acquisition before allowing
    the Asset to enter the Society Asset Register.

    Asset creation is delegated entirely to
    Asset Factory.
    """

    #
    # Validate business legitimacy.
    #

    _validate_acquisition(
        acquisition_mode=acquisition_mode,
        acquisition_data=acquisition_data,
    )

    valuation_amount = Decimal(
        acquisition_data["valuation_amount"]
    )

    valuation_date = acquisition_data.get(
        "valuation_date",
        date.today(),
    )

    valuation_type = _valuation_type_for_acquisition(
        acquisition_mode,
    )

    #
    # Acquire Asset + Valuation atomically.
    #

    with transaction.atomic():

        asset = create_asset(
            society=society,
            asset_type=asset_type,
            name=name,
            manufacturer=manufacturer,
            serial_number=serial_number,
            installed_on=installed_on,
            wing=wing,
            floor=floor,
            flat=flat,
        )

        create_asset_valuation(
            asset=asset,
            valuation_type=valuation_type,
            amount=valuation_amount,
            valuation_date=valuation_date,
            remarks=acquisition_data.get(
                "remarks",
                "",
            ),
        )

        return asset


__all__ = [
    "PURCHASED",
    "BUILDER_HANDOVER",
    "CONSTRUCTED",
    "DONATION",
    "LEGACY",
    "acquire_asset",
]