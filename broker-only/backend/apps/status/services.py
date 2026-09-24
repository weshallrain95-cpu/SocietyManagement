"""Unit status engine (Data Model §4, PRD STAT-01..08).

Downgrades are cheap, upgrades are expensive:
  * any broker holding a listing can make a unit *less* available at once;
  * making it available again after LET/SOLD/OFF_MARKET needs the verified owner,
    or (with no verified owner on the platform) independent broker consensus.
"""

from datetime import timedelta

from django.conf import settings
from django.db import connection, transaction
from django.utils import timezone

from common.events import emit
from common.hashchain import GENESIS, chain_hash
from common.links import create_link
from common.models import ShareLink
from common.notify import queue_for_admin, send_message

from .models import State, StatusConfirmation, StatusEvent, StatusReport, TxnType, UnitStatus

DOWNGRADES = {State.ON_HOLD, State.LET, State.SOLD, State.OFF_MARKET}
CLOSED = {State.LET, State.SOLD, State.OFF_MARKET}
_LEDGER_LOCK = 815_002


class StatusError(Exception):
    pass


class Actor:
    """Who is making a status claim: broker | owner | owner_via_broker | visit_feedback | system | admin | consensus."""

    def __init__(self, type, org=None, user=None):
        self.type, self.org, self.user = type, org, user

    @classmethod
    def broker(cls, org, user=None):
        return cls("broker", org=org, user=user)

    @classmethod
    def owner(cls, user):
        return cls("owner", user=user)

    @classmethod
    def system(cls):
        return cls("system")


def get_status(unit, txn_type) -> UnitStatus:
    now = timezone.now()
    st, _ = UnitStatus.objects.get_or_create(
        unit=unit, txn_type=txn_type, defaults={"since": now, "last_confirmed_at": now, "source_type": "system"}
    )
    return st


def verified_owner(unit):
    from apps.masterdata.models import OwnershipClaim

    claim = (
        # An owner who registered with proof (declared, D14) counts; a checked owner comes first.
        OwnershipClaim.objects.filter(unit=unit, status__in=[OwnershipClaim.Status.VERIFIED, OwnershipClaim.Status.DECLARED])
        .select_related("user")
        .order_by("-status", "created_at")
        .first()
    )
    return claim.user if claim else None


def _validate(txn_type, state):
    if state == State.LET and txn_type != TxnType.RENT:
        raise StatusError("LET applies to rentals only")
    if state == State.SOLD and txn_type == TxnType.RENT:
        raise StatusError("SOLD applies to sale listings only")


@transaction.atomic
def report(
    unit, txn_type: str, new_state: str, actor: Actor, *, reason: str = "", available_from=None, licence_end_date=None
) -> UnitStatus:
    """Apply a status claim from any actor. Returns the (possibly unchanged) master status."""
    _validate(txn_type, new_state)
    st = UnitStatus.objects.select_for_update().get(pk=get_status(unit, txn_type).pk)
    StatusReport.objects.create(
        unit=unit, txn_type=txn_type, reported_state=new_state, actor_type=actor.type, org=actor.org, user=actor.user
    )
    now = timezone.now()

    if new_state in DOWNGRADES:
        if st.state == new_state:
            _touch(st)
            return st
        extra = {"hold_org": actor.org if new_state == State.ON_HOLD else None}
        if new_state == State.LET:
            extra["licence_end_date"] = licence_end_date
        _transition(st, new_state, actor, reason, confirmed_by_owner=actor.type == "owner", **extra)
        return st

    if new_state != State.AVAILABLE:
        raise StatusError(f"Unsupported target state {new_state}")

    owner = verified_owner(unit)
    if actor.type in ("owner", "admin") or (actor.type == "owner_via_broker" and owner is None):
        _transition(st, State.AVAILABLE, actor, reason, confirmed_by_owner=actor.type == "owner", available_from=available_from)
        if actor.type == "owner":
            _settle_pending_confirmations(unit, txn_type, "yes")
        return st

    if st.state == State.AVAILABLE:
        _touch(st)  # a reconfirmation
        return st

    if st.state == State.ON_HOLD:
        if actor.org is not None and st.hold_org_id == actor.org.pk:
            _transition(st, State.AVAILABLE, actor, reason or "hold released", available_from=available_from)
        # Another broker cannot release someone else's hold; holds expire on their own (decay_stale).
        return st

    previous = st.state
    if st.state != State.AVAILABLE_UNCONFIRMED:
        _transition(st, State.AVAILABLE_UNCONFIRMED, actor, reason, available_from=available_from)
    if owner is not None:
        request_owner_confirmation(unit, txn_type, previous_state=previous, org=actor.org, owner=owner)
    else:
        _apply_consensus(st, now)
    return st


def _apply_consensus(st: UnitStatus, now) -> None:
    rules = settings.OB_STATUS_RULES
    since = now - timedelta(days=rules["consensus_window_days"])
    orgs = (
        StatusReport.objects.filter(
            unit_id=st.unit_id, txn_type=st.txn_type, reported_state=State.AVAILABLE, created_at__gte=since, actor_type="broker"
        )
        .exclude(org__isnull=True)
        .values_list("org_id", flat=True)
        .distinct()
    )
    if len(set(orgs)) >= rules["consensus_brokers"]:
        _transition(st, State.AVAILABLE, Actor("consensus"), "independent broker consensus")


def _touch(st: UnitStatus) -> None:
    st.last_confirmed_at = timezone.now()
    st.save(update_fields=["last_confirmed_at", "updated_at"])


def _transition(st: UnitStatus, to_state: str, actor: Actor, reason: str, *, confirmed_by_owner=False, **fields) -> None:
    from_state = st.state
    now = timezone.now()
    st.state = to_state
    st.since = now
    st.last_confirmed_at = now
    st.source_type = actor.type
    st.confirmed_by_owner = confirmed_by_owner
    for k, v in fields.items():
        if k in ("available_from", "licence_end_date") and v is None and to_state not in (State.LET,):
            continue
        setattr(st, k, v)
    if to_state != State.ON_HOLD:
        st.hold_org = None
    st.version += 1
    st.save()
    _append_ledger(st, from_state, to_state, actor, reason)
    emit(
        "unit_status.changed",
        unit_id=st.unit_id,
        txn_type=st.txn_type,
        from_state=from_state,
        to_state=to_state,
        actor_type=actor.type,
        actor_org_id=getattr(actor.org, "pk", None),
    )


def _append_ledger(st, from_state, to_state, actor, reason) -> StatusEvent:
    with connection.cursor() as cur:
        cur.execute("SELECT pg_advisory_xact_lock(%s)", [_LEDGER_LOCK])
    last = StatusEvent.objects.order_by("-seq").only("hash").first()
    ev = StatusEvent(
        at=timezone.now(),
        unit_id=st.unit_id,
        txn_type=st.txn_type,
        from_state=from_state,
        to_state=to_state,
        actor_type=actor.type,
        actor_org_id=getattr(actor.org, "pk", None),
        actor_user_id=getattr(actor.user, "pk", None),
        reason=reason[:300],
        prev_hash=last.hash if last else GENESIS,
    )
    ev.hash = chain_hash(ev.prev_hash, ev.payload())
    ev.save(force_insert=True)
    return ev


def verify_ledger() -> dict:
    prev = GENESIS
    n = 0
    for ev in StatusEvent.objects.order_by("seq").iterator(chunk_size=2000):
        if ev.prev_hash != prev or chain_hash(prev, ev.payload()) != ev.hash:
            return {"ok": False, "checked": n, "broken_at_seq": ev.seq}
        prev = ev.hash
        n += 1
    return {"ok": True, "checked": n, "head": prev}


def request_owner_confirmation(unit, txn_type, *, previous_state, org, owner) -> StatusConfirmation | None:
    pending = StatusConfirmation.objects.filter(unit=unit, txn_type=txn_type, response="", link__expires_at__gt=timezone.now())
    if pending.exists():
        return None
    conf = StatusConfirmation.objects.create(
        unit=unit, txn_type=txn_type, requested_state=State.AVAILABLE, previous_state=previous_state, requested_by_org=org, owner=owner
    )
    link, token = create_link(ShareLink.Purpose.STATUS_CONFIRMATION, conf, hours=settings.OB_STATUS_RULES["confirmation_ttl_hours"])
    conf.link = link
    conf.save(update_fields=["link"])
    send_message(
        owner.phone,
        "status_confirmation",
        {
            "unit": str(unit),
            "question": "Is your flat available?",
            "url": f"{settings.OB_PUBLIC_BASE_URL}/c/{token}",
        },
        user=owner,
    )
    conf._token = token  # returned to callers/tests only; never stored
    return conf


@transaction.atomic
def owner_responds(conf: StatusConfirmation, response: str, *, available_from=None) -> UnitStatus:
    if conf.response:
        raise StatusError("Already answered")
    conf.response = response
    conf.response_date = available_from
    conf.responded_at = timezone.now()
    conf.save(update_fields=["response", "response_date", "responded_at"])
    owner_actor = Actor.owner(conf.owner)
    st = UnitStatus.objects.select_for_update().get(unit=conf.unit, txn_type=conf.txn_type)
    if response in ("yes", "available_from"):
        _transition(st, State.AVAILABLE, owner_actor, "owner confirmed", confirmed_by_owner=True, available_from=available_from)
    else:
        revert = conf.previous_state if conf.previous_state in CLOSED else State.OFF_MARKET
        _transition(st, revert, owner_actor, "owner denied availability", confirmed_by_owner=True)
        _record_contradiction(conf)
    _settle_pending_confirmations(conf.unit, conf.txn_type, response, exclude=conf.pk)
    return st


def _settle_pending_confirmations(unit, txn_type, response, exclude=None):
    qs = StatusConfirmation.objects.filter(unit=unit, txn_type=txn_type, response="")
    if exclude:
        qs = qs.exclude(pk=exclude)
    qs.update(response=response, responded_at=timezone.now())


def _record_contradiction(conf: StatusConfirmation) -> None:
    """STAT-08: an owner contradicting a broker lowers that broker's listing accuracy; repeats go to admin."""
    org = conf.requested_by_org
    if org is None:
        return
    from apps.orgs.models import BrokerOrg

    BrokerOrg.objects.filter(pk=org.pk).update(listing_accuracy=max(0, float(org.listing_accuracy) - 0.02))
    recent = StatusConfirmation.objects.filter(
        requested_by_org=org, response="no", responded_at__gte=timezone.now() - timedelta(days=30)
    ).count()
    if recent >= 2:
        queue_for_admin("status_conflict", org, f"{org.name}: owners denied availability {recent} times in 30 days")


def decay_stale(now=None) -> int:
    """STAT-06: AVAILABLE without reconfirmation for too long -> AVAILABLE_UNCONFIRMED."""
    now = now or timezone.now()
    n = 0
    hold_days = settings.OB_STATUS_RULES.get("hold_days", 7)
    for st in UnitStatus.objects.filter(state=State.ON_HOLD, since__lt=now - timedelta(days=hold_days)).select_for_update(skip_locked=True):
        _transition(st, State.AVAILABLE_UNCONFIRMED, Actor.system(), f"hold expired after {hold_days} days")
        n += 1
    for txn, days in settings.OB_STATUS_RULES["decay_days"].items():
        stale = UnitStatus.objects.filter(state=State.AVAILABLE, txn_type=txn, last_confirmed_at__lt=now - timedelta(days=days))
        for st in stale.select_for_update(skip_locked=True):
            _transition(st, State.AVAILABLE_UNCONFIRMED, Actor.system(), f"not reconfirmed for {days} days")
            n += 1
    return n
