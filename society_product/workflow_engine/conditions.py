# Register condition functions here. Conditions accept (ctx, payload) and return bool.
# Keep them simple and explicit; you can swap this for a dynamic rule engine later.

def always_true(ctx, payload):
    return True

def member_has_email(ctx, payload):
    # Example: payload may contain member_email
    return bool(payload.get("email"))

# registry mapping string keys to functions
CONDITIONS = {
    "always": always_true,
    "member_has_email": member_has_email,
}
