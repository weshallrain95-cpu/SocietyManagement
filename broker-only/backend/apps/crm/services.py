"""Customer book services, including offline customers who never install the app (OFF-01..14)."""
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.identity import otp
from common import crypto, rls
from common.links import create_link, resolve_link
from common.models import ShareLink
from common.notify import send_message

from .models import Customer, CustomerInteraction, Requirement, Shortlist, ShortlistItem


class CrmError(Exception):
    pass


def log(customer: Customer, kind: str, summary: str = "", *, user=None, ref=None, duration_s=None, at=None):
    return CustomerInteraction.objects.create(
        org_id=customer.org_id,
        customer=customer,
        kind=kind,
        summary=summary[:500],
        by_user=user,
        occurred_at=at or timezone.now(),
        duration_s=duration_s,
        ref_type=ref._meta.label_lower if ref is not None else "",
        ref_id=ref.pk if ref is not None else None,
    )


@transaction.atomic
def capture_customer(*, org, user, phone: str, name: str = "", source: str = Customer.Source.WALK_IN,
                     notes: str = "") -> tuple[Customer, bool]:
    """OFF-01 / CRM-05: one record per phone number per broker; repeat capture returns the same customer."""
    e164 = crypto.normalise_phone(phone)
    ph = crypto.phone_hash(e164)
    existing = Customer.objects.filter(org=org, phone_hash=ph).first()
    if existing:
        if name and not existing.name:
            existing.name = name
            existing.save(update_fields=["name"])
        return existing, False
    c = Customer.objects.create(
        org=org, phone_hash=ph, phone_enc=crypto.encrypt(e164), name=name, source=source, notes=notes, created_by=user
    )
    from apps.identity.models import User

    pu = User.objects.filter(phone_hash=ph).first()
    if pu:
        c.platform_user = pu
        c.save(update_fields=["platform_user"])
    log(c, CustomerInteraction.Kind.SYSTEM, f"Customer added ({c.get_source_display()})", user=user)
    return c, True


def request_consent(customer: Customer, *, method: str, user, note: str = "") -> dict:
    """OFF-02: consent without the app. Only name, number and requirement are kept until it is confirmed."""
    if method == "otp":
        code = otp.request_otp(customer.phone)
        log(customer, CustomerInteraction.Kind.SYSTEM, "Consent OTP sent", user=user)
        return {"sent": "otp", **({"dev_code": code} if code else {})}
    if method in ("link", "attested"):
        link, token = create_link(ShareLink.Purpose.CONSENT, customer, hours=24 * 7, recipient_phone_hash=customer.phone_hash)
        send_message(
            customer.phone,
            "consent_request",
            {"broker": customer_org_name(customer), "url": f"{settings.OB_PUBLIC_BASE_URL}/consent/{token}"},
            phone_hash=customer.phone_hash,
        )
        if method == "attested":
            customer.consent_state = Customer.Consent.ATTESTED_VERBAL
            customer.consent_evidence = {"attested_by": str(user.pk), "at": timezone.now().isoformat(), "note": note[:200]}
            customer.save(update_fields=["consent_state", "consent_evidence"])
        log(customer, CustomerInteraction.Kind.SYSTEM, f"Consent requested ({method})", user=user)
        return {"sent": "link", "token": token}
    raise CrmError("method must be otp, link or attested")


def confirm_consent_otp(customer: Customer, code: str, *, user) -> Customer:
    try:
        otp.verify_otp(customer.phone, code)
    except otp.OtpError as e:
        raise CrmError(str(e)) from e
    customer.consent_state = Customer.Consent.OTP_CONFIRMED
    customer.consent_evidence = {"method": "otp", "at": timezone.now().isoformat(), "by": str(user.pk)}
    customer.save(update_fields=["consent_state", "consent_evidence"])
    log(customer, CustomerInteraction.Kind.SYSTEM, "Consent confirmed by OTP", user=user)
    return customer


def confirm_consent_link(token: str, *, agree: bool) -> Customer:
    link = resolve_link(token, ShareLink.Purpose.CONSENT, consume=True)
    with rls.platform_context():
        customer = Customer.objects.get(pk=link.target_id)
        customer.consent_state = Customer.Consent.LINK_CONFIRMED if agree else Customer.Consent.WITHDRAWN
        customer.consent_evidence = {"method": "link", "at": timezone.now().isoformat(), "agree": agree}
        customer.save(update_fields=["consent_state", "consent_evidence"])
        log(customer, CustomerInteraction.Kind.LINK_OPENED, "Consent " + ("given" if agree else "declined") + " via link")
    return customer


def customer_org_name(customer) -> str:
    from apps.orgs.models import BrokerOrg

    return BrokerOrg.objects.filter(pk=customer.org_id).values_list("name", flat=True).first() or ""


def ensure_can_message(customer: Customer) -> None:
    if not customer.can_message:
        raise CrmError("The customer has not given consent yet. Send a consent request first.")


def link_platform_user(user) -> int:
    """OFF-09: an offline customer who installs the app sees their own shared records with each broker."""
    with rls.platform_context():
        return Customer.objects.filter(phone_hash=user.phone_hash, platform_user__isnull=True).update(platform_user=user)


def add_requirement(customer: Customer, data: dict, *, localities=()) -> Requirement:
    req = Requirement.objects.create(org_id=customer.org_id, customer=customer, **data)
    if localities:
        req.localities.set(localities)
    log(customer, CustomerInteraction.Kind.NOTE, f"Requirement: {describe(req)}", ref=req)
    return req


def update_requirement(req: Requirement, data: dict) -> Requirement:
    """MATCH-05: every change bumps the version so a mid-tour change is traceable."""
    for k, v in data.items():
        setattr(req, k, v)
    req.version += 1
    req.save()
    log(req.customer, CustomerInteraction.Kind.NOTE, f"Requirement updated (v{req.version}): {describe(req)}", ref=req)
    return req


def describe(req) -> str:
    noun = "rent" if req.txn_type == "RENT" else "purchase"
    bhk = f"{req.bhk_min:g}" if req.bhk_min == req.bhk_max else f"{req.bhk_min:g}-{req.bhk_max:g}"
    budget = f"₹{req.budget_max:,}" + ("/month" if req.txn_type == "RENT" else "")
    parts = [f"{bhk} BHK for {noun}", f"up to {budget}"]
    if req.must_haves:
        parts.append("must have: " + ", ".join(k.replace("_", " ") for k in req.must_haves))
    if req.house_rule_needs:
        parts.append("needs: " + ", ".join(k.replace("_", " ") for k in req.house_rule_needs))
    return "; ".join(parts)


@transaction.atomic
def create_shortlist(customer: Customer, listings, *, requirement=None, title="") -> Shortlist:
    sl = Shortlist.objects.create(org_id=customer.org_id, customer=customer, requirement=requirement, title=title)
    for i, listing in enumerate(listings):
        if listing.org_id != customer.org_id:
            raise CrmError("A shortlist can only contain your own listings")
        ShortlistItem.objects.create(org_id=customer.org_id, shortlist=sl, listing=listing, position=i)
    return sl


def share_shortlist(sl: Shortlist, *, user) -> str:
    """OFF-03: WhatsApp/SMS link to a light web page; responses flow back into the CRM."""
    ensure_can_message(sl.customer)
    link, token = create_link(ShareLink.Purpose.SHORTLIST, sl, hours=24 * 14, max_uses=10_000,
                              recipient_phone_hash=sl.customer.phone_hash)
    url = f"{settings.OB_PUBLIC_BASE_URL}/s/{token}"
    send_message(sl.customer.phone, "shortlist_shared", {"broker": customer_org_name(sl.customer), "count": sl.items.count(), "url": url},
                 phone_hash=sl.customer.phone_hash)
    sl.shared_at = timezone.now()
    sl.save(update_fields=["shared_at"])
    log(sl.customer, CustomerInteraction.Kind.WHATSAPP, f"Shortlist of {sl.items.count()} flats shared", user=user, ref=sl)
    return token


def respond_to_shortlist_item(token: str, item_id, response: str) -> ShortlistItem:
    link = resolve_link(token, ShareLink.Purpose.SHORTLIST, consume=False)
    if response not in ShortlistItem.Response.values:
        raise CrmError("Invalid response")
    with rls.platform_context():
        item = ShortlistItem.objects.select_related("shortlist__customer").get(pk=item_id, shortlist_id=link.target_id)
        item.customer_response = response
        item.responded_at = timezone.now()
        item.save(update_fields=["customer_response", "responded_at"])
        log(item.shortlist.customer, CustomerInteraction.Kind.SHORTLIST_RESPONSE, f"{response.replace('_', ' ')}: listing {item.listing_id}")
    return item
