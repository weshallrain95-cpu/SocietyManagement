from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class LiveConsumer(AsyncJsonWebsocketConsumer):
    """One socket per app session. Groups: user.<id>, broker.<org> and visit_plan.<id> on request.

    Client messages: {"type": "heartbeat"} | {"type": "offline"} | {"type": "watch_plan", "plan_id": ...}
    Server messages: {"event": "enquiry.new" | "proposal.new" | "visit_plan.updated" | ..., "data": {...}}
    """

    async def connect(self):
        self.user = self.scope.get("ob_user")
        if not self.user:
            await self.close(code=4401)
            return
        self.org = self.scope["ob_claims"].get("org")
        self.groups_joined = [f"user.{self.user.pk}"] + ([f"broker.{self.org}"] if self.org else [])
        for g in self.groups_joined:
            await self.channel_layer.group_add(g, self.channel_name)
        await self.accept()
        if self.org:
            await self._heartbeat()

    async def disconnect(self, code):
        for g in getattr(self, "groups_joined", []):
            await self.channel_layer.group_discard(g, self.channel_name)

    async def receive_json(self, content, **kwargs):
        kind = content.get("type")
        if kind == "heartbeat" and self.org:
            await self._heartbeat()
        elif kind == "offline" and self.org:
            await self._offline()
        elif kind == "watch_plan" and self.org:
            plan_id = content.get("plan_id")
            if await self._owns_plan(plan_id):
                g = f"visit_plan.{plan_id}"
                await self.channel_layer.group_add(g, self.channel_name)
                self.groups_joined.append(g)
        await self.send_json({"event": "ack", "data": {"type": kind}})

    async def push(self, message):
        await self.send_json({"event": message["event"], "data": message["data"]})

    @database_sync_to_async
    def _heartbeat(self):
        from .presence import heartbeat

        heartbeat(self.org, self.user.pk)

    @database_sync_to_async
    def _offline(self):
        from .presence import go_offline

        go_offline(self.org, self.user.pk)

    @database_sync_to_async
    def _owns_plan(self, plan_id):
        from apps.visits.models import VisitPlan
        from common import rls

        try:
            with rls.org_context(self.org):
                return VisitPlan.objects.filter(pk=plan_id).exists()
        except Exception:  # noqa: BLE001 - malformed id
            return False
