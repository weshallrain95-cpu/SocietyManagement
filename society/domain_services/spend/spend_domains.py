"""
===============================================================================
Society Operational Domains

Defines the canonical operational domains used throughout SocietyOS.

These domains are BUSINESS concepts.

They are NOT accounting categories.

They are intentionally stable and should rarely change.
===============================================================================
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class OperationalDomain:
    code: str
    display_name: str
    description: str


SECURITY_SAFETY = OperationalDomain(
    code="SECURITY_SAFETY",
    display_name="Security & Safety",
    description="Protection of residents, property and common areas.",
)

UTILITIES = OperationalDomain(
    code="UTILITIES",
    display_name="Utilities",
    description="Essential utility services consumed by the society.",
)

HOUSEKEEPING_SANITATION = OperationalDomain(
    code="HOUSEKEEPING_SANITATION",
    display_name="Housekeeping & Sanitation",
    description="Cleaning, waste management and hygiene.",
)

REPAIRS_MAINTENANCE = OperationalDomain(
    code="REPAIRS_MAINTENANCE",
    display_name="Repairs & Maintenance",
    description="Routine repair and upkeep of society infrastructure.",
)

EQUIPMENT_INFRASTRUCTURE = OperationalDomain(
    code="EQUIPMENT_INFRASTRUCTURE",
    display_name="Equipment & Infrastructure",
    description="Infrastructure and operational equipment purchases.",
)

GARDEN_LANDSCAPING = OperationalDomain(
    code="GARDEN_LANDSCAPING",
    display_name="Garden & Landscaping",
    description="Garden upkeep and landscape improvements.",
)

ADMINISTRATION = OperationalDomain(
    code="ADMINISTRATION",
    display_name="Administration",
    description="Administrative and office operations.",
)

STAFF_WELFARE = OperationalDomain(
    code="STAFF_WELFARE",
    display_name="Staff & Welfare",
    description="Employee compensation and welfare.",
)

COMPLIANCE_INSURANCE = OperationalDomain(
    code="COMPLIANCE_INSURANCE",
    display_name="Compliance & Insurance",
    description="Legal, statutory and insurance obligations.",
)

COMMUNITY_EVENTS = OperationalDomain(
    code="COMMUNITY_EVENTS",
    display_name="Community & Events",
    description="Resident engagement and community activities.",
)

TECHNOLOGY_DIGITAL_SERVICES = OperationalDomain(
    code="TECHNOLOGY_DIGITAL",
    display_name="Technology & Digital Services",
    description="Technology platforms and digital infrastructure.",
)

CONTRACTORS_PROJECTS = OperationalDomain(
    code="CONTRACTORS_PROJECTS",
    display_name="Contractors & Projects",
    description="Major works, capital projects and contractor-led initiatives.",
)


ALL_OPERATIONAL_DOMAINS = (
    SECURITY_SAFETY,
    UTILITIES,
    HOUSEKEEPING_SANITATION,
    REPAIRS_MAINTENANCE,
    EQUIPMENT_INFRASTRUCTURE,
    GARDEN_LANDSCAPING,
    ADMINISTRATION,
    STAFF_WELFARE,
    COMPLIANCE_INSURANCE,
    COMMUNITY_EVENTS,
    TECHNOLOGY_DIGITAL_SERVICES,
    CONTRACTORS_PROJECTS,
)