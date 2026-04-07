from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def get_bylaw_schema(request):

    return Response({
        "fields": [

            # ================= FINANCIAL =================
            {
                "key": "share_value",
                "label": "Share Value (₹)",
                "type": "number",
                "default": 50,
                "required": True,
                "legal_reference": "Model Bye-law: Share capital structure"
            },
            {
                "key": "minimum_shares",
                "label": "Minimum Shares per Member",
                "type": "number",
                "default": 10,
                "required": True,
            },
            {
                "key": "entrance_fee",
                "label": "Entrance Fee (₹)",
                "type": "number",
                "default": 100,
                "required": True,
            },

            # ================= MAINTENANCE =================
            {
                "key": "maintenance_basis",
                "label": "Maintenance Charge Basis",
                "type": "select",
                "options": ["flat_area", "equal"],
                "default": "flat_area",
                "required": True,
            },
            {
                "key": "sinking_fund_percent",
                "label": "Sinking Fund (%)",
                "type": "number",
                "default": 0.25,
                "required": True,
            },
            {
                "key": "repair_fund_percent",
                "label": "Repair Fund (%)",
                "type": "number",
                "default": 0.75,
                "required": True,
            },

            # ================= PENALTIES =================
            {
                "key": "late_payment_interest_percent",
                "label": "Late Payment Interest (%)",
                "type": "number",
                "default": 18,
                "required": True,
            },
            
            # ================= NON-OCCUPANCY (FIXED) =================
            {
                "key": "non_occupancy_mode",
                "label": "Non-Occupancy Charge Type",
                "type": "select",
                "options": ["percentage", "fixed_amount"],
                "default": "percentage",
            },
            {
                "key": "non_occupancy_charge_percent",
                "label": "Non-Occupancy Charges (%)",
                "type": "number",
                "default": 10,
            },
            {
                "key": "non_occupancy_charge_fixed",
                "label": "Non-Occupancy Charges (₹)",
                "type": "number",
                "default": 2000,
            },

            # ================= GOVERNANCE =================
            {
                "key": "committee_size",
                "label": "Committee Size",
                "type": "number",
                "default": 3,
                "min": 3,
                "max": 21,
            },
            {
                "key": "committee_term_years",
                "label": "Committee Term (Years)",
                "type": "number",
                "default": 5,
                "required": True,
            },

            # ================= VOTING =================
            {
                "key": "quorum_general_body_percent",
                "label": "General Body Quorum (%)",
                "type": "number",
                "default": 25,
                "required": True,
            },
            {
                "key": "redevelopment_consent_percent",
                "label": "Redevelopment Consent (%)",
                "type": "number",
                "default": 75,
                "required": True,
            },

            
            # ================= GOVERNANCE ADDITIONS =================
            {
                "key": "parking_allocation_method",
                "label": "Parking Allocation Method",
                "type": "select",
                "options": ["first_come", "lottery", "fixed"],
                "default": "lottery",
            },
            {
                "key": "transfer_fee",
                "label": "Transfer Fee (₹)",
                "type": "number",
                "default": 25000,
            },
            {
                "key": "subletting_allowed",
                "label": "Is Subletting Allowed?",
                "type": "select",
                "options": ["yes", "no"],
                "default": "yes",
            },
        ]
    })