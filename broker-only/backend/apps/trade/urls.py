from django.urls import path

from . import api

urlpatterns = [
    path("trade/contacts", api.ContactListCreate.as_view()),
    path("trade/contacts/import", api.ContactImport.as_view()),
    path("trade/contacts/<uuid:pk>", api.ContactDetail.as_view()),
    path("trade/blasts", api.BlastListCreate.as_view()),
    path("trade/blasts/preview", api.BlastPreview.as_view()),
    path("trade/blasts/<uuid:pk>", api.BlastDetail.as_view()),
    path("trade/inbox", api.Inbox.as_view()),
    path("trade/inbox/<uuid:pk>/reply", api.InboxReply.as_view()),
]
