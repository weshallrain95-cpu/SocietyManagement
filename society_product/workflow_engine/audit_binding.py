# Integration point with your AuditHooks / event bus.
from society_product.api.gateway.audit_hooks import AuditHooks

def emit_workflow_event(ctx, event_type: str, details: dict):
    try:
        AuditHooks.after(ctx, f"workflow:{event_type}", details)
    except Exception:
        # don't raise - auditing failures must not stop workflows
        pass
