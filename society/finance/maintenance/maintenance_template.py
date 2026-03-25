from society.finance.maintenance.bylaw_mapping import BYLAW_MAINTENANCE_MAP
from society.models import MaintenanceCharge

MAINTENANCE_TEMPLATE = [

    {"code": "SERVICE_CHARGES", "name": "Service Charges", "basis": "EQUAL"},
    {"code": "REPAIR_FUND", "name": "Repair Fund", "basis": "AREA"},
    {"code": "SINKING_FUND", "name": "Sinking Fund", "basis": "AREA"},
    {"code": "COMMON_ELECTRICITY", "name": "Common Electricity", "basis": "EQUAL"},
    {"code": "WATER_CHARGES", "name": "Water Charges", "basis": "PER_INLET"},
    {"code": "PARKING_CHARGES", "name": "Parking Charges", "basis": "PER_SLOT"},
    {"code": "NON_OCCUPANCY", "name": "Non Occupancy Charges", "basis": "PERCENT_MAINT"},
    {"code": "INSURANCE", "name": "Insurance Charges", "basis": "AREA"},
    {"code": "EDUCATION_FUND", "name": "Education & Training Fund", "basis": "PER_FLAT"},
    {"code": "ELECTION_FUND", "name": "Election Fund", "basis": "PER_FLAT"},
]

def seed_maintenance_template(society):

    for code, data in BYLAW_MAINTENANCE_MAP.items():

        MaintenanceCharge.objects.get_or_create(

            society=society,
            code=code,

            defaults={
                "name": data["name"],
                "basis": data["basis"],
                "rate": 0,
            },
        )

