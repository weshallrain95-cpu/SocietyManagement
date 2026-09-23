import pytest
from channels.testing import WebsocketCommunicator

from apps.identity.tokens import issue_tokens
from apps.marketplace import presence
from config.asgi import application

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.asyncio]


async def test_socket_requires_token():
    comm = WebsocketCommunicator(application, "/ws/")
    connected, code = await comm.connect()
    assert not connected


async def test_broker_socket_sets_presence_and_receives_pushes(broker_a):
    from asgiref.sync import sync_to_async
    from channels.layers import get_channel_layer

    org, user = broker_a
    token = (await sync_to_async(issue_tokens)(user, org_id=org.pk, role="broker_principal"))["access"]
    comm = WebsocketCommunicator(application, f"/ws/?token={token}")
    connected, _ = await comm.connect()
    assert connected
    assert await sync_to_async(presence.is_online)(org.pk)
    await get_channel_layer().group_send(f"broker.{org.pk}", {"type": "push", "event": "enquiry.new", "data": {"summary": "2 BHK"}})
    msg = await comm.receive_json_from(timeout=2)
    assert msg == {"event": "enquiry.new", "data": {"summary": "2 BHK"}}
    await comm.send_json_to({"type": "offline"})
    await comm.receive_json_from(timeout=2)
    assert not await sync_to_async(presence.is_online)(org.pk)
    await comm.disconnect()
