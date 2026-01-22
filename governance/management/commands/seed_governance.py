# governance/management/commands/seed_governance.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from governance.models import Policy, PolicyRule


class Command(BaseCommand):
    help = "Seed default governance policies"

    def handle(self, *args, **options):
        if Policy.objects.exists():
            self.stdout.write(self.style.WARNING("Policies already exist — skipping seeding"))
            return

        def create_policy(code, name, description, scope="GLOBAL"):
            return Policy.objects.create(
                code=code,
                name=name,
                description=description,
                scope=scope,
                version=1,
                is_active=True,
                effective_from=timezone.now(),
            )

        def add_rule(policy, effect, condition, priority):
            return PolicyRule.objects.create(
                policy=policy,
                effect=effect,
                condition=condition,
                priority=priority,
            )

        # =========================
        # SYSTEM_CORE_PROTECTION
        # =========================
        p = create_policy(
            "SYSTEM_CORE_PROTECTION",
            "System Core Protection",
            "Protect core system execution"
        )
        add_rule(p, "ALLOW", {"actor": "SYSTEM"}, 1)
        add_rule(p, "ALLOW", {"actor": "SERVICE"}, 2)
        add_rule(p, "DENY", {"actor": "USER"}, 3)

        # =========================
        # FINANCE_CRITICAL_GUARDS
        # =========================
        p = create_policy(
            "FINANCE_CRITICAL_GUARDS",
            "Finance Critical Guards",
            "Protect financial operations"
        )
        add_rule(p, "ALLOW", {"action": "DISBURSE", "dual_control": True}, 1)
        add_rule(p, "SOFT_DENY", {"action": "EXPORT", "resource": "LEDGER"}, 2)
        add_rule(p, "DENY", {"action": "DELETE", "resource": "TRANSACTION"}, 3)

        # =========================
        # GOVERNANCE_IMMUTABILITY
        # =========================
        p = create_policy(
            "GOVERNANCE_IMMUTABILITY",
            "Governance Immutability",
            "Protect governance layer"
        )
        add_rule(p, "DENY", {"resource": "AUDIT_EVENT"}, 1)
        add_rule(p, "DENY", {"resource": "POLICY"}, 2)

        # =========================
        # DATA_GUARD
        # =========================
        p = create_policy(
            "DATA_GUARD",
            "Data Guard",
            "Protect sensitive data"
        )
        add_rule(p, "ALLOW", {"action": "EXPORT", "audit_log": True}, 1)
        add_rule(p, "DENY", {"action": "DELETE", "resource": "ARCHIVE"}, 2)
        add_rule(p, "ALLOW", {"actor": "SYSTEM", "action": "BACKUP"}, 3)

        # =========================
        # COMPLIANCE_PROTECTION
        # =========================
        p = create_policy(
            "COMPLIANCE_PROTECTION",
            "Compliance Protection",
            "Protect statutory & compliance data"
        )
        add_rule(p, "DENY", {"resource": "STATUTORY_RECORD"}, 1)
        add_rule(p, "SOFT_DENY", {"resource": "COMPLIANCE_EVENT"}, 2)
        add_rule(p, "ALLOW", {"action": "EXPORT", "audit_log": True}, 3)

        # =========================
        # COMMUNICATION_BASELINE
        # =========================
        p = create_policy(
            "COMMUNICATION_BASELINE",
            "Communication Baseline",
            "Protect communications"
        )
        add_rule(p, "ALLOW", {"action": "DELETE", "owner": True}, 1)
        add_rule(p, "ALLOW", {"role": "SECRETARY", "action": "BROADCAST"}, 2)
        add_rule(p, "ALLOW", {"role": "MODERATOR", "action": "MODERATE"}, 3)

        # =========================
        # OBSERVE_ALL
        # =========================
        p = create_policy(
            "OBSERVE_ALL",
            "Observe All",
            "System-wide observation policy"
        )
        add_rule(p, "OBSERVE", {"__any__": True}, 999)

        self.stdout.write(self.style.SUCCESS("✅ Governance policies seeded successfully"))
