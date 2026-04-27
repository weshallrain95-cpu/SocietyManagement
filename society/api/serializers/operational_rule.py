from rest_framework import serializers
from society.models import OperationalRule


class OperationalRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationalRule
        fields = [
            # SCR18
            "billing_target",
            "vacant_type",
            "vacant_value",
            "dispute_enabled",
            "dispute_hold_bill",
            "dispute_apply_interest",
            "waiver_authority",
            "approval_mode",
            "manager_enabled",

            # SCR19 (ADD THESE)
            "max_spend_without_approval",
            "committee_approval_limit",
            "member_approval_required_above",   # keep for compatibility
            "max_cash_spend_allowed",
            "financial_controls_configured",
        ]