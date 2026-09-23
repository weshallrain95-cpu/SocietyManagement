from urllib.parse import parse_qs

from channels.db import database_sync_to_async


class JwtQueryAuthMiddleware:
    """WebSocket auth: ?token=<access JWT>. Browsers cannot set headers on WebSocket upgrades."""

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        token = (parse_qs(scope.get("query_string", b"").decode()).get("token") or [None])[0]
        scope["ob_user"], scope["ob_claims"] = await self._resolve(token)
        return await self.inner(scope, receive, send)

    @database_sync_to_async
    def _resolve(self, token):
        if not token:
            return None, {}
        from rest_framework_simplejwt.exceptions import TokenError
        from rest_framework_simplejwt.tokens import AccessToken

        from apps.identity.models import User
        from apps.orgs.models import Membership

        try:
            claims = AccessToken(token)
        except TokenError:
            return None, {}
        user = User.objects.filter(pk=claims["user_id"], status="active").first()
        org = claims.get("org")
        if user and org and not Membership.objects.filter(user=user, org_id=org, active=True).exists():
            org = None
        return user, {"org": org, "role": claims.get("role")}
