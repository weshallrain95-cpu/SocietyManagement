import os

from django.conf import settings

from reportlab.platypus import (
    SimpleDocTemplate,
)

from reportlab.lib.units import mm

from society.finance.maintenance.maintenance_bill_context import (
    build_maintenance_bill_payload,
)

from statutory.document_engine.templates.maintenance_bill_template_v2 import (
    render_maintenance_bill_story,
)


def generate_flat_bill_pdf(flat_bill):

    society = flat_bill.bill.society
    flat = flat_bill.flat
    month = flat_bill.bill.billing_month

    folder = os.path.join(
        settings.MEDIA_ROOT,
        "maintenance_bills",
    )

    os.makedirs(
        folder,
        exist_ok=True,
    )

    filename = (
        f"{society.id}_{flat.id}_{month}.pdf"
    )

    filepath = os.path.join(
        folder,
        filename,
    )

    payload = (
        build_maintenance_bill_payload(
            flat_bill
        )
    )

    document = SimpleDocTemplate(
        filepath,

        leftMargin=8 * mm,
        rightMargin=8 * mm,

        topMargin=8 * mm,
        bottomMargin=8 * mm,
    )

    story = (
        render_maintenance_bill_story(
            payload
        )
    )

    document.build(
        story
    )

    return filepath