from dataclasses import dataclass
from typing import Optional

from .acquisition_types import (
    SERVICE,
    CONSUMABLE,
    ASSET,
)

from .spend_domains import OperationalDomain

from .spend_domains import SECURITY_SAFETY
from .spend_domains import UTILITIES
from .spend_domains import HOUSEKEEPING_SANITATION
from .spend_domains import REPAIRS_MAINTENANCE
from .spend_domains import EQUIPMENT_INFRASTRUCTURE
from .spend_domains import GARDEN_LANDSCAPING
from .spend_domains import ADMINISTRATION
from .spend_domains import STAFF_WELFARE
from .spend_domains import COMPLIANCE_INSURANCE
from .spend_domains import COMMUNITY_EVENTS
from .spend_domains import TECHNOLOGY_DIGITAL_SERVICES
from .spend_domains import CONTRACTORS_PROJECTS



@dataclass(frozen=True)
class SpendItem:

    code: str

    display_name: str

    operational_domain: OperationalDomain

    acquisition_type: str

    description: str

    asset_category: Optional[str] = None

    asset_type: Optional[str] = None




# =============================================================================
# Security & Safety
# =============================================================================

SECURITY_AGENCY = SpendItem(
    code="SECURITY_AGENCY",
    display_name="Security Agency",
    operational_domain=SECURITY_SAFETY,
    acquisition_type=SERVICE,
    description="Monthly security agency services.",
)

CCTV_SYSTEM = SpendItem(
    code="CCTV_SYSTEM",
    display_name="CCTV System",
    operational_domain=SECURITY_SAFETY,
    acquisition_type=ASSET,
    description="CCTV surveillance equipment.",
    asset_category="SECURITY",
    asset_type="CCTV_CAMERA",
)

ACCESS_CONTROL = SpendItem(
    code="ACCESS_CONTROL",
    display_name="Access Control",
    operational_domain=SECURITY_SAFETY,
    acquisition_type=ASSET,
    description="Access control systems including RFID, biometric and smart entry.",
    asset_category="SECURITY",
    asset_type="ACCESS_CONTROL_SYSTEM",
)

BOOM_BARRIER = SpendItem(
    code="BOOM_BARRIER",
    display_name="Boom Barrier",
    operational_domain=SECURITY_SAFETY,
    acquisition_type=ASSET,
    description="Vehicle entry and exit boom barrier system.",
    asset_category="SECURITY",
    asset_type="BOOM_BARRIER",
)

INTERCOM = SpendItem(
    code="INTERCOM",
    display_name="Intercom",
    operational_domain=SECURITY_SAFETY,
    acquisition_type=ASSET,
    description="Intercom communication system.",
    asset_category="COMMUNICATION",
    asset_type="INTERCOM_SYSTEM",
)

FIRE_SAFETY_EQUIPMENT = SpendItem(
    code="FIRE_SAFETY_EQUIPMENT",
    display_name="Fire Safety Equipment",
    operational_domain=SECURITY_SAFETY,
    acquisition_type=ASSET,
    description="Fire extinguishers, hydrants and other fire safety equipment.",
    asset_category="FIRE_SAFETY",
    asset_type="FIRE_EXTINGUISHER",
)

FIRE_SAFETY_MAINTENANCE = SpendItem(
    code="FIRE_SAFETY_MAINTENANCE",
    display_name="Fire Safety Maintenance",
    operational_domain=SECURITY_SAFETY,
    acquisition_type=SERVICE,
    description="Inspection, testing and annual maintenance of fire safety systems.",
)

SAFETY_SIGNAGE = SpendItem(
    code="SAFETY_SIGNAGE",
    display_name="Safety Signage",
    operational_domain=SECURITY_SAFETY,
    acquisition_type=CONSUMABLE,
    description="Safety signs, emergency exit boards and warning notices.",
)

EMERGENCY_EQUIPMENT = SpendItem(
    code="EMERGENCY_EQUIPMENT",
    display_name="Emergency Equipment",
    operational_domain=SECURITY_SAFETY,
    acquisition_type=ASSET,
    description="Emergency response equipment including stretchers and emergency kits.",
    asset_category="SAFETY",
    asset_type="EMERGENCY_LIGHTING",
)

# =============================================================================
# Utilities
# =============================================================================

COMMON_AREA_ELECTRICITY = SpendItem(
    code="COMMON_AREA_ELECTRICITY",
    display_name="Common Area Electricity",
    operational_domain=UTILITIES,
    acquisition_type=SERVICE,
    description="Electricity charges for common areas and shared infrastructure.",
)

WATER_CHARGES = SpendItem(
    code="WATER_CHARGES",
    display_name="Water Charges",
    operational_domain=UTILITIES,
    acquisition_type=SERVICE,
    description="Municipal water supply charges.",
)

WATER_TANKER = SpendItem(
    code="WATER_TANKER",
    display_name="Water Tanker",
    operational_domain=UTILITIES,
    acquisition_type=SERVICE,
    description="Water tanker supply during shortages.",
)

GENERATOR_FUEL = SpendItem(
    code="GENERATOR_FUEL",
    display_name="Generator Fuel",
    operational_domain=UTILITIES,
    acquisition_type=CONSUMABLE,
    description="Diesel or other fuel used for generator operation.",
)

INTERNET = SpendItem(
    code="INTERNET",
    display_name="Internet",
    operational_domain=UTILITIES,
    acquisition_type=SERVICE,
    description="Internet connectivity for society operations.",
)

TELEPHONE = SpendItem(
    code="TELEPHONE",
    display_name="Telephone",
    operational_domain=UTILITIES,
    acquisition_type=SERVICE,
    description="Telephone and landline services.",
)

GAS = SpendItem(
    code="GAS",
    display_name="Gas",
    operational_domain=UTILITIES,
    acquisition_type=SERVICE,
    description="Gas supply for common facilities.",
)

# =============================================================================
# Housekeeping & Sanitation
# =============================================================================

HOUSEKEEPING_AGENCY = SpendItem(
    code="HOUSEKEEPING_AGENCY",
    display_name="Housekeeping Agency",
    operational_domain=HOUSEKEEPING_SANITATION,
    acquisition_type=SERVICE,
    description="Housekeeping and cleaning agency services.",
)

CLEANING_SUPPLIES = SpendItem(
    code="CLEANING_SUPPLIES",
    display_name="Cleaning Supplies",
    operational_domain=HOUSEKEEPING_SANITATION,
    acquisition_type=CONSUMABLE,
    description="Cleaning chemicals, mops, brushes and consumable cleaning materials.",
)

GARBAGE_DISPOSAL = SpendItem(
    code="GARBAGE_DISPOSAL",
    display_name="Garbage Disposal",
    operational_domain=HOUSEKEEPING_SANITATION,
    acquisition_type=SERVICE,
    description="Garbage collection and disposal services.",
)

PEST_CONTROL = SpendItem(
    code="PEST_CONTROL",
    display_name="Pest Control",
    operational_domain=HOUSEKEEPING_SANITATION,
    acquisition_type=SERVICE,
    description="Pest control and fumigation services.",
)

DRAIN_CLEANING = SpendItem(
    code="DRAIN_CLEANING",
    display_name="Drain Cleaning",
    operational_domain=HOUSEKEEPING_SANITATION,
    acquisition_type=SERVICE,
    description="Cleaning and maintenance of drainage systems.",
)

SEWAGE_CLEANING = SpendItem(
    code="SEWAGE_CLEANING",
    display_name="Sewage Cleaning",
    operational_domain=HOUSEKEEPING_SANITATION,
    acquisition_type=SERVICE,
    description="Cleaning of sewage lines, chambers and related infrastructure.",
)

# =============================================================================
# Repairs & Maintenance
# =============================================================================

CIVIL_REPAIR = SpendItem(
    code="CIVIL_REPAIR",
    display_name="Civil Repair",
    operational_domain=REPAIRS_MAINTENANCE,
    acquisition_type=SERVICE,
    description="Civil repair and masonry maintenance works.",
)

PAINTING = SpendItem(
    code="PAINTING",
    display_name="Painting",
    operational_domain=REPAIRS_MAINTENANCE,
    acquisition_type=SERVICE,
    description="Painting and repainting works.",
)

PLUMBING_REPAIR = SpendItem(
    code="PLUMBING_REPAIR",
    display_name="Plumbing Repair",
    operational_domain=REPAIRS_MAINTENANCE,
    acquisition_type=SERVICE,
    description="Repair and maintenance of plumbing systems.",
)

ELECTRICAL_REPAIR = SpendItem(
    code="ELECTRICAL_REPAIR",
    display_name="Electrical Repair",
    operational_domain=REPAIRS_MAINTENANCE,
    acquisition_type=SERVICE,
    description="Repair and maintenance of electrical systems.",
)

LIFT_MAINTENANCE = SpendItem(
    code="LIFT_MAINTENANCE",
    display_name="Lift Maintenance",
    operational_domain=REPAIRS_MAINTENANCE,
    acquisition_type=SERVICE,
    description="Annual maintenance and repair of lifts.",
)

WATERPROOFING = SpendItem(
    code="WATERPROOFING",
    display_name="Waterproofing",
    operational_domain=REPAIRS_MAINTENANCE,
    acquisition_type=SERVICE,
    description="Waterproofing repair and maintenance works.",
)

ROAD_REPAIR = SpendItem(
    code="ROAD_REPAIR",
    display_name="Road Repair",
    operational_domain=REPAIRS_MAINTENANCE,
    acquisition_type=SERVICE,
    description="Repair of internal roads and paved areas.",
)

COMPOUND_WALL_REPAIR = SpendItem(
    code="COMPOUND_WALL_REPAIR",
    display_name="Compound Wall Repair",
    operational_domain=REPAIRS_MAINTENANCE,
    acquisition_type=SERVICE,
    description="Repair of compound walls and boundary structures.",
)

ROOF_REPAIR = SpendItem(
    code="ROOF_REPAIR",
    display_name="Roof Repair",
    operational_domain=REPAIRS_MAINTENANCE,
    acquisition_type=SERVICE,
    description="Repair and maintenance of roofs and terraces.",
)

GLASS_REPAIR = SpendItem(
    code="GLASS_REPAIR",
    display_name="Glass Repair",
    operational_domain=REPAIRS_MAINTENANCE,
    acquisition_type=SERVICE,
    description="Replacement and repair of glass installations.",
)

METAL_FABRICATION = SpendItem(
    code="METAL_FABRICATION",
    display_name="Metal Fabrication",
    operational_domain=REPAIRS_MAINTENANCE,
    acquisition_type=SERVICE,
    description="Metal fabrication and welding works.",
)

CARPENTRY = SpendItem(
    code="CARPENTRY",
    display_name="Carpentry",
    operational_domain=REPAIRS_MAINTENANCE,
    acquisition_type=SERVICE,
    description="Carpentry and wood repair works.",
)

MASONRY = SpendItem(
    code="MASONRY",
    display_name="Masonry",
    operational_domain=REPAIRS_MAINTENANCE,
    acquisition_type=SERVICE,
    description="Brickwork, blockwork and masonry services.",
)

# =============================================================================
# Equipment & Infrastructure
# =============================================================================

WATER_PUMP = SpendItem(
    code="WATER_PUMP",
    display_name="Water Pump",
    operational_domain=EQUIPMENT_INFRASTRUCTURE,
    acquisition_type=ASSET,
    description="Water pumping equipment.",
    asset_category="MECHANICAL",
    asset_type="DOMESTIC_WATER_PUMP",
)

GENERATOR = SpendItem(
    code="GENERATOR",
    display_name="Generator",
    operational_domain=EQUIPMENT_INFRASTRUCTURE,
    acquisition_type=ASSET,
    description="Power backup generator.",
    asset_category="ELECTRICAL",
    asset_type="DIESEL_GENERATOR",
)

LIFT = SpendItem(
    code="LIFT",
    display_name="Lift",
    operational_domain=EQUIPMENT_INFRASTRUCTURE,
    acquisition_type=ASSET,
    description="Passenger or service lift.",
    asset_category="BUILDING_SYSTEM",
    asset_type="PASSENGER_LIFT",
)

SOLAR_SYSTEM = SpendItem(
    code="SOLAR_SYSTEM",
    display_name="Solar System",
    operational_domain=EQUIPMENT_INFRASTRUCTURE,
    acquisition_type=ASSET,
    description="Solar power generation system.",
    asset_category="ENERGY",
    asset_type="SOLAR_POWER_SYSTEM",

)

CCTV_EQUIPMENT = SpendItem(
    code="CCTV_EQUIPMENT",
    display_name="CCTV Equipment",
    operational_domain=EQUIPMENT_INFRASTRUCTURE,
    acquisition_type=ASSET,
    description="CCTV cameras, DVRs, NVRs and related hardware.",
    asset_category="SECURITY",
    asset_type="CCTV_CAMERA",
)

FURNITURE = SpendItem(
    code="FURNITURE",
    display_name="Furniture",
    operational_domain=EQUIPMENT_INFRASTRUCTURE,
    acquisition_type=ASSET,
    description="Office and common area furniture.",
    asset_category="FURNITURE",
    asset_type="OFFICE_FURNITURE",
)

OFFICE_EQUIPMENT = SpendItem(
    code="OFFICE_EQUIPMENT",
    display_name="Office Equipment",
    operational_domain=EQUIPMENT_INFRASTRUCTURE,
    acquisition_type=ASSET,
    description="General office equipment.",
    asset_category="OFFICE",
    asset_type="OFFICE_FURNITURE",
)

COMPUTER = SpendItem(
    code="COMPUTER",
    display_name="Dell OptiPlex Desktop",
    operational_domain=EQUIPMENT_INFRASTRUCTURE,
    acquisition_type=ASSET,
    description="Desktop or laptop computer.",
    asset_category="IT",
    asset_type="COMPUTER",
)

PRINTER = SpendItem(
    code="PRINTER",
    display_name="Printer",
    operational_domain=EQUIPMENT_INFRASTRUCTURE,
    acquisition_type=ASSET,
    description="Printer or multifunction device.",
    asset_category="IT",
    asset_type="PRINTER",
)

GARDEN_EQUIPMENT = SpendItem(
    code="GARDEN_EQUIPMENT",
    display_name="Garden Equipment",
    operational_domain=EQUIPMENT_INFRASTRUCTURE,
    acquisition_type=ASSET,
    description="Garden maintenance equipment.",
    asset_category="GARDEN",
    asset_type="GARDEN_EQUIPMENT",
)

GYM_EQUIPMENT = SpendItem(
    code="GYM_EQUIPMENT",
    display_name="Gym Equipment",
    operational_domain=EQUIPMENT_INFRASTRUCTURE,
    acquisition_type=ASSET,
    description="Gym and fitness equipment.",
    asset_category="RECREATIONAL",
    asset_type="GYM_EQUIPMENT",
)

BUILDING_LIGHTING = SpendItem(
    code="BUILDING_LIGHTING",
    display_name="Building Lighting",
    description="Lighting fixtures and replaceable lighting components for common areas.",
    operational_domain=EQUIPMENT_INFRASTRUCTURE,
    acquisition_type=CONSUMABLE,
)

FITNESS_CONSUMABLES = SpendItem(
    code="FITNESS_CONSUMABLES",
    display_name="Fitness Consumables",
    description="Consumable items for fitness and wellness programs.",
    operational_domain=EQUIPMENT_INFRASTRUCTURE,
    acquisition_type=CONSUMABLE,
)

PLAYGROUND_EQUIPMENT = SpendItem(
    code="PLAYGROUND_EQUIPMENT",
    display_name="Playground Equipment",
    description="Children's playground equipment.",
    operational_domain=EQUIPMENT_INFRASTRUCTURE,
    acquisition_type=ASSET,
    asset_category="RECREATIONAL",
    asset_type="PLAYGROUND_EQUIPMENT",
)

# =============================================================================
# Garden & Landscaping
# =============================================================================

GARDEN_MAINTENANCE = SpendItem(
    code="GARDEN_MAINTENANCE",
    display_name="Garden Maintenance",
    operational_domain=GARDEN_LANDSCAPING,
    acquisition_type=SERVICE,
    description="Routine maintenance of gardens and landscaped areas.",
)

PLANTS_TREES = SpendItem(
    code="PLANTS_TREES",
    display_name="Plants & Trees",
    operational_domain=GARDEN_LANDSCAPING,
    acquisition_type=ASSET,
    description="Purchase of plants, trees and permanent landscaping vegetation.",
    asset_category="LANDSCAPING",
    asset_type="PLANTS_TREES",
)

FERTILIZERS = SpendItem(
    code="FERTILIZERS",
    display_name="Fertilizers",
    operational_domain=GARDEN_LANDSCAPING,
    acquisition_type=CONSUMABLE,
    description="Fertilizers, manure and soil nutrients.",
)

LAWN_MAINTENANCE = SpendItem(
    code="LAWN_MAINTENANCE",
    display_name="Lawn Maintenance",
    operational_domain=GARDEN_LANDSCAPING,
    acquisition_type=SERVICE,
    description="Lawn mowing, trimming and upkeep services.",
)

IRRIGATION_EQUIPMENT = SpendItem(
    code="IRRIGATION_EQUIPMENT",
    display_name="Irrigation Equipment",
    operational_domain=GARDEN_LANDSCAPING,
    acquisition_type=ASSET,
    description="Garden irrigation systems and watering equipment.",
    asset_category="LANDSCAPING",
    asset_type="IRRIGATION_EQUIPMENT",
)

# =============================================================================
# Administration
# =============================================================================

AUDIT_FEES = SpendItem(
    code="AUDIT_FEES",
    display_name="Audit Fees",
    operational_domain=ADMINISTRATION,
    acquisition_type=SERVICE,
    description="Statutory and internal audit services.",
)

LEGAL_FEES = SpendItem(
    code="LEGAL_FEES",
    display_name="Legal Fees",
    operational_domain=ADMINISTRATION,
    acquisition_type=SERVICE,
    description="Legal advisory and litigation services.",
)

PROFESSIONAL_CONSULTANCY = SpendItem(
    code="PROFESSIONAL_CONSULTANCY",
    display_name="Professional Consultancy",
    operational_domain=ADMINISTRATION,
    acquisition_type=SERVICE,
    description="Professional consultancy services including engineering and management advisors.",
)

PRINTING_STATIONERY = SpendItem(
    code="PRINTING_STATIONERY",
    display_name="Printing & Stationery",
    operational_domain=ADMINISTRATION,
    acquisition_type=CONSUMABLE,
    description="Printing, paper, registers and stationery items.",
)

COURIER = SpendItem(
    code="COURIER",
    display_name="Courier",
    operational_domain=ADMINISTRATION,
    acquisition_type=SERVICE,
    description="Courier and document delivery services.",
)

OFFICE_SUPPLIES = SpendItem(
    code="OFFICE_SUPPLIES",
    display_name="Office Supplies",
    operational_domain=ADMINISTRATION,
    acquisition_type=CONSUMABLE,
    description="General office consumables and supplies.",
)

SOFTWARE_SUBSCRIPTION = SpendItem(
    code="SOFTWARE_SUBSCRIPTION",
    display_name="Software Subscription",
    operational_domain=ADMINISTRATION,
    acquisition_type=SERVICE,
    description="Recurring subscriptions for operational software.",
)

BANK_CHARGES = SpendItem(
    code="BANK_CHARGES",
    display_name="Bank Charges",
    operational_domain=ADMINISTRATION,
    acquisition_type=SERVICE,
    description="Bank fees, transaction charges and account maintenance charges.",
)

# =============================================================================
# Staff & Welfare
# =============================================================================

SALARY = SpendItem(
    code="SALARY",
    display_name="Salary",
    operational_domain=STAFF_WELFARE,
    acquisition_type=SERVICE,
    description="Salary and wages paid to society staff.",
)

BONUS = SpendItem(
    code="BONUS",
    display_name="Bonus",
    operational_domain=STAFF_WELFARE,
    acquisition_type=SERVICE,
    description="Bonus and incentive payments to staff.",
)

UNIFORM = SpendItem(
    code="UNIFORM",
    display_name="Uniform",
    operational_domain=STAFF_WELFARE,
    acquisition_type=CONSUMABLE,
    description="Uniforms and related apparel for society staff.",
)

TRAINING = SpendItem(
    code="TRAINING",
    display_name="Training",
    operational_domain=STAFF_WELFARE,
    acquisition_type=SERVICE,
    description="Training and skill development for staff.",
)

MEDICAL_ASSISTANCE = SpendItem(
    code="MEDICAL_ASSISTANCE",
    display_name="Medical Assistance",
    operational_domain=STAFF_WELFARE,
    acquisition_type=SERVICE,
    description="Medical assistance and healthcare support for staff.",
)

STAFF_WELFARE_PROGRAM = SpendItem(
    code="STAFF_WELFARE",
    display_name="Staff Welfare",
    operational_domain=STAFF_WELFARE,
    acquisition_type=SERVICE,
    description="General employee welfare and staff benefit initiatives.",
)

# =============================================================================
# Compliance & Insurance
# =============================================================================

INSURANCE_PREMIUM = SpendItem(
    code="INSURANCE_PREMIUM",
    display_name="Insurance Premium",
    operational_domain=COMPLIANCE_INSURANCE,
    acquisition_type=SERVICE,
    description="Insurance premiums for society assets and liabilities.",
)

GOVERNMENT_FEES = SpendItem(
    code="GOVERNMENT_FEES",
    display_name="Government Fees",
    operational_domain=COMPLIANCE_INSURANCE,
    acquisition_type=SERVICE,
    description="Government fees payable to statutory authorities.",
)

REGISTRATION_CHARGES = SpendItem(
    code="REGISTRATION_CHARGES",
    display_name="Registration Charges",
    operational_domain=COMPLIANCE_INSURANCE,
    acquisition_type=SERVICE,
    description="Registration and filing charges.",
)

LICENSES = SpendItem(
    code="LICENSES",
    display_name="Licenses",
    operational_domain=COMPLIANCE_INSURANCE,
    acquisition_type=SERVICE,
    description="License renewals and statutory permits.",
)

INSPECTION_FEES = SpendItem(
    code="INSPECTION_FEES",
    display_name="Inspection Fees",
    operational_domain=COMPLIANCE_INSURANCE,
    acquisition_type=SERVICE,
    description="Fees for statutory inspections and certifications.",
)

STATUTORY_COMPLIANCE = SpendItem(
    code="STATUTORY_COMPLIANCE",
    display_name="Statutory Compliance",
    operational_domain=COMPLIANCE_INSURANCE,
    acquisition_type=SERVICE,
    description="Professional services for statutory compliance.",
)

# =============================================================================
# Community & Events
# =============================================================================

FESTIVAL_CELEBRATION = SpendItem(
    code="FESTIVAL_CELEBRATION",
    display_name="Festival Celebration",
    operational_domain=COMMUNITY_EVENTS,
    acquisition_type=SERVICE,
    description="Festival celebration expenses.",
)

ANNUAL_GENERAL_MEETING = SpendItem(
    code="ANNUAL_GENERAL_MEETING",
    display_name="Annual General Meeting",
    operational_domain=COMMUNITY_EVENTS,
    acquisition_type=SERVICE,
    description="Expenses for Annual General Meeting.",
)

SOCIETY_EVENTS = SpendItem(
    code="SOCIETY_EVENTS",
    display_name="Society Events",
    operational_domain=COMMUNITY_EVENTS,
    acquisition_type=SERVICE,
    description="Community and social event expenses.",
)

NOTICE_BOARD = SpendItem(
    code="NOTICE_BOARD",
    display_name="Notice Board",
    operational_domain=COMMUNITY_EVENTS,
    acquisition_type=ASSET,
    description="Notice boards and display installations.",
    asset_category="COMMUNITY",
    asset_type="NOTICE_BOARD",
)

DECORATIONS = SpendItem(
    code="DECORATIONS",
    display_name="Decorations",
    operational_domain=COMMUNITY_EVENTS,
    acquisition_type=CONSUMABLE,
    description="Decorative materials and event decorations.",
)

COMMUNITY_ACTIVITIES = SpendItem(
    code="COMMUNITY_ACTIVITIES",
    display_name="Community Activities",
    operational_domain=COMMUNITY_EVENTS,
    acquisition_type=SERVICE,
    description="Resident engagement and community activities.",
)

# =============================================================================
# Technology & Digital Services
# =============================================================================

WEBSITE = SpendItem(
    code="WEBSITE",
    display_name="Website",
    operational_domain=TECHNOLOGY_DIGITAL_SERVICES,
    acquisition_type=SERVICE,
    description="Society website services.",
)

MOBILE_APP = SpendItem(
    code="MOBILE_APP",
    display_name="Mobile App",
    operational_domain=TECHNOLOGY_DIGITAL_SERVICES,
    acquisition_type=SERVICE,
    description="Mobile application services.",
)

ACCESS_SOFTWARE = SpendItem(
    code="ACCESS_SOFTWARE",
    display_name="Access Software",
    operational_domain=TECHNOLOGY_DIGITAL_SERVICES,
    acquisition_type=SERVICE,
    description="Visitor and access management software.",
)

ACCOUNTING_SOFTWARE = SpendItem(
    code="ACCOUNTING_SOFTWARE",
    display_name="Accounting Software",
    operational_domain=TECHNOLOGY_DIGITAL_SERVICES,
    acquisition_type=SERVICE,
    description="Accounting and finance software.",
)

CLOUD_SERVICES = SpendItem(
    code="CLOUD_SERVICES",
    display_name="Cloud Services",
    operational_domain=TECHNOLOGY_DIGITAL_SERVICES,
    acquisition_type=SERVICE,
    description="Cloud hosting and infrastructure services.",
)

DIGITAL_COMMUNICATION = SpendItem(
    code="DIGITAL_COMMUNICATION",
    display_name="Digital Communication",
    operational_domain=TECHNOLOGY_DIGITAL_SERVICES,
    acquisition_type=SERVICE,
    description="Digital communication platforms.",
)

SMS_EMAIL_SERVICES = SpendItem(
    code="SMS_EMAIL_SERVICES",
    display_name="SMS & Email Services",
    operational_domain=TECHNOLOGY_DIGITAL_SERVICES,
    acquisition_type=SERVICE,
    description="Bulk SMS and email communication services.",
)

# =============================================================================
# Contractors & Projects
# =============================================================================

BUILDING_PAINTING_PROJECT = SpendItem(
    code="BUILDING_PAINTING_PROJECT",
    display_name="Building Painting Project",
    operational_domain=CONTRACTORS_PROJECTS,
    acquisition_type=SERVICE,
    description="Major building painting project.",
)

STRUCTURAL_REPAIRS = SpendItem(
    code="STRUCTURAL_REPAIRS",
    display_name="Structural Repairs",
    operational_domain=CONTRACTORS_PROJECTS,
    acquisition_type=SERVICE,
    description="Major structural repair works.",
)

TERRACE_WATERPROOFING_PROJECT = SpendItem(
    code="TERRACE_WATERPROOFING_PROJECT",
    display_name="Terrace Waterproofing Project",
    operational_domain=CONTRACTORS_PROJECTS,
    acquisition_type=SERVICE,
    description="Major terrace waterproofing project.",
)

BUILDING_RENOVATION = SpendItem(
    code="BUILDING_RENOVATION",
    display_name="Building Renovation",
    operational_domain=CONTRACTORS_PROJECTS,
    acquisition_type=SERVICE,
    description="Building renovation project.",
)

LIFT_MODERNIZATION = SpendItem(
    code="LIFT_MODERNIZATION",
    display_name="Lift Modernization",
    operational_domain=CONTRACTORS_PROJECTS,
    acquisition_type=SERVICE,
    description="Lift modernization project.",
)

SOLAR_INSTALLATION = SpendItem(
    code="SOLAR_INSTALLATION",
    display_name="Solar Installation",
    operational_domain=CONTRACTORS_PROJECTS,
    acquisition_type=SERVICE,
    description="Solar installation project.",
)

STP_INSTALLATION_UPGRADE = SpendItem(
    code="STP_INSTALLATION_UPGRADE",
    display_name="STP Installation / Upgrade",
    operational_domain=CONTRACTORS_PROJECTS,
    acquisition_type=SERVICE,
    description="STP installation and upgrade project.",
)

RAINWATER_HARVESTING = SpendItem(
    code="RAINWATER_HARVESTING",
    display_name="Rainwater Harvesting",
    operational_domain=CONTRACTORS_PROJECTS,
    acquisition_type=SERVICE,
    description="Rainwater harvesting project.",
)

MAJOR_CIVIL_WORKS = SpendItem(
    code="MAJOR_CIVIL_WORKS",
    display_name="Major Civil Works",
    operational_domain=CONTRACTORS_PROJECTS,
    acquisition_type=SERVICE,
    description="Major civil engineering works.",
)

MAJOR_ELECTRICAL_WORKS = SpendItem(
    code="MAJOR_ELECTRICAL_WORKS",
    display_name="Major Electrical Works",
    operational_domain=CONTRACTORS_PROJECTS,
    acquisition_type=SERVICE,
    description="Major electrical infrastructure works.",
)

MAJOR_PLUMBING_WORKS = SpendItem(
    code="MAJOR_PLUMBING_WORKS",
    display_name="Major Plumbing Works",
    operational_domain=CONTRACTORS_PROJECTS,
    acquisition_type=SERVICE,
    description="Major plumbing infrastructure works.",
)

COMPOUND_REDEVELOPMENT = SpendItem(
    code="COMPOUND_REDEVELOPMENT",
    display_name="Compound Redevelopment",
    operational_domain=CONTRACTORS_PROJECTS,
    acquisition_type=SERVICE,
    description="Compound redevelopment project.",
)

LANDSCAPING_PROJECT = SpendItem(
    code="LANDSCAPING_PROJECT",
    display_name="Landscaping Project",
    operational_domain=CONTRACTORS_PROJECTS,
    acquisition_type=SERVICE,
    description="Major landscaping project.",
)

INFRASTRUCTURE_UPGRADE = SpendItem(
    code="INFRASTRUCTURE_UPGRADE",
    display_name="Infrastructure Upgrade",
    operational_domain=CONTRACTORS_PROJECTS,
    acquisition_type=SERVICE,
    description="Major infrastructure upgrade project.",
)


ALL_SPEND_ITEMS = (
    SECURITY_AGENCY,
    CCTV_SYSTEM,
    ACCESS_CONTROL,
    BOOM_BARRIER,
    INTERCOM,
    FIRE_SAFETY_EQUIPMENT,
    FIRE_SAFETY_MAINTENANCE,
    SAFETY_SIGNAGE,
    EMERGENCY_EQUIPMENT,
    COMMON_AREA_ELECTRICITY,
    WATER_CHARGES,
    WATER_TANKER,
    GENERATOR_FUEL,
    INTERNET,
    TELEPHONE,
    GAS,
    HOUSEKEEPING_AGENCY,
    CLEANING_SUPPLIES,
    GARBAGE_DISPOSAL,
    PEST_CONTROL,
    DRAIN_CLEANING,
    SEWAGE_CLEANING,
    CIVIL_REPAIR,
    PAINTING,
    PLUMBING_REPAIR,
    ELECTRICAL_REPAIR,
    LIFT_MAINTENANCE,
    WATERPROOFING,
    ROAD_REPAIR,
    COMPOUND_WALL_REPAIR,
    ROOF_REPAIR,
    GLASS_REPAIR,
    METAL_FABRICATION,
    CARPENTRY,
    MASONRY,
    WATER_PUMP,
    GENERATOR,
    LIFT,
    SOLAR_SYSTEM,
    CCTV_EQUIPMENT,
    FURNITURE,
    OFFICE_EQUIPMENT,
    COMPUTER,
    PRINTER,
    GARDEN_EQUIPMENT,
    GYM_EQUIPMENT,
    BUILDING_LIGHTING,
    FITNESS_CONSUMABLES,
    PLAYGROUND_EQUIPMENT,
    GARDEN_MAINTENANCE,
    PLANTS_TREES,
    FERTILIZERS,
    LAWN_MAINTENANCE,
    IRRIGATION_EQUIPMENT,
    AUDIT_FEES,
    LEGAL_FEES,
    PROFESSIONAL_CONSULTANCY,
    PRINTING_STATIONERY,
    COURIER,
    OFFICE_SUPPLIES,
    SOFTWARE_SUBSCRIPTION,
    BANK_CHARGES,
    SALARY,
    BONUS,
    UNIFORM,
    TRAINING,
    MEDICAL_ASSISTANCE,
    STAFF_WELFARE_PROGRAM,
    INSURANCE_PREMIUM,
    GOVERNMENT_FEES,
    REGISTRATION_CHARGES,
    LICENSES,
    INSPECTION_FEES,
    STATUTORY_COMPLIANCE,
    FESTIVAL_CELEBRATION,
    ANNUAL_GENERAL_MEETING,
    SOCIETY_EVENTS,
    NOTICE_BOARD,
    DECORATIONS,
    COMMUNITY_ACTIVITIES,
    WEBSITE,
    MOBILE_APP,
    ACCESS_SOFTWARE,
    ACCOUNTING_SOFTWARE,
    CLOUD_SERVICES,
    DIGITAL_COMMUNICATION,
    SMS_EMAIL_SERVICES,
    BUILDING_PAINTING_PROJECT,
    STRUCTURAL_REPAIRS,
    TERRACE_WATERPROOFING_PROJECT,
    BUILDING_RENOVATION,
    LIFT_MODERNIZATION,
    SOLAR_INSTALLATION,
    STP_INSTALLATION_UPGRADE,
    RAINWATER_HARVESTING,
    MAJOR_CIVIL_WORKS,
    MAJOR_ELECTRICAL_WORKS,
    MAJOR_PLUMBING_WORKS,
    COMPOUND_REDEVELOPMENT,
    LANDSCAPING_PROJECT,
    INFRASTRUCTURE_UPGRADE,
)
