from django.db import models

from common.models import BaseModel


class MatchRun(BaseModel):
    org = models.ForeignKey("orgs.BrokerOrg", on_delete=models.CASCADE, related_name="+", db_column="broker_org_id")
    requirement = models.ForeignKey("crm.Requirement", on_delete=models.CASCADE, related_name="match_runs")
    requirement_version = models.PositiveIntegerField()
    include_unconfirmed = models.BooleanField(default=True)
    n_considered = models.PositiveIntegerField(default=0)
    n_matched = models.PositiveIntegerField(default=0)


class MatchResult(BaseModel):
    org = models.ForeignKey("orgs.BrokerOrg", on_delete=models.CASCADE, related_name="+", db_column="broker_org_id")
    run = models.ForeignKey(MatchRun, on_delete=models.CASCADE, related_name="results")
    listing = models.ForeignKey("inventory.Listing", on_delete=models.CASCADE, related_name="+")
    score = models.PositiveSmallIntegerField()
    excluded = models.BooleanField(default=False)
    explanation = models.JSONField(default=list)

    class Meta:
        ordering = ["excluded", "-score"]
