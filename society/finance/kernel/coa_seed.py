from society.models import ChartOfAccount
from django.db import transaction

@transaction.atomic
def seed_core_coa(society):
    
    """
    Seeds core Chart of Accounts for a society.
    Idempotent and safe to run multiple times.
    """

    CORE_ACCOUNTS = [

        # 🏦 ASSETS
        {
            "code": "CASH_MAIN",
            "name": "Cash in Hand",
            "account_type": "ASSET",
            "account_category": "CASH",
            "subtype": None,
            "system_account": "CASH_ON_HAND",
            "is_postable": True,
            "requires_entity": False,
        },
        {
            "code": "BANK_MAIN",
            "name": "Bank Account (Primary)",
            "account_type": "ASSET",
            "account_category": "BANK",
            "subtype": None,
            "system_account": "BANK_FUNDS",
            "is_postable": True,
            "requires_entity": False,
        },

        # 📥 MEMBER CONTROL
        {
            "code": "MEMBER_RECEIVABLES",
            "name": "Member Receivables",
            "account_type": "ASSET",
            "account_category": "MEMBER",
            "subtype": None,
            "system_account": "MEMBER_RECEIVABLES",
            "is_postable": False,
            "requires_entity": True,
        },

        # 📤 VENDOR CONTROL
        {
            "code": "VENDOR_PAYABLES",
            "name": "Vendor Payables",
            "account_type": "LIABILITY",
            "account_category": "VENDOR",
            "subtype": None,
            "system_account": "VENDOR_PAYABLES",
            "is_postable": False,
            "requires_entity": True,
        },

        # 💰 INCOME
        {
            "code": "MAINT_CHARGES",
            "name": "Maintenance Charges",
            "account_type": "INCOME",
            "account_category": "INCOME",
            "subtype": "MAINTENANCE",
            "system_account": "MAINTENANCE_INCOME",
            "is_postable": True,
            "requires_entity": True,
        },

        # 📉 EXPENSES
        {
            "code": "ELECTRICITY_EXP",
            "name": "Electricity Expense",
            "account_type": "EXPENSE",
            "account_category": "EXPENSE",
            "subtype": None,
            "system_account": "UTILITY_EXPENSE",
            "is_postable": True,
            "requires_entity": False,
        },
        {
            "code": "SALARY_EXP",
            "name": "Salary Expense",
            "account_type": "EXPENSE",
            "account_category": "EXPENSE",
            "subtype": None,
            "system_account": "ADMINISTRATIVE_EXPENSE",
            "is_postable": True,
            "requires_entity": False,
        },

        # 🧾 TAX
        {
            "code": "GST_OUTPUT_PAYABLE",
            "name": "GST Output Payable",
            "account_type": "LIABILITY",
            "account_category": "GENERAL",
            "subtype": None,
            "is_postable": True,
            "requires_entity": False,
        },

        # 🏛 EQUITY

        {
            "code": "SHARE_CAPITAL",
            "name": "Share Capital",
            "account_type": "EQUITY",
            "account_category": "FUND",
            "subtype": None,
            "equity_type": "SHARE_CAPITAL",
            "is_postable": True,
            "requires_entity": False,
        },
        {
            "code": "CORPUS_FUND",
            "name": "Corpus Fund",
            "account_type": "EQUITY",
            "account_category": "FUND",
            "subtype": None,
            "equity_type": "CORPUS_FUND",
            "is_postable": True,
            "requires_entity": False,
        },
        {
            "code": "SINKING_FUND",
            "name": "Sinking Fund",
            "account_type": "EQUITY",
            "account_category": "FUND",
            "subtype": None,
            "equity_type": "SINKING_FUND",
            "is_postable": True,
            "requires_entity": False,
        },
        {
            "code": "REPAIR_FUND",
            "name": "Repair Fund",
            "account_type": "EQUITY",
            "account_category": "FUND",
            "subtype": None,
            "equity_type": "REPAIR_FUND",
            "is_postable": True,
            "requires_entity": False,
        },
        {
            "code": "RETAINED_EARNINGS",
            "name": "Retained Earnings",
            "account_type": "EQUITY",
            "account_category": "FUND",
            "subtype": None,
            "equity_type": "RETAINED_EARNINGS",
            "is_postable": True,
            "requires_entity": False,
        },

    ]

    for acc in CORE_ACCOUNTS:
        obj, created = ChartOfAccount.objects.get_or_create(
            society=society,
            code=acc["code"],
            defaults={
                "name": acc["name"],
                "account_type": acc["account_type"],
                "account_category": acc["account_category"],
                "subtype": acc["subtype"],
                "equity_type": acc.get("equity_type"),
                "system_account": acc.get("system_account"),
                "is_postable": acc["is_postable"],
                "requires_entity": acc["requires_entity"],
                "is_system": True,
                "is_active": True,
            },
        )

        # 🔒 Safety update (only controlled fields)
        if not created:
            updated = False

            if obj.account_type != acc["account_type"]:
                obj.account_type = acc["account_type"]
                updated = True

            if obj.account_category != acc["account_category"]:
                obj.account_category = acc["account_category"]
                updated = True

            if obj.subtype != acc["subtype"]:
                obj.subtype = acc["subtype"]
                updated = True

            if obj.equity_type != acc.get("equity_type"):
                obj.equity_type = acc.get("equity_type")
                updated = True

            if obj.system_account != acc.get("system_account"):
                obj.system_account = acc.get("system_account")
                updated = True

            if obj.name != acc["name"]:
                obj.name = acc["name"]
                updated = True

            if obj.is_system is False:
                obj.is_system = True
                updated = True

            if obj.is_active is False:
                obj.is_active = True
                updated = True

            # Enforce control accounts
            if acc["code"] in ["MEMBER_RECEIVABLES", "VENDOR_PAYABLES"]:
                if obj.is_postable is True:
                    obj.is_postable = False
                    updated = True
                if obj.requires_entity is False:
                    obj.requires_entity = True
                    updated = True

            if updated:
                obj.save()

    return True