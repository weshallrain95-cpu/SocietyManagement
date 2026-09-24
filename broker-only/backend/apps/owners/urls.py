from django.urls import path

from . import api

urlpatterns = [
    path("owner/flats", api.OwnerFlats.as_view()),
    path("owner/flats/<uuid:pk>", api.OwnerFlatDetail.as_view()),
    path("owner/flats/<uuid:pk>/terms", api.OwnerTerms.as_view()),
    path("owner/flats/<uuid:pk>/media", api.OwnerMedia.as_view()),
    path("owner/flats/<uuid:pk>/brokers", api.OwnerBrokersNearby.as_view()),
    path("owner/flats/<uuid:pk>/invite", api.OwnerInviteView.as_view()),
    path("owner/flats/<uuid:pk>/brokers/<uuid:org_id>/allowed", api.OwnerAllowBroker.as_view()),
    path("owner/flats/<uuid:pk>/brokers/<uuid:org_id>/review", api.OwnerReviewBroker.as_view()),
    path("owner/media/<uuid:media_id>", api.OwnerMediaDelete.as_view()),
    path("owner-invites", api.BrokerInvites.as_view()),
    path("owner-invites/<uuid:pk>/<slug:action>", api.BrokerInviteAction.as_view()),
]
