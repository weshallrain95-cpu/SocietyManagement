"""Society de-duplication: candidate generation + scoring (Data Model §5.3-5.4).

Signals that are missing (no coordinates, no pin code, no confirmed alias) are left out of
the weighted average rather than counted as zero, so a clean exact-name match can still auto-match.
Ambiguity is caught by the runner-up gap instead.
"""
from dataclasses import dataclass, field

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Q
from rapidfuzz import fuzz
from rapidfuzz.distance import JaroWinkler

from .models import Locality, Society, SocietyAlias
from .normalise import NormalisedName, normalise_name, skeleton

WEIGHTS = {"name": 0.40, "alias": 0.20, "geo": 0.20, "locality": 0.10, "pincode": 0.10}
GEO_RADIUS_M = 1500
AUTO_THRESHOLD = 0.90
AUTO_GAP = 0.10
CONFIRM_THRESHOLD = 0.60
MIN_NAME_FOR_CONFIRM = 0.75  # never ask a broker to confirm a society whose name barely resembles theirs


@dataclass
class Candidate:
    society: Society
    score: float
    signals: dict = field(default_factory=dict)

    def as_dict(self):
        s = self.society
        return {
            "society_id": str(s.id),
            "name": s.canonical_name,
            "locality": s.locality.name,
            "status": s.status,
            "score": round(self.score, 3),
            "signals": {k: round(v, 3) for k, v in self.signals.items()},
            "location": {"lat": s.location.y, "lng": s.location.x},
        }


@dataclass
class Decision:
    action: str  # auto | confirm | provisional
    candidates: list[Candidate]

    @property
    def best(self):
        return self.candidates[0] if self.candidates else None


def name_similarity(a: NormalisedName, b: NormalisedName) -> float:
    if not a.tokens or not b.tokens:
        return 0.0
    scores = [
        fuzz.token_sort_ratio(a.text, b.text) / 100,
        JaroWinkler.similarity(a.compact, b.compact),
        JaroWinkler.similarity(a.skeleton, b.skeleton),
    ]
    if a.strong and b.strong:
        scores.append(JaroWinkler.similarity(a.strong_compact, b.strong_compact))
    best = max(scores)
    # Two names that share no distinctive word at all ("Sai Heights" vs "Om Heights") are penalised.
    if a.strong and b.strong and not (set(a.strong) & set(b.strong)) and JaroWinkler.similarity(a.strong_compact, b.strong_compact) < 0.85:
        best *= 0.75
    return best


def find_candidates(raw_name: str, *, point=None, pincode: str = "", locality: Locality | None = None,
                    micro_market=None, include_provisional_for_org=None, limit: int = 5) -> list[Candidate]:
    q = normalise_name(raw_name)
    if not q.tokens:
        return []
    locality_hint = normalise_name(q.locality_hint).text if q.locality_hint else ""

    base = Society.objects.select_related("locality")
    visible = Q(status=Society.Status.ACTIVE)
    if include_provisional_for_org:
        visible |= Q(status=Society.Status.PROVISIONAL, proposed_by_org=include_provisional_for_org)
    base = base.filter(visible)
    if micro_market is not None:
        base = base.filter(locality__micro_market=micro_market)

    ids = set(
        base.annotate(sim=TrigramSimilarity("name_normalised", q.text)).filter(sim__gt=0.2).order_by("-sim").values_list("id", flat=True)[:30]
    )
    alias_hits = (
        SocietyAlias.objects.filter(society__in=base)
        .annotate(sim=TrigramSimilarity("alias_normalised", q.text))
        .filter(sim__gt=0.3)
        .order_by("-sim")
        .values_list("society_id", "alias_normalised")[:30]
    )
    alias_names: dict = {}
    for sid, alias_norm in alias_hits:
        ids.add(sid)
        alias_names.setdefault(sid, []).append(alias_norm)
    if point is not None:
        ids |= set(base.filter(location__dwithin=(point, D(m=GEO_RADIUS_M))).values_list("id", flat=True)[:30])
    # Skeleton match catches transliterations the trigram index misses.
    sk = skeleton(q.strong_compact or q.compact)
    if len(sk) >= 5:
        ids |= set(base.filter(name_normalised__istartswith=q.tokens[0][:3]).values_list("id", flat=True)[:50])

    qs = base.filter(id__in=ids)
    if point is not None:
        qs = qs.annotate(dist=Distance("location", point))
    hint_locality_ids = set()
    if locality is None and locality_hint:
        hint_locality_ids = set(Locality.objects.filter(name_normalised=locality_hint).values_list("id", flat=True))
    out = []
    for s in qs:
        cand_name = normalise_name(s.canonical_name)
        # The name signal is the best match against the canonical name or any learned alias.
        name_sim = name_similarity(q, cand_name)
        alias_sim = max((name_similarity(q, normalise_name(a)) for a in alias_names.get(s.id, [])), default=0.0)
        sig = {"name": max(name_sim, alias_sim)}
        if alias_sim >= 0.95:
            sig["alias"] = 1.0  # a spelling a human has confirmed before; only counted when present
        if point is not None:
            sig["geo"] = max(0.0, 1 - s.dist.m / GEO_RADIUS_M)
        if pincode:
            sig["pincode"] = 1.0 if s.pincode == pincode else 0.0
        if locality is not None:
            sig["locality"] = 1.0 if s.locality_id == locality.id else 0.0
        elif hint_locality_ids:  # only a hint that names a real locality counts ("thane" is a city, not a locality)
            sig["locality"] = 1.0 if s.locality_id in hint_locality_ids else 0.0
        weight = sum(WEIGHTS[k] for k in sig)
        score = sum(WEIGHTS[k] * v for k, v in sig.items()) / weight
        # Name is the anchor: a strong geo/locality match cannot rescue a different name.
        score = min(score, sig["name"] + 0.15)
        out.append(Candidate(s, score, sig))
    out.sort(key=lambda c: c.score, reverse=True)
    return out[:limit]


def decide(candidates: list[Candidate]) -> Decision:
    if not candidates:
        return Decision("provisional", [])
    best = candidates[0].score
    runner = candidates[1].score if len(candidates) > 1 else 0.0
    if best >= AUTO_THRESHOLD and best - runner >= AUTO_GAP:
        return Decision("auto", candidates)
    if best >= CONFIRM_THRESHOLD and candidates[0].signals.get("name", 0) >= MIN_NAME_FOR_CONFIRM:
        return Decision("confirm", candidates)
    return Decision("provisional", candidates)


def learn_alias(society: Society, raw: str, source: str, org=None) -> None:
    """Every confirmation teaches the registry a spelling (MD-03)."""
    norm = normalise_name(raw).text
    if not norm or norm == society.name_normalised:
        return
    alias, created = SocietyAlias.objects.get_or_create(
        society=society, alias_normalised=norm, defaults={"alias_raw": raw, "source": source, "created_by_org": org}
    )
    if not created:
        SocietyAlias.objects.filter(pk=alias.pk).update(confirmations=alias.confirmations + 1)
