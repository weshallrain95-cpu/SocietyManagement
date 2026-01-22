from django.db import models
from communications.domain.entities.scope import CommunicationScope
from communications.domain.entities.channel import CommunicationChannel
from communications.domain.entities.context import CommunicationContext
from communications.domain.entities.participant import CommunicationParticipant
from communications.domain.entities.thread import CommunicationThread
from communications.domain.entities.message import CommunicationMessage

__all__ = [
    "CommunicationScope",
    "CommunicationChannel",
    "CommunicationContext",
    "CommunicationParticipant",
    "CommunicationThread",
    "CommunicationMessage",
]

# Create your models here.
