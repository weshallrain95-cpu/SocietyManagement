class OperationsEngine:
    @staticmethod
    def create_task(ctx, payload):
        return {
            "status": "task_created",
            "task": payload.get("task"),
            "society_id": ctx.society_id
        }
