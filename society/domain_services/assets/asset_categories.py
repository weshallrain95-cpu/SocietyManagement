# ==========================================================
# Asset Operating Model
# Lifts & Vertical Transportation
# ==========================================================

LIFTS_AND_VERTICAL_TRANSPORT = {

    "definition": {

        "code": "LIFTS_AND_VERTICAL_TRANSPORT",

        "name": "Lifts & Vertical Transportation",

        "description":
            "Vertical transportation assets owned and operated by the society.",

        "purpose":
            "Provides safe movement of residents, visitors and goods between floors.",

    },

    "asset_types": {

        "PASSENGER_LIFT": {

            "definition": {

                "code": "PASSENGER_LIFT",

                "name": "Passenger Lift",

                "description":
                    "Passenger elevator installed for resident movement.",

            },

            "intelligence": {

                "classification": {

                    "asset_class": "INFRASTRUCTURE",

                    "criticality": "HIGH",

                    "movable": False,

                    "depreciable": True,

                    "requires_asset_tag": True,

                },

                "operations": {

                    "requires_location": True,

                    "supports_amc": True,

                    "supports_warranty": True,

                    "supports_breakdown_history": True,

                    "supports_service_history": True,

                    "supports_insurance": True,

                },

                "governance": {

                    "requires_installation_date": True,

                    "requires_vendor": True,

                    "requires_serial_number": True,

                },

            },

            "components": {

                "LIFT_CAR": {
                    "name": "Lift Car"
                },

                "LIFT_CONTROLLER": {
                    "name": "Lift Controller"
                },

                "MACHINE": {
                    "name": "Lift Machine"
                },

                "DOOR_SYSTEM": {
                    "name": "Door System"
                },

                "CONTROL_PANEL": {
                    "name": "Control Panel"
                },

                "ARD_SYSTEM": {
                    "name": "Automatic Rescue Device"
                },

            },

        },

        "SERVICE_LIFT": {

            "definition": {

                "code": "SERVICE_LIFT",

                "name": "Service Lift",

            },

        },

        "CAR_LIFT": {

            "definition": {

                "code": "CAR_LIFT",

                "name": "Car Lift",

            },

        },

        "ESCALATOR": {

            "definition": {

                "code": "ESCALATOR",

                "name": "Escalator",

            },

        },

    },

}


# ==========================================================
# Electrical Infrastructure
# ==========================================================

ELECTRICAL_INFRASTRUCTURE = {

    "definition": {

        "code": "ELECTRICAL_INFRASTRUCTURE",

        "name": "Electrical Infrastructure",

        "description":
            "Electrical assets owned and operated by the society for supplying and distributing power.",

        "purpose":
            "Supports uninterrupted electrical infrastructure for common facilities and services.",

    },

    "asset_types": {

        "DIESEL_GENERATOR": {

            "definition": {

                "code": "DIESEL_GENERATOR",

                "name": "Diesel Generator",

                "description":
                    "Standby power generation equipment.",

            },

            "intelligence": {

                "classification": {

                    "asset_class": "INFRASTRUCTURE",

                    "criticality": "HIGH",

                    "movable": False,

                    "depreciable": True,

                    "requires_asset_tag": True,

                },

                "operations": {

                    "requires_location": True,

                    "supports_amc": True,

                    "supports_warranty": True,

                    "supports_breakdown_history": True,

                    "supports_service_history": True,

                    "supports_insurance": True,

                    "supports_running_hours": True,

                },

                "governance": {

                    "requires_installation_date": True,

                    "requires_vendor": True,

                    "requires_serial_number": True,

                },

            },

            "components": {

                "ENGINE": {

                    "name": "Engine"

                },

                "ALTERNATOR": {

                    "name": "Alternator"

                },

                "CONTROL_PANEL": {

                    "name": "Control Panel"

                },

                "BATTERY": {

                    "name": "Starting Battery"

                },

                "FUEL_TANK": {

                    "name": "Fuel Tank"

                },

                "EXHAUST_SYSTEM": {

                    "name": "Exhaust System"

                },

            },

        },

        "MAIN_LT_PANEL": {

            "definition": {

                "code": "MAIN_LT_PANEL",

                "name": "Main LT Panel",

            },

            "intelligence": {

                "classification": {

                    "asset_class": "INFRASTRUCTURE",

                    "criticality": "HIGH",

                    "movable": False,

                    "depreciable": True,

                    "requires_asset_tag": True,

                },

            },

        },

        "DISTRIBUTION_PANEL": {

            "definition": {

                "code": "DISTRIBUTION_PANEL",

                "name": "Distribution Panel",

            },

        },

        "TRANSFORMER": {

            "definition": {

                "code": "TRANSFORMER",

                "name": "Transformer",

            },

        },

        "CAPACITOR_BANK": {

            "definition": {

                "code": "CAPACITOR_BANK",

                "name": "Capacitor Bank",

            },

        },

        "ELECTRICAL_METER": {

            "definition": {

                "code": "ELECTRICAL_METER",

                "name": "Electrical Meter",

            },

        },

        "UPS_SYSTEM": {

            "definition": {

                "code": "UPS_SYSTEM",

                "name": "UPS System",

            },

        },

        "INVERTER_SYSTEM": {

            "definition": {

                "code": "INVERTER_SYSTEM",

                "name": "Inverter System",

            },

        },

        "SOLAR_POWER_SYSTEM": {

            "definition": {

                "code": "SOLAR_POWER_SYSTEM",

                "name": "Solar Power System",

            },

        },

    },

}


# ==========================================================
# Water Systems
# ==========================================================

WATER_SYSTEMS = {

    "definition": {

        "code": "WATER_SYSTEMS",

        "name": "Water Systems",

        "description":
            "Water storage, pumping, treatment and distribution assets owned by the society.",

        "purpose":
            "Supports uninterrupted supply, storage, treatment and distribution of water throughout the society.",

    },

    "asset_types": {

        "DOMESTIC_WATER_PUMP": {

            "definition": {

                "code": "DOMESTIC_WATER_PUMP",

                "name": "Domestic Water Pump",

                "description":
                    "Pump used for domestic water supply.",

            },

            "intelligence": {

                "classification": {

                    "asset_class": "INFRASTRUCTURE",

                    "criticality": "HIGH",

                    "movable": False,

                    "depreciable": True,

                    "requires_asset_tag": True,

                },

                "operations": {

                    "requires_location": True,

                    "supports_amc": True,

                    "supports_warranty": True,

                    "supports_breakdown_history": True,

                    "supports_service_history": True,

                    "supports_running_hours": True,

                    "supports_insurance": True,

                },

                "governance": {

                    "requires_installation_date": True,

                    "requires_vendor": True,

                    "requires_serial_number": True,

                },

            },

            "components": {

                "MOTOR": {

                    "name": "Motor"

                },

                "PUMP": {

                    "name": "Pump Assembly"

                },

                "CONTROL_PANEL": {

                    "name": "Control Panel"

                },

                "PRESSURE_GAUGE": {

                    "name": "Pressure Gauge"

                },

                "VALVES": {

                    "name": "Valves"

                },

            },

        },

        "BOOSTER_PUMP": {

            "definition": {

                "code": "BOOSTER_PUMP",

                "name": "Booster Pump",

            },

        },

        "SUBMERSIBLE_PUMP": {

            "definition": {

                "code": "SUBMERSIBLE_PUMP",

                "name": "Submersible Pump",

            },

        },

        "OVERHEAD_WATER_TANK": {

            "definition": {

                "code": "OVERHEAD_WATER_TANK",

                "name": "Overhead Water Tank",

            },

        },

        "UNDERGROUND_WATER_TANK": {

            "definition": {

                "code": "UNDERGROUND_WATER_TANK",

                "name": "Underground Water Tank",

            },

        },

        "HYDROPNEUMATIC_SYSTEM": {

            "definition": {

                "code": "HYDROPNEUMATIC_SYSTEM",

                "name": "Hydropneumatic System",

            },

        },

        "WATER_SOFTENING_PLANT": {

            "definition": {

                "code": "WATER_SOFTENING_PLANT",

                "name": "Water Softening Plant",

            },

        },

        "WATER_FILTRATION_PLANT": {

            "definition": {

                "code": "WATER_FILTRATION_PLANT",

                "name": "Water Filtration Plant",

            },

        },

        "STP_PLANT": {

            "definition": {

                "code": "STP_PLANT",

                "name": "Sewage Treatment Plant",

            },

        },

        "RAINWATER_HARVESTING_SYSTEM": {

            "definition": {

                "code": "RAINWATER_HARVESTING_SYSTEM",

                "name": "Rainwater Harvesting System",

            },

        },

        "WATER_METERS": {

            "definition": {

                "code": "WATER_METERS",

                "name": "Water Meter",

            },

        },

        "PIPE_NETWORK": {

            "definition": {

                "code": "PIPE_NETWORK",

                "name": "Water Distribution Network",

            },

        },

    },

}


# ==========================================================
# Fire Safety Systems
# ==========================================================

FIRE_SAFETY_SYSTEMS = {

    "definition": {

        "code": "FIRE_SAFETY_SYSTEMS",

        "name": "Fire Safety Systems",

        "description":
            "Fire prevention, detection, suppression and emergency response assets owned by the society.",

        "purpose":
            "Protects life and property through statutory fire safety infrastructure.",

    },

    "asset_types": {

        "FIRE_EXTINGUISHER": {

            "definition": {

                "code": "FIRE_EXTINGUISHER",

                "name": "Fire Extinguisher",

                "description":
                    "Portable fire suppression equipment.",

            },

            "intelligence": {

                "classification": {

                    "asset_class": "SAFETY",

                    "criticality": "CRITICAL",

                    "movable": True,

                    "depreciable": True,

                    "requires_asset_tag": True,

                },

                "operations": {

                    "requires_location": True,

                    "supports_amc": True,

                    "supports_warranty": True,

                    "supports_service_history": True,

                    "supports_inspection_schedule": True,

                    "supports_expiry_tracking": True,

                },

                "governance": {

                    "requires_installation_date": True,

                    "requires_vendor": True,

                    "requires_serial_number": True,

                    "requires_fire_audit": True,

                },

            },

            "components": {

                "CYLINDER": {

                    "name": "Cylinder"

                },

                "PRESSURE_GAUGE": {

                    "name": "Pressure Gauge"

                },

                "DISCHARGE_HOSE": {

                    "name": "Discharge Hose"

                },

                "NOZZLE": {

                    "name": "Nozzle"

                },

                "SAFETY_PIN": {

                    "name": "Safety Pin"

                },

            },

        },

        "FIRE_HYDRANT_SYSTEM": {

            "definition": {

                "code": "FIRE_HYDRANT_SYSTEM",

                "name": "Fire Hydrant System",

            },

        },

        "FIRE_PUMP": {

            "definition": {

                "code": "FIRE_PUMP",

                "name": "Fire Pump",

            },

        },

        "JOCKEY_PUMP": {

            "definition": {

                "code": "JOCKEY_PUMP",

                "name": "Jockey Pump",

            },

        },

        "SPRINKLER_SYSTEM": {

            "definition": {

                "code": "SPRINKLER_SYSTEM",

                "name": "Automatic Sprinkler System",

            },

        },

        "FIRE_ALARM_SYSTEM": {

            "definition": {

                "code": "FIRE_ALARM_SYSTEM",

                "name": "Fire Alarm System",

            },

        },

        "SMOKE_DETECTOR": {

            "definition": {

                "code": "SMOKE_DETECTOR",

                "name": "Smoke Detector",

            },

        },

        "HEAT_DETECTOR": {

            "definition": {

                "code": "HEAT_DETECTOR",

                "name": "Heat Detector",

            },

        },

        "MANUAL_CALL_POINT": {

            "definition": {

                "code": "MANUAL_CALL_POINT",

                "name": "Manual Call Point",

            },

        },

        "HOOTER_AND_SIREN": {

            "definition": {

                "code": "HOOTER_AND_SIREN",

                "name": "Hooter & Siren",

            },

        },

        "EXIT_SIGNAGE": {

            "definition": {

                "code": "EXIT_SIGNAGE",

                "name": "Emergency Exit Signage",

            },

        },

        "EMERGENCY_LIGHTING": {

            "definition": {

                "code": "EMERGENCY_LIGHTING",

                "name": "Emergency Lighting",

            },

        },

        "FIRE_CONTROL_PANEL": {

            "definition": {

                "code": "FIRE_CONTROL_PANEL",

                "name": "Fire Control Panel",

            },

        },

        "FIRE_WATER_STORAGE": {

            "definition": {

                "code": "FIRE_WATER_STORAGE",

                "name": "Fire Water Storage Tank",

            },

        },

    },

}


# ==========================================================
# Security & Surveillance Systems
# ==========================================================

SECURITY_SURVEILLANCE = {

    "definition": {

        "code": "SECURITY_SURVEILLANCE",

        "name": "Security & Surveillance Systems",

        "description":
            "Security, access control and surveillance assets owned and operated by the society.",

        "purpose":
            "Protects residents, visitors and common property through monitoring, access control and security infrastructure.",

    },

    "asset_types": {

        "CCTV_CAMERA": {

            "definition": {

                "code": "CCTV_CAMERA",

                "name": "CCTV Camera",

                "description":
                    "Fixed or PTZ surveillance camera.",

            },

            "intelligence": {

                "classification": {

                    "asset_class": "SECURITY",

                    "criticality": "HIGH",

                    "movable": False,

                    "depreciable": True,

                    "requires_asset_tag": True,

                },

                "operations": {

                    "requires_location": True,

                    "supports_amc": True,

                    "supports_warranty": True,

                    "supports_service_history": True,

                    "supports_breakdown_history": True,

                    "supports_insurance": True,

                },

                "governance": {

                    "requires_installation_date": True,

                    "requires_vendor": True,

                    "requires_serial_number": True,

                },

            },

            "components": {

                "CAMERA_BODY": {

                    "name": "Camera Body"

                },

                "LENS": {

                    "name": "Lens"

                },

                "MOUNTING_BRACKET": {

                    "name": "Mounting Bracket"

                },

                "POWER_SUPPLY": {

                    "name": "Power Supply"

                },

                "NETWORK_MODULE": {

                    "name": "Network Module"

                },

            },

        },

        "NETWORK_VIDEO_RECORDER": {

            "definition": {

                "code": "NETWORK_VIDEO_RECORDER",

                "name": "Network Video Recorder (NVR)",

            },

        },

        "DIGITAL_VIDEO_RECORDER": {

            "definition": {

                "code": "DIGITAL_VIDEO_RECORDER",

                "name": "Digital Video Recorder (DVR)",

            },

        },

        "VIDEO_MANAGEMENT_SERVER": {

            "definition": {

                "code": "VIDEO_MANAGEMENT_SERVER",

                "name": "Video Management Server",

            },

        },

        "ACCESS_CONTROL_SYSTEM": {

            "definition": {

                "code": "ACCESS_CONTROL_SYSTEM",

                "name": "Access Control System",

            },

        },

        "BIOMETRIC_ACCESS_SYSTEM": {

            "definition": {

                "code": "BIOMETRIC_ACCESS_SYSTEM",

                "name": "Biometric Access System",

            },

        },

        "RFID_ACCESS_SYSTEM": {

            "definition": {

                "code": "RFID_ACCESS_SYSTEM",

                "name": "RFID Access System",

            },

        },

        "BOOM_BARRIER": {

            "definition": {

                "code": "BOOM_BARRIER",

                "name": "Boom Barrier",

            },

        },

        "VIDEO_DOOR_PHONE": {

            "definition": {

                "code": "VIDEO_DOOR_PHONE",

                "name": "Video Door Phone",

            },

        },

        "INTERCOM_SYSTEM": {

            "definition": {

                "code": "INTERCOM_SYSTEM",

                "name": "Intercom System",

            },

        },

        "GUARD_PATROL_SYSTEM": {

            "definition": {

                "code": "GUARD_PATROL_SYSTEM",

                "name": "Guard Patrol System",

            },

        },

        "VISITOR_MANAGEMENT_KIOSK": {

            "definition": {

                "code": "VISITOR_MANAGEMENT_KIOSK",

                "name": "Visitor Management Kiosk",

            },

        },

        "METAL_DETECTOR": {

            "definition": {

                "code": "METAL_DETECTOR",

                "name": "Metal Detector",

            },

        },

    },

}

# ==========================================================
# Movable Assets
# ==========================================================

MOVABLE_ASSETS = {

    "definition": {

        "code": "MOVABLE_ASSETS",

        "name": "Movable Assets",

        "description":
            "Movable operational assets owned and managed by the society.",

        "purpose":
            "Supports day-to-day society operations through movable assets and equipment.",

    },

    "asset_types": {

        "OFFICE_FURNITURE": {

            "definition": {

                "code": "OFFICE_FURNITURE",

                "name": "Office Furniture",

            },

        },

        "COMPUTER": {

            "definition": {

                "code": "COMPUTER",

                "name": "Computer",

            },

        },

        "PRINTER": {

            "definition": {

                "code": "PRINTER",

                "name": "Printer",

            },

        },

        "NOTICE_BOARD": {

            "definition": {

                "code": "NOTICE_BOARD",

                "name": "Notice Board",

            },

        },

        "FURNITURE": {

            "definition": {

                "code": "FURNITURE",

                "name": "Furniture",

            },

        },

        "GARDEN_EQUIPMENT": {

            "definition": {

                "code": "GARDEN_EQUIPMENT",

                "name": "Garden Equipment",

            },

        },

        "GYM_EQUIPMENT": {

            "definition": {

                "code": "GYM_EQUIPMENT",

                "name": "Gym Equipment",

            },

        },

        "PLAYGROUND_EQUIPMENT": {

            "definition": {

                "code": "PLAYGROUND_EQUIPMENT",

                "name": "Playground Equipment",

            },

        },

        "PLANTS_TREES": {

            "definition": {

                "code": "PLANTS_TREES",

                "name": "Plants & Trees",

            },

        },

        "IRRIGATION_EQUIPMENT": {

            "definition": {

                "code": "IRRIGATION_EQUIPMENT",

                "name": "Irrigation Equipment",

            },

        },

    },

}

# ==========================================================
# Asset Registry
# ==========================================================
#
# Canonical registry of every supported asset family.
#
# This registry is the single entry point for:
#
# - Asset Factory
# - Asset Intelligence
# - Asset Validation
# - Asset Search
# - Asset Registry
#
# New asset families MUST be registered here.
#
# ==========================================================

ASSET_CATEGORY_REGISTRY = {
    "LIFTS_AND_VERTICAL_TRANSPORT": LIFTS_AND_VERTICAL_TRANSPORT,
    "ELECTRICAL_INFRASTRUCTURE": ELECTRICAL_INFRASTRUCTURE,
    "WATER_SYSTEMS": WATER_SYSTEMS,
    "FIRE_SAFETY_SYSTEMS": FIRE_SAFETY_SYSTEMS,
    "SECURITY_SURVEILLANCE": SECURITY_SURVEILLANCE,
    "MOVABLE_ASSETS": MOVABLE_ASSETS,
}
