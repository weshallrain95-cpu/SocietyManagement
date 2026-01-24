# society/legal/integration/state/services/state_conflict_resolver.py

class StateConflictResolver:
    """
    Resolves conflicting legal states.
    """

    def resolve(self, old_state: dict, new_state: dict) -> dict:
        # Supremacy-based resolution
        old_rank = old_state.get("authority_state", {}).get("supremacy_rank", 999)
        new_rank = new_state.get("authority_state", {}).get("supremacy_rank", 999)

        if new_rank < old_rank:
            return new_state
        if old_rank < new_rank:
            return old_state

        # Canon priority
        if new_state.get("canon_state") and not old_state.get("canon_state"):
            return new_state

        # Audit chronology fallback
        return new_state
