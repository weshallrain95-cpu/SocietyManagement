from society.models import (
    FlatMaintenanceBill,
)

from society.finance.maintenance.maintenance_bill_context import (
    build_maintenance_bill_payload,
)

from society_product.channels.recipient_resolver import (
    resolve_person_for_flat,
)

from society.finance.maintenance.bill_generator import (
    generate_flat_bill_pdf,
)


def build_maintenance_bill_context(
    event,
):

    flat_bill = (
        FlatMaintenanceBill.objects
        .select_related(
            "flat",
            "bill",
        )
        .get(
            id=event.reference_id
        )
    )

    person = resolve_person_for_flat(
        flat_bill.flat
    )

    billing_payload = (
        build_maintenance_bill_payload(
            flat_bill
        )
    )

    pdf_path = (
        generate_flat_bill_pdf(
            flat_bill
        )
    )

    return {

        "flat_bill":
            flat_bill,

        "person":
            person,

        "email":

            person.email

            if person
            else None,

        "phone":

            person.phone

            if person
            else None,

        "billing_payload":
            billing_payload,
        
        "pdf_path":
            pdf_path,

            
    }