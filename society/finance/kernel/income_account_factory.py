from society.finance.kernel.account_factory import get_or_create_account


INCOME_ACCOUNT_MAP = {

    # 🧍 MEMBER CORE
    "MAINTENANCE": {
        "code": "INC_MAINT",
        "name": "Maintenance Charges",
        "requires_entity": True,
    },
    "WATER_CHARGES": {
        "code": "INC_WATER",
        "name": "Water Charges",
        "requires_entity": True,
    },
    "ELECTRICITY_RECOVERY": {
        "code": "INC_ELECTRICITY",
        "name": "Electricity Recovery",
        "requires_entity": True,
    },
    "SERVICE_CHARGES": {
        "code": "INC_SERVICE",
        "name": "Service Charges",
        "requires_entity": True,
    },
    "NON_OCCUPANCY": {
        "code": "INC_NON_OCC",
        "name": "Non-Occupancy Charges",
        "requires_entity": True,
    },
    "PARKING": {
        "code": "INC_PARKING",
        "name": "Parking Charges",
        "requires_entity": True,
    },
    "TRANSFER_FEES": {
        "code": "INC_TRANSFER",
        "name": "Transfer Fees",
        "requires_entity": True,
    },
    "INTEREST_ON_DUES": {
        "code": "INC_INTEREST",
        "name": "Interest on Dues",
        "requires_entity": True,
    },
    "PENALTY": {
        "code": "INC_PENALTY",
        "name": "Penalty Charges",
        "requires_entity": True,
    },
    "SINKING_FUND_CONTRIBUTION": {
        "code": "INC_SINKING",
        "name": "Sinking Fund Contribution",
        "requires_entity": True,
    },
    "REPAIR_FUND_CONTRIBUTION": {
        "code": "INC_REPAIR",
        "name": "Repair Fund Contribution",
        "requires_entity": True,
    },

    # 🏊 AMENITIES
    "GYM": {
        "code": "INC_GYM",
        "name": "Gym Fees",
        "requires_entity": False,
    },
    "SWIMMING_POOL": {
        "code": "INC_POOL",
        "name": "Swimming Pool Fees",
        "requires_entity": False,
    },
    "CLUBHOUSE": {
        "code": "INC_CLUB",
        "name": "Clubhouse Charges",
        "requires_entity": False,
    },
    "HALL_BOOKING": {
        "code": "INC_HALL",
        "name": "Hall Booking Charges",
        "requires_entity": False,
    },
    "SPORTS": {
        "code": "INC_SPORTS",
        "name": "Sports Facility Charges",
        "requires_entity": False,
    },

    # 🏢 COMMERCIAL
    "TOWER_RENT": {
        "code": "INC_TOWER",
        "name": "Tower Rent",
        "requires_entity": False,
    },
    "ADVERTISEMENT": {
        "code": "INC_ADS",
        "name": "Advertisement Income",
        "requires_entity": False,
    },
    "SHOP_RENT": {
        "code": "INC_SHOP",
        "name": "Shop Rent",
        "requires_entity": False,
    },
    "ATM_RENT": {
        "code": "INC_ATM",
        "name": "ATM Rent",
        "requires_entity": False,
    },
    "SOLAR_LEASE": {
        "code": "INC_SOLAR",
        "name": "Solar Lease Income",
        "requires_entity": False,
    },

    # 🏦 FINANCIAL
    "BANK_INTEREST": {
        "code": "INC_BANK_INT",
        "name": "Bank Interest",
        "requires_entity": False,
    },
    "FD_INTEREST": {
        "code": "INC_FD_INT",
        "name": "FD Interest",
        "requires_entity": False,
    },
    "INVESTMENT_INCOME": {
        "code": "INC_INVEST",
        "name": "Investment Income",
        "requires_entity": False,
    },

    # 🔧 SERVICE
    "DOCUMENT_CHARGES": {
        "code": "INC_DOC",
        "name": "Document Charges",
        "requires_entity": False,
    },
    "NOC_FEES": {
        "code": "INC_NOC",
        "name": "NOC Fees",
        "requires_entity": False,
    },
    "SERVICE_CHARGES_MISC": {
        "code": "INC_MISC_SERVICE",
        "name": "Misc Service Charges",
        "requires_entity": False,
    },

    # 🎁 OTHER
    "DONATIONS": {
        "code": "INC_DONATION",
        "name": "Donations",
        "requires_entity": False,
    },
    "SCRAP_SALE": {
        "code": "INC_SCRAP",
        "name": "Scrap Sale",
        "requires_entity": False,
    },
    "MISC_INCOME": {
        "code": "INC_MISC",
        "name": "Miscellaneous Income",
        "requires_entity": False,
    },
}


def get_income_account(*, society, subtype):
    """
    Returns or creates income account based on subtype.
    """

    if subtype not in INCOME_ACCOUNT_MAP:
        raise ValueError(f"Invalid income subtype: {subtype}")

    config = INCOME_ACCOUNT_MAP[subtype]

    return get_or_create_account(
        society=society,
        code=config["code"],
        name=config["name"],
        account_type="INCOME",
        account_category="INCOME",
        subtype=subtype,
        is_postable=True,
        requires_entity=config["requires_entity"],
    )