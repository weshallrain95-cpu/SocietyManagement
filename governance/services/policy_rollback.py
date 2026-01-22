# governance/services/policy_rollback.py

from django.db import transaction
from django.utils import timezone
from governance.models import Policy
from society.audit_emitter import emit_audit_event


class PolicyRollbackError(Exception):
    pass


class PolicyRollbackService:

    @staticmethod
    @transaction.atomic
    def rollback_to_version(code: str, target_version: int, actor="SYSTEM"):
        policies = Policy.objects.filter(code=code).order_by("-version")

        if not policies.exists():
            raise PolicyRollbackError(f"No policy found for code={code}")

        target = policies.filter(version=target_version).first()
        if not target:
            raise PolicyRollbackError(
                f"Target version {target_version} not found for policy {code}"
            )

        # Deactivate all
        policies.update(is_active=False, effective_to=timezone.now())

        # Activate target
        target.is_active = True
        target.effective_to = None
        target.save()

        # Audit log
        emit_audit_event(
            event_type="POLICY_ROLLBACK",
            domain="GOVERNANCE",
            object_type="POLICY",
            object_id=str(target.id),
            payload={
                "policy_code": code,
                "rollback_type": "VERSION",
                "target_version": target_version,
                "activated_version": target.version,
                "timestamp": timezone.now().isoformat()
            },
            actor_id=str(actor)
        )

        return target

    @staticmethod
    @transaction.atomic
    def rollback_to_timestamp(code: str, timestamp, actor="SYSTEM"):
        policies = Policy.objects.filter(
            code=code,
            created_at__lte=timestamp
        ).order_by("-created_at")

        if not policies.exists():
            raise PolicyRollbackError(
                f"No policy versions exist before {timestamp} for {code}"
            )

        target = policies.first()

        # Deactivate all
        Policy.objects.filter(code=code).update(is_active=False, effective_to=timezone.now())

        # Activate target
        target.is_active = True
        target.effective_to = None
        target.save()

        # Audit log
        emit_audit_event(
            event_type="POLICY_ROLLBACK",
            domain="GOVERNANCE",
            object_type="POLICY",
            object_id=str(target.id),
            payload={
                "policy_code": code,
                "rollback_type": "TIMESTAMP",
                "target_timestamp": str(timestamp),
                "activated_version": target.version,
                "timestamp": timezone.now().isoformat()
            },
            actor_id=str(actor)
        )

        return target
