from django.utils import timezone
from governance.models import Policy, PolicyRule
from society.audit_emitter import emit_audit_event
from django.db import transaction


class PolicyVersioningService:

    @staticmethod
    @transaction.atomic
    def create_new_version(policy_code: str, name=None, description=None):
        current = (
            Policy.objects
            .filter(code=policy_code, is_active=True)
            .order_by("-version")
            .first()
        )

        if not current:
            raise ValueError(f"No active policy found for {policy_code}")

        # deactivate current
        current.is_active = False
        current.effective_to = timezone.now()
        current.save()

        # create new version
        new_policy = Policy.objects.create(
            code=current.code,
            name=name or current.name,
            description=description or current.description,
            scope=current.scope,
            version=current.version + 1,
            is_active=True,
            effective_from=timezone.now()
        )

        # clone rules
        rules = PolicyRule.objects.filter(policy=current)
        for r in rules:
            PolicyRule.objects.create(
                policy=new_policy,
                effect=r.effect,
                condition=r.condition,
                priority=r.priority
            )

        # audit
        emit_audit_event(
            event_type="POLICY_VERSION_CREATED",
            domain="GOVERNANCE",
            object_type="POLICY",
            object_id=new_policy.code,
            payload={
                "policy_code": policy_code,
                "old_version": current.version,
                "new_version": new_policy.version,
            },
            actor_id="SYSTEM"
        )

        return new_policy

    @staticmethod
    @transaction.atomic
    def rollback(policy_code: str, target_version: int):
        current = Policy.objects.filter(code=policy_code, is_active=True).first()
        target = Policy.objects.filter(code=policy_code, version=target_version).first()

        if not target:
            raise ValueError("Target version not found")

        # deactivate current
        if current:
            current.is_active = False
            current.effective_to = timezone.now()
            current.save()

        # activate target
        target.is_active = True
        target.effective_to = None
        target.save()

        emit_audit_event(
            event_type="POLICY_ROLLBACK",
            domain="GOVERNANCE",
            object_type="POLICY",
            object_id=policy_code,
            payload={
                "from_version": current.version if current else None,
                "to_version": target_version,
            },
            actor_id="SYSTEM"
        )

        return target
