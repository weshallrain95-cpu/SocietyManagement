class ComplaintsEngine:
    @staticmethod
    def report_complaint(ctx, payload):
        return {
            "status": "complaint_reported",
            "issue": payload.get("issue"),
            "society_id": ctx.society_id
        }
