from bylaws.models import BylawClause

HOOK_PATTERNS = {

    "maintenance": {
        "code": "MAINTENANCE_CHARGE_BASIS",
        "parameter": "maintenance_charge_basis",
        "default": "flat_area"
    },

    "interest": {
        "code": "LATE_PAYMENT_INTEREST",
        "parameter": "late_payment_interest_percent",
        "default": 18
    },

    "non-occupancy": {
        "code": "NON_OCCUPANCY_CHARGE",
        "parameter": "non_occupancy_charge_percent",
        "default": 10
    },

    "committee": {
        "code": "COMMITTEE_SIZE",
        "parameter": "committee_size",
        "default": 11
    },

    "election": {
        "code": "COMMITTEE_TERM",
        "parameter": "committee_term_years",
        "default": 5
    },

    "audit": {
        "code": "AUDIT_FREQUENCY",
        "parameter": "audit_frequency_years",
        "default": 1
    },

    "redevelopment": {
        "code": "REDEVELOPMENT_CONSENT",
        "parameter": "redevelopment_consent_percent",
        "default": 75
    },

}

class BylawInterpreter:

    @staticmethod
    def scan_clauses():

        clauses = BylawClause.objects.all()

        discovered_hooks = []

        for clause in clauses:

            text = f"{clause.title} {clause.legal_text}".lower()

            for keyword, hook in HOOK_PATTERNS.items():

                if keyword in text:

                    discovered_hooks.append({
                        "hook_code": hook["code"],
                        "parameter": hook["parameter"],
                        "default_value": hook["default"],
                        "clause": clause.title,
                    })

        return discovered_hooks

from society.models import GovernanceRule


def seed_rules():

    hooks = BylawInterpreter.scan_clauses()

    for h in hooks:

        GovernanceRule.objects.get_or_create(

            code=h["hook_code"],

            defaults={
                "description": h["parameter"],
                "parameter_key": h["parameter"],
                "default_value": h["default_value"],
            }
        )

