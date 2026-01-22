class CommunicationEngine:
    def send_message(self, context):
        pass
from communications.domain.entities.message import CommunicationMessage
from communications.domain.entities.thread import CommunicationThread
from communications.domain.entities.participant import CommunicationParticipant


class CommunicationEngine:
    def send_message(self, payload):

        sender = payload["sender"]
        content = payload["content"]
        context = payload["context"]

        # Expect context to include thread
        thread = payload.get("thread")

        if not thread:
            raise Exception("Thread context missing")

        message = CommunicationMessage.objects.create(
            thread=thread,
            sender=sender,
            content=content,
            governance_decision="allow"
        )

        return message
