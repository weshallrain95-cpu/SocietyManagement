from society.models import NotificationEvent


class CommunicationsEngine:

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

        flat = event.flat
        member = flat.primary_member

        email = member.email
        phone = member.phone

        payload = event.payload

        send_email(
            to=email,
            subject="Maintenance Bill Generated",
            message=f"Your maintenance bill for {payload['billing_month']} is {payload['amount']}",
        )

        send_sms(
            to=phone,
            message=f"Maintenance bill ₹{payload['amount']} generated.",
        )


    def send_receipt_notification(self, event):

        payload = event.payload

        send_email(
            to=payload.get("email"),
            subject="Payment Receipt",
            message=f"Payment of ₹{payload.get('amount')} received.",
        )


    def send_notice_notification(self, event):

        payload = event.payload

        send_email(
            to=payload.get("email"),
            subject="Society Notice",
            message=payload.get("message"),
        )
        