from governance.models import GovernanceControl
from django.db import transaction


class GovernanceControlService:

    @staticmethod
    def get_control():
        obj, _ = GovernanceControl.objects.get_or_create(id=1)
        return obj

    @staticmethod
    @transaction.atomic
    def set_mode(mode: str):
        ctrl = GovernanceControlService.get_control()
        ctrl.enforcement_mode = mode
        ctrl.save()
        return ctrl

    @staticmethod
    def is_strict():
        return GovernanceControlService.get_control().enforcement_mode == "STRICT"

    @staticmethod
    def is_progressive():
        return GovernanceControlService.get_control().enforcement_mode == "PROGRESSIVE"

    @staticmethod
    def is_observe():
        return GovernanceControlService.get_control().enforcement_mode == "OBSERVE_ONLY"
