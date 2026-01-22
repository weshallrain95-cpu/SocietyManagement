ROLE_ROUTING_MATRIX = {
    "admin": ["admin", "committee", "member", "vendor", "system"],
    "committee": ["admin", "member", "vendor", "system"],
    "member": ["committee", "system"],
    "vendor": ["committee", "system"],
    "system": ["admin", "committee", "member", "vendor"],
}
