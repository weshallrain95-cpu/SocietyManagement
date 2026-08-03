"""
Asset Valuation Service

Purpose
-------
Creates and manages financial valuation records for society assets.

This service is responsible only for valuation.

It does NOT:

- create assets
- acquire assets
- depreciate assets
- post accounting entries
- perform revaluations

Those responsibilities belong to their respective services.
"""

from __future__ import annotations

from decimal import Decimal
from datetime import date

from django.db import (
    IntegrityError,
    transaction,
)

from society.models import (
    Asset,
    AssetValuation,
)


# ==========================================================
# Exceptions
# ==========================================================


class AssetValuationError(Exception):
    """Base exception for asset valuation."""


class InvalidValuationTypeError(AssetValuationError):
    """Unsupported valuation type."""


class ValuationValidationError(AssetValuationError):
    """Valuation validation failed."""

class DuplicateAssetValuationError(AssetValuationError):
    """Asset already has this valuation type."""


# ==========================================================
# Supported Valuation Types
# ==========================================================

ORIGINAL_COST = "ORIGINAL_COST"

OPENING_BALANCE = "OPENING_BALANCE"

FAIR_VALUE = "FAIR_VALUE"


VALUATION_TYPES = {
    ORIGINAL_COST,
    OPENING_BALANCE,
    FAIR_VALUE,
}


# ==========================================================
# Public API
# ==========================================================


@transaction.atomic
def create_asset_valuation(
    *,
    asset: Asset,
    valuation_type: str,
    amount: Decimal,
    valuation_date: date,
    remarks: str = "",
) -> AssetValuation:
    """
    Creates an opening or subsequent valuation for an asset.

    Public API.
    """

    _validate_valuation_type(
        valuation_type,
    )

    _validate_amount(
        amount,
    )

    _validate_amount(
        amount,
    )

    valuation = _build_valuation(
        asset=asset,
        valuation_type=valuation_type,
        amount=amount,
        valuation_date=valuation_date,
        remarks=remarks,
    )

    try:
        valuation.save()
    except IntegrityError as exc:
        raise DuplicateAssetValuationError(
            f"Asset already has a {valuation_type} valuation."
        ) from exc

    return valuation


# ==========================================================
# Private Helpers
# ==========================================================


def _validate_valuation_type(
    valuation_type: str,
) -> None:

    if valuation_type not in VALUATION_TYPES:
        raise InvalidValuationTypeError(
            f"Unsupported valuation type: {valuation_type}"
        )


def _validate_amount(
    amount: Decimal,
) -> None:

    if amount is None:
        raise ValuationValidationError(
            "Valuation amount is required."
        )

    if amount <= Decimal("0.00"):
        raise ValuationValidationError(
            "Valuation amount must be greater than zero."
        )


def _build_valuation(
    *,
    asset: Asset,
    valuation_type: str,
    amount: Decimal,
    valuation_date: date,
    remarks: str,
) -> AssetValuation:

    return AssetValuation(
        asset=asset,
        valuation_type=valuation_type,
        amount=amount,
        valuation_date=valuation_date,
        remarks=remarks,
    )