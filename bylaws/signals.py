from django.db.models.signals import post_save
from django.dispatch import receiver
from bylaws.models import BylawDraft, BylawDecision, DecisionSession
from society.models import Case


@receiver(post_save, sender=BylawDraft)
def seed_decision_sessions(sender, instance, created, **kwargs):
    if not created:
        return

    decisions = BylawDecision.objects.filter(is_active=True)

    for decision in decisions:
        DecisionSession.objects.get_or_create(
            draft=instance,
            decision=decision
        )


@receiver(post_save, sender=Case)
def create_bylaw_draft_for_case(sender, instance, created, **kwargs):
    if created and instance.case_type == "prereg":
        if not hasattr(instance, "bylawdraft"):
            BylawDraft.objects.create(case=instance)
