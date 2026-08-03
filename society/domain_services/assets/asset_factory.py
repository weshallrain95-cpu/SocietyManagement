"""
==========================================================
SocietyOS Asset Factory
==========================================================

Purpose
-------
Single entry point responsible for creating Asset records.

The factory is intentionally responsible only for:

    • validating creation requests
    • loading the Asset Operating Model
    • resolving asset intelligence
    • generating asset numbers
    • constructing Asset objects

The factory deliberately does NOT manage:

    • AMC
    • Warranty
    • Components
    • Lifecycle
    • Inspections
    • Service History
    • Breakdown History

Those responsibilities belong to dedicated domain services.

Public API
----------

create_asset(...)

Author
------
SocietyOS Platform

"""

from __future__ import annotations

from typing import Any
from typing import Dict
from typing import Optional

from django.db import transaction

from society.models import (
    Asset,
    Society,
    Wing,
    Floor,
    Flat,
)

from society.domain_services.assets.asset_categories import (
    ASSET_CATEGORY_REGISTRY,
)


# ==========================================================
# Constants
# ==========================================================

ASSET_NUMBER_PREFIX = "AST"

ASSET_NUMBER_PADDING = 6


# ==========================================================
# Exceptions
# ==========================================================

class AssetFactoryError(Exception):
    """
    Base Asset Factory exception.
    """
    pass


class InvalidAssetTypeError(AssetFactoryError):
    """
    Asset type does not exist inside the operating model.
    """
    pass


class InvalidSocietyError(AssetFactoryError):
    """
    Society supplied to factory is invalid.
    """
    pass


class InvalidLocationError(AssetFactoryError):
    """
    Invalid asset location.
    """
    pass

class AssetRequirementError(AssetFactoryError):
    """
    Raised when an Asset does not satisfy
    requirements defined by the Asset
    Operating Model.
    """
    pass

# ==========================================================
# Registry Loader
# ==========================================================

_ASSET_TYPE_REGISTRY: Dict[str, Dict[str, Any]] = {}

_REGISTRY_INITIALIZED = False


def _initialize_registry() -> None:
    """
    Converts the operating model into an O(1)
    lookup registry.

    This executes only once.
    """

    global _REGISTRY_INITIALIZED

    if _REGISTRY_INITIALIZED:
        return

    for category_code, category in ASSET_CATEGORY_REGISTRY.items():

        asset_types = category.get("asset_types", {})

        for asset_type_code, asset_definition in asset_types.items():

            _ASSET_TYPE_REGISTRY[asset_type_code] = {

                "category": category_code,

                "category_definition": category.get(
                    "definition",
                    {},
                ),

                "asset_definition": asset_definition.get(
                    "definition",
                    {},
                ),

                "intelligence": asset_definition.get(
                    "intelligence",
                    {},
                ),

                "components": asset_definition.get(
                    "components",
                    {},
                ),

                "defaults": asset_definition.get(
                    "defaults",
                    {},
                ),
            }

    _REGISTRY_INITIALIZED = True


# ==========================================================
# Asset Definition
# ==========================================================

def _load_asset_definition(
    asset_type: str,
) -> Dict[str, Any]:
    """
    Returns complete metadata for an asset type.
    """

    _initialize_registry()

    try:
        return _ASSET_TYPE_REGISTRY[asset_type]

    except KeyError:

        raise InvalidAssetTypeError(
            f"Unsupported asset type '{asset_type}'."
        )


# ==========================================================
# Validation Helpers
# ==========================================================

def _validate_society(
    society: Society,
) -> None:

    if society is None:
        raise InvalidSocietyError(
            "Society is mandatory."
        )

    if not isinstance(society, Society):
        raise InvalidSocietyError(
            "Invalid Society instance."
        )


def _validate_location(
    wing: Optional[Wing],
    floor: Optional[Floor],
    flat: Optional[Flat],
) -> None:
    """
    Validates location hierarchy.

    Future versions may introduce
    deeper structural validation.
    """

    if floor and wing is None:
        raise InvalidLocationError(
            "Floor cannot exist without Wing."
        )

    if flat:

        if wing is None:
            raise InvalidLocationError(
                "Flat requires Wing."
            )

        if floor is None:
            raise InvalidLocationError(
                "Flat requires Floor."
            )

# ==========================================================
# Operating Model Validation
# ==========================================================

def _validate_asset_requirements(
    *,
    metadata: Dict[str, Any],
    manufacturer: Optional[str],
    serial_number: Optional[str],
    installed_on,
) -> None:
    """
    Validates requirements defined by the
    Asset Operating Model.

    Validation is completely metadata driven.

    No asset-specific logic should ever
    appear inside this function.
    """

    intelligence = metadata.get(
        "intelligence",
        {},
    )

    governance = intelligence.get(
        "governance",
        {},
    )

    #
    # Vendor / Manufacturer
    #

    if governance.get("requires_vendor"):

        if not manufacturer:

            raise AssetRequirementError(
                "This asset type requires a manufacturer."
            )

    #
    # Serial Number
    #

    if governance.get("requires_serial_number"):

        if not serial_number:

            raise AssetRequirementError(
                "This asset type requires a serial number."
            )

    #
    # Installation Date
    #

    if governance.get("requires_installation_date"):

        if installed_on is None:

            raise AssetRequirementError(
                "This asset type requires an installation date."
            )
def _validate_name(
    name: str,
) -> None:

    if not name:
        raise AssetFactoryError(
            "Asset name is required."
        )

    if len(name.strip()) == 0:
        raise AssetFactoryError(
            "Asset name cannot be blank."
        )


def _validate_inputs(
    *,
    society: Society,
    asset_type: str,
    name: str,
    manufacturer: Optional[str],
    serial_number: Optional[str],
    installed_on,
    wing: Optional[Wing],
    floor: Optional[Floor],
    flat: Optional[Flat],
) -> Dict[str, Any]:
    """
    Performs all pre-creation validation.

    Returns resolved operating-model metadata.
    """

    _validate_society(society)

    _validate_name(name)

    _validate_location(
        wing,
        floor,
        flat,
    )

    metadata = _load_asset_definition(
        asset_type,
    )

    _validate_asset_requirements(
        metadata=metadata,
        manufacturer=manufacturer,
        serial_number=serial_number,
        installed_on=installed_on,
    )

    return metadata


# ==========================================================
# Asset Number Generation
# ==========================================================

def _generate_asset_number(
    society: Society,
) -> str:
    """
    Generates the next sequential Asset Number
    for the supplied society.

    Asset numbering is completely independent
    for every society.

    Examples

        Society A
            AST-000001
            AST-000002

        Society B
            AST-000001
            AST-000002

    Asset numbers are derived from the Asset
    Register itself rather than database IDs.
    """

    highest_sequence = 0

    asset_numbers = (
        Asset.objects
        .filter(
            society=society,
        )
        .values_list(
            "asset_number",
            flat=True,
        )
    )

    for asset_number in asset_numbers:

        if not asset_number:
            continue

        try:

            prefix, number = asset_number.split("-")

            if prefix != ASSET_NUMBER_PREFIX:
                continue

            highest_sequence = max(
                highest_sequence,
                int(number),
            )

        except (ValueError, IndexError):
            #
            # Ignore malformed historical numbers.
            #
            continue

    next_sequence = highest_sequence + 1

    return (
        f"{ASSET_NUMBER_PREFIX}-"
        f"{next_sequence:0{ASSET_NUMBER_PADDING}d}"
    )


# ==========================================================
# Default Resolution
# ==========================================================

def _resolve_default(
    metadata: Dict[str, Any],
    key: str,
    fallback: Any,
) -> Any:
    """
    Reads a default value from the operating model.

    Falls back to the supplied value if absent.
    """

    defaults = metadata.get(
        "defaults",
        {},
    )

    return defaults.get(
        key,
        fallback,
    )


# ==========================================================
# Asset Construction
# ==========================================================

def _build_asset(
    *,
    society: Society,
    metadata: Dict[str, Any],
    asset_number: str,
    name: str,
    description: str,
    manufacturer: Optional[str],
    model: Optional[str],
    serial_number: Optional[str],
    wing: Optional[Wing],
    floor: Optional[Floor],
    flat: Optional[Flat],
    location_description: Optional[str],
    installed_on,
    commissioned_on,
    origin: str,
) -> Asset:
    """
    Creates an unsaved Asset instance.

    No database writes occur here.
    """

    intelligence = metadata.get(
        "intelligence",
        {},
    )

    profile = intelligence.get(
        "classification",
        {},
    )

    asset = Asset(

        society=society,

        asset_number=asset_number,

        name=name,

        description=description,

        category=metadata["category"],

        asset_type=metadata["asset_definition"]["code"],

        origin=origin,

        manufacturer=manufacturer,

        model=model,

        serial_number=serial_number,

        wing=wing,

        floor=floor,

        flat=flat,

        location_description=location_description,

        installed_on=installed_on,

        commissioned_on=commissioned_on,

        criticality=profile.get(
            "criticality",
            "MEDIUM",
        ),

        expected_life_years=_resolve_default(
            metadata,
            "expected_life_years",
            None,
        ),

        status=_resolve_default(
            metadata,
            "status",
            "ACTIVE",
        ),

        condition=_resolve_default(
            metadata,
            "condition",
            "GOOD",
        ),

        is_active=True,
    )

    return asset


# ==========================================================
# Persistence
# ==========================================================

def _save_asset(
    asset: Asset,
) -> Asset:
    """
    Persists the Asset.

    Exists separately so future versions can
    introduce hooks without changing the factory.
    """

    asset.save()

    return asset


# ==========================================================
# Public API
# ==========================================================

@transaction.atomic
def create_asset(
    *,
    society: Society,
    asset_type: str,
    name: str,
    description: str = "",
    manufacturer: Optional[str] = None,
    model: Optional[str] = None,
    serial_number: Optional[str] = None,
    wing: Optional[Wing] = None,
    floor: Optional[Floor] = None,
    flat: Optional[Flat] = None,
    location_description: Optional[str] = None,
    installed_on=None,
    commissioned_on=None,
    origin: str = "PURCHASED",
) -> Asset:
    """
    Creates a new Asset.

    This is the ONLY supported entry point for creating
    Asset records inside SocietyOS.

    Responsibilities
    ----------------

    • Validate input

    • Resolve Asset Operating Model

    • Derive category automatically

    • Generate Asset Number

    • Construct Asset

    • Persist Asset

    Returns
    -------

    Newly created Asset instance.
    """

    metadata = _validate_inputs(
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

    asset_number = _generate_asset_number(
        society,
    )

    asset = _build_asset(
        society=society,
        metadata=metadata,
        asset_number=asset_number,
        name=name.strip(),
        description=description.strip(),
        manufacturer=manufacturer,
        model=model,
        serial_number=serial_number,
        wing=wing,
        floor=floor,
        flat=flat,
        location_description=location_description,
        installed_on=installed_on,
        commissioned_on=commissioned_on,
        origin=origin,
    )

    return _save_asset(
        asset,
    )


# ==========================================================
# Public Exports
# ==========================================================

__all__ = [
    "create_asset",
]