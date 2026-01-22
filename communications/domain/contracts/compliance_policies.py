RETENTION_POLICIES = {
    "complaint": {
        "retain_years": 7,
        "archive": True,
        "legal_hold": True
    },
    "notice": {
        "retain_years": 5,
        "archive": True,
        "legal_hold": False
    },
    "document_request": {
        "retain_years": 8,
        "archive": True,
        "legal_hold": True
    },
    "governance": {
        "retain_years": 10,
        "archive": True,
        "legal_hold": True
    },
    "general": {
        "retain_years": 3,
        "archive": False,
        "legal_hold": False
    }
}

ACCESS_POLICIES = {
    "member": ["complaint", "notice", "general"],
    "committee": ["complaint", "notice", "document_request", "governance", "general"],
    "admin": ["all"],
    "system": ["all"],
}

DATA_LIFECYCLE = {
    "active": "ACTIVE",
    "archived": "ARCHIVED",
    "deleted": "DELETED",
    "legal_hold": "LEGAL_HOLD"
}
