MODERATION_MODES = {
    "OBSERVE": "observe",   # log only
    "ENFORCE": "enforce",   # block / restrict / escalate
}

MODERATION_RULES = {
    # keyword-based examples (placeholder)
    "abuse": {
        "keywords": ["abuse", "threat", "violence"],
        "action": "escalate",
        "severity": "high"
    },
    "spam": {
        "keywords": ["buy now", "free", "click here"],
        "action": "block",
        "severity": "medium"
    },
}

ROLE_MODERATION_AUTHORITY = {
    "admin": ["all"],
    "committee": ["member", "vendor"],
    "system": ["all"],
}
