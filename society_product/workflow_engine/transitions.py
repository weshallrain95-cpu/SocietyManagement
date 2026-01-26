# For now transitions are implicit in ProcessGraph edges; this module can grow into condition-based transitions.
def should_execute(node, ctx, payload, conditions_registry):
    """
    Returns True if node should execute, false if should be skipped.
    If node.condition is None -> execute.
    """
    if not node.condition:
        return True
    cond = conditions_registry.get(node.condition)
    if not cond:
        # unknown condition - default to False (safe)
        return False
    try:
        return bool(cond(ctx, payload))
    except Exception:
        return False
