from society.models import (
    NotificationEvent,
    FlatOwnership,
    FlatOwner,
)

from society_product.channels.email_channel import (
    EmailChannel,
)

from society_product.channels.sms_channel import (
    SMSChannel,
)

from society_product.channels.whatsapp_channel import (
    WhatsAppChannel,
)

from society_product.channels.maintenance_bill_context import (
    build_maintenance_bill_context,
)

class CommunicationsEngine:

    def resolve_recipient(self, event):

        return resolve_person_for_flat(
            event.flat
        )

    def process_queue(self, limit=50):

        events = (
            NotificationEvent.objects
            .filter(status="PENDING")
            .order_by("created_at")[:limit]
        )

        processed = 0

        for event in events:

            try:
                self.route_event(event)

                event.status = "DELIVERED"
                event.save(update_fields=["status"])

                processed += 1

            except Exception:

                event.status = "FAILED"
                event.save(update_fields=["status"])

        return processed


    def route_event(self, event):

        if event.event_type == "MAINTENANCE_BILL":
            self.send_bill_notification(event)

        elif event.event_type == "PAYMENT_RECEIPT":
            self.send_receipt_notification(event)

        elif event.event_type == "NOTICE":
            self.send_notice_notification(event)


    def send_bill_notification(self, event):

        ctx = build_maintenance_bill_context(
            event
        )

        person = ctx["person"]

        if not person:
            raise ValueError(
                f"No active recipient for flat {event.flat_id}"
            )

        email = ctx["email"]

        phone = ctx["phone"]

        billing_payload = (
            ctx["billing_payload"]
        )

        member_name = (
            billing_payload["member"]["member_name"]
        )

        billing_month = (
            billing_payload["bill"]["billing_month_label"]
        )

        due_date = (
            billing_payload["bill"]["due_date"]
        )

        net_payable = (
            billing_payload["account_position"]["net_payable"]
        )

        EmailChannel.send(
            to=email,
            subject=(
                f"Maintenance Bill - "
                f"{billing_month}"
            ),
            message=(
                f"Dear {member_name},\n\n"
                f"Your maintenance bill for "
                f"{billing_month} has been generated.\n\n"
                f"Total Payable: ₹{net_payable}\n"
                f"Due Date: {due_date}"
            ),
            attachments=[
                ctx["pdf_path"]
            ],
        )

        SMSChannel.send(
            to=phone,
            message=(
                f"Maintenance Bill "
                f"₹{net_payable} "
                f"Due {due_date}"
            ),
        )

        WhatsAppChannel.send(
            to=phone,

            message=(
                f"Hello {member_name}\n\n"
                f"Maintenance Bill Generated\n\n"
                f"Month: {billing_month}\n"
                f"Amount: ₹{net_payable}\n"
                f"Due Date: {due_date}"
            ),

            attachment=ctx["pdf_path"],
        )


    def send_receipt_notification(self, event):

        payload = event.payload

        EmailChannel.send(
            to=payload.get("email"),
            subject="Payment Receipt",
            message=(
                f"Payment of ₹{payload.get('amount')} "
                f"received."
            ),
        )


    def send_notice_notification(self, event):

        payload = event.payload

        EmailChannel.send(
            to=payload.get("email"),
            subject="Society Notice",
            message=payload.get("message"),
        )
        