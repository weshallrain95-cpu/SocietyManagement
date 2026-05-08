from society.finance.kernel.account_factory import get_or_create_account


EXPENSE_ACCOUNT_MAP = {

    # ⚡ OPERATIONS
    "COMMON_ELECTRICITY": {
        "code": "EXP_ELEC_COMMON",
        "name": "Common Area Electricity",
        "requires_entity": False,
    },
    "WATER": {
        "code": "EXP_WATER",
        "name": "Water Charges",
        "requires_entity": False,
    },
    "SECURITY": {
        "code": "EXP_SECURITY",
        "name": "Security Expenses",
        "requires_entity": True,
    },
    "CLEANING": {
        "code": "EXP_CLEANING",
        "name": "Cleaning Expenses",
        "requires_entity": True,
    },
    "GARBAGE_COLLECTION": {
        "code": "EXP_GARBAGE",
        "name": "Garbage Collection",
        "requires_entity": True,
    },
    "FACILITY_MANAGEMENT": {
        "code": "EXP_FM",
        "name": "Facility Management",
        "requires_entity": True,
    },
    "LANDSCAPING": {
        "code": "EXP_LANDSCAPE",
        "name": "Landscaping",
        "requires_entity": True,
    },

    # 🔧 MAINTENANCE
    "REPAIRS": {
        "code": "EXP_REPAIRS",
        "name": "General Repairs",
        "requires_entity": True,
    },
    "BUILDING_REPAIRS": {
        "code": "EXP_BUILDING",
        "name": "Building Repairs",
        "requires_entity": True,
    },
    "INFRASTRUCTURE_MAINTENANCE": {
        "code": "EXP_INFRA",
        "name": "Infrastructure Maintenance",
        "requires_entity": True,
    },
    "AMC": {
        "code": "EXP_AMC",
        "name": "Annual Maintenance Contracts",
        "requires_entity": True,
    },
    "EQUIPMENT_MAINTENANCE": {
        "code": "EXP_EQUIP",
        "name": "Equipment Maintenance",
        "requires_entity": True,
    },
    "LIFT_MAINTENANCE": {
        "code": "EXP_LIFT",
        "name": "Lift Maintenance",
        "requires_entity": True,
    },
    "FIRE_SAFETY_MAINTENANCE": {
        "code": "EXP_FIRE",
        "name": "Fire Safety Maintenance",
        "requires_entity": True,
    },
    "PLUMBING": {
        "code": "EXP_PLUMBING",
        "name": "Plumbing Work",
        "requires_entity": True,
    },
    "ELECTRICAL_REPAIRS": {
        "code": "EXP_ELECTRICAL",
        "name": "Electrical Repairs",
        "requires_entity": True,
    },

    # 👷 STAFF
    "SALARY": {
        "code": "EXP_SALARY",
        "name": "Salary Expenses",
        "requires_entity": False,
    },
    "WAGES": {
        "code": "EXP_WAGES",
        "name": "Wages",
        "requires_entity": False,
    },
    "BONUS": {
        "code": "EXP_BONUS",
        "name": "Bonus",
        "requires_entity": False,
    },
    "CONTRACT_LABOUR": {
        "code": "EXP_CONTRACT",
        "name": "Contract Labour",
        "requires_entity": True,
    },

    # 🏦 FINANCIAL
    "BANK_CHARGES": {
        "code": "EXP_BANK",
        "name": "Bank Charges",
        "requires_entity": False,
    },
    "INTEREST_PAID": {
        "code": "EXP_INTEREST",
        "name": "Interest Paid",
        "requires_entity": False,
    },

    # 🧾 STATUTORY
    "PROPERTY_TAX": {
        "code": "EXP_TAX",
        "name": "Property Tax",
        "requires_entity": False,
    },
    "INSURANCE": {
        "code": "EXP_INSURANCE",
        "name": "Insurance",
        "requires_entity": False,
    },
    "LICENSE_FEES": {
        "code": "EXP_LICENSE",
        "name": "License Fees",
        "requires_entity": False,
    },
    "GOVERNMENT_FEES": {
        "code": "EXP_GOVT",
        "name": "Government Fees",
        "requires_entity": False,
    },

    # 🎁 OTHER
    "MISC_EXPENSE": {
        "code": "EXP_MISC",
        "name": "Miscellaneous Expense",
        "requires_entity": False,
    },
}


def get_expense_account(*, society, subtype):
    """
    Returns or creates expense account based on subtype.
    """

    if subtype not in EXPENSE_ACCOUNT_MAP:
        raise ValueError(f"Invalid expense subtype: {subtype}")

    config = EXPENSE_ACCOUNT_MAP[subtype]

    return get_or_create_account(
        society=society,
        code=config["code"],
        name=config["name"],
        account_type="EXPENSE",
        account_category="EXPENSE",
        subtype=subtype,
        is_postable=True,
        requires_entity=config["requires_entity"],
    )