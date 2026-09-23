from django.db import transaction

from .engine import run
from .models import MatchResult, MatchRun


@transaction.atomic
def match_requirement(req, *, include_unconfirmed=True) -> MatchRun:
    results = run(req, org_id=req.org_id, include_unconfirmed=include_unconfirmed, include_excluded=True)
    mr = MatchRun.objects.create(
        org_id=req.org_id,
        requirement=req,
        requirement_version=req.version,
        include_unconfirmed=include_unconfirmed,
        n_considered=len(results),
        n_matched=sum(not r.excluded for r in results),
    )
    MatchResult.objects.bulk_create(
        MatchResult(org_id=req.org_id, run=mr, listing=r.listing, score=r.score, excluded=r.excluded, explanation=r.explanation)
        for r in results
    )
    return mr
