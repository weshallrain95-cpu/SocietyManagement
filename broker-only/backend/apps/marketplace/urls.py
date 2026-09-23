from django.urls import path

from . import api

urlpatterns = [
    path("map/supply", api.MapView.as_view()),
    path("enquiries", api.EnquiryListCreate.as_view()),
    path("enquiries/<uuid:pk>", api.EnquiryDetail.as_view()),
    path("enquiries/<uuid:pk>/close", api.EnquiryClose.as_view()),
    path("enquiries/<uuid:pk>/proposals", api.ProposalCreate.as_view()),
    path("enquiries/<uuid:pk>/report", api.EnquiryReport.as_view()),
    path("proposals/<uuid:pk>/accept", api.ProposalAccept.as_view()),
    path("broker/leads", api.BrokerLeads.as_view()),
    path("presence", api.PresenceView.as_view()),
]
