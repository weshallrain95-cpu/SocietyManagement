from django.urls import path

from . import api, broadcast_api

urlpatterns = [
    path("customers", api.CustomerListCreate.as_view()),
    path("broadcasts", broadcast_api.BroadcastListCreate.as_view()),
    path("broadcasts/preview", broadcast_api.BroadcastPreview.as_view()),
    path("me/updates", broadcast_api.MyUpdates.as_view()),
    path("me/updates/mute", broadcast_api.MuteBroker.as_view()),
    path("customers/<uuid:pk>", api.CustomerDetail.as_view()),
    path("customers/<uuid:pk>/timeline", api.TimelineView.as_view()),
    path("customers/<uuid:pk>/interactions", api.InteractionCreate.as_view()),
    path("customers/<uuid:pk>/consent", api.ConsentView.as_view()),
    path("customers/<uuid:pk>/consent/verify", api.ConsentVerifyView.as_view()),
    path("customers/<uuid:pk>/requirements", api.RequirementCreate.as_view()),
    path("customers/<uuid:pk>/shortlists", api.ShortlistCreate.as_view()),
    path("requirements/<uuid:pk>", api.RequirementDetail.as_view()),
    path("requirements/<uuid:pk>/match", api.MatchView.as_view()),
    path("shortlists/<uuid:pk>/share", api.ShortlistShare.as_view()),
    path("public/shortlists/<str:token>", api.PublicShortlistView.as_view()),
    path("public/shortlists/<str:token>/items/<uuid:item_id>", api.PublicShortlistRespond.as_view()),
    path("public/consent/<str:token>", api.PublicConsentView.as_view()),
]
