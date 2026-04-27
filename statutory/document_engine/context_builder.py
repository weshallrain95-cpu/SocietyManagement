from society.models import FlatOwnership, FlatOwner
from statutory.models import SocietyConsent



def build_derived_context(society):

    # 🔹 PROMOTER TABLE
    ownerships = FlatOwnership.objects.filter(
        flat__society=society,
        is_active=True
    ).select_related("flat")

    promoter_rows = []

    for o in ownerships:
        owners = FlatOwner.objects.filter(
            ownership=o
        ).select_related("person")

        for owner in owners:
            promoter_rows.append({
                "name": owner.person.full_name,
                "flat_number": o.flat.flat_number,
                "share": owner.ownership_percentage,
                "address": society.address,
            })

    # 🔹 COUNTS
    promoter_count = len(promoter_rows)

    # 🔹 CONSENT %
    consent_total = SocietyConsent.objects.filter(
        society=society
    ).count()

    consent_approved = SocietyConsent.objects.filter(
        society=society,
        status="APPROVED"
    ).count()

    consent_percent = (
        (consent_approved / consent_total) * 100
        if consent_total > 0 else 0
    )

    return {
        "promoter_member_table": promoter_rows,
        "promoter_count": promoter_count,
        "consent_percent": consent_percent,
        "members_present": promoter_rows,
    }


def build_template_context(society, ux_payload: dict):

    derived = build_derived_context(society)

    context = {}

    # 🔹 System fields
    context["society_name"] = society.name
    context["society_address"] = society.address

    # 🔹 Derived
    context.update(derived)

    # 🔹 UX payload
    context.update(ux_payload or {})

    # 🔥 FINAL OVERRIDE (authoritative)
    if ux_payload and ux_payload.get("number_of_promoters"):
        context["promoter_count"] = ux_payload["number_of_promoters"]

    return context