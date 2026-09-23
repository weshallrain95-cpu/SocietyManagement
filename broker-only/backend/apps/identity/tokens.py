from rest_framework_simplejwt.tokens import RefreshToken


def issue_tokens(user, *, org_id=None, role="customer") -> dict:
    refresh = RefreshToken.for_user(user)
    refresh["role"] = role
    refresh["org"] = str(org_id) if org_id else None
    return {"access": str(refresh.access_token), "refresh": str(refresh), "role": role, "org": refresh["org"]}
