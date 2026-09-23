"""One unit, one truth: resolve competing observations into a single value (Data Model §6)."""

import math
from collections import defaultdict
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from common.hashchain import canonical

from .models import AttributeDef, AttributeObservation, ResolvedAttribute, Unit

SOURCE_WEIGHT = {
    "computed": 10.0,
    "owner_verified": 8.0,
    "admin": 6.0,
    "owner_via_broker": 4.0,
    "visit_feedback": 3.0,
    "broker": 2.0,
    "upload": 1.5,
    "customer": 1.0,
}
HALF_LIFE_DAYS = {"house_rule": 30, "default": 180}
DISPUTE_RATIO = 0.40
# Resolved values mirrored onto Unit columns for fast SQL filtering.
UNIT_MIRROR = {"bhk": "bhk", "carpet_area_sqft": "carpet_sqft", "property_type": "property_type", "floor_no": "floor"}


def _category_kind(attr: AttributeDef) -> str:
    return "house_rule" if "house rule" in attr.category.lower() else "default"


def _reliability(obs: AttributeObservation) -> float:
    if obs.source_type in ("broker", "upload", "owner_via_broker") and obs.source_org_id:
        acc = float(obs.source_org.listing_accuracy)
        return max(0.5, min(1.2, 0.5 + acc * 0.7))
    return 1.0


def observation_weight(obs: AttributeObservation, attr: AttributeDef, now=None) -> float:
    now = now or timezone.now()
    age_days = max(0.0, (now - obs.observed_at).total_seconds() / 86400)
    half = HALF_LIFE_DAYS[_category_kind(attr)]
    decay = 1.0 if obs.source_type == "computed" else math.pow(0.5, age_days / half)
    return SOURCE_WEIGHT.get(obs.source_type, 1.0) * _reliability(obs) * decay * float(obs.confidence)


def resolve(subject_type: str, subject_id, attr: AttributeDef) -> ResolvedAttribute | None:
    observations = list(
        AttributeObservation.objects.filter(subject_type=subject_type, subject_id=subject_id, attr=attr)
        .select_related("source_org")
        .order_by("observed_at")
    )
    if not observations:
        ResolvedAttribute.objects.filter(subject_type=subject_type, subject_id=subject_id, attr=attr).delete()
        return None

    # Authority short-circuits: computed facts and a verified owner always win for their attributes.
    authoritative = {"computed": ("computed",), "owner": ("owner_verified",), "admin": ("admin",)}.get(attr.authority, ())
    auth_obs = [o for o in observations if o.source_type in authoritative]
    if auth_obs:
        latest = auth_obs[-1]
        return _store(subject_type, subject_id, attr, latest.value, latest.source_type, support=1, disputed=False)

    now = timezone.now()
    totals: dict[str, float] = defaultdict(float)
    actors: dict[str, set] = defaultdict(set)
    values: dict[str, object] = {}
    best_source: dict[str, tuple[float, str]] = {}
    # Only each actor's latest report counts (a broker changing their mind is not two votes).
    latest_by_actor = {}
    for o in observations:
        latest_by_actor[(o.source_type, o.source_org_id, o.source_user_id)] = o
    for o in latest_by_actor.values():
        key = canonical({"v": o.value})
        w = observation_weight(o, attr, now)
        totals[key] += w
        actors[key].add((o.source_org_id, o.source_user_id))
        values[key] = o.value
        if w > best_source.get(key, (0, ""))[0]:
            best_source[key] = (w, o.source_type)
    ranked = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
    win_key, win_w = ranked[0]
    disputed = False
    if len(ranked) > 1:
        run_key, run_w = ranked[1]
        disputed = run_w >= DISPUTE_RATIO * win_w and len(actors[run_key]) >= 2
    return _store(subject_type, subject_id, attr, values[win_key], best_source[win_key][1], support=len(actors[win_key]), disputed=disputed)


def _store(subject_type, subject_id, attr, value, source, *, support, disputed) -> ResolvedAttribute:
    ra, _ = ResolvedAttribute.objects.update_or_create(
        subject_type=subject_type,
        subject_id=subject_id,
        attr=attr,
        defaults={"value": value, "resolved_source_type": source, "support": support, "disputed": disputed},
    )
    if subject_type == "unit" and attr.key in UNIT_MIRROR:
        col = UNIT_MIRROR[attr.key]
        v = value
        if col in ("bhk", "carpet_sqft") and v is not None:
            v = Decimal(str(v))
        Unit.objects.filter(pk=subject_id).update(**{col: v})
    return ra


def record(
    subject, attr_key: str, value, *, source_type: str, user=None, org=None, confidence=1.0, observed_at=None, resolve_now: bool = True
) -> AttributeObservation | None:
    """Add an observation (validated against the dictionary) and re-resolve."""
    attr = AttributeDef.objects.filter(key=attr_key, active=True).first()
    if attr is None:
        return None
    value = validate_value(attr, value)
    subject_type = {"unit": "unit", "building": "building", "society": "society"}[subject._meta.model_name]
    if attr.scope != subject_type and attr.scope != "listing":
        # A building-level fact reported against a unit is stored on the building.
        subject = _lift_scope(subject, attr.scope)
        subject_type = attr.scope
    with transaction.atomic():
        obs = AttributeObservation.objects.create(
            subject_type=subject_type,
            subject_id=subject.pk,
            attr=attr,
            value=value,
            source_type=source_type,
            source_user=user,
            source_org=org,
            confidence=confidence,
            observed_at=observed_at or timezone.now(),
        )
        if resolve_now:
            resolve(subject_type, subject.pk, attr)
    return obs


def _lift_scope(subject, scope):
    if scope == "building" and subject._meta.model_name == "unit":
        return subject.building
    if scope == "society":
        if subject._meta.model_name == "unit":
            return subject.building.society
        if subject._meta.model_name == "building":
            return subject.society
    raise ValueError(f"Cannot record a {scope}-level attribute on a {subject._meta.model_name}")


class InvalidValue(ValueError):
    pass


def validate_value(attr: AttributeDef, value):
    t = attr.value_type
    if value is None or value == "":
        raise InvalidValue(f"{attr.key}: empty value")
    if t == "bool":
        if isinstance(value, bool):
            return value
        s = str(value).strip().lower()
        if s in ("y", "yes", "true", "1", "allowed", "available", "ha", "haan"):
            return True
        if s in ("n", "no", "false", "0", "not allowed", "na", "nahi"):
            return False
        raise InvalidValue(f"{attr.key}: expected yes/no, got {value!r}")
    if t in ("int", "numeric", "money"):
        try:
            num = float(str(value).replace(",", "").replace("₹", "").strip())
        except ValueError as e:
            raise InvalidValue(f"{attr.key}: expected a number, got {value!r}") from e
        return int(num) if t in ("int", "money") else num
    if t == "enum":
        return _match_enum(attr, value)
    if t == "multi_enum":
        items = value if isinstance(value, list) else [v for v in str(value).replace(";", ",").split(",") if v.strip()]
        return sorted({_match_enum(attr, v) for v in items})
    return str(value).strip()


# How brokers actually answer yes/no questions about enum attributes.
YES_NO_ALIASES = {
    "pets_allowed": {"yes": "case-by-case", "y": "case-by-case", "allowed": "case-by-case", "no": "no", "n": "no"},
    "society_pet_policy": {"yes": "allowed", "no": "not allowed"},
}
GENERIC_YES = {"yes", "y", "ok", "allowed", "haan", "ha"}
GENERIC_NO = {"no", "n", "not allowed", "nahi", "na"}


def _match_enum(attr, value):
    allowed = attr.allowed_values or []
    s = str(value).strip().lower()
    alias = YES_NO_ALIASES.get(attr.key, {}).get(s)
    if alias in allowed:
        return alias
    if s in GENERIC_YES and "allowed" in allowed:
        return "allowed"
    if s in GENERIC_NO and "not allowed" in allowed:
        return "not allowed"
    for a in allowed:
        if s == str(a).lower():
            return a
    for a in allowed:  # tolerate "semi furnished" vs "semi-furnished"
        if s.replace("-", " ") == str(a).lower().replace("-", " "):
            return a
    if attr.key == "bhk":
        return s
    raise InvalidValue(f"{attr.key}: {value!r} is not one of {allowed}")
