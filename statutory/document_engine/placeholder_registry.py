PLACEHOLDER_REGISTRY = {

    # 🔹 SYSTEM
    "society_name": lambda s, d, ux: s.name,
    "society_address": lambda s, d, ux: s.address,
    "registration_number": lambda s, d, ux: s.registration_number,
    "registration_date": lambda s, d, ux: s.registration_date,
    "registrar_office": lambda s, d, ux: s.registrar_office,
    "state_code": lambda s, d, ux: s.state_code,

    # 🔹 DERIVED
    "promoter_member_table": lambda s, d, ux: d["promoter_member_table"],
    "promoter_count": lambda s, d, ux: d["promoter_count"],
    "consent_percent": lambda s, d, ux: d["consent_percent"],
    "members_present": lambda s, d, ux: d["members_present"],

    # 🔹 GOVERNANCE
    "share_value": lambda s, d, ux: ux.get("share_value"),

    # 🔹 UX INPUTS
    "chief_promoter_name": lambda s, d, ux: ux.get("chief_promoter_name"),
    "meeting_date": lambda s, d, ux: ux.get("meeting_date"),
    "meeting_place": lambda s, d, ux: ux.get("meeting_place"),
    "bank_name": lambda s, d, ux: ux.get("bank_name"),
    "bank_branch": lambda s, d, ux: ux.get("bank_branch"),

    # 🔹 BUILDER NOTICE (UX INPUTS)
    "notice_date": lambda s, d, ux: ux.get("notice_date"),
    "builder_name": lambda s, d, ux: ux.get("builder_name"),
    "builder_address": lambda s, d, ux: ux.get("builder_address"),
    "rera_number": lambda s, d, ux: ux.get("rera_number"),

    # 🔹 PROJECT CONTEXT (UX PASSED)
    "project_name": lambda s, d, ux: ux.get("project_name"),
    "project_address": lambda s, d, ux: ux.get("project_address"),

}