"""
==========================================================
SocietyOS
Payables Operating Model
Canonical Payables Knowledge Base
==========================================================

Version : 1.0
Status  : ACTIVE

This module defines the complete operational vocabulary for
payables within SocietyOS.

The Finance Kernel never invents business knowledge.

It consumes the knowledge defined here.

SCR35 hydrates from this file.

Changing this file changes the operational language of
SocietyOS and should therefore be treated as an
architectural decision.

==========================================================
"""


# ==========================================================
# Utilities
# ==========================================================

UTILITIES = {

    "definition": {

        "code": "UTILITIES",

        "name": "Utilities",

        "description":
            "Essential utility services required for the day-to-day operation of the housing society.",

        "purpose":
            "Provides uninterrupted utility services for common infrastructure and shared facilities.",

    },

    "heads": {

        "COMMON_AREA_ELECTRICITY": {

            "definition": {

                "code": "COMMON_AREA_ELECTRICITY",

                "name": "Common Area Electricity",

                "description":
                    "Electricity consumed in all common areas of the society.",

                "purpose":
                    "Powers common infrastructure including lighting, lifts, pumps and shared facilities.",

            },

            "intelligence": {

                "business": {

                    "nature": "SERVICE",

                    "default_recurring": True,

                    "default_frequency": "MONTHLY",

                    "vendor_required": True,

                    "multiple_vendors_allowed": True,

                },

                "governance": {

                    "default_approval": "SECRETARY",

                    "committee_resolution_required": False,

                },

                "funding": {

                    "default_source": "OPERATING_FUND",

                    "allowed_sources": [
                        "OPERATING_FUND",
                    ],

                },

                "accounting": {

                    "coa_code": "EXP_ELEC_COMMON",

                    "requires_vendor_control": True,

                    "requires_entity": True,

                },

                "taxation": {

                    "gst_possible": True,

                    "tds_possible": False,

                    "input_tax_credit_possible": True,

                },

                "budgeting": {

                    "budgetable": True,

                    "forecastable": True,

                    "variance_tracking": True,

                },

                "operations": {

                    "requires_contract": False,

                    "requires_invoice": True,

                    "supports_amc": False,

                    "meter_based": True,

                },

                "financial_presentation": {

                    "income_expense_statement": True,

                    "balance_sheet": False,

                    "cash_flow": "OPERATING",

                },

                "ui": {

                    "enabled_by_default": True,

                    "user_can_disable": True,

                },

            },
            

            "children": {

                "COMMON_LIGHTING": {

                    "name": "Common Lighting"

                },

                "LIFT_ELECTRICITY": {

                    "name": "Lift Electricity"

                },

                "WATER_PUMP_ELECTRICITY": {

                    "name": "Water Pump Electricity"

                },

                "GARDEN_LIGHTING": {

                    "name": "Garden Lighting"

                },

                "CLUBHOUSE_ELECTRICITY": {

                    "name": "Clubhouse Electricity"

                },

                "GENERATOR_ELECTRICITY": {

                    "name": "Generator Electricity"

                },

            },

        },

        "WATER_CHARGES": {

            "definition": {

                "code": "WATER_CHARGES",

                "name": "Water Charges",

                "description":
                    "Recurring expenditure for supplying water to the society.",

                "purpose":
                    "Ensures uninterrupted water availability for all residents.",

            },

            "intelligence": {

                "business": {

                    "nature": "UTILITY",

                    "default_recurring": True,

                    "default_frequency": "MONTHLY",

                    "vendor_required": True,

                    "multiple_vendors_allowed": True,

                },

                "governance": {

                    "default_approval": "SECRETARY",

                    "committee_resolution_required": False,

                },

                "funding": {

                    "default_source": "OPERATING_FUND",

                    "allowed_sources": [
                        "OPERATING_FUND",
                    ],

                },

                "accounting": {

                    "coa_code": "EXP_WATER",

                    "requires_vendor_control": True,

                    "requires_entity": True,

                },

                "taxation": {

                    "gst_possible": True,

                    "tds_possible": False,

                    "input_tax_credit_possible": True,

                },

                "budgeting": {

                    "budgetable": True,

                    "forecastable": True,

                    "variance_tracking": True,

                },

                "operations": {

                    "requires_invoice": True,

                    "meter_based": False,

                },

                "financial_presentation": {

                    "income_expense_statement": True,

                    "balance_sheet": False,

                    "cash_flow": "OPERATING",

                },

                "ui": {

                    "enabled_by_default": True,

                    "user_can_disable": True,

                },

            },

            "children": {

                "MUNICIPAL_WATER": {

                    "name": "Municipal Water"

                },

                "WATER_TANKERS": {

                    "name": "Water Tankers"

                },

                "BOREWELL_WATER": {

                    "name": "Borewell Water"

                },

                "WATER_TREATMENT": {

                    "name": "Water Treatment"

                },

            },

        },

        "GENERATOR_FUEL": {

            "definition": {

                "code": "GENERATOR_FUEL",

                "name": "Generator Fuel",

                "description":
                    "Fuel used for standby power generation.",

                "purpose":
                    "Maintains essential services during power outages.",

            },

            "intelligence": {

                "business": {

                    "nature": "CONSUMABLE",

                    "default_recurring": False,

                    "vendor_required": True,

                },

                "governance": {

                    "default_approval": "SECRETARY",

                },

                "funding": {

                    "default_source": "OPERATING_FUND",

                },

                "accounting": {

                    "coa_code": "EXP_GENERATOR_FUEL",

                    "requires_vendor_control": True,

                },

                "financial_presentation": {

                    "income_expense_statement": True,

                    "balance_sheet": False,

                    "cash_flow": "OPERATING",

                },

            },

            "children": {

                "DIESEL": {

                    "name": "Diesel"

                },

                "BIO_DIESEL": {

                    "name": "Bio Diesel"

                    },
                },
            },
        },

        "UTILITY_CONSUMABLES": {

            "definition": {

                "code": "UTILITY_CONSUMABLES",

                "name": "Utility Consumables",

                "description":
                    "Consumables required for operating and maintaining utility infrastructure.",

                "purpose":
                    "Provides operational materials consumed during utility maintenance and servicing.",

            },

            "intelligence": {

                "business": {

                    "nature": "CONSUMABLE",

                    "default_recurring": False,

                    "vendor_required": True,

                },

                "accounting": {

                    "coa_code": "EXP_UTILITY_CONSUMABLES",

                    "requires_vendor_control": True,

                },

                "financial_presentation": {

                    "income_expense_statement": True,

                    "balance_sheet": False,

                    "cash_flow": "OPERATING",

                },

            },

            "children": {

                "ELECTRICAL_CONSUMABLES": {
                    "name": "Electrical Consumables"
                },

                "PLUMBING_CONSUMABLES": {
                    "name": "Plumbing Consumables"
                },

                "WATER_TREATMENT_CHEMICALS": {
                    "name": "Water Treatment Chemicals"
                },

                "GENERATOR_CONSUMABLES": {
                    "name": "Generator Consumables"
                },

                "UTILITY_SPARES": {
                    "name": "Utility Spare Parts"
                },

            },

        },

    },


# ==========================================================
# Security & Safety
# ==========================================================

SECURITY_SAFETY = {

    "definition": {

        "code": "SECURITY_SAFETY",

        "name": "Security & Safety",

        "description":
            "Operational expenditure incurred to protect residents, visitors, staff and society assets.",

        "purpose":
            "Maintains the physical security, surveillance and safety infrastructure of the society.",

    },

    "heads": {

        "SECURITY_AGENCY": {

            "definition": {

                "code": "SECURITY_AGENCY",

                "name": "Security Agency",

                "description":
                    "Professional security agency providing guards and security services.",

                "purpose":
                    "Provides manned security services for the society.",

            },

            "intelligence": {

                "business": {

                    "nature": "SERVICE",

                    "default_recurring": True,

                    "default_frequency": "MONTHLY",

                    "vendor_required": True,

                    "multiple_vendors_allowed": False,

                },

                "governance": {

                    "default_approval": "SECRETARY",

                    "committee_resolution_required": False,

                },

                "funding": {

                    "default_source": "OPERATING_FUND",

                    "allowed_sources": [
                        "OPERATING_FUND",
                    ],

                },

                "accounting": {

                    "coa_code": "EXP_SECURITY",

                    "requires_vendor_control": True,

                    "requires_entity": True,

                },

                "taxation": {

                    "gst_possible": True,

                    "tds_possible": True,

                    "input_tax_credit_possible": True,

                },

                "budgeting": {

                    "budgetable": True,

                    "forecastable": True,

                    "variance_tracking": True,

                },

                "operations": {

                    "requires_contract": True,

                    "requires_invoice": True,

                    "attendance_tracking": True,

                    "service_verification": True,

                },

                "financial_presentation": {

                    "income_expense_statement": True,

                    "balance_sheet": False,

                    "cash_flow": "OPERATING",

                },

                "ui": {

                    "enabled_by_default": True,

                    "user_can_disable": True,

                },

            },

            "children": {

                "DAY_SHIFT_SECURITY": {

                    "name": "Day Shift Security"

                },

                "NIGHT_SHIFT_SECURITY": {

                    "name": "Night Shift Security"

                },

                "LADY_SECURITY_GUARD": {

                    "name": "Lady Security Guard"

                },

                "TEMPORARY_SECURITY": {

                    "name": "Temporary Security"

                },

            },

        },

        "CCTV_MAINTENANCE": {

            "definition": {

                "code": "CCTV_MAINTENANCE",

                "name": "CCTV Maintenance",

                "description":
                    "Maintenance and servicing of CCTV surveillance systems.",

                "purpose":
                    "Ensures continuous operation of surveillance infrastructure.",

            },

            "intelligence": {

                "business": {

                    "nature": "AMC",

                    "default_recurring": True,

                    "default_frequency": "YEARLY",

                    "vendor_required": True,

                },

                "governance": {

                    "default_approval": "SECRETARY",

                },

                "funding": {

                    "default_source": "OPERATING_FUND",

                },

                "accounting": {

                    "coa_code": "EXP_CCTV",

                    "requires_vendor_control": True,

                },

                "taxation": {

                    "gst_possible": True,

                    "tds_possible": True,

                },

                "budgeting": {

                    "budgetable": True,

                    "forecastable": True,

                },

                "operations": {

                    "requires_contract": True,

                    "requires_invoice": True,

                    "supports_amc": True,

                },

                "financial_presentation": {

                    "income_expense_statement": True,

                    "balance_sheet": False,

                    "cash_flow": "OPERATING",

                },

            },

            "children": {

                "AMC": {

                    "name": "Annual Maintenance Contract"

                },

                "CAMERA_REPLACEMENT": {

                    "name": "Camera Replacement"

                },

                "DVR_SERVICE": {

                    "name": "DVR / NVR Service"

                },

            },

        },

        "ACCESS_CONTROL_SYSTEM": {

            "definition": {

                "code": "ACCESS_CONTROL_SYSTEM",

                "name": "Access Control System",

                "description":
                    "Maintenance of biometric, RFID and access control systems.",

                "purpose":
                    "Controls and monitors authorised entry into society premises.",

            },

            "intelligence": {

                "business": {

                    "nature": "AMC",

                    "default_recurring": True,

                    "vendor_required": True,

                },

                "accounting": {

                    "coa_code": "EXP_ACCESS_CONTROL",

                    "requires_vendor_control": True,

                },

            },

            "children": {

                "BIOMETRIC_SYSTEM": {

                    "name": "Biometric System"

                },

                "RFID_SYSTEM": {

                    "name": "RFID Access"

                },

                "SMART_GATE_SYSTEM": {

                    "name": "Smart Gate System"

                },

            },

        },

        "FIRE_SAFETY_MAINTENANCE": {

            "definition": {

                "code": "FIRE_SAFETY_MAINTENANCE",

                "name": "Fire Safety Maintenance",

                "description":
                    "Inspection and maintenance of fire fighting equipment.",

                "purpose":
                    "Maintains statutory fire safety readiness.",

            },

            "intelligence": {

                "business": {

                    "nature": "STATUTORY_SERVICE",

                    "default_recurring": True,

                    "vendor_required": True,

                },

                "operations": {

                    "requires_compliance_certificate": True,

                    "requires_service_report": True,

                },

                "accounting": {

                    "coa_code": "EXP_FIRE",

                    "requires_vendor_control": True,

                },

            },

            "children": {

                "FIRE_EXTINGUISHERS": {

                    "name": "Fire Extinguishers"

                },

                "FIRE_PUMP": {

                    "name": "Fire Pump"

                },

                "FIRE_ALARM_SYSTEM": {

                    "name": "Fire Alarm System"

                },

                "HYDRANT_SYSTEM": {

                    "name": "Hydrant System"

                },

            },

                    "children": {

                "FIRE_EXTINGUISHERS": {

                    "name": "Fire Extinguishers"

                },

                "FIRE_PUMP": {

                    "name": "Fire Pump"

                },

                "FIRE_ALARM_SYSTEM": {

                    "name": "Fire Alarm System"

                },

                "HYDRANT_SYSTEM": {

                    "name": "Hydrant System"

                },

            },

        },

        "SECURITY_CONSUMABLES": {

            "definition": {

                "code": "SECURITY_CONSUMABLES",

                "name": "Security Consumables",

                "description":
                    "Consumables and operational supplies used by security personnel and safety operations.",

                "purpose":
                    "Supports day-to-day security operations through recurring consumable purchases.",

            },

            "intelligence": {

                "business": {

                    "nature": "CONSUMABLE",

                    "default_recurring": False,

                    "vendor_required": True,

                },

                "governance": {

                    "default_approval": "SECRETARY",

                },

                "funding": {

                    "default_source": "OPERATING_FUND",

                },

                "accounting": {

                    "coa_code": "EXP_SECURITY_CONSUMABLES",

                    "requires_vendor_control": True,

                },

                "financial_presentation": {

                    "income_expense_statement": True,

                    "balance_sheet": False,

                    "cash_flow": "OPERATING",

                },

            },

            "children": {

                "SECURITY_UNIFORMS": {

                    "name": "Security Uniforms"

                },

                "ID_CARDS": {

                    "name": "Identity Cards"

                },

                "TORCHES_AND_BATTERIES": {

                    "name": "Torches & Batteries"

                },

                "REFLECTIVE_JACKETS": {

                    "name": "Reflective Jackets"

                },

                "VISITOR_REGISTER_BOOKS": {

                    "name": "Visitor Register Books"

                },

                "WHISTLES_AND_SAFETY_ACCESSORIES": {

                    "name": "Whistles & Safety Accessories"

                },

            },

        },

    },

}


# ==========================================================
# Housekeeping & Sanitation
# ==========================================================

HOUSEKEEPING_SANITATION = {

    "definition": {

        "code": "HOUSEKEEPING_SANITATION",

        "name": "Housekeeping & Sanitation",

        "description":
            "Operational expenditure incurred for cleanliness, hygiene and sanitation of the society.",

        "purpose":
            "Maintains a clean, hygienic and healthy living environment for all residents.",

    },

    "heads": {

        "HOUSEKEEPING_SERVICES": {

            "definition": {

                "code": "HOUSEKEEPING_SERVICES",

                "name": "Housekeeping Services",

                "description":
                    "Professional housekeeping services for common areas.",

                "purpose":
                    "Provides routine cleaning of society premises.",

            },

            "intelligence": {

                "business": {

                    "nature": "SERVICE",

                    "default_recurring": True,

                    "default_frequency": "MONTHLY",

                    "vendor_required": True,

                    "multiple_vendors_allowed": False,

                },

                "governance": {

                    "default_approval": "SECRETARY",

                    "committee_resolution_required": False,

                },

                "funding": {

                    "default_source": "OPERATING_FUND",

                    "allowed_sources": [
                        "OPERATING_FUND",
                    ],

                },

                "accounting": {

                    "coa_code": "EXP_HOUSEKEEPING",

                    "requires_vendor_control": True,

                    "requires_entity": True,

                },

                "taxation": {

                    "gst_possible": True,

                    "tds_possible": True,

                    "input_tax_credit_possible": True,

                },

                "budgeting": {

                    "budgetable": True,

                    "forecastable": True,

                    "variance_tracking": True,

                },

                "operations": {

                    "requires_contract": True,

                    "requires_invoice": True,

                    "service_verification": True,

                },

                "financial_presentation": {

                    "income_expense_statement": True,

                    "balance_sheet": False,

                    "cash_flow": "OPERATING",

                },

                "ui": {

                    "enabled_by_default": True,

                    "user_can_disable": True,

                },

            },

            "children": {

                "COMMON_AREA_CLEANING": {

                    "name": "Common Area Cleaning"

                },

                "STAIRCASE_CLEANING": {

                    "name": "Staircase Cleaning"

                },

                "LOBBY_CLEANING": {

                    "name": "Lobby Cleaning"

                },

                "BASEMENT_CLEANING": {

                    "name": "Basement Cleaning"

                },

                "TERRACE_CLEANING": {

                    "name": "Terrace Cleaning"

                },

            },

        },

        "GARBAGE_COLLECTION": {

            "definition": {

                "code": "GARBAGE_COLLECTION",

                "name": "Garbage Collection",

                "description":
                    "Collection and disposal of solid waste generated by the society.",

                "purpose":
                    "Maintains proper waste disposal and environmental hygiene.",

            },

            "intelligence": {

                "business": {

                    "nature": "SERVICE",

                    "default_recurring": True,

                    "default_frequency": "MONTHLY",

                    "vendor_required": True,

                },

                "governance": {

                    "default_approval": "SECRETARY",

                },

                "funding": {

                    "default_source": "OPERATING_FUND",

                },

                "accounting": {

                    "coa_code": "EXP_GARBAGE",

                    "requires_vendor_control": True,

                },

                "taxation": {

                    "gst_possible": True,

                    "tds_possible": True,

                },

                "budgeting": {

                    "budgetable": True,

                    "forecastable": True,

                },

                "operations": {

                    "requires_contract": True,

                    "requires_invoice": True,

                },

                "financial_presentation": {

                    "income_expense_statement": True,

                    "balance_sheet": False,

                    "cash_flow": "OPERATING",

                },

            },

            "children": {

                "DAILY_COLLECTION": {

                    "name": "Daily Garbage Collection"

                },

                "BULK_WASTE_COLLECTION": {

                    "name": "Bulk Waste Collection"

                },

                "RECYCLABLE_WASTE": {

                    "name": "Recyclable Waste Disposal"

                },

            },

        },

        "PEST_CONTROL": {

            "definition": {

                "code": "PEST_CONTROL",

                "name": "Pest Control",

                "description":
                    "Periodic pest control treatment for common areas.",

                "purpose":
                    "Protects residents and infrastructure from pest infestation.",

            },

            "intelligence": {

                "business": {

                    "nature": "SERVICE",

                    "default_recurring": True,

                    "default_frequency": "QUARTERLY",

                    "vendor_required": True,

                },

                "governance": {

                    "default_approval": "SECRETARY",

                },

                "funding": {

                    "default_source": "OPERATING_FUND",

                },

                "accounting": {

                    "coa_code": "EXP_PEST_CONTROL",

                    "requires_vendor_control": True,

                },

                "operations": {

                    "requires_invoice": True,

                    "requires_service_report": True,

                },

                "financial_presentation": {

                    "income_expense_statement": True,

                    "balance_sheet": False,

                    "cash_flow": "OPERATING",

                },

            },

            "children": {

                "GENERAL_PEST_CONTROL": {

                    "name": "General Pest Control"

                },

                "TERMITE_CONTROL": {

                    "name": "Termite Control"

                },

                "MOSQUITO_CONTROL": {

                    "name": "Mosquito Control"

                },

                "RODENT_CONTROL": {

                    "name": "Rodent Control"

                },

            },

        },

        "WATER_TANK_CLEANING": {

            "definition": {

                "code": "WATER_TANK_CLEANING",

                "name": "Water Tank Cleaning",

                "description":
                    "Cleaning and sanitization of overhead and underground water tanks.",

                "purpose":
                    "Maintains potable water quality for residents.",

            },

            "intelligence": {

                "business": {

                    "nature": "SERVICE",

                    "default_recurring": True,

                    "default_frequency": "HALF_YEARLY",

                    "vendor_required": True,

                },

                "operations": {

                    "requires_completion_certificate": True,

                    "requires_invoice": True,

                },

                "accounting": {

                    "coa_code": "EXP_TANK_CLEANING",

                    "requires_vendor_control": True,

                },

                "financial_presentation": {

                    "income_expense_statement": True,

                    "balance_sheet": False,

                    "cash_flow": "OPERATING",

                },

            },

            "children": {

                "OVERHEAD_TANK": {

                    "name": "Overhead Water Tank"

                },

                "UNDERGROUND_TANK": {

                    "name": "Underground Water Tank"

                },

            },

        },

        "DRAIN_AND_SEWER_CLEANING": {

            "definition": {

                "code": "DRAIN_AND_SEWER_CLEANING",

                "name": "Drain & Sewer Cleaning",

                "description":
                    "Cleaning and maintenance of drainage and sewer networks.",

                "purpose":
                    "Prevents blockages and ensures proper wastewater flow.",

            },

            "intelligence": {

                "business": {

                    "nature": "SERVICE",

                    "default_recurring": False,

                    "vendor_required": True,

                },

                "accounting": {

                    "coa_code": "EXP_DRAIN_CLEANING",

                    "requires_vendor_control": True,

                },

                "operations": {

                    "requires_invoice": True,

                    "emergency_call_supported": True,

                },

                "financial_presentation": {

                    "income_expense_statement": True,

                    "balance_sheet": False,

                    "cash_flow": "OPERATING",

                },

            },

            "children": {

                "DRAIN_CLEANING": {

                    "name": "Drain Cleaning"

                },

                "SEWER_LINE_CLEANING": {

                    "name": "Sewer Line Cleaning"

                },

                "MANHOLE_CLEANING": {

                    "name": "Manhole Cleaning"

                },

            },

                    "children": {

                "DRAIN_CLEANING": {

                    "name": "Drain Cleaning"

                },

                "SEWER_LINE_CLEANING": {

                    "name": "Sewer Line Cleaning"

                },

                "MANHOLE_CLEANING": {

                    "name": "Manhole Cleaning"

                },

            },

        },

        "HOUSEKEEPING_CONSUMABLES": {

            "definition": {

                "code": "HOUSEKEEPING_CONSUMABLES",

                "name": "Housekeeping Consumables",

                "description":
                    "Consumables used for routine cleaning, sanitation and housekeeping operations.",

                "purpose":
                    "Provides cleaning materials and hygiene supplies required for maintaining common areas.",

            },

            "intelligence": {

                "business": {

                    "nature": "CONSUMABLE",

                    "default_recurring": True,

                    "default_frequency": "MONTHLY",

                    "vendor_required": True,

                },

                "governance": {

                    "default_approval": "SECRETARY",

                },

                "funding": {

                    "default_source": "OPERATING_FUND",

                },

                "accounting": {

                    "coa_code": "EXP_HOUSEKEEPING_CONSUMABLES",

                    "requires_vendor_control": True,

                },

                "taxation": {

                    "gst_possible": True,

                    "tds_possible": False,

                },

                "budgeting": {

                    "budgetable": True,

                    "forecastable": True,

                },

                "operations": {

                    "requires_invoice": True,

                },

                "financial_presentation": {

                    "income_expense_statement": True,

                    "balance_sheet": False,

                    "cash_flow": "OPERATING",

                },

            },

            "children": {

                "FLOOR_CLEANER": {

                    "name": "Floor Cleaner"

                },

                "TOILET_CLEANER": {

                    "name": "Toilet Cleaner"

                },

                "GLASS_CLEANER": {

                    "name": "Glass Cleaner"

                },

                "DISINFECTANT": {

                    "name": "Disinfectant"

                },

                "GARBAGE_BAGS": {

                    "name": "Garbage Bags"

                },

                "BROOMS": {

                    "name": "Brooms"

                },

                "MOPS": {

                    "name": "Mops"

                },

                "BRUSHES": {

                    "name": "Brushes"

                },

                "CLEANING_CLOTHS": {

                    "name": "Cleaning Cloths"

                },

                "AIR_FRESHENERS": {

                    "name": "Air Fresheners"

                },

                "TISSUE_PRODUCTS": {

                    "name": "Tissue Products"

                },

                "LIQUID_SOAP": {

                    "name": "Liquid Soap"

                },

                "HAND_SANITIZER": {

                    "name": "Hand Sanitizer"

                },

            },

        },

    },

}


# ==========================================================
# Repairs & Maintenance
# ==========================================================

REPAIRS_MAINTENANCE = {

    "definition": {

        "code": "REPAIRS_MAINTENANCE",

        "name": "Repairs & Maintenance",

        "description":
            "Operational expenditure incurred to preserve, repair and maintain the society's common infrastructure and services.",

        "purpose":
            "Ensures that common assets remain functional, safe and serviceable throughout their operational life.",

    },

    "heads": {

        "GENERAL_REPAIRS": {

            "definition": {

                "code": "GENERAL_REPAIRS",

                "name": "General Repairs",

                "description":
                    "Routine repairs that do not belong to a specialised maintenance category.",

                "purpose":
                    "Restores normal operation of common facilities.",

            },

            "intelligence": {

                "business": {

                    "nature": "REPAIR",

                    "default_recurring": False,

                    "vendor_required": True,

                },

                "governance": {

                    "default_approval": "SECRETARY",

                },

                "funding": {

                    "default_source": "OPERATING_FUND",

                },

                "accounting": {

                    "coa_code": "EXP_GENERAL_REPAIRS",

                    "requires_vendor_control": True,

                },

                "operations": {

                    "requires_invoice": True,

                    "supports_emergency_work": True,

                    "requires_completion_verification": True,

                },

                "financial_presentation": {

                    "income_expense_statement": True,

                    "balance_sheet": False,

                    "cash_flow": "OPERATING",

                },

            },

            "children": {

                "MASONRY": {"name": "Masonry Repairs"},

                "CARPENTRY": {"name": "Carpentry Repairs"},

                "WELDING": {"name": "Welding Repairs"},

                "LOCKSMITH": {"name": "Locksmith Services"},

            },

        },

        "BUILDING_MAINTENANCE": {

            "definition": {

                "code": "BUILDING_MAINTENANCE",

                "name": "Building Maintenance",

                "description":
                    "Maintenance of structural and architectural components of buildings.",

                "purpose":
                    "Preserves the physical condition of society buildings.",

            },

            "intelligence": {

                "business": {

                    "nature": "MAINTENANCE",

                    "default_recurring": False,

                    "vendor_required": True,

                },

                "accounting": {

                    "coa_code": "EXP_BUILDING",

                    "requires_vendor_control": True,

                },

                "financial_presentation": {

                    "income_expense_statement": True,

                    "balance_sheet": False,

                    "cash_flow": "OPERATING",

                },

            },

            "children": {

                "PLASTER_REPAIR": {"name": "Plaster Repair"},

                "LEAKAGE_REPAIR": {"name": "Leakage Repair"},

                "CRACK_REPAIR": {"name": "Crack Repair"},

                "WATERPROOFING_REPAIR": {"name": "Waterproofing Repair"},

                "PAINT_TOUCHUP": {"name": "Paint Touch-up"},

            },

        },

        "LIFT_MAINTENANCE": {

            "definition": {

                "code": "LIFT_MAINTENANCE",

                "name": "Lift Maintenance",

                "description":
                    "Routine servicing and repair of elevators.",

                "purpose":
                    "Ensures safe and uninterrupted lift operations.",

            },

            "intelligence": {

                "business": {

                    "nature": "AMC",

                    "default_recurring": True,

                    "default_frequency": "MONTHLY",

                    "vendor_required": True,

                },

                "operations": {

                    "requires_contract": True,

                    "requires_service_report": True,

                    "supports_breakdown_calls": True,

                },

                "accounting": {

                    "coa_code": "EXP_LIFT",

                    "requires_vendor_control": True,

                },

                "financial_presentation": {

                    "income_expense_statement": True,

                    "balance_sheet": False,

                    "cash_flow": "OPERATING",

                },

            },

            "children": {

                "AMC": {"name": "Annual Maintenance Contract"},

                "BREAKDOWN_SERVICE": {"name": "Breakdown Service"},

                "SPARE_PARTS": {"name": "Lift Spare Parts"},

                "SAFETY_INSPECTION": {"name": "Safety Inspection"},

            },

        },

        "PLUMBING_MAINTENANCE": {

            "definition": {

                "code": "PLUMBING_MAINTENANCE",

                "name": "Plumbing Maintenance",

            },

            "intelligence": {

                "business": {

                    "nature": "MAINTENANCE",

                    "vendor_required": True,

                },

                "accounting": {

                    "coa_code": "EXP_PLUMBING",

                    "requires_vendor_control": True,

                },

            },

            "children": {

                "PIPE_REPAIR": {"name": "Pipe Repair"},

                "VALVE_REPLACEMENT": {"name": "Valve Replacement"},

                "LEAK_REPAIR": {"name": "Leak Repair"},

                "SANITARY_FIXTURE_REPAIR": {

                    "name": "Sanitary Fixture Repair"

                },

            },

        },

        "ELECTRICAL_MAINTENANCE": {

            "definition": {

                "code": "ELECTRICAL_MAINTENANCE",

                "name": "Electrical Maintenance",

            },

            "intelligence": {

                "business": {

                    "nature": "MAINTENANCE",

                    "vendor_required": True,

                },

                "accounting": {

                    "coa_code": "EXP_ELECTRICAL",

                    "requires_vendor_control": True,

                },

            },

            "children": {

                "WIRING_REPAIR": {"name": "Wiring Repair"},

                "DISTRIBUTION_PANEL": {"name": "Distribution Panel"},

                "COMMON_SWITCHGEAR": {"name": "Common Switchgear"},

                "LIGHTING_REPAIR": {"name": "Lighting Repair"},

            },

        },

        "PUMP_MAINTENANCE": {

            "definition": {

                "code": "PUMP_MAINTENANCE",

                "name": "Pump Maintenance",

            },

            "intelligence": {

                "business": {

                    "nature": "AMC",

                    "default_recurring": True,

                    "vendor_required": True,

                },

                "accounting": {

                    "coa_code": "EXP_PUMP",

                    "requires_vendor_control": True,

                },

            },

            "children": {

                "WATER_PUMP": {"name": "Water Pump"},

                "BOOSTER_PUMP": {"name": "Booster Pump"},

                "SEWAGE_PUMP": {"name": "Sewage Pump"},

            },

        },

        "GENERATOR_MAINTENANCE": {

            "definition": {

                "code": "GENERATOR_MAINTENANCE",

                "name": "Generator Maintenance",

            },

            "intelligence": {

                "business": {

                    "nature": "AMC",

                    "default_recurring": True,

                    "vendor_required": True,

                },

                "accounting": {

                    "coa_code": "EXP_GENERATOR",

                    "requires_vendor_control": True,

                },

            },

            "children": {

                "PREVENTIVE_SERVICE": {

                    "name": "Preventive Service"

                },

                "BREAKDOWN_SERVICE": {

                    "name": "Breakdown Service"

                },

                "SPARE_PARTS": {

                    "name": "Generator Spare Parts"

                },

            },

        },

        "STP_MAINTENANCE": {

            "definition": {

                "code": "STP_MAINTENANCE",

                "name": "Sewage Treatment Plant Maintenance",

            },

            "intelligence": {

                "business": {

                    "nature": "AMC",

                    "default_recurring": True,

                    "vendor_required": True,

                },

                "accounting": {

                    "coa_code": "EXP_STP",

                    "requires_vendor_control": True,

                },

            },

            "children": {

                "PLANT_SERVICE": {

                    "name": "Plant Service"

                },

                "CHEMICAL_CALIBRATION": {

                    "name": "Chemical Calibration"

                },

                "LAB_TESTING": {

                    "name": "Laboratory Testing"

                },

            },

                    "children": {

                "PLANT_SERVICE": {

                    "name": "Plant Service"

                },

                "CHEMICAL_CALIBRATION": {

                    "name": "Chemical Calibration"

                },

                "LAB_TESTING": {

                    "name": "Laboratory Testing"

                },

            },

        },

        "REPAIR_CONSUMABLES": {

            "definition": {

                "code": "REPAIR_CONSUMABLES",

                "name": "Repair Consumables",

                "description":
                    "Materials and consumables used during repair and maintenance activities.",

                "purpose":
                    "Provides operational materials required to execute civil, plumbing, electrical and mechanical repairs.",

            },

            "intelligence": {

                "business": {

                    "nature": "CONSUMABLE",

                    "default_recurring": False,

                    "vendor_required": True,

                    "multiple_vendors_allowed": True,

                },

                "governance": {

                    "default_approval": "SECRETARY",

                },

                "funding": {

                    "default_source": "OPERATING_FUND",

                },

                "accounting": {

                    "coa_code": "EXP_REPAIR_CONSUMABLES",

                    "requires_vendor_control": True,

                },

                "taxation": {

                    "gst_possible": True,

                    "tds_possible": False,

                    "input_tax_credit_possible": True,

                },

                "budgeting": {

                    "budgetable": True,

                    "forecastable": True,

                    "variance_tracking": True,

                },

                "operations": {

                    "requires_invoice": True,

                    "supports_stock_purchase": True,

                },

                "financial_presentation": {

                    "income_expense_statement": True,

                    "balance_sheet": False,

                    "cash_flow": "OPERATING",

                },

            },

            "children": {

                "CEMENT": {

                    "name": "Cement"

                },

                "SAND": {

                    "name": "Sand"

                },

                "BRICKS": {

                    "name": "Bricks"

                },

                "PUTTY": {

                    "name": "Wall Putty"

                },

                "PAINT": {

                    "name": "Paint"

                },

                "PRIMER": {

                    "name": "Primer"

                },

                "WATERPROOFING_CHEMICALS": {

                    "name": "Waterproofing Chemicals"

                },

                "PVC_PIPES": {

                    "name": "PVC Pipes"

                },

                "PIPE_FITTINGS": {

                    "name": "Pipe Fittings"

                },

                "VALVES": {

                    "name": "Valves"

                },

                "ELECTRICAL_WIRES": {

                    "name": "Electrical Wires"

                },

                "SWITCHES_AND_MCBS": {

                    "name": "Switches & MCBs"

                },

                "LED_FIXTURES": {

                    "name": "LED Fixtures"

                },

                "FASTENERS": {

                    "name": "Fasteners"

                },

                "ADHESIVES_AND_SEALANTS": {

                    "name": "Adhesives & Sealants"

                },

                "HARDWARE_ITEMS": {

                    "name": "General Hardware"

                },

            },

        },

    },

}


# ==========================================================
# Staff & Human Resources
# ==========================================================

STAFF_HUMAN_RESOURCES = {

    "definition": {

        "code": "STAFF_HUMAN_RESOURCES",

        "name": "Staff & Human Resources",

        "description":
            "Operational expenditure relating to society employees, manpower and workforce management.",

        "purpose":
            "Supports the recruitment, employment, welfare and development of personnel engaged in society operations.",

    },

    "heads": {

        "SALARIES": {

            "definition": {

                "code": "SALARIES",

                "name": "Salaries",

                "description":
                    "Monthly salary payments made to permanent employees.",

                "purpose":
                    "Compensates permanent employees for services rendered.",

            },

            "intelligence": {

                "business": {

                    "nature": "PAYROLL",

                    "default_recurring": True,

                    "default_frequency": "MONTHLY",

                    "vendor_required": False,

                    "employee_required": True,

                },

                "governance": {

                    "default_approval": "SECRETARY",

                },

                "funding": {

                    "default_source": "OPERATING_FUND",

                },

                "accounting": {

                    "coa_code": "EXP_SALARY",

                    "requires_employee_control": True,

                },

                "taxation": {

                    "tds_possible": True,

                    "statutory_deductions_supported": True,

                },

                "budgeting": {

                    "budgetable": True,

                    "forecastable": True,

                    "variance_tracking": True,

                },

                "operations": {

                    "attendance_linked": True,

                    "payroll_linked": True,

                    "requires_payroll_run": True,

                },

                "financial_presentation": {

                    "income_expense_statement": True,

                    "balance_sheet": False,

                    "cash_flow": "OPERATING",

                },

            },

            "children": {

                "MANAGER": {
                    "name": "Society Manager"
                },

                "ADMINISTRATIVE_STAFF": {
                    "name": "Administrative Staff"
                },

                "OFFICE_ASSISTANT": {
                    "name": "Office Assistant"
                },

            },

        },

        "WAGES": {

            "definition": {

                "code": "WAGES",

                "name": "Wages",

                "description":
                    "Payments made to daily-rated or casual workers.",

                "purpose":
                    "Compensates temporary manpower engaged by the society.",

            },

            "intelligence": {

                "business": {

                    "nature": "PAYROLL",

                    "default_recurring": False,

                    "employee_required": True,

                },

                "accounting": {

                    "coa_code": "EXP_WAGES",

                    "requires_employee_control": True,

                },

            },

            "children": {

                "DAILY_WAGES": {
                    "name": "Daily Wages"
                },

                "CASUAL_LABOUR": {
                    "name": "Casual Labour"
                },

            },

        },

        "CONTRACT_LABOUR": {

            "definition": {

                "code": "CONTRACT_LABOUR",

                "name": "Contract Labour",

                "description":
                    "Payments to agencies supplying contractual manpower.",

                "purpose":
                    "Supports outsourced staffing requirements.",

            },

            "intelligence": {

                "business": {

                    "nature": "SERVICE",

                    "default_recurring": True,

                    "vendor_required": True,

                },

                "accounting": {

                    "coa_code": "EXP_CONTRACT",

                    "requires_vendor_control": True,

                },

                "taxation": {

                    "gst_possible": True,

                    "tds_possible": True,

                },

            },

            "children": {

                "HOUSEKEEPING_MANPOWER": {
                    "name": "Housekeeping Manpower"
                },

                "SECURITY_MANPOWER": {
                    "name": "Security Manpower"
                },

                "TECHNICAL_MANPOWER": {
                    "name": "Technical Manpower"
                },

            },

        },

        "STAFF_WELFARE": {

            "definition": {

                "code": "STAFF_WELFARE",

                "name": "Staff Welfare",

                "description":
                    "Employee welfare and well-being expenses.",

                "purpose":
                    "Promotes staff welfare and workplace well-being.",

            },

            "intelligence": {

                "business": {

                    "nature": "WELFARE",

                    "vendor_required": True,

                },

                "accounting": {

                    "coa_code": "EXP_STAFF_WELFARE",

                    "requires_vendor_control": True,

                },

            },

            "children": {

                "MEDICAL_ASSISTANCE": {
                    "name": "Medical Assistance"
                },

                "REFRESHMENTS": {
                    "name": "Refreshments"
                },

                "UNIFORMS": {
                    "name": "Uniforms"
                },

                "SAFETY_GEAR": {
                    "name": "Safety Gear"
                },

            },

        },

        "RECRUITMENT": {

            "definition": {

                "code": "RECRUITMENT",

                "name": "Recruitment",

            },

            "children": {

                "ADVERTISEMENT": {
                    "name": "Recruitment Advertisement"
                },

                "BACKGROUND_VERIFICATION": {
                    "name": "Background Verification"
                },

            },

        },

        "TRAINING": {

            "definition": {

                "code": "TRAINING",

                "name": "Training",

            },

            "children": {

                "SAFETY_TRAINING": {
                    "name": "Safety Training"
                },

                "TECHNICAL_TRAINING": {
                    "name": "Technical Training"
                },

            },

        },

        "OVERTIME": {

            "definition": {

                "code": "OVERTIME",

                "name": "Overtime",

            },

        },

        "BONUS": {

            "definition": {

                "code": "BONUS",

                "name": "Bonus",

            },

        },

        "EMPLOYEE_BENEFITS": {

            "definition": {

                "code": "EMPLOYEE_BENEFITS",

                "name": "Employee Benefits",

            },

            "children": {

                "LEAVE_ENCASHMENT": {
                    "name": "Leave Encashment"
                },

                "EX_GRATIA": {
                    "name": "Ex-Gratia"
                },

            },

        },

    },

}


# ==========================================================
# Administration
# ==========================================================

ADMINISTRATION = {

    "definition": {

        "code": "ADMINISTRATION",

        "name": "Administration",

        "description":
            "Operational expenditure incurred for managing the administrative functions of the society.",

        "purpose":
            "Supports the day-to-day administration, communication, documentation and office operations of the society.",

    },

    "heads": {

        "OFFICE_SUPPLIES": {

            "definition": {

                "code": "OFFICE_SUPPLIES",

                "name": "Office Supplies",

                "description":
                    "Routine office supplies consumed during society administration.",

                "purpose":
                    "Supports daily office operations.",

            },

            "intelligence": {

                "business": {

                    "nature": "CONSUMABLE",

                    "default_recurring": True,

                    "vendor_required": True,

                },

                "accounting": {

                    "coa_code": "EXP_OFFICE_SUPPLIES",

                    "requires_vendor_control": True,

                },

                "financial_presentation": {

                    "income_expense_statement": True,

                    "balance_sheet": False,

                    "cash_flow": "OPERATING",

                },

            },

            "children": {

                "STATIONERY": {

                    "name": "Stationery"

                },

                "FILES_AND_REGISTERS": {

                    "name": "Files & Registers"

                },

                "PRINTER_CONSUMABLES": {

                    "name": "Printer Consumables"

                },

                "OFFICE_MISCELLANEOUS": {

                    "name": "Miscellaneous Office Supplies"

                },

            },

        },

        "PRINTING_AND_PHOTOCOPYING": {

            "definition": {

                "code": "PRINTING_AND_PHOTOCOPYING",

                "name": "Printing & Photocopying",

            },

            "intelligence": {

                "business": {

                    "nature": "SERVICE",

                    "vendor_required": True,

                },

                "accounting": {

                    "coa_code": "EXP_PRINTING",

                    "requires_vendor_control": True,

                },

            },

            "children": {

                "NOTICE_PRINTING": {

                    "name": "Notice Printing"

                },

                "DOCUMENT_PRINTING": {

                    "name": "Document Printing"

                },

                "PHOTOCOPYING": {

                    "name": "Photocopying"

                },

                "LAMINATION": {

                    "name": "Lamination"

                },

            },

        },

        "COURIER_AND_POSTAGE": {

            "definition": {

                "code": "COURIER_AND_POSTAGE",

                "name": "Courier & Postage",

            },

            "intelligence": {

                "business": {

                    "nature": "SERVICE",

                    "vendor_required": True,

                },

                "accounting": {

                    "coa_code": "EXP_POSTAGE",

                    "requires_vendor_control": True,

                },

            },

            "children": {

                "REGISTERED_POST": {

                    "name": "Registered Post"

                },

                "SPEED_POST": {

                    "name": "Speed Post"

                },

                "COURIER_SERVICE": {

                    "name": "Courier Service"

                },

            },

        },

        "SOFTWARE_SUBSCRIPTIONS": {

            "definition": {

                "code": "SOFTWARE_SUBSCRIPTIONS",

                "name": "Software Subscriptions",

            },

            "intelligence": {

                "business": {

                    "nature": "SUBSCRIPTION",

                    "default_recurring": True,

                    "vendor_required": True,

                },

                "accounting": {

                    "coa_code": "EXP_SOFTWARE",

                    "requires_vendor_control": True,

                },

            },

            "children": {

                "ACCOUNTING_SOFTWARE": {

                    "name": "Accounting Software"

                },

                "SOCIETY_MANAGEMENT_SOFTWARE": {

                    "name": "Society Management Software"

                },

                "EMAIL_SERVICES": {

                    "name": "Email Services"

                },

                "DIGITAL_SIGNATURE": {

                    "name": "Digital Signature Services"

                },

            },

        },

        "CLOUD_AND_HOSTING": {

            "definition": {

                "code": "CLOUD_AND_HOSTING",

                "name": "Cloud & Hosting",

            },

            "intelligence": {

                "business": {

                    "nature": "SUBSCRIPTION",

                    "default_recurring": True,

                    "vendor_required": True,

                },

                "accounting": {

                    "coa_code": "EXP_CLOUD",

                    "requires_vendor_control": True,

                },

            },

            "children": {

                "CLOUD_HOSTING": {

                    "name": "Cloud Hosting"

                },

                "DOMAIN_REGISTRATION": {

                    "name": "Domain Registration"

                },

                "SSL_CERTIFICATES": {

                    "name": "SSL Certificates"

                },

                "BACKUP_SERVICES": {

                    "name": "Backup Services"

                },

            },

        },

        "COMPUTER_MAINTENANCE": {

            "definition": {

                "code": "COMPUTER_MAINTENANCE",

                "name": "Computer Maintenance",

            },

            "intelligence": {

                "business": {

                    "nature": "SERVICE",

                    "vendor_required": True,

                },

                "accounting": {

                    "coa_code": "EXP_COMPUTER",

                    "requires_vendor_control": True,

                },

            },

            "children": {

                "HARDWARE_REPAIR": {

                    "name": "Hardware Repair"

                },

                "SOFTWARE_SUPPORT": {

                    "name": "Software Support"

                },

                "AMC": {

                    "name": "Computer AMC"

                },

            },

        },

        "COMMUNICATION_EXPENSES": {

            "definition": {

                "code": "COMMUNICATION_EXPENSES",

                "name": "Communication Expenses",

            },

            "intelligence": {

                "business": {

                    "nature": "SERVICE",

                    "default_recurring": True,

                    "vendor_required": True,

                },

                "accounting": {

                    "coa_code": "EXP_COMMUNICATION",

                    "requires_vendor_control": True,

                },

            },

            "children": {

                "MOBILE_CONNECTIONS": {

                    "name": "Mobile Connections"

                },

                "OFFICE_TELEPHONE": {

                    "name": "Office Telephone"

                },

                "SMS_SERVICES": {

                    "name": "SMS Services"

                },

            },

        },

        "WEBSITE_AND_DIGITAL_PRESENCE": {

            "definition": {

                "code": "WEBSITE_AND_DIGITAL_PRESENCE",

                "name": "Website & Digital Presence",

            },

            "intelligence": {

                "business": {

                    "nature": "SERVICE",

                    "vendor_required": True,

                },

                "accounting": {

                    "coa_code": "EXP_WEBSITE",

                    "requires_vendor_control": True,

                },

            },

            "children": {

                "WEBSITE_MAINTENANCE": {

                    "name": "Website Maintenance"

                },

                "CONTENT_UPDATES": {

                    "name": "Content Updates"

                },

            },

        },

    },

}


# ==========================================================
# Legal, Audit & Compliance
# ==========================================================

LEGAL_AUDIT_COMPLIANCE = {

    "definition": {

        "code": "LEGAL_AUDIT_COMPLIANCE",

        "name": "Legal, Audit & Compliance",

        "description":
            "Professional, statutory and governance-related services required to maintain legal and regulatory compliance.",

        "purpose":
            "Ensures the society fulfills its legal, statutory and governance obligations through qualified professionals and regulatory filings.",

    },

    "heads": {

        "STATUTORY_AUDIT": {

            "definition": {

                "code": "STATUTORY_AUDIT",

                "name": "Statutory Audit",

                "description":
                    "Annual statutory audit conducted by an appointed auditor.",

                "purpose":
                    "Provides independent certification of the society's financial statements.",

            },

            "intelligence": {

                "business": {

                    "nature": "PROFESSIONAL_SERVICE",

                    "default_recurring": True,

                    "default_frequency": "YEARLY",

                    "vendor_required": True,

                },

                "governance": {

                    "default_approval": "GENERAL_BODY",

                    "committee_resolution_required": True,

                },

                "funding": {

                    "default_source": "OPERATING_FUND",

                },

                "accounting": {

                    "coa_code": "EXP_STAT_AUDIT",

                    "requires_vendor_control": True,

                },

                "taxation": {

                    "gst_possible": True,

                    "tds_possible": True,

                },

                "operations": {

                    "requires_engagement_letter": True,

                    "requires_invoice": True,

                    "requires_audit_report": True,

                },

                "financial_presentation": {

                    "income_expense_statement": True,

                    "balance_sheet": False,

                    "cash_flow": "OPERATING",

                },

            },

            "children": {

                "ANNUAL_STATUTORY_AUDIT": {

                    "name": "Annual Statutory Audit"

                },

                "SPECIAL_AUDIT": {

                    "name": "Special Audit"

                },

            },

        },

        "INTERNAL_AUDIT": {

            "definition": {

                "code": "INTERNAL_AUDIT",

                "name": "Internal Audit",

            },

            "intelligence": {

                "business": {

                    "nature": "PROFESSIONAL_SERVICE",

                    "vendor_required": True,

                },

                "accounting": {

                    "coa_code": "EXP_INTERNAL_AUDIT",

                    "requires_vendor_control": True,

                },

            },

        },

        "LEGAL_SERVICES": {

            "definition": {

                "code": "LEGAL_SERVICES",

                "name": "Legal Services",

            },

            "intelligence": {

                "business": {

                    "nature": "PROFESSIONAL_SERVICE",

                    "vendor_required": True,

                },

                "accounting": {

                    "coa_code": "EXP_LEGAL",

                    "requires_vendor_control": True,

                },

                "taxation": {

                    "gst_possible": True,

                    "tds_possible": True,

                },

            },

            "children": {

                "LEGAL_CONSULTATION": {

                    "name": "Legal Consultation"

                },

                "LITIGATION": {

                    "name": "Litigation"

                },

                "DOCUMENT_DRAFTING": {

                    "name": "Document Drafting"

                },

                "NOTICE_PREPARATION": {

                    "name": "Notice Preparation"

                },

            },

        },

        "PROFESSIONAL_CONSULTANCY": {

            "definition": {

                "code": "PROFESSIONAL_CONSULTANCY",

                "name": "Professional Consultancy",

            },

            "children": {

                "CHARTERED_ACCOUNTANT": {

                    "name": "Chartered Accountant"

                },

                "COMPANY_SECRETARY": {

                    "name": "Company Secretary"

                },

                "ARCHITECT": {

                    "name": "Architect"

                },

                "ENGINEERING_CONSULTANT": {

                    "name": "Engineering Consultant"

                },

                "VALUER": {

                    "name": "Government Approved Valuer"

                },

            },

        },

        "REGISTRAR_AND_GOVERNMENT_FILINGS": {

            "definition": {

                "code": "REGISTRAR_AND_GOVERNMENT_FILINGS",

                "name": "Registrar & Government Filings",

            },

            "children": {

                "REGISTRAR_FEES": {

                    "name": "Registrar Fees"

                },

                "CERTIFIED_COPIES": {

                    "name": "Certified Copies"

                },

                "DOCUMENT_REGISTRATION": {

                    "name": "Document Registration"

                },

                "ONLINE_FILING_CHARGES": {

                    "name": "Online Filing Charges"

                },

            },

        },

        "COMPLIANCE_CERTIFICATION": {

            "definition": {

                "code": "COMPLIANCE_CERTIFICATION",

                "name": "Compliance Certification",

            },

            "children": {

                "FIRE_COMPLIANCE": {

                    "name": "Fire Compliance"

                },

                "STRUCTURAL_CERTIFICATION": {

                    "name": "Structural Certification"

                },

                "LIFT_CERTIFICATION": {

                    "name": "Lift Certification"

                },

                "ELECTRICAL_CERTIFICATION": {

                    "name": "Electrical Certification"

                },

            },

        },

        "DOCUMENTATION_AND_RECORDS": {

            "definition": {

                "code": "DOCUMENTATION_AND_RECORDS",

                "name": "Documentation & Records",

            },

            "children": {

                "DOCUMENT_SCANNING": {

                    "name": "Document Scanning"

                },

                "RECORD_DIGITIZATION": {

                    "name": "Record Digitization"

                },

                "ARCHIVAL_SERVICES": {

                    "name": "Archival Services"

                },

            },

                    "children": {

                "DOCUMENT_SCANNING": {

                    "name": "Document Scanning"

                },

                "RECORD_DIGITIZATION": {

                    "name": "Record Digitization"

                },

                "ARCHIVAL_SERVICES": {

                    "name": "Archival Services"

                },

            },

        },

        "LEGAL_DOCUMENTATION_MATERIALS": {

            "definition": {

                "code": "LEGAL_DOCUMENTATION_MATERIALS",

                "name": "Legal Documentation Materials",

                "description":
                    "Statutory materials and documentation required for governance, legal compliance and official society records.",

                "purpose":
                    "Supports execution of statutory documentation, legal records and governance processes.",

            },

            "intelligence": {

                "business": {

                    "nature": "DOCUMENTATION",

                    "default_recurring": False,

                    "vendor_required": True,

                },

                "governance": {

                    "default_approval": "SECRETARY",

                    "committee_resolution_required": False,

                },

                "funding": {

                    "default_source": "OPERATING_FUND",

                },

                "accounting": {

                    "coa_code": "EXP_LEGAL_DOCUMENTATION",

                    "requires_vendor_control": True,

                },

                "taxation": {

                    "gst_possible": True,

                    "tds_possible": False,

                },

                "budgeting": {

                    "budgetable": True,

                    "forecastable": True,

                },

                "operations": {

                    "requires_invoice": True,

                },

                "financial_presentation": {

                    "income_expense_statement": True,

                    "balance_sheet": False,

                    "cash_flow": "OPERATING",

                },

            },

            "children": {

                "STAMP_PAPER": {

                    "name": "Stamp Paper"

                },

                "E_STAMP_CHARGES": {

                    "name": "E-Stamp Charges"

                },

                "NOTARIAL_CHARGES": {

                    "name": "Notarial Charges"

                },

                "SHARE_CERTIFICATE_STATIONERY": {

                    "name": "Share Certificate Stationery"

                },

                "BYLAW_PRINTING": {

                    "name": "By-law Printing"

                },

                "MEMBERSHIP_FORMS": {

                    "name": "Membership Forms"

                },

                "NOMINATION_FORMS": {

                    "name": "Nomination Forms"

                },

                "TRANSFER_FORMS": {

                    "name": "Transfer Forms"

                },

                "STATUTORY_REGISTERS": {

                    "name": "Statutory Registers"

                },

                "MINUTE_BOOKS": {

                    "name": "Minute Books"

                },

                "SOCIETY_RECORD_BOOKS": {

                    "name": "Society Record Books"

                },

                "OFFICIAL_SEAL_AND_RUBBER_STAMPS": {

                    "name": "Official Seal & Rubber Stamps"

                },

            },

        },

    },

}


# ==========================================================
# Financial Expenses
# ==========================================================

FINANCIAL_EXPENSES = {

    "definition": {

        "code": "FINANCIAL_EXPENSES",

        "name": "Financial Expenses",

        "description":
            "Operational expenditure incurred for banking, payment processing and financial services.",

        "purpose":
            "Supports the society's banking relationships, payment infrastructure and financing activities.",

    },

    "heads": {

        "BANK_CHARGES": {

            "definition": {

                "code": "BANK_CHARGES",

                "name": "Bank Charges",

                "description":
                    "Routine service charges levied by banks.",

                "purpose":
                    "Covers operational banking costs incurred by the society.",

            },

            "intelligence": {

                "business": {

                    "nature": "BANKING_SERVICE",

                    "default_recurring": True,

                    "vendor_required": True,

                },

                "governance": {

                    "default_approval": "TREASURER",

                },

                "funding": {

                    "default_source": "OPERATING_FUND",

                },

                "accounting": {

                    "coa_code": "EXP_BANK",

                    "requires_vendor_control": False,

                },

                "financial_presentation": {

                    "income_expense_statement": True,

                    "balance_sheet": False,

                    "cash_flow": "OPERATING",

                },

            },

            "children": {

                "ACCOUNT_MAINTENANCE": {

                    "name": "Account Maintenance Charges"

                },

                "SMS_ALERTS": {

                    "name": "SMS Alert Charges"

                },

                "NEFT_RTGS_CHARGES": {

                    "name": "NEFT / RTGS Charges"

                },

                "IMPS_CHARGES": {

                    "name": "IMPS Charges"

                },

                "CHEQUE_BOOK_CHARGES": {

                    "name": "Cheque Book Charges"

                },

            },

        },

        "INTEREST_PAID": {

            "definition": {

                "code": "INTEREST_PAID",

                "name": "Interest Paid",

            },

            "intelligence": {

                "business": {

                    "nature": "FINANCE_COST",

                    "vendor_required": True,

                },

                "accounting": {

                    "coa_code": "EXP_INTEREST",

                    "requires_vendor_control": False,

                },

            },

            "children": {

                "BANK_LOAN_INTEREST": {

                    "name": "Bank Loan Interest"

                },

                "OVERDRAFT_INTEREST": {

                    "name": "Overdraft Interest"

                },

                "LATE_PAYMENT_INTEREST": {

                    "name": "Late Payment Interest"

                },

            },

        },

        "PAYMENT_GATEWAY_CHARGES": {

            "definition": {

                "code": "PAYMENT_GATEWAY_CHARGES",

                "name": "Payment Gateway Charges",

            },

            "intelligence": {

                "business": {

                    "nature": "FINANCIAL_SERVICE",

                    "default_recurring": True,

                    "vendor_required": True,

                },

                "accounting": {

                    "coa_code": "EXP_PAYMENT_GATEWAY",

                    "requires_vendor_control": True,

                },

            },

            "children": {

                "UPI_GATEWAY_FEES": {

                    "name": "UPI Gateway Fees"

                },

                "CARD_PROCESSING_FEES": {

                    "name": "Card Processing Fees"

                },

                "NET_BANKING_FEES": {

                    "name": "Net Banking Processing Fees"

                },

                "PAYMENT_COLLECTION_CHARGES": {

                    "name": "Payment Collection Charges"

                },

            },

        },

        "CHEQUE_PROCESSING": {

            "definition": {

                "code": "CHEQUE_PROCESSING",

                "name": "Cheque Processing",

            },

            "children": {

                "CHEQUE_CLEARING": {

                    "name": "Cheque Clearing Charges"

                },

                "CHEQUE_RETURN": {

                    "name": "Cheque Return Charges"

                },

                "STOP_PAYMENT": {

                    "name": "Stop Payment Charges"

                },

            },

        },

        "LOAN_PROCESSING": {

            "definition": {

                "code": "LOAN_PROCESSING",

                "name": "Loan Processing",

            },

            "children": {

                "PROCESSING_FEES": {

                    "name": "Loan Processing Fees"

                },

                "DOCUMENTATION_FEES": {

                    "name": "Loan Documentation Fees"

                },

                "VALUATION_FEES": {

                    "name": "Loan Valuation Charges"

                },

            },

        },

        "FINANCIAL_SERVICE_CHARGES": {

            "definition": {

                "code": "FINANCIAL_SERVICE_CHARGES",

                "name": "Financial Service Charges",

            },

            "children": {

                "BANK_CERTIFICATES": {

                    "name": "Bank Certificates"

                },

                "BANK_GUARANTEE_CHARGES": {

                    "name": "Bank Guarantee Charges"

                },

                "ESCROW_SERVICES": {

                    "name": "Escrow Service Charges"

                },

                "FINANCIAL_CONSULTANCY": {

                    "name": "Financial Consultancy"

                },

            },

        },

    },

}


# ==========================================================
# Insurance & Risk Management
# ==========================================================

INSURANCE_RISK_MANAGEMENT = {

    "definition": {

        "code": "INSURANCE_RISK_MANAGEMENT",

        "name": "Insurance & Risk Management",

        "description":
            "Operational expenditure incurred to protect the society against financial, legal and operational risks.",

        "purpose":
            "Transfers insurable risks from the society to approved insurance providers.",

    },

    "heads": {

        "BUILDING_INSURANCE": {

            "definition": {

                "code": "BUILDING_INSURANCE",

                "name": "Building Insurance",

                "description":
                    "Insurance covering society buildings and permanent structures.",

                "purpose":
                    "Protects society buildings against insured risks such as fire, natural calamities and accidental damage.",

            },

            "intelligence": {

                "business": {

                    "nature": "INSURANCE",

                    "default_recurring": True,

                    "default_frequency": "YEARLY",

                    "vendor_required": True,

                },

                "governance": {

                    "default_approval": "MANAGING_COMMITTEE",

                    "committee_resolution_required": True,

                },

                "funding": {

                    "default_source": "OPERATING_FUND",

                },

                "accounting": {

                    "coa_code": "EXP_BUILDING_INSURANCE",

                    "requires_vendor_control": True,

                },

                "operations": {

                    "requires_policy_document": True,

                    "requires_policy_expiry_tracking": True,

                    "supports_claim_management": True,

                },

                "financial_presentation": {

                    "income_expense_statement": True,

                    "balance_sheet": False,

                    "cash_flow": "OPERATING",

                },

            },

            "children": {

                "FIRE_POLICY": {

                    "name": "Fire Insurance"

                },

                "NATURAL_DISASTER_COVER": {

                    "name": "Natural Disaster Cover"

                },

                "SPECIAL_PERILS": {

                    "name": "Special Perils Cover"

                },

            },

        },

        "EQUIPMENT_INSURANCE": {

            "definition": {

                "code": "EQUIPMENT_INSURANCE",

                "name": "Equipment Insurance",

            },

            "intelligence": {

                "business": {

                    "nature": "INSURANCE",

                    "default_recurring": True,

                    "vendor_required": True,

                },

                "accounting": {

                    "coa_code": "EXP_EQUIPMENT_INSURANCE",

                    "requires_vendor_control": True,

                },

            },

            "children": {

                "LIFT_INSURANCE": {

                    "name": "Lift Insurance"

                },

                "GENERATOR_INSURANCE": {

                    "name": "Generator Insurance"

                },

                "PUMP_INSURANCE": {

                    "name": "Pump Insurance"

                },

                "STP_INSURANCE": {

                    "name": "STP Insurance"

                },

            },

        },

        "EMPLOYEE_INSURANCE": {

            "definition": {

                "code": "EMPLOYEE_INSURANCE",

                "name": "Employee Insurance",

            },

            "intelligence": {

                "business": {

                    "nature": "INSURANCE",

                    "vendor_required": True,

                },

                "accounting": {

                    "coa_code": "EXP_EMPLOYEE_INSURANCE",

                    "requires_vendor_control": True,

                },

            },

            "children": {

                "GROUP_MEDICAL": {

                    "name": "Group Medical Insurance"

                },

                "GROUP_ACCIDENT": {

                    "name": "Group Personal Accident"

                },

            },

        },

        "PUBLIC_LIABILITY_INSURANCE": {

            "definition": {

                "code": "PUBLIC_LIABILITY_INSURANCE",

                "name": "Public Liability Insurance",

            },

            "intelligence": {

                "business": {

                    "nature": "INSURANCE",

                    "vendor_required": True,

                },

                "accounting": {

                    "coa_code": "EXP_PUBLIC_LIABILITY",

                    "requires_vendor_control": True,

                },

            },

            "children": {

                "THIRD_PARTY_CLAIMS": {

                    "name": "Third Party Liability"

                },

            },

        },

        "FIDELITY_INSURANCE": {

            "definition": {

                "code": "FIDELITY_INSURANCE",

                "name": "Fidelity Insurance",

            },

            "intelligence": {

                "business": {

                    "nature": "INSURANCE",

                    "vendor_required": True,

                },

                "accounting": {

                    "coa_code": "EXP_FIDELITY",

                    "requires_vendor_control": True,

                },

            },

            "children": {

                "EMPLOYEE_FIDELITY": {

                    "name": "Employee Fidelity Guarantee"

                },

                "OFFICE_BEARER_FIDELITY": {

                    "name": "Committee Fidelity Cover"

                },

            },

        },

        "CYBER_AND_DIGITAL_RISK": {

            "definition": {

                "code": "CYBER_AND_DIGITAL_RISK",

                "name": "Cyber & Digital Risk Insurance",

            },

            "intelligence": {

                "business": {

                    "nature": "INSURANCE",

                    "vendor_required": True,

                },

                "accounting": {

                    "coa_code": "EXP_CYBER_INSURANCE",

                    "requires_vendor_control": True,

                },

            },

            "children": {

                "CYBER_SECURITY_POLICY": {

                    "name": "Cyber Security Insurance"

                },

                "DATA_BREACH_COVER": {

                    "name": "Data Breach Cover"

                },

            },

        },

        "OTHER_RISK_COVERS": {

            "definition": {

                "code": "OTHER_RISK_COVERS",

                "name": "Other Risk Covers",

            },

            "children": {

                "DIRECTORS_AND_OFFICERS": {

                    "name": "Directors & Officers Liability"

                },

                "TERRORISM_COVER": {

                    "name": "Terrorism Cover"

                },

                "MACHINERY_BREAKDOWN": {

                    "name": "Machinery Breakdown Insurance"

                },

            },

        },

    },

}


# ==========================================================
# Community & Welfare
# ==========================================================

COMMUNITY_WELFARE = {

    "definition": {

        "code": "COMMUNITY_WELFARE",

        "name": "Community & Welfare",

        "description":
            "Operational expenditure incurred for resident engagement, cultural activities, welfare initiatives and community development.",

        "purpose":
            "Promotes community participation, resident welfare and social harmony within the society.",

    },

    "heads": {

        "CULTURAL_EVENTS": {

            "definition": {

                "code": "CULTURAL_EVENTS",

                "name": "Cultural Events",

                "description":
                    "Society-sponsored cultural programmes and celebrations.",

                "purpose":
                    "Encourages resident participation through cultural activities.",

            },

            "intelligence": {

                "business": {

                    "nature": "COMMUNITY_ACTIVITY",

                    "default_recurring": False,

                    "vendor_required": True,

                },

                "governance": {

                    "default_approval": "MANAGING_COMMITTEE",

                    "committee_resolution_required": True,

                },

                "funding": {

                    "default_source": "OPERATING_FUND",

                },

                "accounting": {

                    "coa_code": "EXP_CULTURAL_EVENTS",

                    "requires_vendor_control": True,

                },

                "financial_presentation": {

                    "income_expense_statement": True,

                    "balance_sheet": False,

                    "cash_flow": "OPERATING",

                },

            },

            "children": {

                "INDEPENDENCE_DAY": {
                    "name": "Independence Day"
                },

                "REPUBLIC_DAY": {
                    "name": "Republic Day"
                },

                "FOUNDATION_DAY": {
                    "name": "Society Foundation Day"
                },

                "ANNUAL_DAY": {
                    "name": "Annual Day"
                },

            },

        },

        "FESTIVAL_CELEBRATIONS": {

            "definition": {

                "code": "FESTIVAL_CELEBRATIONS",

                "name": "Festival Celebrations",

            },

            "intelligence": {

                "business": {

                    "nature": "COMMUNITY_ACTIVITY",

                    "vendor_required": True,

                },

                "accounting": {

                    "coa_code": "EXP_FESTIVALS",

                    "requires_vendor_control": True,

                },

            },

            "children": {

                "GANESH_FESTIVAL": {
                    "name": "Ganesh Festival"
                },

                "DIWALI": {
                    "name": "Diwali"
                },

                "HOLI": {
                    "name": "Holi"
                },

                "NAVRATRI": {
                    "name": "Navratri"
                },

                "CHRISTMAS": {
                    "name": "Christmas"
                },

                "EID": {
                    "name": "Eid"
                },

                "NEW_YEAR": {
                    "name": "New Year Celebration"
                },

            },

        },

        "SPORTS_AND_RECREATION": {

            "definition": {

                "code": "SPORTS_AND_RECREATION",

                "name": "Sports & Recreation",

            },

            "intelligence": {

                "business": {

                    "nature": "COMMUNITY_ACTIVITY",

                    "vendor_required": True,

                },

                "accounting": {

                    "coa_code": "EXP_SPORTS",

                    "requires_vendor_control": True,

                },

            },

            "children": {

                "SPORTS_EVENTS": {
                    "name": "Sports Events"
                },

                "TOURNAMENTS": {
                    "name": "Sports Tournaments"
                },

                "FITNESS_PROGRAMMES": {
                    "name": "Fitness Programmes"
                },

                "CHILDREN_ACTIVITIES": {
                    "name": "Children Activities"
                },

            },

        },

        "CLUBHOUSE_AND_SOCIAL_EVENTS": {

            "definition": {

                "code": "CLUBHOUSE_AND_SOCIAL_EVENTS",

                "name": "Clubhouse & Social Events",

            },

            "intelligence": {

                "business": {

                    "nature": "COMMUNITY_ACTIVITY",

                    "vendor_required": True,

                },

                "accounting": {

                    "coa_code": "EXP_CLUBHOUSE_EVENTS",

                    "requires_vendor_control": True,

                },

            },

            "children": {

                "COMMUNITY_MEETINGS": {
                    "name": "Community Meetings"
                },

                "RESIDENT_PROGRAMMES": {
                    "name": "Resident Programmes"
                },

                "WORKSHOPS": {
                    "name": "Workshops & Awareness Sessions"
                },

            },

        },

        "WELFARE_ACTIVITIES": {

            "definition": {

                "code": "WELFARE_ACTIVITIES",

                "name": "Welfare Activities",

            },

            "intelligence": {

                "business": {

                    "nature": "COMMUNITY_WELFARE",

                    "vendor_required": True,

                },

                "accounting": {

                    "coa_code": "EXP_WELFARE",

                    "requires_vendor_control": True,

                },

            },

            "children": {

                "SENIOR_CITIZEN_PROGRAMMES": {
                    "name": "Senior Citizen Programmes"
                },

                "HEALTH_CAMPS": {
                    "name": "Health Camps"
                },

                "BLOOD_DONATION": {
                    "name": "Blood Donation Camps"
                },

                "EMERGENCY_ASSISTANCE": {
                    "name": "Emergency Welfare"
                },

            },

        },

        "COMMUNITY_CONSUMABLES": {

            "definition": {

                "code": "COMMUNITY_CONSUMABLES",

                "name": "Community Consumables",

                "description":
                    "Consumables used during community programmes and welfare activities.",

            },

            "intelligence": {

                "business": {

                    "nature": "CONSUMABLE",

                    "vendor_required": True,

                },

                "accounting": {

                    "coa_code": "EXP_COMMUNITY_CONSUMABLES",

                    "requires_vendor_control": True,

                },

            },

            "children": {

                "DECORATION_MATERIAL": {
                    "name": "Decoration Material"
                },

                "STAGE_SETUP": {
                    "name": "Stage Setup Materials"
                },

                "BANNERS": {
                    "name": "Banners & Signage"
                },

                "PRIZES_AND_TROPHIES": {
                    "name": "Prizes & Trophies"
                },

                "EVENT_STATIONERY": {
                    "name": "Event Stationery"
                },

                "REFRESHMENTS": {
                    "name": "Refreshments"
                },

            },

        },

    },

}


# ==========================================================
# Miscellaneous
# ==========================================================

MISCELLANEOUS = {

    "definition": {

        "code": "MISCELLANEOUS",

        "name": "Miscellaneous",

        "description":
            "Operational expenditure that genuinely does not belong to any defined payable category.",

        "purpose":
            "Captures exceptional and infrequent operational expenditure while encouraging proper classification elsewhere.",

    },

    "heads": {

        "DONATIONS": {

            "definition": {

                "code": "DONATIONS",

                "name": "Donations",

            },

            "intelligence": {

                "business": {

                    "nature": "DISCRETIONARY",

                    "vendor_required": False,

                },

                "governance": {

                    "default_approval": "GENERAL_BODY",

                    "committee_resolution_required": True,

                },

                "accounting": {

                    "coa_code": "EXP_DONATIONS",

                },

            },

        },

        "PENALTIES_AND_FINES": {

            "definition": {

                "code": "PENALTIES_AND_FINES",

                "name": "Penalties & Fines",

            },

            "intelligence": {

                "business": {

                    "nature": "NON_ROUTINE",

                },

                "accounting": {

                    "coa_code": "EXP_PENALTIES",

                },

            },

            "children": {

                "MUNICIPAL_FINE": {

                    "name": "Municipal Fine"

                },

                "REGULATORY_PENALTY": {

                    "name": "Regulatory Penalty"

                },

                "CONTRACTUAL_PENALTY": {

                    "name": "Contractual Penalty"

                },

            },

        },

        "EXCEPTIONAL_OPERATIONAL_EXPENSE": {

            "definition": {

                "code": "EXCEPTIONAL_OPERATIONAL_EXPENSE",

                "name": "Exceptional Operational Expense",

            },

            "intelligence": {

                "business": {

                    "nature": "EXCEPTION",

                },

                "governance": {

                    "committee_resolution_required": True,

                },

                "accounting": {

                    "coa_code": "EXP_EXCEPTIONAL",

                },

            },

        },

    },

}


# ==========================================================
# Major Works & Projects
# ==========================================================

MAJOR_WORKS_PROJECTS = {

    "definition": {

        "code": "MAJOR_WORKS_PROJECTS",

        "name": "Major Works & Projects",

        "description":
            "Large-scale capital and infrastructure projects requiring enhanced governance, budgeting and execution controls.",

        "purpose":
            "Supports long-term preservation, enhancement and development of society infrastructure.",

    },

    "heads": {

        "STRUCTURAL_REPAIRS": {

            "definition": {

                "code": "STRUCTURAL_REPAIRS",

                "name": "Structural Repairs",

            },

            "intelligence": {

                "business": {

                    "nature": "CAPITAL_PROJECT",

                    "default_recurring": False,

                    "vendor_required": True,

                },

                "governance": {

                    "default_approval": "GENERAL_BODY",

                    "committee_resolution_required": True,

                    "tender_required": True,

                },

                "funding": {

                    "default_source": "SINKING_FUND",

                    "allowed_sources": [

                        "SINKING_FUND",

                        "SPECIAL_LEVY",

                        "BANK_LOAN",

                    ],

                },

                "operations": {

                    "project_based": True,

                    "milestone_billing": True,

                    "completion_certificate": True,

                    "retention_supported": True,

                },

            },

        },

        "BUILDING_PAINTING": {},

        "WATERPROOFING_PROJECTS": {},

        "LIFT_MODERNIZATION": {},

        "SOLAR_INSTALLATION": {},

        "INFRASTRUCTURE_UPGRADES": {},

        "MAJOR_RENOVATION": {},

        "CAPITAL_IMPROVEMENTS": {},

        "NEW_EQUIPMENT_INSTALLATION": {},

    },

}

